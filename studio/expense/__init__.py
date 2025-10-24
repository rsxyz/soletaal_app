# studio/expense/__init__.py

from flask import Blueprint

# Define the blueprint
expense_bp = Blueprint(
    'expense_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Import routes after blueprint creation
from studio.expense.routes import expense_routes
