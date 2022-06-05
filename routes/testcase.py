from flask.json import jsonify
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import Account, db, Testcase

testcase = Blueprint('testcase', __name__, url_prefix='/testcase')

@testcase.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403

    # 권한 체크 필요
    
    testcase = Testcase(userId, data['assignment_id'], data['input'], data['output'])

    try:
        db.session.add(testcase)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

@testcase.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403

    testcase = Testcase.query.filter_by(id=id).first()

    testcase.enable = False

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200