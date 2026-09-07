from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AuditRecord(db.Model):
    __tablename__ = 'audit_records'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    status_code = db.Column(db.Integer, nullable=True)
    response_time_ms = db.Column(db.Float, nullable=True)
    title = db.Column(db.String(300), nullable=True)
    meta_description = db.Column(db.Text, nullable=True)
    h1_count = db.Column(db.Integer, default=0)
    images_without_alt = db.Column(db.Integer, default=0)
    total_images = db.Column(db.Integer, default=0)
    broken_links_count = db.Column(db.Integer, default=0)
    audit_score = db.Column(db.Integer, nullable=False)
    deductions = db.Column(db.Text, nullable=True)  # JSON-like string of deductions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)