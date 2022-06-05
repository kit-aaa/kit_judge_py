from flask.json import jsonify
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from werkzeug.utils import secure_filename
import os

from database import Account, Classroom, TestResult, db, AccountType, Assignment, Testcase

assignment = Blueprint('assignment', __name__, url_prefix='/assignment')

# 업로드 허용할 확장자
ALLOWED_EXTENSIONS = {'zip', 'java'}

# 확장자 체크
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 강의 전체 과제 조회
@assignment.route('/', methods=['GET'])
@jwt_required()
def lookup():
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assigns = Assignment.query.filter_by(classroomId=data['classroom_id'])

    # 권한 체크 필요

    return jsonify([{"id": a.id, "name": a.title, "date": a.date.isoformat(), "start_date": a.startDate.isoformat(), "end_date": a.endDate.isoformat()} for a in assigns]), 200

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
    try:
        start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M:%S.%f')
        end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M:%S.%f')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    assign = Assignment(userId, data['classroom_id'], data['title'], data['desc'], start_date, end_date)

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
    
    assign = Assignment.query.filter_by(id=id).first()

    if assign.enable == False:
        return '', 404

    # 권한 체크 필요

    # 교수가 낸 과제면 parent_id, score, feedback, filename은 null
    return jsonify({'id': assign.id,
    'author_id': assign.authorId,
    'author_name': assign.author.name,
    'title': assign.title,
    'desc': assign.desc,
    'date': assign.date.isoformat(),
    'start_date': assign.startDate.isoformat(),
    'end_date': assign.endDate.isoformat(),
    'parent_id': assign.parentId,
    'score': assign.score,
    'feedback': assign.feedback,
    'filename': assign.filename}), 200

# 과제 수정
@assignment.route('/<id>', methods=['PUT'])
@jwt_required()
def modify(id):
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assign = Assignment.query.filter_by(id=id).first()

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

# 과제 비활성화(삭제)
@assignment.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assign = Assignment.query.filter_by(id=id).first()

    # 권한 체크 필요

    assign.enable = False

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return '', 200

# 과제 제출 (학생)
@assignment.route('/<id>/submit', methods=['POST'])
@jwt_required()
def submit(id):
    userId = get_jwt_identity()
    data = request.form.get('data')

    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'error': 'Blank file submitted'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        assign = Assignment(userId, data['classroom_id'], None, data['desc'], None, None)
        assign.parentId = id
        assign.filename = filename

        try:
            db.session.add(assign)
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return '', 200

# 제출 과제 조회 (교수)
@assignment.route('/<id>/submissions', methods=['GET'])
@jwt_required()
def lookup_submissions(id):
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assigns = Assignment.query.filter_by(parentId=id)

    # 권한 체크 필요

    return jsonify([{'id': assign.id, 'author_id': assign.authorId, 'date': assign.date.isoformat(), 'author_name': assign.author.name, 'score': assign.score} for assign in assigns]), 200

# 피드백 등록
@assignment.route('/<id>/feedback', methods=['POST'])
@jwt_required()
def create_feedback(id):
    data = request.get_json()
    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    assign = Assignment.query.filter_by(id=id).first()

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
    
    testcases = Testcase.query.filter_by(assignmentId=id)
    
    return jsonify([{'id': testcase.id, 'assignment_id': testcase.assignmentId, 'input': testcase.input, 'output': testcase.output, 'enable': testcase.enable} for testcase in testcases]), 200

# 테스트 결과 목록 조회
@assignment.route('/<id>/testresult', methods=['GET'])
@jwt_required()
def lookup_testresult(id):    
    userId = get_jwt_identity()
    user = Account.query.filter_by(id=userId).first()

    if user.disabled:
        return jsonify({'error': 'Account disabled'}), 403
    
    testResults = TestResult.query.filter_by(assignmentId=id)
    
    return jsonify([{'id': result.id, 'assignment_id': result.assignmentId, "testcase_id": result.testcaseId, "date": result.time, "is_success": result.success, "fail_cause": result.failCause} for result in testResults]), 200