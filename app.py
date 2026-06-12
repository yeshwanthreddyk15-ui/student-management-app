from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'admin' or 'student'
    students = db.relationship('Student', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


SUBJECTS = ['English', 'Maths', 'Science', 'Social', 'Computer']


def build_mark_summary(student):
    marks = {subject: None for subject in SUBJECTS}
    for mark in student.marks:
        if mark.subject in marks:
            marks[mark.subject] = mark.score
    total = sum(value for value in marks.values() if value is not None)
    percentage = 0
    max_total = len(SUBJECTS) * 100
    if max_total > 0:
        percentage = (total / max_total) * 100
    return {'student': student, 'marks': marks, 'total': total, 'percentage': percentage}


def compute_all_student_summaries():
    summaries = [build_mark_summary(student) for student in Student.query.all()]
    summaries.sort(key=lambda item: item['total'], reverse=True)

    rank = 0
    previous_total = None
    count = 0
    for item in summaries:
        count += 1
        if previous_total is None or item['total'] < previous_total:
            rank = count
        item['rank'] = rank
        previous_total = item['total']
    return summaries


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    marks = db.relationship('Mark', backref='student', lazy=True)


class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    admin_exists = User.query.filter_by(role='admin').first() is not None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'student')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        # Check if someone is trying to register as admin when admin already exists
        if role == 'admin' and admin_exists:
            flash('Admin already exists. You can only register as a student.', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', admin_exists=admin_exists)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        student_summaries = compute_all_student_summaries()
        student_list = sorted(
            student_summaries,
            key=lambda item: (item['student'].user.username if item['student'].user else item['student'].name).lower()
        )
        return render_template('index.html', student_summaries=student_summaries, student_list=student_list, subjects=SUBJECTS)

    student = Student.query.filter_by(user_id=current_user.id).first()
    student_summary = None
    if student:
        all_summaries = compute_all_student_summaries()
        student_summary = next((item for item in all_summaries if item['student'].id == student.id), None)
    return render_template('index.html', student=student, subjects=SUBJECTS, summary=student_summary)


@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Only admin can view users', 'danger')
        return redirect(url_for('index'))
    all_users = User.query.all()
    return render_template('users.html', users=all_users)


@app.route('/student/new', methods=['GET', 'POST'])
@login_required
def new_student():
    if current_user.role != 'admin':
        flash('Only admins can add students', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        course = request.form.get('course')
        password = request.form.get('password')
        username = name

        if not name or not password:
            flash('Name and password are required for the student account.', 'danger')
            return redirect(url_for('new_student'))

        if User.query.filter_by(username=username).first():
            flash('A student with this name already exists. Please use a different name.', 'danger')
            return redirect(url_for('new_student'))

        user = User(username=username, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        s = Student(name=name, email=email, course=course, user_id=user.id)
        db.session.add(s)
        db.session.commit()
        flash('Student added successfully with student account.', 'success')
        return redirect(url_for('index'))

    return render_template('student_form.html', student=None)


@app.route('/student/<int:id>')
@login_required
def view_student(id):
    student = Student.query.get_or_404(id)
    if current_user.role != 'admin' and student.user_id != current_user.id:
        flash('You do not have permission to view this profile', 'danger')
        return redirect(url_for('index'))

    all_summaries = compute_all_student_summaries()
    student_summary = next((item for item in all_summaries if item['student'].id == student.id), None)
    return render_template('student_profile.html', student=student, subjects=SUBJECTS, summary=student_summary)


@app.route('/student/<int:id>/marks/edit', methods=['GET', 'POST'])
@login_required
def edit_marks(id):
    if current_user.role != 'admin':
        flash('Only admins can edit marks', 'danger')
        return redirect(url_for('index'))

    student = Student.query.get_or_404(id)
    existing_marks = {mark.subject: mark for mark in student.marks}

    if request.method == 'POST':
        for subject in SUBJECTS:
            key = subject.replace(' ', '_').lower()
            score_value = request.form.get(f'score_{key}')
            if score_value is not None and score_value.strip() != '':
                score = float(score_value)
                if subject in existing_marks:
                    existing_marks[subject].score = score
                else:
                    db.session.add(Mark(student_id=student.id, subject=subject, score=score))
            elif subject in existing_marks:
                db.session.delete(existing_marks[subject])

        db.session.commit()
        flash('Marks updated successfully', 'success')
        return redirect(url_for('view_student', id=student.id))

    return render_template('student_marks.html', student=student, subjects=SUBJECTS)


@app.route('/student/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if current_user.role != 'admin' and student.user_id != current_user.id:
        flash('You do not have permission to edit this student', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email')
        student.course = request.form.get('course')
        db.session.commit()
        flash('Student updated successfully', 'success')
        return redirect(url_for('index'))
    return render_template('student_form.html', student=student)


@app.route('/student/<int:id>/delete', methods=['POST'])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    
    if current_user.role != 'admin' and student.user_id != current_user.id:
        flash('You do not have permission to delete this student', 'danger')
        return redirect(url_for('index'))

    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
