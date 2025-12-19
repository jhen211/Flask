from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Role
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Welcome back!', 'success')
            
            # Redirect to dashboard instead of 'next' page
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # Populate role choices dynamically
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
    if form.validate_on_submit():
        pwd = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=pwd,
            role_id=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('User registered', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)
