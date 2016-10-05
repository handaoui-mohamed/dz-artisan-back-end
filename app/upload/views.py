#!/usr/bin/env python 
from app import db, app, auth
import os
from flask import abort, request, jsonify, g, send_from_directory
from werkzeug import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from app.upload.models import Upload


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Route that will process the file upload
@app.route('/api/upload', methods=['POST'])
@auth.login_required
def upload():
    uploaded_files = request.files.getlist("file")
    user_id = request.form.get('user_id')   
    filenames = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            directory = os.path.join(UPLOAD_FOLDER, '%s/'%g.user.username)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, filename)
            i = 0
            while os.path.exists(file_path):
                filename = "%s%s"%(i,filename)
                file_path = os.path.join(directory, filename)
            file.save(file_path)
            uploaded_file = Upload(name=filename,path=file_path,user_id=user_id)
            db.session.add(uploaded_file)
            db.session.commit()
            filenames.append(filename)
    return jsonify({'element':g.user.to_json()})


@app.route('/api/uploads/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_file(id):
    file = Upload.query.get(id)
    if file and file.user_id == g.user.id:
        db.session.delete(file)
        db.session.commit()
        os.remove(file.path)
    return jsonify({'element':g.user.to_json()})


@app.route('/api/uploads/<string:username>/<string:filename>')
def get_file(username, filename):
    directory = os.path.join(UPLOAD_FOLDER, '%s/'%username)
    return send_from_directory(directory, filename)
