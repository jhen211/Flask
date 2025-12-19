from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, Role, NavItem
from forms import UserForm
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role or current_user.role.name != 'Admin':
            flash('Admin access required', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ---------------- Users ----------------
@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = UserForm()
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
    if form.validate_on_submit():
        u = User(
            username=form.username.data,
            email=form.email.data,
            password_hash='placeholder',  # Rehash later
            role_id=form.role.data
        )
        db.session.add(u)
        db.session.commit()
        flash('User created — set password via rehash script', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/user_form.html', form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        db.session.commit()
        flash('User updated', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/user_form.html', form=form)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted', 'info')
    return redirect(url_for('admin.list_users'))

# ---------------- Nav Items ----------------
@admin_bp.route('/nav')
@login_required
@admin_required
def list_nav():
    nav_items = NavItem.query.order_by(NavItem.position).all()
    return render_template('admin/nav.html', nav_items=nav_items)

@admin_bp.route('/nav/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_nav():
    form = UserForm()  # You can create a NavItemForm for better clarity
    if request.method == 'POST':
        title = request.form.get('title')
        endpoint = request.form.get('endpoint')
        position = request.form.get('position', 0)
        roles_allowed = request.form.get('roles_allowed', '')
        visible = bool(request.form.get('visible'))
        nav = NavItem(title=title, endpoint=endpoint, position=position,
                      roles_allowed=roles_allowed, visible=visible)
        db.session.add(nav)
        db.session.commit()
        flash('Nav item created', 'success')
        return redirect(url_for('admin.list_nav'))
    return render_template('admin/nav_form.html')

@admin_bp.route('/nav/<int:nav_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_nav(nav_id):
    nav = NavItem.query.get_or_404(nav_id)
    if request.method == 'POST':
        nav.title = request.form.get('title')
        nav.endpoint = request.form.get('endpoint')
        nav.position = request.form.get('position', 0)
        nav.roles_allowed = request.form.get('roles_allowed', '')
        nav.visible = bool(request.form.get('visible'))
        db.session.commit()
        flash('Nav item updated', 'success')
        return redirect(url_for('admin.list_nav'))
    return render_template('admin/nav_form.html', nav=nav)

@admin_bp.route('/nav/<int:nav_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_nav(nav_id):
    nav = NavItem.query.get_or_404(nav_id)
    db.session.delete(nav)
    db.session.commit()
    flash('Nav item deleted', 'info')
    return redirect(url_for('admin.list_nav'))
