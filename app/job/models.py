from app import db


UserJob = db.Table(
    'UserJob',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('User_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'))
)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.Text)
    users = db.relationship('User', secondary=UserJob, backref='Job')

    def to_json_min(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'users': [element.to_json() for element in self.users]
        }
    
    def remove_user(self, user):
        users.remove(user)
        return self
