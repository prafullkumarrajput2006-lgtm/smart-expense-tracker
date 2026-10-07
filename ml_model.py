import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Enhanced training data with 290+ balanced samples for maximum accuracy
data = {
    'description': [
        # Food - 45 samples (expanded to cover grocery stores and restaurants better)
        'Bought groceries', 'Supermarket shopping', 'Fresh vegetables', 'Meat and fish',
        'Dinner at restaurant', 'Lunch buffet', 'Fast food meal', 'Pizza delivery',
        'Breakfast cafe', 'Coffee shop', 'Bakery items', 'Ice cream', 'Snacks',
        'Food court meal', 'Takeaway food', 'Restaurant bill', 'Grocery store',
        'Fruits and vegetables', 'Dairy products', 'Weekly groceries', 'Food items',
        'Dining out', 'Meal at hotel', 'Catering service', 'Food delivery',
        'Cooking ingredients', 'Spices and condiments', 'Beverage purchase', 'Dessert shop', 'Street food',
        'Chicken biryani', 'Fried rice', 'Kottu roti', 'Dosa and idli', 'Sandwich shop',
        'Cargills food mart', 'Keells super groceries', 'Arpico supermarket food',
        'Organic food store', 'Vegetable market', 'Fish market', 'Butcher shop',
        'Food hall dining', 'Buffet restaurant', 'Cafe meal',
        

        # Transport - 35 samples
        'Uber ride', 'Taxi fare', 'Bus ticket', 'Train ticket', 'Metro card',
        'Petrol station', 'Fuel for car', 'Gas refill', 'Diesel fuel', 'Vehicle fuel',
        'Auto rickshaw', 'Cab service', 'Public transport', 'Railway pass',
        'Airport shuttle', 'Parking fee', 'Toll charges', 'Vehicle maintenance',
        'Car wash', 'Bike repair', 'Transportation cost', 'Commute expense',
        'Bus pass', 'Monthly transport', 'Ride sharing', 'Three wheeler',
        'Long distance bus', 'Express train', 'Flight booking', 'Travel fare',
        'Tuk tuk ride', 'CTB bus', 'Railway season ticket', 'Highway toll', 'Vehicle service',
        
        
        # Bills - 40 samples
        'Electricity bill', 'Water bill', 'Internet bill', 'Mobile bill',
        'Phone recharge', 'Broadband payment', 'Cable TV', 'Utility bill',
        'Monthly rent', 'House rent', 'Apartment rent', 'Rental payment',
        'Gas cylinder', 'LPG refill', 'Electricity payment', 'Water charges',
        'Telephone bill', 'Postpaid bill', 'WiFi subscription', 'DTH recharge',
        'Maintenance charges', 'Society fees', 'Property tax', 'Municipal tax',
        'Sewage charges', 'Common area charges', 'Power bill', 'Energy bill',
        'Landline bill', 'Broadband bill', 'TV subscription', 'Utility payment',
        'Monthly dues', 'Service charges', 'Building maintenance',
        'CEB bill', 'Water board', 'Dialog mobile', 'SLT fiber', 'Apartment maintenance',
        
        # Entertainment - 30 samples
        'Netflix subscription', 'Amazon Prime', 'Spotify premium', 'YouTube premium',
        'Movie tickets', 'Cinema hall', 'Concert tickets', 'Event pass',
        'Gaming subscription', 'PlayStation Plus', 'Xbox Game Pass', 'Steam game',
        'Theme park entry', 'Amusement park', 'Museum ticket', 'Zoo entry',
        'Sports event', 'Cricket match', 'Football game', 'Theater show',
        'Music festival', 'Art exhibition', 'Entertainment cost', 'Hobby class', 'Fun activity',
        'Streaming service', 'Disney Plus', 'HBO Max', 'Video game', 'Recreation expense',
        
        # Shopping - 30 samples (reduced and more specific to non-food items)
        'Clothes shopping', 'New shirt', 'Shoes purchase', 'Dress buying',
        'Online shopping', 'Amazon order', 'Flipkart purchase', 'Electronics store',
        'Mobile phone', 'Laptop purchase', 'Headphones', 'Accessories',
        'Furniture shopping', 'Home decor', 'Kitchenware', 'Appliances',
        'Books and stationery', 'Gift items', 'Cosmetics', 'Personal care products',
        'Jewelry purchase', 'Watch shopping', 'Bag and luggage', 'Sports equipment', 'Toy store',
        'Fashion accessories', 'Gadget purchase', 'Home appliances', 'Office supplies', 'Designer wear',
        
        # Healthcare - 35 samples
        'Doctor consultation', 'Medical checkup', 'Lab tests', 'Blood test',
        'Pharmacy bill', 'Medicine purchase', 'Prescription drugs', 'Health supplements',
        'Hospital bill', 'Clinic visit', 'Dental checkup', 'Eye test',
        'Physiotherapy', 'Medical insurance', 'Health insurance premium', 'Vaccination',
        'X-ray scan', 'CT scan', 'MRI scan', 'Medical procedure',
        'Surgery cost', 'Hospital admission', 'Emergency treatment', 'First aid', 'Healthcare cost',
        'Doctor fees', 'Hospital charges', 'Dental treatment', 'Eye care', 'Health checkup',
        'Medicine from pharmacy', 'Prescription cost', 'Medical test', 'Health screening', 'Clinic fees',
        
        # Education - 25 samples
        'School fees', 'College tuition', 'Course enrollment', 'Online course',
        'Udemy course', 'Coursera subscription', 'Books and notes', 'Study materials',
        'Exam fees', 'Certification cost', 'Workshop registration', 'Seminar fees',
        'Training program', 'Educational expense', 'Learning platform',
        'University fees', 'Academic books', 'Tutorial classes', 'Language course', 'Skill development',
        'Professional training', 'Vocational course', 'Degree program', 'Diploma course', 'Educational materials',
        
        # Other - 25 samples
        'Miscellaneous expense', 'Random purchase', 'Charity donation', 'Gift giving',
        'Pet food', 'Pet grooming', 'Salon visit', 'Haircut',
        'Laundry service', 'Dry cleaning', 'Photography', 'Printing service',
        'Courier charges', 'Postage', 'General expense',
        'Beauty parlor', 'Spa treatment', 'Grooming service', 'Pet supplies',
        'Hobby materials', 'Craft supplies', 'Personal grooming', 'Wellness', 'Self care',
        'Miscellaneous cost'
    ],
    'category': (
        ['Food'] * 45 +
        ['Transport'] * 35 +
        ['Bills'] * 40 +
        ['Entertainment'] * 30 +
        ['Shopping'] * 30 +
        ['Healthcare'] * 35 +
        ['Education'] * 25 +
        ['Other'] * 25
    )
}

df = pd.DataFrame(data)

# Preprocess data with TF-IDF (better than CountVectorizer for text classification)
vectorizer = TfidfVectorizer(
    max_features=150,  # Increased feature space
    ngram_range=(1, 3),  # Use unigrams, bigrams, and trigrams for better context
    lowercase=True,
    stop_words='english',
    min_df=1,  # Minimum document frequency
    max_df=0.8  # Maximum document frequency
)
X = vectorizer.fit_transform(df['description'])
y = df['category']

# Split data with stratification to maintain category distribution
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model with optimized alpha for better generalization
model = MultinomialNB(alpha=0.05)  # Lower alpha for more confidence
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Test confidence scores on sample data
print("\n🔍 Sample Confidence Tests:")
test_samples = ['Electricity bill', 'Doctor visit', 'Supermarket groceries', 'Uber ride']
for sample in test_samples:
    X_test_sample = vectorizer.transform([sample])
    pred = model.predict(X_test_sample)[0]
    prob = model.predict_proba(X_test_sample)[0].max() * 100
    print(f"   '{sample}' → {pred} ({prob:.1f}% confidence)")

# Save model and vectorizer
joblib.dump(model, 'expense_categorizer_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print(f"\n✅ Model trained and saved successfully!")
print(f"📈 Training samples: {len(df)}")
print(f"🏷️  Categories: {', '.join(df['category'].unique())}")