from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    studentId = db.Column(db.Integer, nullable=True)
    disabled = db.Column(db.Boolean, default=False)

    def __init__(self, email, pw, name, type, studentId):
        self.email = email
        self.set_password(pw)
        self.name = name
        self.type = type
        self.studentId = studentId

    def set_password(self, password):
        self.pw = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.pw, password)

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    ownerId = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    classId = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    desc = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    parentId = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=False)

class ClassApprove(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classId = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    studentId = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    approve = db.Column(db.Boolean, nullable=False, default=False)

class Testcase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignmentId = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignmentId = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    testcaseId = db.Column(db.Integer, db.ForeignKey('testcase.id'), nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    failCause = db.Column(db.Text, nullable=False)

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)