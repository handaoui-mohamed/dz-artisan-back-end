import os
from app import db, app
from config import HOST_URL, UPLOAD_FOLDER

# file upload
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_json(self, username):
        return {
            'id': self.id,
            'path': os.path.join(HOST_URL, UPLOAD_FOLDER, username, self.name).replace("\\", "/"),
            'name': self.name,
            'user_id': self.user_id
        }


# file upload
class ProfilePicture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_json(self, username):
        return {
            'id': self.id,
            'path': os.path.join(HOST_URL, UPLOAD_FOLDER, 'profile', username, self.name).replace("\\", "/"),
            'name': self.name,
            'user_id': self.user_id
        }