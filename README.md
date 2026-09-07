# Sanfaani Website Health & SEO Auditor (Option 1)

A responsive, privacy-conscious Flask web application that accepts a public website URL, inspects technical SEO health (HTTP responsiveness, meta tags, heading structure, image accessibility, broken links), calculates a transparent audit score (0–100), stores historical audits, and exports CSV reports.

## Features
- **HTTP Verification:** Analyzes status codes and response latency.
- **On-Page SEO Checks:** Evaluates `<title>` and `<meta name="description">` presence and character length.
- **Structural Integrity:** Verifies single `<h1>` tag presence and checks for broken internal links.
- **Accessibility:** Detects `<img>` elements missing `alt` attributes.
- **Transparent Scoring:** Deductions are explained line-by-line.
- **Reporting & History:** Persistent audit logs with full CSV export capabilities.

## Architecture & Project Structure
- `app.py`: Flask entry point, routes, and application configuration.
- `models/database.py`: SQLAlchemy schema (`AuditRecord`) and database initialization.
- `services/project_logic.py`: Core business logic, URL validation, and BeautifulSoup web scraping.
- `templates/`: Jinja2 templates extending `base.html` (`index`, `result`, `history`, `about`, `error`).
- `static/style.css`: Clean, mobile-responsive custom stylesheet.
- `tests/test_app.py`: Automated pytest test suite covering normal, boundary, and failure behaviors.

## Database Schema (`AuditRecord`)
- `id` (Integer, Primary Key)
- `url` (String, Required)
- `status_code` (Integer)
- `response_time_ms` (Float)
- `title` (String)
- `meta_description` (Text)
- `h1_count` (Integer)
- `images_without_alt` (Integer)
- `total_images` (Integer)
- `broken_links_count` (Integer)
- `audit_score` (Integer)
- `deductions` (Text / JSON string)
- `created_at` (DateTime)

## Local Setup & Installation
1. Clone repository:
   ```bash
   git clone [https://github.com/abdulmuminmuhammadjamiu384-prog/sanfaani-seo-auditor.git]
   cd sanfaani-seo-auditori9