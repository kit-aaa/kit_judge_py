import enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class AccountType(enum.Enum):
    student = 1
    professor = 2
    admin = 3

# https://michaelcho.me/article/using-python-enums-in-sqlalchemy-models
class IntEnum(db.TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """
    impl = db.Integer

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(IntEnum(AccountType), nullable=False)
    studentId = db.Column(db.Integer, nullable=True)
    disabled = db.Column(db.Boolean, default=False)
    classrooms = association_proxy('classroom_associations', 'classroom')

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
    disabled = db.Column(db.Boolean, default=False)
    owner = db.relationship('Account', uselist=False)
    students = association_proxy('student_associations', 'student')

    def __init__(self, name, year, semester, ownerId):
        self.name = name
        self.year = year
        self.semester = semester
        self.ownerId = ownerId

    def as_dict(self):
       return {"id": self.id, "name": self.name, "year": self.year, "semester": self.semester, "professor_name": self.owner.name}

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    classroomId = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    title = db.Column(db.String(120), nullable=True)
    desc = db.Column(db.String(120), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    startDate = db.Column(db.DateTime, nullable=True)
    endDate = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    parentId = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)

    def __init__(self, author, classroomId, title, desc, startDate, endDate, parentId):
        self.author = author
        self.classroomId = classroomId
        self.title = title
        self.desc = desc
        self.startDate = startDate
        self.endDate = endDate
        self.parentId = parentId

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ClassApprove(db.Model):
    classroomId = db.Column(db.Integer, db.ForeignKey('classroom.id'), primary_key=True)
    studentId = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    approve = db.Column(db.Boolean, nullable=False, default=False)
    
    student = db.relationship(Account, backref="classroom_associations")
    classroom = db.relationship(Classroom, backref="student_associations")

    def __init__(self, classroomId, studentId, approve):
        self.classroomId = classroomId
        self.studentId = studentId
        self.approve = approve

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