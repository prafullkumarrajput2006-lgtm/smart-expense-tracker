from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import joblib
from ocr import extract_text_from_image, extract_text_and_fields
from models import db, User, Expense, Budget
from budget_routes import register_budget_routes
import jwt
from datetime import datetime, timedelta
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'  # Change this!

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Load the trained ML model and vectorizer
model = joblib.load('expense_categorizer_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Basic route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Smart Expense Tracker API!"})


# Auth decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_email = data['email']
            current_user = User.query.filter_by(email=current_user_email).first()
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Register budget routes
register_budget_routes(app, token_required)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
    
    email = data['email']
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400
    
    # Create new user with hashed password
    user = User(name=data.get('name', ''), email=email)
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully", "user": user.to_dict()}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
    
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = jwt.encode({
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        "token": token,
        "user": user.to_dict()
    })

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({"user": current_user.to_dict()})

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.json or {}
    name = data.get('name')
    # We keep email immutable for simplicity; extend as needed
    if name:
        current_user.name = name
        db.session.commit()
    return jsonify({"message": "Profile updated", "user": current_user.to_dict()})

@app.route('/upload', methods=['POST'])
def upload_receipt():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Extract text + parsed fields using OCR
    try:
        ocr_data = extract_text_and_fields(filepath)
    except Exception:
        # fallback to plain text in case of any unexpected error
        extracted_text = extract_text_from_image(filepath)
        ocr_data = {"text": extracted_text, "fields": {}}
    return jsonify({
        "extracted_text": ocr_data.get("text"),
        "text": ocr_data.get("text"),
        "fields": ocr_data.get("fields", {}),
        "lines": ocr_data.get("lines", []),
    })

@app.route('/categorize', methods=['POST'])
def categorize_expense():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    # Support both 'description' and 'text' fields
    text = data.get('description') or data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Check if receipt_type is provided from OCR
    receipt_type = data.get('receipt_type', '').lower()
    vendor = data.get('vendor', '')
    
    # Smart categorization: Use receipt_type to create better description
    categorization_text = text
    if receipt_type:
        # Map receipt types to category hints
        receipt_to_category_hints = {
            'grocery': 'Supermarket groceries food shopping',
            'restaurant': 'Restaurant dining food meal',
            'fuel': 'Petrol fuel gas station transport',
            'utilities': 'Electricity water gas utility bill payment',
            'pharmacy': 'Pharmacy medicine medical healthcare',
            'transportation': 'Taxi uber ride transport fare',
            'online': 'Online purchase shopping order',
        }
        
        # Use the hint if available, otherwise combine vendor + receipt_type
        if receipt_type in receipt_to_category_hints:
            categorization_text = receipt_to_category_hints[receipt_type]
        elif vendor:
            categorization_text = f"{vendor} {receipt_type}"
    
    # Limit text length to avoid confusion (use first 100 chars or smart text)
    if len(categorization_text) > 200:
        # If it's very long (full receipt text), try to extract vendor/key info
        lines = categorization_text.split('\n')
        # Use first few meaningful lines
        categorization_text = ' '.join(lines[:3])[:100]

    vectorized_desc = vectorizer.transform([categorization_text])
    category = model.predict(vectorized_desc)[0]
    proba = model.predict_proba(vectorized_desc)[0]
    confidence = max(proba)

    return jsonify({
        "category": category, 
        "confidence": float(confidence),
        "categorization_text": categorization_text  # For debugging
    })

@app.route('/add', methods=['POST'])
@token_required
def add_expense(current_user):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    expense = Expense(
        user_id=current_user.id,
        vendor=data.get('vendor', ''),
        date=data.get('date', ''),
        description=data.get('description', ''),
        amount=float(data.get('amount', 0)),
        category=data.get('category', '')
    )
    
    db.session.add(expense)
    db.session.commit()
    
    return jsonify({"message": "Expense added", "expense": expense.to_dict()}), 201

@app.route('/list', methods=['GET'])
@token_required
def list_expenses(current_user):
    # Query expenses for the current user only
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.created_at.desc()).all()
    return jsonify([e.to_dict() for e in expenses])

@app.route('/delete/<int:expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    
    db.session.delete(expense)
    db.session.commit()
    
    return jsonify({"message": "Expense deleted"})

@app.route('/update/<int:expense_id>', methods=['PUT'])
@token_required
def update_expense(current_user, expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    
    data = request.json
    if data.get('vendor'): 
        expense.vendor = data['vendor']
    if data.get('date'): 
        expense.date = data['date']
    if data.get('description'): 
        expense.description = data['description']
    if data.get('amount'): 
        expense.amount = float(data['amount'])
    if data.get('category'): 
        expense.category = data['category']
    
    db.session.commit()
    
    return jsonify({"message": "Expense updated", "expense": expense.to_dict()})

if __name__ == '__main__':
    app.run(debug=True)
