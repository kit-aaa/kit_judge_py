from flask.json import jsonify
from flask import Blueprint, request
from database import Account, TokenBlocklist, db

from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, create_refresh_token

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Account.query.filter_by(email=data['email']).first()

    if user:
        if user.disabled:
            return jsonify({'error': 'Account disabled'}), 403
            
        if user.check_password(data['password']):
            return jsonify({'access_token': create_access_token(identity=user.id), 'refresh_token': create_refresh_token(identity=user.id)}), 200

    return jsonify({'error': 'Authentication failed'}), 401

@auth.route('/logout', methods=['DELETE'])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, type=ttype, created_at=now))
    db.session.commit()
    return '', 200

@auth.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200
