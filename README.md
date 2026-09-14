# django_web_showcase

# dwf_portfolio

## 🚀 Production Infrastructure

This project is built using a decoupled architecture pattern that supports containerized or PaaS execution:

- **Procfile:** Configured to launch a high-performance Gunicorn WSGI worker process thread.
- **Dockerfile:** Ready to build an isolated, production-grade container layout.
- **Database Sandbox:** Configured to read a pre-seeded `db.sqlite3` file for self-contained, frictionless local testing and zero-maintenance preview sandboxes.
