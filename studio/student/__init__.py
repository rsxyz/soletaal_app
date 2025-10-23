# studio/student/__init__.py

from flask import Blueprint

# Define the blueprint
student_bp = Blueprint(
    'student_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Import routes after blueprint creation
from studio.student.routes import student_routes
