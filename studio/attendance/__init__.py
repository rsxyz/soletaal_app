# studio/attendance/__init__.py

from flask import Blueprint

# Define the blueprint
attendance_bp = Blueprint(
    'attendance_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Import routes after blueprint creation
from studio.attendance.routes import attendance_routes
