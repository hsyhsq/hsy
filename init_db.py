"""
数据库初始化脚本
运行: python init_db.py
"""

import pymysql

# 修改为您的数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '111111',  # 请修改
    'charset': 'utf8mb4'
}

DB_NAME = 'course_booking_web'


def init_database():
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.select_db(DB_NAME)

            # 教师表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    teacher_no VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    avatar VARCHAR(200),
                    title VARCHAR(50),
                    department VARCHAR(100),
                    bio TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 学员表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    student_no VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    avatar VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 课程表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    course_no VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    teacher_id INT NOT NULL,
                    cover VARCHAR(200),
                    description TEXT,
                    category VARCHAR(50),
                    total_hours INT DEFAULT 0,
                    price DECIMAL(10,2) DEFAULT 0,
                    original_price DECIMAL(10,2),
                    max_students INT DEFAULT 30,
                    enrolled_count INT DEFAULT 0,
                    start_date DATE,
                    schedule VARCHAR(200),
                    location VARCHAR(100),
                    status ENUM('draft', 'open', 'ongoing', 'closed') DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
                )
            """)

            # 课程预约表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS course_bookings (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    booking_no VARCHAR(30) UNIQUE NOT NULL,
                    student_id INT NOT NULL,
                    course_id INT NOT NULL,
                    student_name VARCHAR(50) NOT NULL,
                    student_phone VARCHAR(20),
                    remark TEXT,
                    status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
                    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (course_id) REFERENCES courses(id)
                )
            """)

            # 插入示例教师数据
            cursor.execute("SELECT COUNT(*) as cnt FROM teachers")
            if cursor.fetchone()[0] == 0:
                teachers = [
                    ('T001', '张明远', 'https://picsum.photos/id/100/100/100', '教授', '计算机学院',
                     '10年教学经验，专注全栈开发'),
                    ('T002', '陈雅琳', 'https://picsum.photos/id/20/100/100', '副教授', '设计学院',
                     '前腾讯高级设计师，8年UI/UX经验'),
                    ('T003', '王瑞华', 'https://picsum.photos/id/26/100/100', '讲师', '数据科学学院',
                     'Kaggle竞赛导师，擅长数据分析'),
                    ('T004', '李婉晴', 'https://picsum.photos/id/29/100/100', '副教授', '人工智能学院',
                     'AI领域专家，发表多篇顶会论文'),
                ]
                cursor.executemany(
                    "INSERT INTO teachers (teacher_no, name, avatar, title, department, bio) VALUES (%s, %s, %s, %s, %s, %s)",
                    teachers
                )

            # 获取教师ID映射
            cursor.execute("SELECT id, teacher_no FROM teachers")
            teacher_map = {row[1]: row[0] for row in cursor.fetchall()}

            # 插入示例课程数据
            cursor.execute("SELECT COUNT(*) as cnt FROM courses")
            if cursor.fetchone()[0] == 0:
                courses = [
                    ('C001', 'Python全栈开发', teacher_map['T001'], 'https://picsum.photos/id/0/300/200',
                     '从零基础到全栈工程师，涵盖Python基础、Django、Flask、前端框架', '编程开发', 60, 2999, 3999, 25, 0,
                     '2024-06-01', '每周二、四 19:00-21:00', '教学楼A-101', 'open'),
                    ('C002', 'UI/UX设计实战', teacher_map['T002'], 'https://picsum.photos/id/10/300/200',
                     '产品设计思维、Figma工具、用户研究方法论', '设计创意', 40, 2499, 3299, 20, 0, '2024-06-03',
                     '每周一、三 19:00-21:00', '设计楼B-202', 'open'),
                    ('C003', '机器学习入门', teacher_map['T003'], 'https://picsum.photos/id/24/300/200',
                     '机器学习基础算法、Scikit-learn、实战项目', '人工智能', 50, 3299, 4299, 30, 0, '2024-06-05',
                     '每周五 19:00-22:00', '实验楼C-303', 'open'),
                    ('C004', '大模型应用开发', teacher_map['T004'], 'https://picsum.photos/id/88/300/200',
                     'GPT API、LangChain、AI应用构建实战', '人工智能', 40, 3999, 4999, 20, 0, '2024-07-01',
                     '每周六 14:00-18:00', '科技楼D-404', 'open'),
                ]
                cursor.executemany("""
                    INSERT INTO courses (course_no, name, teacher_id, cover, description, category, total_hours, price, original_price, max_students, enrolled_count, start_date, schedule, location, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, courses)

            conn.commit()
            print("✅ 数据库初始化成功！")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    init_database()