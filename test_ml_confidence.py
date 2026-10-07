import joblib
import numpy as np

# Load the trained model and vectorizer
model = joblib.load('expense_categorizer_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Test cases - typical receipt descriptions
test_descriptions = [
    'Electricity bill payment',
    'Water board charges',
    'Internet broadband bill',
    'Mobile phone recharge',
    'Supermarket groceries',
    'Restaurant dinner',
    'Uber taxi ride',
    'Petrol station fuel',
    'Netflix subscription',
    'Movie tickets',
    'Doctor consultation',
    'Pharmacy medicines',
    'Laptop purchase',
    'Clothes shopping'
]

print("Testing ML Model Confidence Scores:\n")
print("-" * 80)

for desc in test_descriptions:
    # Transform the description
    X_test = vectorizer.transform([desc])
    
    # Get prediction
    prediction = model.predict(X_test)[0]
    
    # Get probability scores for all categories
    probabilities = model.predict_proba(X_test)[0]
    confidence = np.max(probabilities) * 100
    
    # Get top 3 predictions
    top_indices = np.argsort(probabilities)[::-1][:3]
    top_categories = model.classes_[top_indices]
    top_confidences = probabilities[top_indices] * 100
    
    print(f"\n📝 Description: '{desc}'")
    print(f"✅ Predicted: {prediction} (Confidence: {confidence:.1f}%)")
    print(f"   Top 3 predictions:")
    for cat, conf in zip(top_categories, top_confidences):
        print(f"      - {cat}: {conf:.1f}%")
    print("-" * 80)
