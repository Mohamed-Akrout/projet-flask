import os
from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import main
from models import db, Item, User

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'admin':
        return redirect(url_for('main.index'))
    user_count = User.query.count()
    item_count = Item.query.count()
    return render_template('dashboard.html', user_count=user_count, item_count=item_count)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            flash('Photo saved.')
            return redirect(url_for('main.index'))
    return render_template('upload.html')

@main.route('/redirect_example')
@login_required
def redirect_example():
    return redirect(url_for('main.index'))