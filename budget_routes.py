# Budget routes - to be imported into app.py
from flask import jsonify, request
from models import db, Budget, Expense
from datetime import datetime
from sqlalchemy import or_, func

def register_budget_routes(app, token_required):
    """Register budget-related routes"""
    
    @app.route('/budgets', methods=['GET'])
    @token_required
    def get_budgets(current_user):
        """Get all budgets for the current user"""
        month = request.args.get('month')  # Optional filter by month (YYYY-MM)
        
        query = Budget.query.filter_by(user_id=current_user.id)
        if month:
            query = query.filter_by(month=month)
        
        budgets = query.all()
        return jsonify([b.to_dict() for b in budgets])

    @app.route('/budgets', methods=['POST'])
    @token_required
    def set_budget(current_user):
        """Set or update a budget for a category and month"""
        data = request.json
        if not data or not data.get('category') or not data.get('monthly_limit'):
            return jsonify({"error": "Category and monthly_limit are required"}), 400
        
        category = data['category']
        monthly_limit = float(data['monthly_limit'])
        month = data.get('month', datetime.now().strftime('%Y-%m'))
        
        # Check if budget exists
        budget = Budget.query.filter_by(
            user_id=current_user.id,
            category=category,
            month=month
        ).first()
        
        if budget:
            # Update existing
            budget.monthly_limit = monthly_limit
        else:
            # Create new
            budget = Budget(
                user_id=current_user.id,
                category=category,
                monthly_limit=monthly_limit,
                month=month
            )
            db.session.add(budget)
        
        db.session.commit()
        return jsonify({"message": "Budget saved", "budget": budget.to_dict()}), 201

    @app.route('/budgets/<int:budget_id>', methods=['DELETE'])
    @token_required
    def delete_budget(current_user, budget_id):
        """Delete a budget"""
        budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first()
        if not budget:
            return jsonify({"error": "Budget not found"}), 404
        
        db.session.delete(budget)
        db.session.commit()
        return jsonify({"message": "Budget deleted"})

    @app.route('/budget-alerts', methods=['GET'])
    @token_required
    def get_budget_alerts(current_user):
        """Check if any budgets are exceeded or approaching limit"""
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))
        
        # Get all budgets for this month
        budgets = Budget.query.filter_by(user_id=current_user.id, month=month).all()
        
        alerts = []
        for budget in budgets:
            # Calculate total spending for this month, support 'All' category and robust month detection
            # Prefer matching YYYY-MM prefix on Expense.date, fallback to created_at month
            month_prefix = f"{month}"

            base_filters = [
                Expense.user_id == current_user.id,
                # Month filter: either the string date starts with YYYY-MM or created_at matches month
                or_(
                    Expense.date.like(f"{month_prefix}%"),
                    func.strftime('%Y-%m', Expense.created_at) == month
                )
            ]

            # Category filter: 'All' means no category filter
            if budget.category.lower() != 'all':
                base_filters.append(func.lower(Expense.category) == budget.category.lower())

            total_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(*base_filters).scalar() or 0.0
            
            percentage = (total_spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
            
            status = "ok"
            if percentage >= 100:
                status = "exceeded"
            elif percentage >= 80:
                status = "warning"
            
            alerts.append({
                "budget": budget.to_dict(),
                "spent": total_spent,
                "remaining": budget.monthly_limit - total_spent,
                "percentage": round(percentage, 1),
                "status": status
            })
        
        return jsonify(alerts)
