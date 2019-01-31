from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(32), nullable=False)
    username = db.Column(db.String(64), nullable=True)


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(1024), nullable=True)
    message = db.Column(db.String(1024), nullable=True)
    files = db.Column(db.Integer, nullable=True)
    size = db.Column(db.Integer, nullable=True)

    def __init__(self, user_id: int, file_name: str, message: str = ''):
        self.user_id = user_id
        self.file_name = file_name
        self.message = message


class Receiver(db.Model):
    __tablename__ = 'receivers'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    downloaded_file = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, file_id: int, token: str, email: str):
        self.file_id = file_id
        self.token = token
        self.email = email
        self.downloaded_file = False

