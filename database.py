"""
数据库操作模块
"""

import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '111111',  # 请修改
    'database': 'course_booking_web',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


class CourseDB:
    """课程相关操作"""

    @staticmethod
    def get_all():
        """获取所有课程（包含教师信息）"""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, t.name as teacher_name, t.avatar as teacher_avatar, t.title as teacher_title
                    FROM courses c
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    WHERE c.status != 'closed'
                    ORDER BY c.created_at DESC
                """)
                courses = cursor.fetchall()
                # 计算剩余名额
                for c in courses:
                    c['remaining_seats'] = c['max_students'] - c['enrolled_count']
                return courses
        finally:
            conn.close()

    @staticmethod
    def get_by_id(course_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, t.name as teacher_name, t.avatar as teacher_avatar, t.title as teacher_title, t.bio as teacher_bio
                    FROM courses c
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    WHERE c.id = %s
                """, (course_id,))
                course = cursor.fetchone()
                if course:
                    course['remaining_seats'] = course['max_students'] - course['enrolled_count']
                return course
        finally:
            conn.close()

    @staticmethod
    def get_open_courses():
        """获取可预约课程"""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, t.name as teacher_name, t.avatar as teacher_avatar
                    FROM courses c
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    WHERE c.status = 'open' AND c.enrolled_count < c.max_students
                    ORDER BY c.start_date
                """)
                courses = cursor.fetchall()
                for c in courses:
                    c['remaining_seats'] = c['max_students'] - c['enrolled_count']
                return courses
        finally:
            conn.close()


class BookingDB:
    """预约相关操作"""

    @staticmethod
    def create_booking(student_name, student_phone, course_id, remark=None):
        """创建预约"""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 检查课程状态
                cursor.execute("SELECT * FROM courses WHERE id = %s AND status = 'open'", (course_id,))
                course = cursor.fetchone()
                if not course:
                    return {'success': False, 'message': '课程不存在或未开放'}

                # 检查名额
                enrolled = course['enrolled_count']
                if enrolled >= course['max_students']:
                    return {'success': False, 'message': '课程已满员'}

                # 检查是否重复预约（同一姓名+课程）
                cursor.execute("""
                    SELECT id FROM course_bookings 
                    WHERE student_name = %s AND course_id = %s AND status != 'cancelled'
                """, (student_name, course_id))
                if cursor.fetchone():
                    return {'success': False, 'message': '您已预约过该课程'}

                # 查找或创建学员
                cursor.execute("SELECT id FROM students WHERE phone = %s OR (name = %s AND name != '')",
                               (student_phone, student_name))
                student = cursor.fetchone()

                if not student:
                    # 创建新学员
                    student_no = f"S{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    cursor.execute("""
                        INSERT INTO students (student_no, name, phone) VALUES (%s, %s, %s)
                    """, (student_no, student_name, student_phone))
                    student_id = cursor.lastrowid
                else:
                    student_id = student['id']

                # 生成预约编号
                booking_no = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}{student_id}{course_id}"

                # 创建预约
                cursor.execute("""
                    INSERT INTO course_bookings (booking_no, student_id, course_id, student_name, student_phone, remark)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (booking_no, student_id, course_id, student_name, student_phone, remark))

                conn.commit()

                return {
                    'success': True,
                    'message': '预约成功！请等待确认',
                    'booking_no': booking_no,
                    'student_id': student_id
                }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'预约失败: {str(e)}'}
        finally:
            conn.close()

    @staticmethod
    def confirm_booking(booking_id):
        """确认预约（管理员）"""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT course_id FROM course_bookings WHERE id = %s", (booking_id,))
                booking = cursor.fetchone()
                if booking:
                    cursor.execute("UPDATE courses SET enrolled_count = enrolled_count + 1 WHERE id = %s",
                                   (booking['course_id'],))
                    cursor.execute("UPDATE course_bookings SET status = 'confirmed' WHERE id = %s", (booking_id,))
                    conn.commit()
                    return {'success': True}
                return {'success': False}
        finally:
            conn.close()

    @staticmethod
    def cancel_booking(booking_id, student_name):
        """取消预约"""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT course_id, status FROM course_bookings 
                    WHERE id = %s AND student_name = %s
                """, (booking_id, student_name))
                booking = cursor.fetchone()

                if not booking:
                    return {'success': False, 'message': '预约记录不存在'}

                if booking['status'] == 'cancelled':
                    return {'success': False, 'message': '预约已取消'}

                # 更新预约状态
                cursor.execute("""
                    UPDATE course_bookings SET status = 'cancelled' WHERE id = %s
                """, (booking_id,))

                # 如果是已确认的预约，减少课程已报名人数
                if booking['status'] == 'confirmed':
                    cursor.execute("""
                        UPDATE courses SET enrolled_count = GREATEST(enrolled_count - 1, 0)
                        WHERE id = %s
                    """, (booking['course_id'],))

                conn.commit()
                return {'success': True, 'message': '取消成功'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'取消失败: {str(e)}'}
        finally:
            conn.close()

    @staticmethod
    def get_by_student(student_name, student_phone=None):
        """根据姓名获取预约记录"""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                if student_phone:
                    cursor.execute("""
                        SELECT cb.*, c.name as course_name, c.cover as course_cover, c.schedule, c.location
                        FROM course_bookings cb
                        LEFT JOIN courses c ON cb.course_id = c.id
                        WHERE cb.student_name = %s OR cb.student_phone = %s
                        ORDER BY cb.booking_date DESC
                    """, (student_name, student_phone))
                else:
                    cursor.execute("""
                        SELECT cb.*, c.name as course_name, c.cover as course_cover, c.schedule, c.location
                        FROM course_bookings cb
                        LEFT JOIN courses c ON cb.course_id = c.id
                        WHERE cb.student_name = %s
                        ORDER BY cb.booking_date DESC
                    """, (student_name,))
                return cursor.fetchall()
        finally:
            conn.close()


class TeacherDB:
    @staticmethod
    def get_all():
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM teachers")
                return cursor.fetchall()
        finally:
            conn.close()