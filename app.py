from flask import Flask, render_template
from studio.db.db import init_db
from studio.student import student_bp
from studio.attendance import attendance_bp
from studio.payment import payment_bp
from studio.report import report_bp

import os

app = Flask(__name__,
             template_folder="studio/templates",   # ✅ tell Flask where global templates are
             static_folder="studio/static")        # optional if you use static assets

app.secret_key = "supersecret"

# Register Blueprints
app.register_blueprint(student_bp, url_prefix="/student")
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(payment_bp, url_prefix="/payment")
app.register_blueprint(report_bp, url_prefix="/report")

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
