import base64
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for
from datetime import datetime, timedelta
import os


@login.user_loader
def load_user(id):
    return User.query.get(id)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(128), primary_key=True)
    first_name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    isAdmin = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # date and time
    # token authetication for api
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    attempts = db.relationship("Attempt", backref="user", lazy="dynamic")
    logs = db.relationship("Log", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    ###Token support methods for api

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def to_dict(self):
        data = {
            "id": self.id,
            "password_hash": self.password_hash,
            "first_name": self.first_name,
            "surname": self.surname,
            "isAdmin": self.isAdmin,
            "date": self.date,
        }
        return data

    def from_dict(self, data):
        if "id" in data:
            self.user_id = data["id"]
        if "first_name" in data:
            self.first_name = data["first_name"]
        if "surname" in data:
            self.surname = data["surname"]
        if "isAdmin" in data:
            self.isAdmin = data["isAdmin"]
        if "password_hash" in data:
            self.set_password(data["password_hash"])
        if "date" in data:
            self.date = data["date"]

    def __repr__(self):
        return f"[id: {self.id}, name: {self.__str__()}, isAdmin: {self.isAdmin}]"

    def __str__(self):
        return self.first_name + " " + self.surname


class Attempt(db.Model):
    __tablename__ = "attempts"
    attempt_id = db.Column(db.Integer, primary_key=True)
    answer_1 = db.Column(db.String(256), nullable=True)
    answer_2 = db.Column(db.String(256), nullable=True)
    answer_3 = db.Column(db.String(256), nullable=True)
    answer_4 = db.Column(db.String(256), nullable=True)
    answer_5 = db.Column(db.String(256), nullable=True)
    answer_6 = db.Column(db.String(256), nullable=True)
    answer_7 = db.Column(db.String(256), nullable=True)
    correct_1 = db.Column(db.Boolean, default=False)
    correct_2 = db.Column(db.Boolean, default=False)
    correct_3 = db.Column(db.Boolean, default=False)
    correct_4 = db.Column(db.Boolean, default=False)
    correct_5 = db.Column(db.Boolean, default=False)
    correct_6 = db.Column(db.Boolean, default=False)
    correct_7 = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # date and time
    user_id = db.Column(db.String(128), db.ForeignKey("users.id"))

    def to_dict(self):
        data = {
            "attempt_id": self.attempt_id,
            "answer_1": self.answer_1,
            "answer_2": self.answer_2,
            "answer_3": self.answer_3,
            "answer_4": self.answer_4,
            "answer_5": self.answer_5,
            "answer_6": self.answer_6,
            "answer_7": self.answer_7,
            "correct_1": self.correct_1,
            "correct_2": self.correct_2,
            "correct_3": self.correct_3,
            "correct_4": self.correct_4,
            "correct_5": self.correct_5,
            "correct_6": self.correct_6,
            "correct_7": self.correct_7,
            "date": self.date,
            "user_id": self.user_id,
        }
        return data

    def is_committed(self):
        return (self.user_id is not None) & (self.answer_1 == "potato")

    def from_dict(self, data):
        if "attempt_id" in data:
            self.attempt_id = data["attempt_id"]
        if "answer_1" in data:
            self.answer_1 = data["answer_1"]
        if "answer_2" in data:
            self.answer_2 = data["answer_2"]
        if "answer_3" in data:
            self.answer_3 = data["answer_3"]
        if "answer_4" in data:
            self.answer_4 = data["answer_4"]
        if "answer_5" in data:
            self.answer_5 = data["answer_5"]
        if "answer_6" in data:
            self.answer_6 = data["answer_6"]
        if "answer_7" in data:
            self.answer_7 = data["answer_7"]
        if "correct_1" in data:
            self.correct_1 = data["correct_1"]
        if "correct_2" in data:
            self.correct_2 = data["correct_2"]
        if "correct_3" in data:
            self.correct_3 = data["correct_3"]
        if "correct_4" in data:
            self.correct_4 = data["correct_4"]
        if "correct_5" in data:
            self.correct_5 = data["correct_5"]
        if "correct_6" in data:
            self.correct_6 = data["correct_6"]
        if "correct_7" in data:
            self.correct_7 = data["correct_7"]
        if "date" in data:
            self.date = data["date"]
        if "user_id" in data:
            self.user_id = data["user_id"]

    def __repr__(self):
        return f"[attempt_id: {self.attempt_id}, date: {self.date}, name: {User.query.get(self.user_id).__str__()}]"


class Question(db.Model):
    __tablename__ = "questions"
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256))
    answer_type = db.Column(db.String(256))
    answer_choice_1 = db.Column(db.String(256), nullable=True)
    answer_choice_2 = db.Column(db.String(256), nullable=True)
    answer_choice_3 = db.Column(db.String(256), nullable=True)
    answer_choice_4 = db.Column(db.String(256), nullable=True)
    answer = db.Column(db.String(256))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # date and time

    def to_dict(self):
        data = {
            "question_id": self.question_id,
            "question": self.question,
            "answer_type": self.answer_type,
            "answer_choice_1": self.answer_choice_1,
            "answer_choice_2": self.answer_choice_2,
            "answer_choice_3": self.answer_choice_3,
            "answer_choice_4": self.answer_choice_4,
            "answer": self.answer,
            "date": self.date,
        }
        return data

    def from_dict(self, data):
        if "question_id" in data:
            self.question_id = data["question_id"]
        if "question" in data:
            self.question = data["question"]
        if "answer_type" in data:
            self.answer_type = data["answer_type"]
        if "answer_choice_1" in data:
            self.answer_choice_1 = data["answer_choice_1"]
        if "answer_choice_2" in data:
            self.answer_choice_2 = data["answer_choice_2"]
        if "answer_choice_3" in data:
            self.answer_choice_3 = data["answer_choice_3"]
        if "answer_choice_4" in data:
            self.answer_choice_4 = data["answer_choice_4"]
        if "answer" in data:
            self.answer = data["answer"]
        if "date" in data:
            self.date = data["date"]

    def __repr__(self):
        return f"[question_id: {self.question_id}, question: {self.question}, answer: {self.answer}, date: {self.date}]"


class Log(db.Model):
    __tablename__ = "logs"
    log_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # date and time

    user_id = db.Column(db.String(128), db.ForeignKey("users.id"))

    def to_dict(self):
        data = {
            "log_id": self.log_id,
            "date": self.date,
            "user_id": self.user_id,
        }
        return data

    def from_dict(self, data):
        if "log_id" in data:
            self.log_id = data["log_id"]
        if "date" in data:
            self.date = data["date"]
        if "user_id" in data:
            self.user_id = data["user_id"]

    def __repr__(self):
        return f"[log_id: {self.log_id}, user_id: {self.user_id}, date: {self.date}]"