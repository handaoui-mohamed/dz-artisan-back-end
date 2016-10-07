from app import db


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.Text)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
