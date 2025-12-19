from models import db, User, Role
from werkzeug.security import generate_password_hash

def init_db(app):
    """Create all tables for the database."""
    with app.app_context():
        db.create_all()

def ensure_passwords_hashed(app):
    """Hash any plaintext passwords in the database."""
    with app.app_context():
        users = User.query.all()
        changed = 0
        for u in users:
            ph = u.password_hash or ''
            if ph and not ph.startswith('pbkdf2:'):
                u.password_hash = generate_password_hash(ph)
                changed += 1
        if changed:
            db.session.commit()
        return changed
