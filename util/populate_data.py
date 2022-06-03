from database import *
from datetime import datetime, timedelta

def populate():
    
    # 계정
    user_student = Account("stu1@test.com", "stu1", "홍길동", AccountType.student, 20201111)
    user_student2 = Account("stu2@test.com", "stu2", "김길동", AccountType.student, 20222222)
    user_professor = Account("prof1@test.com", "prof1", "김교수", AccountType.professor, None)
    user_professor2 = Account("prof2@test.com", "prof2", "박교수", AccountType.professor, None)
    user_admin = Account("admin@test.com", "admin", "관리자", AccountType.admin, None)

    db.session.add(user_student)
    db.session.add(user_student2)
    db.session.add(user_professor)
    db.session.add(user_professor2)
    db.session.add(user_admin)

    db.session.commit()

    # 강의실
    prof1_classroom = Classroom("강의실1", "2022", "1", 3)
    prof2_classroom = Classroom("강의실2", "2022", "3", 4)

    db.session.add(prof1_classroom)
    db.session.add(prof2_classroom)

    db.session.commit()

    # 과제
    classroom1_assign = Assignment(3, 1, "강의실1 과제", "아시죠?", datetime.now() - timedelta(days=14), datetime.now() + timedelta(days=14))
    classroom1_assign2 = Assignment(3, 1, "강의실1 과제2", "테스트 숙제", datetime.now() - timedelta(days=14), datetime.now() + timedelta(days=14))
    classroom2_assign = Assignment(4, 2, "강의실2 과제", "수업시간에 이야기 한거 제출하세요", datetime.now() - timedelta(days=14), datetime.now() + timedelta(days=14))
    classroom2_assign2 = Assignment(4, 2, "강의실2 과제2", "수업시간에 이야기 한거 제출하세요!!!!!", datetime.now() - timedelta(days=14), datetime.now() + timedelta(days=14))

    db.session.add(classroom1_assign)
    db.session.add(classroom1_assign2)
    db.session.add(classroom2_assign)
    db.session.add(classroom2_assign2)

    db.session.commit()

    # 강의실 이수생
    student_classroom1_approve = ClassApprove(1, 1, True)
    student_classroom2_noapprove = ClassApprove(2, 1, False)

    student2_classroom1_approve = ClassApprove(1, 2, True)
    student2_classroom2_approve = ClassApprove(2, 2, True)

    db.session.add(student_classroom1_approve)
    db.session.add(student_classroom2_noapprove)
    db.session.add(student2_classroom1_approve)
    db.session.add(student2_classroom2_approve)

    db.session.commit()