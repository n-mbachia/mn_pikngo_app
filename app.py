# app.py

from logging import DEBUG
import os
import secrets
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import ContentForm, AdminSignupForm
from flask_login import logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)

# Define Content model
class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # author = Column(String(100), nullable=False, default='')
                       
# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()

# Route for registering admin users
@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    form = AdminSignupForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different email.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!', 'success')
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html', form=form)

# Route for admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['admin_logged_in'] = True
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin_login.html')

# Route for admin dashboard
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form = ContentForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        # author = form.author.data  # Add this line to get author information from the form
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = None
        else:
            filename = None

        new_content = Content(title=title, body=body, image_filename=filename)  # Include author information when creating new content
        db.session.add(new_content)
        db.session.commit()

        flash('Content added successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    contents = Content.query.all()

    return render_template('admin_dashboard.html', form=form, contents=contents)


# Route for editing content
@app.route('/admin/edit_content/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form = ContentForm()
    content = Content.query.get(content_id)

    if form.validate_on_submit():
        content.title = form.title.data
        content.body = form.body.data

        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            content.image_filename = filename

        db.session.commit()

        flash('Content updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    if content:
        form.title.data = content.title
        form.body.data = content.body
        return render_template('edit_content.html', form=form, content_id=content_id)
    else:
        flash('Content not found', 'danger')
        return redirect(url_for('admin_dashboard'))

# Route for deleting content
@app.route('/admin/delete_content/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    content = Content.query.get_or_404(content_id)
    db.session.delete(content)
    db.session.commit()
    flash('Post deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

# Route for deleting a post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Content.query.get_or_404(post_id)
    if post.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

# Route for displaying the homepage
@app.route('/')
def index():
    # latest_posts = Content.query.order_by(Content.created_at.desc()).limit(2).all()
    # older_posts = Content.query.order_by(Content.created_at.desc()).offset(2).all()
    return render_template('index.html') # latest_posts=latest_posts, older_posts=older_posts)

from flask import send_file

@app.route('/menu')
def download_menu():
    # Assuming your PDF menu file is located in the static folder
    menu_path = 'static/pikngo_menu.pdf'
    # Provide a filename for the downloaded file (optional)
    filename = 'pikngo_menu.pdf'
    # Send the file to the user for download
    return send_file(menu_path, as_attachment=True)

# Route for displaying a single post
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Content.query.get(post_id)
    if post:
        return render_template('post.html', post=post)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

# Route for displaying earlier posts
@app.route('/earlier_posts')
def earlier_posts():
    posts = Content.query.order_by(Content.created_at.desc()).all()
    return render_template('earlier_posts.html', posts=posts)

if __name__ == '__main__':
    init_db()
    app.run(debug=DEBUG, host='localhost', port=5000)

"""
@app.route('/admin/register', methods=['GET', 'POST'])
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
@app.route('/admin/edit_content/<int:content_id>', methods=['GET', 'POST'])
@app.route('/earlier_posts')
@app.route('/post/<int:post_id>')
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@app.route('/')
@app.route('/logout')
"""
