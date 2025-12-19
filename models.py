from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Required by flask-login
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def has_role(self, role_name):
        return self.role and self.role.name == role_name

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.name if self.role else None
        }

class NavItem(db.Model):
    __tablename__ = 'nav_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, default=0)
    roles_allowed = db.Column(db.String(255))
    visible = db.Column(db.Boolean, default=True)

class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    amount = db.Column(db.Numeric(12,2), nullable=False)
    description = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship('User', foreign_keys=[created_by])

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'subcategory': self.subcategory,
            'amount': float(self.amount),
            'description': self.description,
            'recorded_at': self.recorded_at.isoformat(),
            'created_by': self.created_by
        }

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    units = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Course {self.code} - {self.title}>"
