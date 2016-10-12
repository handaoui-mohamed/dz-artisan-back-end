#!/usr/bin/env python 
from app import db, app
import os
from flask import abort, request, jsonify, g, send_from_directory
from werkzeug import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, basedir
from app.upload.models import Upload
from app.upload.models import ProfilePicture
from app.user.views import login_required


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Route that will process the file upload
@app.route('/api/upload', methods=['POST'])
@login_required
def upload():
    file = request.files.get("file")
    user_id = g.user.id
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        directory = os.path.join(UPLOAD_FOLDER, g.user.username)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)
        i = 0
        while os.path.exists(file_path):
            filename = "%s%s"%(i,filename)
            file_path = os.path.join(directory, filename)
        file.save(file_path)
        uploaded_file = Upload(name=filename,user_id=user_id)
        db.session.add(uploaded_file)
        db.session.commit()
    return jsonify({'element':g.user.to_json()})


@app.route('/api/uploads/<int:id>', methods=['DELETE'])
@login_required
def delete_file(id):
    file = Upload.query.get(id)
    if file and file.user_id == g.user.id:
        db.session.delete(file)
        db.session.commit()
        file_path = os.path.join(UPLOAD_FOLDER, g.user.username, file.name)
        os.remove(file_path)
        return jsonify({'success': 'true'}), 200
    else:
        abort(404)

@app.route('/api/uploads/<string:username>/<string:filename>')
def get_file(username, filename):
    directory = os.path.join(basedir, UPLOAD_FOLDER, username)
    return send_from_directory(directory, filename)


# profile picture upload
@app.route('/api/upload/profile', methods=['POST'])
@login_required
def upload_profile_image():
    file = request.files.get("profile_image")
    user_id = g.user.id
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        directory = os.path.join(UPLOAD_FOLDER, g.user.username, 'profile')
        if os.path.exists(directory):
            old_pictures = ProfilePicture.query.all()
            for picture in old_pictures:
                file_path = os.path.join(UPLOAD_FOLDER, g.user.username, 'profile', picture.name)
                if os.path.exists(file_path):
                    db.session.delete(picture)
                    db.session.commit()
                    os.remove(file_path)
        else:
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)
        file.save(file_path)
        uploaded_image = ProfilePicture(name=filename,user_id=user_id)
        db.session.add(uploaded_image)
        db.session.commit()
    return jsonify({'element':g.user.to_json()})


@app.route('/api/uploads/profile/<int:id>', methods=['DELETE'])
@login_required
def delete_profile_image(id):
    file = ProfilePicture.query.get(id)
    if file and file.user_id == g.user.id:
        
        return jsonify({'success': 'true'}), 200
    else:
        abort(404)


@app.route('/api/uploads/profile/<string:username>/<string:filename>')
def get_profile_image(username, filename):
    directory = os.path.join(basedir, UPLOAD_FOLDER, username, 'profile')
    print os.path.exists(directory)
    return send_from_directory(directory, filename)