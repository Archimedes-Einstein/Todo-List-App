from wsgiref.validate import validator

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column
from sqlalchemy import String, Integer,Float
from datetime import datetime
from email_validator import validate_email,EmailNotValidError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_required,login_user,logout_user,current_user,UserMixin
from flask_bootstrap import Bootstrap5
from unicodedata import normalize, category


class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SECRET_KEY'] = "sjmo2923j9dor34fj3hgv893rj089vj35iikw"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap5(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
db.init_app(app)
class User(UserMixin,db.Model):
     id: Mapped[int] = mapped_column(Integer,primary_key=True)
     name: Mapped[str] = mapped_column(String, nullable=False)
     email: Mapped[str] = mapped_column(String, nullable=False)
     password: Mapped[str] = mapped_column(String, nullable=False)
class Todo(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user:
        return user
    return redirect(url_for('home'))
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    email = request.form.get('email')
    user = User.query.where(User.email == email).scalar()
    password = request.form.get('password')
    if request.method == 'POST':
        if email:
            try:
                validated_email = validate_email(email)
            except EmailNotValidError:
                flash(category='Invalid email',message="Please input a valid email")
                return redirect(url_for('login'))
            else:
                if user:
                    if password:
                        if bcrypt.check_password_hash(user.password, password):
                            login_user(user)
                            return redirect(url_for('user_page'))
                        flash(category='Invalid password', message='Please input a valid password.')
                        return redirect(url_for('login'))
                    else:
                        flash(category='Invalid password', message='Please fill in the password field.')
                        return redirect(url_for('login'))

                flash(category='Invalid email',message='Please this email is not registered')
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
@app.route('/sign-up', methods=['POST','GET'])
def sign_up():
    email = request.form.get('email')
    user = User.query.where(User.email == email).scalar()
    password = request.form.get('password')
    name = request.form.get('name')
    if request.method == 'POST':
        if email:
            try:
                validated_email = validate_email(email)
            except EmailNotValidError:
                flash(category='Invalid email',message="Please input a valid email")
                return redirect(url_for('login'))
            else:
                normalized_email = validated_email.normalized
                if user:
                    flash(message='User already exits. Please try logging in instead.')
                    return redirect(url_for('sign_up'))
                if password:
                    if len(password) < 8:
                        flash('Password must be at least 8 characters long')
                        return redirect(url_for('sign_up'))
                    hashed_password = bcrypt.generate_password_hash(password=password)
                    with app.app_context():
                        new_user = User(
                            name=name,
                            email=normalized_email,
                            password=hashed_password
                        )
                        db.session.add(new_user)
                        db.session.commit()
                        load_user(new_user)
                    return redirect(url_for('user_page'))
                else:
                    print(password)
                    flash('Invalid password')
                    return redirect(url_for('sign_up'))
    return render_template('sign-up.html')
@app.route('/my-todos')
@login_required
def todos():
    return render_template('my-todos.html')
@app.route('/user-page')
@login_required
def user_page():
    return render_template('user-page.html')
if __name__ == "__main__":
    app.run(debug=True)