from flask.json import jsonify
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import Assignment, db, AccountType, Account, Classroom, ClassApprove

classroom = Blueprint('classroom', __name__, url_prefix='/classroom')

# 강의 생성 (교수자만 가능)
@classroom.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type != AccountType.professor:
        return jsonify({'error': 'Account type mismatch'}), 403

    classroom = Classroom(data['name'], data['year'], data['semester'], userId)

    try:
        db.session.add(classroom)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

# 내 계정이 속한 강의 조회
@classroom.route('/', methods=['GET'])
@jwt_required()
def lookup():
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403

    if user.type == AccountType.professor:
        classrooms = Classroom.query.filter_by(ownerId=userId)
        return jsonify([c.as_dict() for c in classrooms]), 200
    elif user.type == AccountType.student:
        classrooms = user.classrooms
        return jsonify([c.as_dict() for c in classrooms]), 200
    else:
        return jsonify({'error': 'Account type is not supported'}), 403

# 강의 수강 학생 조회
@classroom.route('/<id>/member', methods=['GET'])
@jwt_required()
def lookup_member(id):
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type != AccountType.professor:
        return jsonify({'error': 'Account type mismatch'}), 403

    classroom = Classroom.query.filter_by(id=id).first()

    if classroom.ownerId != userId:
        return jsonify({'error': 'Account is not owner of this classroom'}), 403
    
    members = classroom.students

    return jsonify([{'account_id': member.id,'student_id': member.studentId ,'name': member.name, 'approved': ClassApprove.query.filter_by(classroomId=id, studentId=member.id).first().approve} for member in members]), 200

# 강의 과제 조회
@classroom.route('/<id>/assignment', methods=['GET'])
@jwt_required()
def lookup_assignment(id):
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403

    is_student = ClassApprove.query.filter_by(studentId=userId, classroomId=id, approve=True).first()
    is_professor = Classroom.query.filter_by(ownerId=userId, id=id).first()

    if is_student is None and is_professor is None:
        return jsonify({'error': 'Account is not associated with this classroom'}), 403
    
    assignments = Assignment.query.filter_by(classroomId=id, parentId=None).all()

    return jsonify([{"id": a.id, "title": a.title, "date": a.date.isoformat(), "start_date": a.startDate.isoformat(), "end_date": a.endDate.isoformat()} for a in assignments]), 200

# ID로 강의 조회
@classroom.route('/<id>', methods=['GET'])
def lookup_by_id(id):
    classroom = Classroom.query.filter_by(id=id).first()

    if not classroom:
        return jsonify({'error': 'Classroom not found'}), 404

    owner = Account.query.filter_by(id=classroom.ownerId).first()

    return jsonify({"class_name": classroom.name, "year": classroom.year, "semester": classroom.semester, "professor_name": owner.name}), 200

# 강의 정보 수정
@classroom.route('/<id>', methods=['PUT'])
@jwt_required()
def modify(id):
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type != AccountType.professor:
        return jsonify({'error': 'Account type mismatch'}), 403

    classroom = Classroom.query.filter_by(id=id).first()

    if classroom.ownerId != userId:
        return jsonify({'error': 'Account is not owner of this classroom'}), 403

    classroom.name = data['name']
    classroom.year = data['year']
    classroom.semester = data['semester']

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

# 강의 비활성화
@classroom.route('/<id>', methods=['DELETE'])
@jwt_required()
def disable(id):
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type != AccountType.professor:
        return jsonify({'error': 'Account type mismatch'}), 403

    classroom = Classroom.query.filter_by(id=id).first()

    if classroom.ownerId != userId:
        return jsonify({'error': 'Account is not owner of this classroom'}), 403

    classroom.disabled = True

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200