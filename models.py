"""
数据操作模型 - CRUD操作
"""

import pymysql
from database import get_connection, DB_NAME
from datetime import datetime


class TeacherModel:
    """教师模型"""

    @staticmethod
    def get_all():
        """获取所有教师"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM teachers WHERE status = 'active'")
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_id(teacher_id):
        """根据ID获取教师"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def create(data):
        """创建教师"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO teachers (teacher_no, name, gender, phone, email, title, department, hire_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data['teacher_no'], data['name'], data.get('gender', '男'),
                    data.get('phone', ''), data.get('email', ''),
                    data.get('title', ''), data.get('department', ''),
                    data.get('hire_date')
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()


class StudentModel:
    """学员模型"""

    @staticmethod
    def get_all():
        """获取所有学员"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM students WHERE status = 'active'")
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_id(student_id):
        """根据ID获取学员"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_by_name(name):
        """根据姓名模糊查询学员"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM students WHERE name LIKE %s", (f'%{name}%',))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create(data):
        """创建学员"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO students (student_no, name, gender, phone, email, birthday, address, register_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data['student_no'], data['name'], data.get('gender', '男'),
                    data.get('phone', ''), data.get('email', ''),
                    data.get('birthday'), data.get('address', ''),
                    data.get('register_date', datetime.now().date())
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def update(student_id, data):
        """更新学员信息"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                fields = []
                values = []
                for key, value in data.items():
                    if value is not None:
                        fields.append(f"{key} = %s")
                        values.append(value)
                values.append(student_id)
                sql = f"UPDATE students SET {', '.join(fields)} WHERE id = %s"
                cursor.execute(sql, values)
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()


class CourseModel:
    """课程模型"""

    @staticmethod
    def get_all():
        """获取所有课程（带教师信息）"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, t.name as teacher_name, t.title as teacher_title
                    FROM courses c
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    WHERE c.status != 'closed'
                    ORDER BY c.created_at DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_id(course_id):
        """根据ID获取课程详情"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, t.name as teacher_name, t.phone as teacher_phone
                    FROM courses c
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    WHERE c.id = %s
                """, (course_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_open_courses():
        """获取开放报名的课程"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, t.name as teacher_name,
                           (c.max_students - c.enrolled_count) as available_seats
                    FROM courses c
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    WHERE c.status = 'open' AND c.enrolled_count < c.max_students
                    ORDER BY c.start_date
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create(data):
        """创建课程"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO courses (course_no, name, teacher_id, description, category, 
                            total_hours, price, max_students, start_date, end_date, schedule, location, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data['course_no'], data['name'], data['teacher_id'],
                    data.get('description', ''), data.get('category', ''),
                    data.get('total_hours', 0), data.get('price', 0),
                    data.get('max_students', 30), data.get('start_date'),
                    data.get('end_date'), data.get('schedule', ''),
                    data.get('location', ''), data.get('status', 'draft')
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()


class CourseBookingModel:
    """课程预约模型"""

    @staticmethod
    def get_all_bookings():
        """获取所有预约记录"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT cb.*, s.name as student_name, c.name as course_name
                    FROM course_bookings cb
                    LEFT JOIN students s ON cb.student_id = s.id
                    LEFT JOIN courses c ON cb.course_id = c.id
                    ORDER BY cb.booking_date DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_student(student_id):
        """获取学员的所有预约"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT cb.*, c.name as course_name, c.schedule, c.location,
                           t.name as teacher_name
                    FROM course_bookings cb
                    LEFT JOIN courses c ON cb.course_id = c.id
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    WHERE cb.student_id = %s AND cb.status != 'cancelled'
                    ORDER BY cb.booking_date DESC
                """, (student_id,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create_booking(student_id, course_id, remark=None):
        """创建预约"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                # 检查课程是否存在且可预约
                cursor.execute("""
                    SELECT id, name, max_students, enrolled_count, status 
                    FROM courses WHERE id = %s
                """, (course_id,))
                course = cursor.fetchone()

                if not course:
                    return {'success': False, 'message': '课程不存在'}

                if course['status'] != 'open':
                    return {'success': False, 'message': '课程未开放报名'}

                if course['enrolled_count'] >= course['max_students']:
                    return {'success': False, 'message': '课程已满员'}

                # 检查是否已预约
                cursor.execute("""
                    SELECT id FROM course_bookings 
                    WHERE student_id = %s AND course_id = %s AND status != 'cancelled'
                """, (student_id, course_id))
                if cursor.fetchone():
                    return {'success': False, 'message': '您已预约过该课程'}

                # 生成预约编号
                booking_no = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}{student_id}{course_id}"

                # 创建预约
                cursor.execute("""
                    INSERT INTO course_bookings (booking_no, student_id, course_id, remark, status)
                    VALUES (%s, %s, %s, %s, 'pending')
                """, (booking_no, student_id, course_id, remark))

                conn.commit()

                return {
                    'success': True,
                    'message': '预约成功，请等待确认',
                    'booking_id': cursor.lastrowid,
                    'booking_no': booking_no
                }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'预约失败: {str(e)}'}
        finally:
            conn.close()

    @staticmethod
    def confirm_booking(booking_id):
        """确认预约（管理员操作）"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                # 获取预约信息
                cursor.execute("""
                    SELECT cb.*, c.max_students, c.enrolled_count 
                    FROM course_bookings cb
                    LEFT JOIN courses c ON cb.course_id = c.id
                    WHERE cb.id = %s
                """, (booking_id,))
                booking = cursor.fetchone()

                if not booking:
                    return {'success': False, 'message': '预约记录不存在'}

                if booking['status'] != 'pending':
                    return {'success': False, 'message': f'当前状态无法确认: {booking["status"]}'}

                if booking['enrolled_count'] >= booking['max_students']:
                    return {'success': False, 'message': '课程已满员，无法确认'}

                # 更新预约状态
                cursor.execute("""
                    UPDATE course_bookings 
                    SET status = 'confirmed', confirmed_at = NOW()
                    WHERE id = %s
                """, (booking_id,))

                # 更新课程已报名人数
                cursor.execute("""
                    UPDATE courses 
                    SET enrolled_count = enrolled_count + 1
                    WHERE id = %s
                """, (booking['course_id'],))

                conn.commit()
                return {'success': True, 'message': '预约已确认'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'确认失败: {str(e)}'}
        finally:
            conn.close()

    @staticmethod
    def cancel_booking(booking_id, reason=None):
        """取消预约"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT course_id, status FROM course_bookings WHERE id = %s
                """, (booking_id,))
                booking = cursor.fetchone()

                if not booking:
                    return {'success': False, 'message': '预约记录不存在'}

                if booking['status'] == 'cancelled':
                    return {'success': False, 'message': '预约已取消'}

                # 更新预约状态
                cursor.execute("""
                    UPDATE course_bookings 
                    SET status = 'cancelled', cancel_reason = %s, cancel_date = NOW()
                    WHERE id = %s
                """, (reason, booking_id))

                # 如果是已确认的预约，减少课程已报名人数
                if booking['status'] == 'confirmed':
                    cursor.execute("""
                        UPDATE courses 
                        SET enrolled_count = GREATEST(enrolled_count - 1, 0)
                        WHERE id = %s
                    """, (booking['course_id'],))

                conn.commit()
                return {'success': True, 'message': '预约已取消'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'取消失败: {str(e)}'}
        finally:
            conn.close()

    @staticmethod
    def mark_attendance(booking_id):
        """标记签到"""
        conn = get_connection()
        conn.select_db(DB_NAME)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE course_bookings 
                    SET attendance_marked = TRUE, status = 'completed'
                    WHERE id = %s AND status = 'confirmed'
                """, (booking_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    return {'success': True, 'message': '签到成功'}
                return {'success': False, 'message': '签到失败，请确认预约状态'}
        finally:
            conn.close()