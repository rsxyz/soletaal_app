# studio/report/__init__.py

from flask import Blueprint

# Define the blueprint
report_bp = Blueprint(
    'report_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Import routes after blueprint creation
from studio.report.routes import report_routes, report_attendance_routes
