# LeadDesk Mini

A lightweight, full-stack CRM tool built with Python, Flask, and SQLite. Developed for the Digital Heroes Internship Task.

## Data Model
The application utilizes an SQLite database via SQLAlchemy with two primary models:
1. **Lead**: Captures public submissions. Includes fields for `name`, `email`, `budget`, `message`, and `status`. I enhanced the baseline requirements by injecting a `created_at` DateTime column. This allows the admin dashboard to automatically sort leads so the newest submissions are always at the top of the pipeline.
2. **Admin**: Stores administrative credentials securely with fields for `username` and `password_hash`. 

## Authentication Approach
To secure the `/admin` and `/update_status` routes, I implemented proper session-based authentication rather than hardcoded strings. 
* I utilized **Flask-Login** to handle session management, ensuring protected routes redirect unauthorized visitors to the login page.
* I utilized **Werkzeug.security** (`generate_password_hash` and `check_password_hash`) using `pbkdf2:sha256` encryption. Passwords are never stored in plaintext in the database, protecting against exposure vulnerabilities.

## Test Credentials
To evaluate the live admin dashboard, use the following credentials:
* **Username:** `admin`
* **Password:** `DigitalHeroes2026`