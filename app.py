from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "study_space_unified_secure_key_123"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_space_unified.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- LOGIN MANAGER SETUP ---
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# --- DATABASE MODELS ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='owner', lazy=True, cascade="all, delete-orphan")
    exams = db.relationship('Exam', backref='owner', lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship('DailyTask', backref='owner', lazy=True, cascade="all, delete-orphan")
    resources = db.relationship('Resource', backref='owner', lazy=True, cascade="all, delete-orphan")
    notes = db.relationship('Note', backref='owner', lazy=True, cascade="all, delete-orphan")

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50))
    due_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DailyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    content = db.Column(db.Text, nullable=False)
    emoji = db.Column(db.String(10), default="💡")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- AUTOMATIC DATABASE CREATION ---
with app.app_context():
    db.create_all()

# --- USER LOADER CALLBACK ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- ADMIN DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access Denied: Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- AUTH ROUTES ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login details', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ADMIN ROUTES ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users, total_users=len(users), total_assignments=Assignment.query.count())

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own admin account!", "danger")
        return redirect(url_for('admin_dashboard'))
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"User deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

# --- DASHBOARD & ACADEMIC TRACKER ROUTES ---
@app.route('/')
@login_required
def dashboard():
    assignments = Assignment.query.filter_by(user_id=current_user.id).order_by(Assignment.due_date.asc()).all()
    exams = Exam.query.filter_by(user_id=current_user.id).order_by(Exam.exam_date.asc()).all()
    daily_tasks = DailyTask.query.filter_by(user_id=current_user.id).all()
    
    total = len(daily_tasks)
    done = len([t for t in daily_tasks if t.is_done])
    progress = (done / total * 100) if total > 0 else 0
    
    return render_template('index.html', 
                           assignments=assignments, 
                           exams=exams, 
                           daily_tasks=daily_tasks, 
                           progress=progress,
                           now=datetime.now())

@app.route('/add_assignment', methods=['POST'])
@login_required
def add_assignment():
    title = request.form.get('title')
    subject = request.form.get('subject')
    date_str = request.form.get('due_date')
    if title and date_str:
        due_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        db.session.add(Assignment(title=title, subject=subject, due_date=due_date, user_id=current_user.id))
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_exam', methods=['POST'])
@login_required
def add_exam():
    subject = request.form.get('subject')
    date_str = request.form.get('exam_date')
    if subject and date_str:
        exam_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        db.session.add(Exam(subject=subject, exam_date=exam_date, user_id=current_user.id))
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    task_name = request.form.get('task_name')
    if task_name:
        db.session.add(DailyTask(task_name=task_name, user_id=current_user.id))
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/toggle_task/<int:id>')
@login_required
def toggle_task(id):
    task = DailyTask.query.get(id)
    if task and task.user_id == current_user.id:
        task.is_done = not task.is_done
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_assignment/<int:id>')
@login_required
def delete_assignment(id):
    item = Assignment.query.get(id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_exam/<int:id>')
@login_required
def delete_exam(id):
    item = Exam.query.get(id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:id>')
@login_required
def delete_task(id):
    item = DailyTask.query.get(id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('dashboard'))

# --- RESOURCE API ENDPOINTS ---
@app.route("/api/resources", methods=["GET"])
@login_required
def get_resources():
    resources = Resource.query.filter_by(user_id=current_user.id).order_by(Resource.id.desc()).all()
    return jsonify([{"id": r.id, "title": r.title, "url": r.url, "category": r.category} for r in resources])

@app.route("/api/resources", methods=["POST"])
@login_required
def add_resource():
    data = request.get_json()
    title = data.get("title", "").strip()
    url = data.get("url", "").strip()
    category = data.get("category", "").strip()

    if not title or not url or not category:
        return jsonify({"error": "All fields are required"}), 400

    new_res = Resource(title=title, url=url, category=category, user_id=current_user.id)
    db.session.add(new_res)
    db.session.commit()

    return jsonify({"id": new_res.id, "title": new_res.title, "url": new_res.url, "category": new_res.category}), 201

# --- NOTE API ENDPOINTS ---
@app.route("/api/notes", methods=["GET"])
@login_required
def get_notes():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.id.desc()).all()
    return jsonify([{"id": n.id, "title": n.title, "content": n.content, "emoji": n.emoji} for n in notes])


@app.route("/api/notes", methods=["POST"])
@login_required
def add_note():
    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    emoji = data.get("emoji", "💡").strip()

    if not content:
        return jsonify({"error": "Note content cannot be empty"}), 400
    
    new_note = Note(title=title, content=content, emoji=emoji, user_id=current_user.id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"id": new_note.id, "title": new_note.title, "content": new_note.content, "emoji": new_note.emoji}), 201

@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted successfully"}), 200

# --- START THE SERVER ---
if __name__ == "__main__":
    app.run(debug=True)