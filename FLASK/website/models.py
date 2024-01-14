from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(30), unique = True)
    password = db.Column(db.String(40))
    hospitalName = db.Column(db.String(30))
    hospitalWeights = db.Column(db.LargeBinary, nullable=True)
    
class FL_Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aggregatedWeights = db.Column(db.LargeBinary, nullable=True)



