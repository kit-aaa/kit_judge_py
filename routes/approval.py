from flask.json import jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

approval = Blueprint('approval', __name__, url_prefix='/approval')

@approval.route('/', methods=['GET'])
@jwt_required()
def lookup():
    pass

@approval.route('/request', methods=['POST'])
@jwt_required()
def create():
    pass

@approval.route('/grant', methods=['POST'])
@jwt_required()
def modify(id):
    pass
