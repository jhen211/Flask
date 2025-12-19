from flask import Flask, render_template, jsonify, redirect, url_for
from flask_login import current_user, login_required
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, NavItem, Record
from db_utils import init_db, ensure_passwords_hashed
from auth import auth_bp, login_manager
from admin import admin_bp
from records import records_bp
from analysis import timeseries
from flask_login import current_user
import plotly.express as px
import pandas as pd
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(records_bp)

@app.route('/')
def index():
    # If logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    # If not logged in, redirect to login
    return redirect(url_for('auth.login'))

# -------------------- Charts Route --------------------
@app.route('/charts')
@login_required 
def charts():
    records = Record.query.order_by(Record.recorded_at).all()
    ts = timeseries(records, 'D')

    if ts.empty:
        # Provide dummy zero-data so Plotly doesn't break
        ts = pd.DataFrame({
            'recorded_at': [datetime.datetime.now()],
            'amount': [0]
        })

    fig = px.line(ts, x='recorded_at', y='amount', title='Daily totals')
    fig_json = fig.to_json()
    return render_template('charts.html', fig_json=fig_json)

# -------------------- Dashboard Route --------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# -------------------- API Routes --------------------
@app.route('/api/stats')
def api_stats():
    records = Record.query.all()
    if not records:
        return jsonify({
            'total_records': 0,
            'total_value': 0,
            'categories': 0,
            'avg_value': 0
        })
    
    from analysis import records_to_df
    df = records_to_df(records)
    
    return jsonify({
        'total_records': len(df),
        'total_value': float(df['amount'].sum()),
        'categories': df['category'].nunique(),
        'avg_value': float(df['amount'].mean())
    })

@app.route('/api/chart-data')
def api_chart_data():
    records = Record.query.all()
    if not records:
        return jsonify({'categories': [], 'values': []})
    
    from analysis import records_to_df
    df = records_to_df(records)
    grouped = df.groupby('category')['amount'].sum().reset_index()
    
    return jsonify({
        'categories': grouped['category'].tolist(),
        'values': grouped['amount'].tolist()
    })

@app.route('/api/records-list')
def api_records_list():
    records = Record.query.order_by(Record.recorded_at.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in records])

# -------------------- Context Processor --------------------
@app.context_processor
def inject_nav():
    nav_items = []
    try:
        items = NavItem.query.filter_by(visible=True).order_by(NavItem.position).all()
        for it in items:
            allowed = True
            role_name = current_user.role.name if current_user.is_authenticated and current_user.role else None
            if it.roles_allowed and role_name:
                allowed = role_name in [r.strip() for r in it.roles_allowed.split(',')]
            if it.roles_allowed and not role_name:
                allowed = False
            if allowed:
                nav_items.append({'title': it.title, 'endpoint': it.endpoint})
    except Exception:
        nav_items = []
    return dict(nav_items=nav_items)

# -------------------- Run --------------------
if __name__ == '__main__':
    with app.app_context():
        init_db(app)
        changed = ensure_passwords_hashed(app)
        if changed:
            print(f"Hashed {changed} seed passwords")
    app.run(debug=True, port=5000)