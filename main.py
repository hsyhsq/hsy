"""
课程预约系统 - 命令行主程序
"""

from database import init_database, test_connection
from models import TeacherModel, StudentModel, CourseModel, CourseBookingModel
import os
from datetime import datetime


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_menu():
    """打印主菜单"""
    print_header("📚 课程预约管理系统")
    print("1. 学员管理")
    print("2. 课程管理")
    print("3. 课程预约")
    print("4. 我的预约")
    print("5. 教师管理")
    print("6. 数据统计")
    print("0. 退出系统")
    print("-" * 50)


def student_menu():
    """学员管理菜单"""
    while True:
        print_header("👨‍🎓 学员管理")
        print("1. 查看所有学员")
        print("2. 添加新学员")
        print("3. 搜索学员")
        print("4. 更新学员信息")
        print("0. 返回主菜单")

        choice = input("\n请选择操作: ").strip()

        if choice == '1':
            students = StudentModel.get_all()
            if students:
                print("\n📋 学员列表:")
                for s in students:
                    print(f"  {s['student_no']} | {s['name']} | {s['gender']} | {s['phone']}")
            else:
                print("暂无学员数据")

        elif choice == '2':
            print("\n添加新学员:")
            data = {
                'student_no': input("学号: ").strip(),
                'name': input("姓名: ").strip(),
                'gender': input("性别(男/女): ").strip(),
                'phone': input("电话: ").strip(),
                'email': input("邮箱: ").strip(),
                'birthday': input("生日(YYYY-MM-DD): ").strip() or None,
                'address': input("地址: ").strip(),
                'register_date': datetime.now().date()
            }
            student_id = StudentModel.create(data)
            print(f"✅ 学员添加成功，ID: {student_id}")

        elif choice == '3':
            keyword = input("请输入姓名关键字: ").strip()
            students = StudentModel.get_by_name(keyword)
            if students:
                for s in students:
                    print(f"  {s['student_no']} | {s['name']} | {s['phone']} | {s['email']}")
            else:
                print("未找到匹配学员")

        elif choice == '4':
            student_id = input("请输入学员ID: ").strip()
            print("留空则不修改该字段")
            data = {}
            name = input("姓名: ").strip()
            if name: data['name'] = name
            phone = input("电话: ").strip()
            if phone: data['phone'] = phone
            email = input("邮箱: ").strip()
            if email: data['email'] = email
            if data:
                StudentModel.update(int(student_id), data)
                print("✅ 学员信息已更新")
            else:
                print("未做任何修改")

        elif choice == '0':
            break
        else:
            print("无效选择")

        input("\n按回车键继续...")


def course_menu():
    """课程管理菜单"""
    while True:
        print_header("📖 课程管理")
        print("1. 查看所有课程")
        print("2. 查看可报名课程")
        print("3. 添加新课程")
        print("4. 课程详情")
        print("0. 返回主菜单")

        choice = input("\n请选择操作: ").strip()

        if choice == '1':
            courses = CourseModel.get_all()
            if courses:
                for c in courses:
                    seats = c['max_students'] - c['enrolled_count']
                    print(
                        f"  {c['course_no']} | {c['name']} | {c['teacher_name']} | 剩余{seats}/{c['max_students']} | {c['status']}")
            else:
                print("暂无课程")

        elif choice == '2':
            courses = CourseModel.get_open_courses()
            if courses:
                print("\n🔥 开放报名课程:")
                for c in courses:
                    seats = c['available_seats']
                    print(f"  {c['course_no']} | {c['name']} | {c['teacher_name']} | 剩余{seats}席 | ¥{c['price']}")
            else:
                print("暂无开放报名的课程")

        elif choice == '3':
            print("\n添加新课程:")
            teachers = TeacherModel.get_all()
            print("可选教师:")
            for t in teachers:
                print(f"  {t['id']}. {t['name']} ({t['title']})")

            data = {
                'course_no': input("课程编号: ").strip(),
                'name': input("课程名称: ").strip(),
                'teacher_id': int(input("教师ID: ").strip()),
                'description': input("课程描述: ").strip(),
                'category': input("课程分类: ").strip(),
                'total_hours': int(input("总课时: ").strip()),
                'price': float(input("价格: ").strip()),
                'max_students': int(input("最大人数: ").strip()),
                'start_date': input("开课日期(YYYY-MM-DD): ").strip(),
                'end_date': input("结课日期(YYYY-MM-DD): ").strip(),
                'schedule': input("上课时间: ").strip(),
                'location': input("上课地点: ").strip(),
                'status': 'open'
            }
            course_id = CourseModel.create(data)
            print(f"✅ 课程添加成功，ID: {course_id}")

        elif choice == '4':
            course_id = input("请输入课程ID: ").strip()
            course = CourseModel.get_by_id(int(course_id))
            if course:
                print(f"""
📌 课程详情:
   课程名称: {course['name']}
   课程编号: {course['course_no']}
   授课教师: {course['teacher_name']} ({course.get('teacher_title', '')})
   分类: {course['category']}
   总课时: {course['total_hours']}
   价格: ¥{course['price']}
   人数: {course['enrolled_count']}/{course['max_students']}
   上课时间: {course['schedule']}
   上课地点: {course['location']}
   课程描述: {course['description']}
                """)
            else:
                print("课程不存在")

        elif choice == '0':
            break

        input("\n按回车键继续...")


def booking_menu():
    """预约菜单"""
    # 先获取或选择学员
    name = input("请输入您的姓名: ").strip()
    students = StudentModel.get_by_name(name)

    if not students:
        print("未找到学员信息，请先注册")
        return

    if len(students) > 1:
        print("找到多个匹配学员，请选择:")
        for s in students:
            print(f"  {s['id']}. {s['name']} ({s['student_no']})")
        student_id = int(input("请输入学员ID: ").strip())
        student = next((s for s in students if s['id'] == student_id), None)
    else:
        student = students[0]

    if not student:
        print("学员选择无效")
        return

    print(f"\n👋 您好，{student['name']}！")

    while True:
        print_header("📅 课程预约")
        print("1. 查看可预约课程")
        print("2. 预约课程")
        print("0. 返回")

        choice = input("\n请选择: ").strip()

        if choice == '1':
            courses = CourseModel.get_open_courses()
            if courses:
                for c in courses:
                    print(
                        f"  {c['id']}. {c['name']} | {c['teacher_name']} | 剩余{c['available_seats']}席 | ¥{c['price']}")
            else:
                print("暂无开放预约的课程")

        elif choice == '2':
            course_id = int(input("请输入课程ID: ").strip())
            remark = input("备注(选填): ").strip()
            result = CourseBookingModel.create_booking(student['id'], course_id, remark)
            print(f"{'✅' if result['success'] else '❌'} {result['message']}")
            if result['success']:
                print(f"预约编号: {result.get('booking_no', '')}")

        elif choice == '0':
            break

        input("\n按回车键继续...")


def my_bookings_menu():
    """查看我的预约"""
    name = input("请输入您的姓名: ").strip()
    students = StudentModel.get_by_name(name)

    if not students:
        print("未找到学员信息")
        return

    student = students[0] if students else None

    while True:
        print_header(f"📋 {student['name']}的预约记录")
        bookings = CourseBookingModel.get_by_student(student['id'])

        if bookings:
            for b in bookings:
                status_emoji = {
                    'pending': '⏳待确认',
                    'confirmed': '✅已确认',
                    'completed': '🎓已完成',
                    'cancelled': '❌已取消'
                }.get(b['status'], b['status'])
                print(f"\n  预约号: {b['booking_no']}")
                print(f"  课程: {b['course_name']}")
                print(f"  状态: {status_emoji}")
                print(f"  时间: {b['booking_date']}")
                if b['schedule']:
                    print(f"  上课: {b['schedule']} @ {b['location']}")
        else:
            print("暂无预约记录")

        print("\n1. 取消预约")
        print("0. 返回")

        choice = input("\n请选择: ").strip()
        if choice == '1':
            booking_no = input("请输入预约编号: ").strip()
            result = CourseBookingModel.cancel_booking_by_no(booking_no, student['id'])
            print(f"{'✅' if result['success'] else '❌'} {result['message']}")
        elif choice == '0':
            break


def main():
    """主程序入口"""
    if not test_connection():
        print("请先配置数据库连接")
        return

    while True:
        clear_screen()
        print_menu()
        choice = input("请选择操作: ").strip()

        if choice == '1':
            student_menu()
        elif choice == '2':
            course_menu()
        elif choice == '3':
            booking_menu()
        elif choice == '4':
            my_bookings_menu()
        elif choice == '5':
            # 教师管理简单展示
            teachers = TeacherModel.get_all()
            print_header("👨‍🏫 教师列表")
            for t in teachers:
                print(f"  {t['teacher_no']} | {t['name']} | {t['title']} | {t['department']}")
            input("\n按回车键继续...")
        elif choice == '6':
            print_header("📊 数据统计")
            courses = CourseModel.get_all()
            total_students = len(StudentModel.get_all())
            total_bookings = len(CourseBookingModel.get_all_bookings())
            print(f"  总课程数: {len(courses)}")
            print(f"  总学员数: {total_students}")
            print(f"  总预约数: {total_bookings}")
            input("\n按回车键继续...")
        elif choice == '0':
            print("感谢使用课程预约系统，再见！")
            break
        else:
            print("无效选择")
            input("按回车键继续...")


if __name__ == '__main__':
    main()