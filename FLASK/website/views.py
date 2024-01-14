from flask import Blueprint, render_template
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template('login.html', user = current_user)

@views.route('/admin_home')
@login_required
def admin_home():
    return render_template('admin_home.html', user = current_user)

@views.route('/hospital_home')
@login_required
def hospital_home():
    return render_template('hospital_home.html', user = current_user)

