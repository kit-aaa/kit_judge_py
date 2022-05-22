from flask.json import jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

classroom = Blueprint('classroom', __name__, url_prefix='/classroom')

@classroom.route('/', methods=['POST'])
@jwt_required()
def create():
    pass

@classroom.route('/<id>', methods=['GET'])
@jwt_required()
def lookup(id):
    pass

@classroom.route('/<id>', methods=['PUT'])
@jwt_required()
def modify(id):
    pass

@classroom.route('/<id>', methods=['DELETE'])
@jwt_required()
def disable(id):
    pass

@classroom.route('/<id>/member', methods=['GET'])
@jwt_required()
def lookup_member(id):
    pass

@classroom.route('/<id>/assignment', methods=['GET'])
@jwt_required()
def lookup_assignment(id):
    pass