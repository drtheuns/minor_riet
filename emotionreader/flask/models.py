from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from .fields import SqliteJSON


db = SQLAlchemy()


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=True)
    user_count = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('Person', back_populates='session', lazy='dynamic')
    video_sessions = db.relationship('VideoSession', back_populates='session')

    def __repr__(self):
        return f'<Session(id={self.id})>' # flake8: noqa

    def __str__(self):
        return f'{self.id}: people{self.user_count}, date({self.date_created})' # flake8: noqa


class Person(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    birthdate = db.Column(db.Date, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))

    session = db.relationship('Session', back_populates='users')
    video_sessions = db.relationship('VideoSession', back_populates='person')

    def __repr__(self):
        return f'<Person(id={self.id}, name={self.name})>' # flake8: noqa


class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    path = db.Column(db.String)
    length = db.Column(db.Integer) # video length in seconds
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    video_sessions = db.relationship('VideoSession', back_populates='video')

    def __repr__(self):
        return f'<Video(id={self.id})>' # flake8: noqa


class VideoSession(db.Model):
    __tablename__ = 'videosession'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    result = db.Column(SqliteJSON)

    session = db.relationship('Session', back_populates='video_sessions')
    person = db.relationship('Person', back_populates='video_sessions')
    video = db.relationship('Video', back_populates='video_sessions')

    def __repr__(self):
        return f'<VideoSession(id={self.id})>' # flake8: noqa
