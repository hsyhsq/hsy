"""
Flask 后端主程序
运行: python app.py
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import CourseDB, BookingDB, TeacherDB

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/courses')
def get_courses():
    """获取所有课程"""
    courses = CourseDB.get_all()
    return jsonify({'success': True, 'data': courses})


@app.route('/api/courses/open')
def get_open_courses():
    """获取可预约课程"""
    courses = CourseDB.get_open_courses()
    return jsonify({'success': True, 'data': courses})


@app.route('/api/courses/<int:course_id>')
def get_course_detail(course_id):
    """获取课程详情"""
    course = CourseDB.get_by_id(course_id)
    if course:
        return jsonify({'success': True, 'data': course})
    return jsonify({'success': False, 'message': '课程不存在'}), 404


@app.route('/api/teachers')
def get_teachers():
    """获取所有教师"""
    teachers = TeacherDB.get_all()
    return jsonify({'success': True, 'data': teachers})


@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """创建预约"""
    data = request.json
    result = BookingDB.create_booking(
        student_name=data.get('student_name'),
        student_phone=data.get('student_phone'),
        course_id=data.get('course_id'),
        remark=data.get('remark')
    )
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """查询预约记录"""
    student_name = request.args.get('student_name')
    student_phone = request.args.get('student_phone')

    if not student_name:
        return jsonify({'success': False, 'message': '请提供姓名'}), 400

    bookings = BookingDB.get_by_student(student_name, student_phone)
    return jsonify({'success': True, 'data': bookings})


@app.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """取消预约"""
    data = request.json
    result = BookingDB.cancel_booking(booking_id, data.get('student_name'))
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)