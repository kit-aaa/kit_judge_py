from flask.json import jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

testcase = Blueprint('testcase', __name__, url_prefix='/testcase')

@testcase.route('/', methods=['POST'])
@jwt_required()
def create():
    pass

@testcase.route('/<id>', methods=['POST'])
@jwt_required()
def lookup_detail(id):
    pass

@testcase.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    pass
