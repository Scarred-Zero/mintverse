from sqlalchemy import Column, Integer, String, Text, DateTime
from ..config.database import db
from datetime import datetime


class Contact(db.Model):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    def __init__(self, name, email, subject, message):
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message

    @classmethod
    def get_all(cls):
        return cls.query.all()

    def data(self):
        return {
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "timestamp": self.timestamp,
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
