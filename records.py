from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Record
from forms import RecordForm
import pandas as pd

records_bp = Blueprint('records', __name__, url_prefix='/records')

@records_bp.route('/')
@login_required
def list_records():
    items = Record.query.order_by(Record.recorded_at.desc()).all()
    return render_template('records/list.html', records=items)

@records_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_record():
    form = RecordForm()
    if form.validate_on_submit():
        r = Record(
            category=form.category.data,
            subcategory=form.subcategory.data,
            amount=form.amount.data,
            description=form.description.data,
            recorded_at=form.recorded_at.data,
            created_by=current_user.id
        )
        db.session.add(r)
        db.session.commit()
        flash('Record added', 'success')
        return redirect(url_for('records.list_records'))
    return render_template('records/form.html', form=form)

@records_bp.route('/<int:rec_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(rec_id):
    r = Record.query.get_or_404(rec_id)
    form = RecordForm(obj=r)
    if form.validate_on_submit():
        r.category = form.category.data
        r.subcategory = form.subcategory.data
        r.amount = form.amount.data
        r.description = form.description.data
        r.recorded_at = form.recorded_at.data
        db.session.commit()
        flash('Record updated', 'success')
        return redirect(url_for('records.list_records'))
    return render_template('records/form.html', form=form, record=r)

@records_bp.route('/<int:rec_id>/delete', methods=['POST'])
@login_required
def delete_record(rec_id):
    r = Record.query.get_or_404(rec_id)
    db.session.delete(r)
    db.session.commit()
    flash('Record deleted', 'info')
    return redirect(url_for('records.list_records'))

@records_bp.route('/upload', methods=['POST'])
@login_required
def upload_csv():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'no file uploaded'}), 400

    df = pd.read_csv(f)
    df['recorded_at'] = pd.to_datetime(df['recorded_at'])
    inserted = 0

    for _, row in df.iterrows():
        rec = Record(
            category=row['category'],
            subcategory=row.get('subcategory'),
            amount=row['amount'],
            description=row.get('description', ''),
            recorded_at=row['recorded_at'].to_pydatetime(),
            created_by=current_user.id
        )
        db.session.add(rec)
        inserted += 1

    db.session.commit()
    return jsonify({'status': 'ok', 'inserted': inserted})
