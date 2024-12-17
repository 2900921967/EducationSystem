from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import hashlib

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Password123$',
    'database': 'EducationSystem',
}

# 数据库连接函数
def get_db_connection():
    return pymysql.connect(**db_config)

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO Users (username, password, user_type) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, hashed_password, user_type))
            conn.commit()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
        except pymysql.IntegrityError:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('register.html')

# 登录页面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM Users WHERE username=%s AND password=%s"
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['user_type'] = user[3]  # user_type
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')

# 功能主界面
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_type = session['user_type']
    username = session['username']

    # 根据用户类型显示不同内容
    if user_type == 'admin':
        return render_template('dashboard_admin.html', username=username)
    elif user_type == 'teacher':
        return render_template('dashboard_teacher.html', username=username)
    elif user_type == 'student':
        return render_template('dashboard_student.html', username=username)
    else:
        flash('Invalid user type.')
        return redirect(url_for('login'))

# 退出登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 管理用户
@app.route('/admin/users', methods=['GET', 'POST'])
def manage_users():
    if 'username' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            username = request.form['username']
            password = hashlib.sha256(request.form['password'].encode()).hexdigest()
            user_type = request.form['user_type']
            query = "INSERT INTO Users (username, password, user_type) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, password, user_type))
            conn.commit()
        elif action == 'delete':
            user_id = request.form['user_id']
            query = "DELETE FROM Users WHERE id=%s"
            cursor.execute(query, (user_id,))
            conn.commit()

    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    conn.close()

    return render_template('admin_users.html', users=users)

# 管理课程
@app.route('/admin/courses', methods=['GET', 'POST'])
def manage_courses():
    if 'username' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            course_name = request.form['course_name']
            course_code = request.form['course_code']
            credits = request.form['credits']
            query = "INSERT INTO Courses (course_name, course_code, credits) VALUES (%s, %s, %s)"
            cursor.execute(query, (course_name, course_code, credits))
            conn.commit()
        elif action == 'delete':
            course_id = request.form['course_id']
            query = "DELETE FROM Courses WHERE id=%s"
            cursor.execute(query, (course_id,))
            conn.commit()

    cursor.execute("SELECT * FROM Courses")
    courses = cursor.fetchall()
    conn.close()

    return render_template('admin_courses.html', courses=courses)

# 查看分配的课程
@app.route('/teacher/courses')
def view_assigned_courses():
    if 'username' not in session or session['user_type'] != 'teacher':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT Courses.course_name, Courses.course_code, Courses.credits 
        FROM TeacherCourses
        JOIN Courses ON TeacherCourses.course_id = Courses.id
        WHERE TeacherCourses.teacher_id = (
            SELECT id FROM Users WHERE username=%s
        )
    """
    cursor.execute(query, (session['username'],))
    courses = cursor.fetchall()
    conn.close()

    return render_template('teacher_courses.html', courses=courses)

# 给学生打分
@app.route('/teacher/grade', methods=['GET', 'POST'])
def grade_students():
    if 'username' not in session or session['user_type'] != 'teacher':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # 处理 POST 请求：添加/更新成绩或删除成绩
    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'delete':
            # 删除成绩
            grade_id = request.form['grade_id']
            query = "DELETE FROM Grades WHERE id=%s"
            cursor.execute(query, (grade_id,))
            conn.commit()
        else:
            # 添加/更新成绩
            student_id = request.form['student_id']
            course_id = request.form['course_id']
            grade = request.form['grade']
            query = """
                INSERT INTO Grades (student_id, course_id, grade)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE grade=%s
            """
            cursor.execute(query, (student_id, course_id, grade, grade))
            conn.commit()

    # 获取课程和学生列表
    cursor.execute("SELECT id, course_name FROM Courses")
    courses = cursor.fetchall()

    cursor.execute("SELECT id, username FROM Users WHERE user_type='student'")
    students = cursor.fetchall()

    # 查询已打分的成绩
    query = """
        SELECT Grades.id, Users.username, Courses.course_name, Grades.grade
        FROM Grades
        JOIN Users ON Grades.student_id = Users.id
        JOIN Courses ON Grades.course_id = Courses.id
    """
    cursor.execute(query)
    graded_students = cursor.fetchall()

    conn.close()
    return render_template('teacher_grade.html', courses=courses, students=students, graded_students=graded_students)

# 查看选修的课程
@app.route('/student/courses')
def view_courses():
    if 'username' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT Courses.course_name, Courses.course_code, Courses.credits 
        FROM Grades
        JOIN Courses ON Grades.course_id = Courses.id
        WHERE Grades.student_id = (
            SELECT id FROM Users WHERE username=%s
        )
    """
    cursor.execute(query, (session['username'],))
    courses = cursor.fetchall()
    conn.close()

    return render_template('student_courses.html', courses=courses)

# 查看自己的成绩
@app.route('/student/grades')
def view_grades():
    if 'username' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT Courses.course_name, Grades.grade 
        FROM Grades
        JOIN Courses ON Grades.course_id = Courses.id
        WHERE Grades.student_id = (
            SELECT id FROM Users WHERE username=%s
        )
    """
    cursor.execute(query, (session['username'],))
    grades = cursor.fetchall()
    conn.close()

    return render_template('student_grades.html', grades=grades)

# 管理教师课程
@app.route('/admin/assign_courses', methods=['GET', 'POST'])
def assign_courses():
    if 'username' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        course_id = request.form['course_id']
        try:
            query = "INSERT INTO TeacherCourses (teacher_id, course_id) VALUES (%s, %s)"
            cursor.execute(query, (teacher_id, course_id))
            conn.commit()
            flash('Course assigned successfully!')
        except pymysql.IntegrityError:
            flash('This course is already assigned to the teacher.')

    # 获取所有教师
    cursor.execute("SELECT id, username FROM Users WHERE user_type='teacher'")
    teachers = cursor.fetchall()

    # 获取所有课程
    cursor.execute("SELECT id, course_name FROM Courses")
    courses = cursor.fetchall()

    # 获取分配记录
    query = """
        SELECT TeacherCourses.id, Users.username, Courses.course_name 
        FROM TeacherCourses
        JOIN Users ON TeacherCourses.teacher_id = Users.id
        JOIN Courses ON TeacherCourses.course_id = Courses.id
    """
    cursor.execute(query)
    assignments = cursor.fetchall()

    conn.close()
    return render_template('admin_assign_courses.html', teachers=teachers, courses=courses, assignments=assignments)

# 删除分配记录
@app.route('/admin/delete_assignment', methods=['POST'])
def delete_assignment():
    if 'username' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    assignment_id = request.form['assignment_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM TeacherCourses WHERE id=%s"
    cursor.execute(query, (assignment_id,))
    conn.commit()
    conn.close()

    flash('Assignment removed successfully!')
    return redirect(url_for('assign_courses'))

if __name__ == '__main__':
    app.run(debug=True)
