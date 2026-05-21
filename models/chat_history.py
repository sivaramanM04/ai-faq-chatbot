from app import db

class ChatHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    message = db.Column(db.Text)

    response = db.Column(db.Text)