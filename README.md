# 💰 Smart Expense Tracker

An AI-powered expense tracking application that helps users manage
expenses using OCR-based receipt scanning and machine-learning-based
expense categorization.

## ✨ Features

-   📷 OCR-based receipt scanning
-   🧾 Automatic receipt data extraction
-   🤖 AI-powered expense categorization
-   📊 Interactive expense charts
-   💰 Budget alerts
-   🔐 JWT-based authentication
-   📈 Expense tracking and analysis

## 🛠️ Tech Stack

### Frontend

-   React
-   Material-UI
-   Chart.js

### Backend

-   Flask
-   SQLAlchemy

### AI / Machine Learning

-   EasyOCR
-   scikit-learn

## 📂 Project Structure

``` text
smart-expense-tracker/
│
├── backend/
│   ├── app.py
│   ├── ml_model.py
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── package.json
│   └── ...
│
└── README.md
```

## 🚀 Quick Start

### Backend Setup

Open a terminal and navigate to the backend folder:

``` powershell
cd backend
```

Create a virtual environment:

``` powershell
python -m venv venv
```

Activate the virtual environment:

``` powershell
.\venv\Scripts\activate
```

Install the required dependencies:

``` powershell
pip install -r requirements.txt
```

Run the ML model:

``` powershell
python ml_model.py
```

Start the Flask backend:

``` powershell
python app.py
```

### Frontend Setup

Open another terminal and navigate to the frontend folder:

``` powershell
cd frontend
```

Install dependencies:

``` powershell
npm install
```

Start the React application:

``` powershell
npm start
```

## 🎯 Project Purpose

The purpose of this project is to simplify personal expense management
by combining traditional expense tracking with OCR and machine learning.

The application can extract information from receipts and use machine
learning to categorize expenses, while providing charts and budget
alerts for better financial tracking.

## 📈 AI & Machine Learning

The project uses:

-   **EasyOCR** for extracting information from receipt images.
-   **scikit-learn** for machine-learning-based expense categorization.

## 🔐 Authentication

The application uses **JWT (JSON Web Token)** based authentication for
user authentication and access control.

## 👨‍💻 Author

**Prafull Kumar**

B.Tech CSE Student

------------------------------------------------------------------------

⭐ This project was created as part of my learning and hands-on
development in **React, Flask, AI/ML and full-stack application
development**.
