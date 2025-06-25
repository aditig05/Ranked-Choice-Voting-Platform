from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    preferences = db.relationship('VotePreference', backref='vote', lazy='dynamic', cascade='all, delete-orphan')

class VotePreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote_id = db.Column(db.Integer, db.ForeignKey('vote.id'))
    candidate = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('vote_id', 'rank', name='unique_rank_per_vote'),
        db.UniqueConstraint('vote_id', 'candidate', name='unique_candidate_per_vote')
    )

def init_db():
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
