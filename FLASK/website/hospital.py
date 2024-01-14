from flask import Blueprint, render_template, redirect, url_for, request, send_file, make_response
from flask_login import login_required,current_user
from .models import User, FL_Model
from . import db
import torch
from io import BytesIO

hospital = Blueprint('hospital', __name__)


@hospital.route('/upload_weights', methods=['GET', 'POST'])
@login_required
def upload_weights():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']
        # Get the current user
        user = User.query.filter_by(id=current_user.id).first()
        # Set the user's weights attribute to the uploaded file's binary data
        user.hospitalWeights = file.read()
        # Commit the changes to the database
        db.session.commit()
        # Redirect to the hospital home page
        return redirect(url_for('views.hospital_home'))
    return render_template('upload_weights.html', user=current_user)


    # return render_template('download_fl_model.html', user=current_user)

@hospital.route('/get_prediction')
@login_required
def get_prediction():
    # Add your code here to handle the prediction
    return render_template('get_prediction.html', user=current_user)

@hospital.route('/download_fl_model')
@login_required
def download_fl_model():
    model = "static/Aggregated model.pth"

    # Return a response with the binary data as a file attachment
    return send_file(model, as_attachment = True)


