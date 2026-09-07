import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from models.database import db, AuditRecord
from services.project_logic import is_valid_url, audit_url

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sanfaani-seo-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///seo_auditor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_url = request.form.get('url', '').strip()
        if not target_url:
            flash('Please enter a website URL.', 'error')
            return redirect(url_for('index'))

        if not is_valid_url(target_url):
            flash('Invalid URL. Make sure it starts with http:// or https://', 'error')
            return redirect(url_for('index'))

        result = audit_url(target_url)

        audit = AuditRecord(
            url=target_url,
            status_code=result['status_code'],
            response_time_ms=result['response_time_ms'],
            title=result['title'],
            meta_description=result['meta_description'],
            h1_count=result['h1_count'],
            images_without_alt=result['images_without_alt'],
            total_images=result['total_images'],
            broken_links_count=result['broken_links_count'],
            audit_score=result['audit_score'],
            deductions=json.dumps(result['deductions'])
        )
        db.session.add(audit)
        db.session.commit()

        return redirect(url_for('result', audit_id=audit.id))

    return render_template('index.html')

@app.route('/audit/<int:audit_id>')
def result(audit_id):
    audit = AuditRecord.query.get_or_404(audit_id)
    deductions_list = json.loads(audit.deductions) if audit.deductions else []
    return render_template('result.html', audit=audit, deductions=deductions_list)

@app.route('/history')
def history():
    audits = AuditRecord.query.order_by(AuditRecord.created_at.desc()).all()
    return render_template('history.html', audits=audits)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/export/csv')
def export_csv():
    audits = AuditRecord.query.order_by(AuditRecord.created_at.desc()).all()
    rows = ["ID,URL,Status,Score,ResponseTime_ms,Images_No_Alt,Broken_Links,Date"]
    for a in audits:
        rows.append(f"{a.id},\"{a.url}\",{a.status_code},{a.audit_score},{a.response_time_ms},{a.images_without_alt},{a.broken_links_count},{a.created_at.strftime('%Y-%m-%d %H:%M')}")
    return Response("\n".join(rows), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=sanfaani_seo_audits.csv"})

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="The requested audit record or page was not found."), 404

if __name__ == '__main__':
    app.run(debug=True)