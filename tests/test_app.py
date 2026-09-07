import pytest
from app import app, db
from services.project_logic import is_valid_url, audit_url
from models.database import AuditRecord

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_valid_url_validation():
    """1. Normal behavior: valid schemes recognized."""
    assert is_valid_url('https://sanfaani.com') is True
    assert is_valid_url('http://example.com/blog') is True

def test_invalid_url_validation():
    """2. Boundary & Failure behavior: malformed URLs rejected."""
    assert is_valid_url('not-a-url') is False
    assert is_valid_url('ftp://files.example.com') is False
    assert is_valid_url('') is False

def test_home_page_loads(client):
    """3. Normal behavior: homepage returns 200 OK."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Website Health &amp; SEO Auditor" in response.data or b"Website Health & SEO Auditor" in response.data

def test_unreachable_url_handling():
    """4. Failure behavior: auditor handles unreachable host without raising uncaught exceptions."""
    result = audit_url('https://unreachable-domain-123456789.org')
    assert result['audit_score'] == 0
    assert result['status_code'] == 0
    assert len(result['deductions']) > 0

def test_csv_export_route(client):
    """5. Normal behavior: CSV export produces accurate header and format."""
    response = client.get('/export/csv')
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment;filename=sanfaani_seo_audits.csv")
    assert b"ID,URL,Status,Score" in response.data