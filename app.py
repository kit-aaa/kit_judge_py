from gevent.pywsgi import WSGIServer
from flask import Flask
from flask_cors import CORS
from database import db, TokenBlocklist
from flask_jwt_extended import JWTManager
from datetime import timedelta

from routes import *
import util
from util import populate_data

app = Flask(__name__)
CORS(app)

ACCESS_EXPIRES = timedelta(hours=1)

app.config['SECRET_KEY'] = 'CHANGEME!'

app.config['JWT_SECRET_KEY'] = 'CHANGEMEPLZ!'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES

jwt = JWTManager(app)

# SQLite for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(approval.approval)
app.register_blueprint(assignment.assignment)
app.register_blueprint(user.user)
app.register_blueprint(auth.auth)
app.register_blueprint(classroom.classroom)
app.register_blueprint(testcase.testcase)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None

if __name__ == "__main__":

    # Init database, 마이그레이션 아님
    db.app = app
    db.init_app(app)
    db.create_all()

    # 샘플데이터 삽입
    populate_data.populate()

    # 프로덕션에서 bind ip 변경할 것
    server = WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()