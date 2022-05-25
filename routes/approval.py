from flask.json import jsonify
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import Account, ClassApprove, db, AccountType

approval = Blueprint('approval', __name__, url_prefix='/approval')

# 승인 요청 목록 조회 (학생)
@approval.route('/', methods=['GET'])
@jwt_required()
def lookup():
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type == AccountType.student:
        classApprove = ClassApprove.query.filter_by(studentId=userId, approve=False)
        return jsonify([c.as_dict() for c in classApprove]), 200
    else:
        return jsonify({'error': 'Account type mismatch'}), 403

# 승인 요청 (학생)
@approval.route('/request', methods=['POST'])
@jwt_required()
def create():
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type == AccountType.student:
        data = request.get_json()

        previous = ClassApprove.query.filter_by(classroomId=data['classroom_id'], studentId=userId).first()
        if previous:
            return jsonify({'error': 'Already exist'}), 403

        classApprove = ClassApprove(data['classroom_id'], userId, False)

        try:
            db.session.add(classApprove)
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        return '', 200
    else:
        return jsonify({'error': 'Account type mismatch'}), 403

# 요청 승인 (교수)
@approval.route('/grant', methods=['POST'])
@jwt_required()
def approve():
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type == AccountType.professor:
        data = request.get_json()
        classApprove = ClassApprove.query.filter_by(classroomId=data['classroom_id'], studentId=data['student_id']).first()
        classApprove.approve = True

        try:
            db.session.add(classApprove)
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        return '', 200
    else:
        return jsonify({'error': 'Account type mismatch'}), 403

# 요청 승인 취소 (교수)
@approval.route('/revoke', methods=['POST'])
@jwt_required()
def approve():
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    if user.type == AccountType.professor:
        data = request.get_json()
        classApprove = ClassApprove.query.filter_by(classroomId=data['classroom_id'], studentId=data['student_id']).first()
        classApprove.approve = False

        try:
            db.session.add(classApprove)
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        return '', 200
    else:
        return jsonify({'error': 'Account type mismatch'}), 403
