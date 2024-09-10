from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Step-1: Configure the app and initialize the database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config['SECRET_KEY'] = '123'  # Needed for session management and flash messages
db = SQLAlchemy(app)

# Step-2: Define User Schema
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Additional attribute to differentiate admin users
    books = db.relationship('Book', backref='owner', lazy="select")

    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

# Define Book Schema
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, title, user_id=None):
        self.title = title
        self.user_id = user_id

# User Registration Route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form  # Check if checkbox is checked
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Try a different one.', 'danger')
            return redirect(url_for('register'))
        
        # Create a new user with admin rights if checkbox is checked
        new_user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registered successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# User Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin  # This sets is_admin in session
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')


# User Dashboard
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    books = user.books if user else []
    return render_template('dashboard.html', user=user, books=books)

# Add a Book
@app.route("/add_book", methods=['POST'])
def add_book():
    if 'user_id' not in session:
        flash('Please log in to add a book.', 'danger')
        return redirect(url_for('login'))

    title = request.form['title']
    user_id = session['user_id']
    new_book = Book(title=title, user_id=user_id)
    db.session.add(new_book)
    db.session.commit()
    flash('Book added successfully!', 'success')
    return redirect(url_for('dashboard'))

# Remove a Book
@app.route("/remove_book/<int:book_id>")
def remove_book(book_id):
    if 'user_id' not in session:
        flash('Please log in to remove a book.', 'danger')
        return redirect(url_for('login'))

    book = Book.query.get(book_id)
    if book and book.owner.id == session['user_id']:
        db.session.delete(book)
        db.session.commit()
        flash('Book removed successfully!', 'success')
    else:
        flash('You do not have permission to remove this book.', 'danger')
    return redirect(url_for('dashboard'))

# Admin Dashboard
@app.route("/admin")
def admin_dashboard():
    if 'is_admin' not in session or not session['is_admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    users = User.query.all()
    books = Book.query.all()
    return render_template('admin_dashboard.html', users=users, books=books)


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Home route to initialize the database
@app.route("/")
def home():
    db.create_all()
    return redirect(url_for('register'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
