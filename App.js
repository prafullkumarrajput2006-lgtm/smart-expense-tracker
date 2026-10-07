import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import UploadReceipt from './components/UploadReceipt';
import ExpenseList from './components/ExpenseList';
import Insights from './components/Insights';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import AddExpense from './components/AddExpense';
import ExpenseHistory from './components/ExpenseHistory';
import Profile from './components/Profile';
import BudgetSettings from './components/BudgetSettings';
import Layout from './components/Layout';
import { AuthProvider, ProtectedRoute } from './context/AuthContext';

const App = () => {
  const dummyData = [
    { category: 'Food', amount: 120 },
    { category: 'Transport', amount: 80 },
    { category: 'Bills', amount: 200 },
  ];

  return (
    <Router>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/add-expense" element={<ProtectedRoute><AddExpense /></ProtectedRoute>} />
            <Route path="/expense-history" element={<ProtectedRoute><ExpenseHistory /></ProtectedRoute>} />
            <Route path="/upload" element={<ProtectedRoute><UploadReceipt /></ProtectedRoute>} />
            <Route path="/expenses" element={<ProtectedRoute><ExpenseList /></ProtectedRoute>} />
            <Route path="/insights" element={<ProtectedRoute><Insights data={dummyData} /></ProtectedRoute>} />
            <Route path="/insights" element={<ProtectedRoute><Insights data={dummyData} /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/budget" element={<ProtectedRoute><BudgetSettings /></ProtectedRoute>} />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
};

export default App;
