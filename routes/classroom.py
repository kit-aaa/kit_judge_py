from flask.json import jsonify
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import Assignment, db, AccountType, Account, Classroom, ClassApprove

classroom = Blueprint('classroom', __name__, url_prefix='/classroom')

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
    
    approves = classroom.approves

    return jsonify([{'account_id': approve.member.id,'student_id': approve.member.studentId ,'name': approve.member.name} for approve in approves]), 200

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

    return jsonify([{'id': assignment.id, 'title': assignment.title, 'start_date': assignment.startDate.isoformat(), 'end_date': assignment.endDate.isoformat()} for assignment in assignments]), 200

@classroom.route('/<id>', methods=['GET'])
def lookup(id):
    classroom = Classroom.query.filter_by(id=id).first()

    if not classroom:
        return jsonify({'error': 'Classroom not found'}), 404

    owner = Account.query.filter_by(id=classroom.ownerId).first()

    return jsonify({"class_name": classroom.name, "year": classroom.year, "semester": classroom.semester, "professor_name": owner.name}), 200

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