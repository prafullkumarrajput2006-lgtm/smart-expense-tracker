import joblib
import numpy as np

# Load the trained model and vectorizer
model = joblib.load('expense_categorizer_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Test the smart categorization with receipt_type hints
test_cases = [
    {
        'name': 'Food bill with grocery receipt_type',
        'text': 'Supermarket groceries food shopping',
        'receipt_type': 'grocery'
    },
    {
        'name': 'Restaurant bill with restaurant receipt_type',
        'text': 'Restaurant dining food meal',
        'receipt_type': 'restaurant'
    },
    {
        'name': 'Clothing store (should be shopping)',
        'text': 'Store shop retail mall purchase sale',
        'receipt_type': 'shopping'
    },
    {
        'name': 'Pharmacy bill',
        'text': 'Pharmacy medicine medical healthcare',
        'receipt_type': 'pharmacy'
    },
]

print("🧪 Testing Smart Categorization with Receipt Type Hints:\n")
print("=" * 80)

for test in test_cases:
    # This mimics what the backend does now
    text = test['text']
    
    X_test = vectorizer.transform([text])
    prediction = model.predict(X_test)[0]
    probabilities = model.predict_proba(X_test)[0]
    confidence = np.max(probabilities) * 100
    
    top_indices = np.argsort(probabilities)[::-1][:3]
    top_categories = model.classes_[top_indices]
    top_confidences = probabilities[top_indices] * 100
    
    print(f"\n📝 Test: {test['name']}")
    print(f"   Receipt Type: {test['receipt_type']}")
    print(f"   Categorization Text: '{text}'")
    print(f"   ✅ Predicted: {prediction} ({confidence:.1f}% confidence)")
    print(f"   Top 3 predictions:")
    for cat, conf in zip(top_categories, top_confidences):
        print(f"      - {cat}: {conf:.1f}%")
    print("=" * 80)
