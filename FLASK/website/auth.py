from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth',__name__)

@auth.route('/hospital_login', methods = ['GET', 'POST'])

def hospital_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        if(user):
            if check_password_hash(user.password, password):
                login_user(user, remember = True)
                flash('Logged in successfully!', category = 'success')
                return redirect(url_for('views.hospital_home'))
            else:
                flash('Incorrect password, try again.',category = 'error')
        else:
            flash('Email does not exist.',category = 'error')
    return render_template('hospital_login.html', user = current_user)

@auth.route('/admin_login', methods = ['GET', 'POST'])

def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        if(user):
            if check_password_hash(user.password, password):
                login_user(user, remember = True)
                flash('Logged in successfully!', category = 'success')
                return redirect(url_for('views.admin_home'))
            else:
                flash('Incorrect password, try again.',category = 'error')
        else:
            flash('Email does not exist.',category = 'error')
    return render_template('admin_login.html', user = current_user)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template('login.html', user = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        hospitalName = request.form.get('hospitalName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email = email).first()
        if user:
            flash('Email already exists', category = 'error')
        elif len(email) < 4:
            flash('Email length must be greater than 3 characters', category = "error")
        elif len(hospitalName) < 2:
            flash('Hospital name length must be greater 1 character', category = "error")
        elif password1 != password2:
            flash('Passwords do not match', category = "error")
        elif len(password1) < 7:
            flash('Password length must be at least 7 characters', category = "error")
        else:
            #Add user to DB
            newUser = User(email = email, hospitalName = hospitalName, password = generate_password_hash(password1, method = 'sha256'))
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser, remember = True)
            flash('Account created successfuly')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user = current_user)