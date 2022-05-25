from unittest import TestCase
from flask.json import jsonify
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import Account, Classroom, TestResult, db, AccountType, Assignment

assignment = Blueprint('assignment', __name__, url_prefix='/assignment')

# 강의 전체 과제 조회
@assignment.route('/', methods=['GET'])
@jwt_required()
def lookup():
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assigns = Assignment.filter_by(classroomId=data['classroom_id'])

    # 권한 체크 필요

    return jsonify([{"id": a.id, "name": a.title, "date": a.date, "start_date": a.startDate, "end_date": a.endDate} for a in assigns]), 200

# 과제 생성
@assignment.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403

    # 권한 체크 필요
    
    assign = Assignment(userId, data['classroom_id'], data['title'], data['desc'], data['start_date'], data['end_date'], data['parent_id'])

    try:
        db.session.add(assign)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

# 과제 조회
@assignment.route('/<id>', methods=['GET'])
@jwt_required()
def lookup_detail(id):
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assign = Assignment.filter_by(id=id).first()

    if assign.enable == False:
        return '', 404

    # 권한 체크 필요

    return jsonify(assign), 200

# 과제/댓글 수정
@assignment.route('/<id>', methods=['PUT'])
@jwt_required()
def modify(id):
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assign = Assignment.filter_by(id=id).first()

    # 권한 체크 필요

    assign.title = data['title']
    assign.desc = data['desc']
    assign.startDate = data['start_date']
    assign.endDate = data['end_date']

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

# 과제/댓글 비활성화
@assignment.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assign = Assignment.filter_by(id=id).first()

    # 권한 체크 필요

    assign.enable = False

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

# 피드백 등록
@assignment.route('/<id>/feedback', methods=['POST'])
@jwt_required()
def create_feedback(id):
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assign = Assignment.filter_by(id=id).first()

    # 권한 체크 필요

    assign.feedback = data['feedback']
    assign.score = data['score']

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

# 테스트케이스 목록 조회
@assignment.route('/<id>/testcase', methods=['GET'])
@jwt_required()
def lookup_testcase(id):    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    testCases = TestCase.filter_by(assignmentId=id)
    
    return jsonify(testCases), 200

# 테스트 결과 목록 조회
@assignment.route('/<id>/testresult', methods=['GET'])
@jwt_required()
def lookup_testcase(id):    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    testResults = TestResult.filter_by(assignmentId=id)
    
    return jsonify(testResults), 200