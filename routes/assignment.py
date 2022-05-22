from flask.json import jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

assignment = Blueprint('assignment', __name__, url_prefix='/assignment')

@assignment.route('/', methods=['GET'])
@jwt_required()
def lookup():
    pass

@assignment.route('/', methods=['POST'])
@jwt_required()
def create():
    pass

@assignment.route('/<id>', methods=['GET'])
@jwt_required()
def lookup_detail(id):
    pass

@assignment.route('/<id>', methods=['PUT'])
@jwt_required()
def modify(id):
    pass

@assignment.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    pass

@assignment.route('/<id>/feedback', methods=['POST'])
@jwt_required()
def create_feedback(id):
    pass

@assignment.route('/<id>/result', methods=['GET'])
@jwt_required()
def lookup_testcase(id):
    pass