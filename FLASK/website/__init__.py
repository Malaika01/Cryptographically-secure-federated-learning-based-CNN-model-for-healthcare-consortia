from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

#Initializing the Database object.
db = SQLAlchemy()
DB_Name = "database.db"

def create_app():
    #Initializing flask environment 
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret key'

    #Storing the Database file
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_Name}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .hospital import hospital
    from .admin import admin

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(hospital, url_prefix = '/')
    app.register_blueprint(admin,url_prefix = '/')

    #Importing Database models
    from .models import User
    create_database(app)

    loginManager = LoginManager()
    loginManager.login_view = 'auth.login'
    loginManager.init_app(app)

    @loginManager.user_loader
    def load_user(id):
            return User.query.get(int(id))
    return app

def create_database(app):
    with app.app_context():
        if not path.exists('instance/' + DB_Name):
            db.create_all()
            print('Database created!')
            from .models import User
            admin = User(email = 'admin@gmail.com', hospitalName = 'admin', password = generate_password_hash('1234567', method = 'sha256'))
            db.session.add(admin)
            db.session.commit()





