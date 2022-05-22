from flask.json import jsonify
from flask import Blueprint, request
from database import db, Account
from flask_jwt_extended import jwt_required, get_jwt_identity

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/', methods=['POST'])
def create():
    data = request.get_json()
    account = Account(data['email'], data['password'], data['name'], data['type'], data['student_id'])
    try:
        db.session.add(account)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return '', 200

@user.route('/me', methods=['PUT'])
@jwt_required()
def modify():
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403

    data = request.get_json()

    user.email = data['email'];
    user.password = data['password'];
    user.name = data['name'];
    user.studentId = data['student_id'];

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@user.route('/me', methods=['DELETE'])
@jwt_required()
def disable():
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    user.disabled = True

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user.route('/me', methods=['GET'])
@jwt_required()
def lookup():
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403

    return jsonify({"email": user.email, "name": user.name, "type": user.type, "student_id": user.studentId}), 200
