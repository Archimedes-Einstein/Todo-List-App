from wsgiref.validate import validator
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from flask_ckeditor import CKEditor
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from flask_bootstrap import Bootstrap5
from forms import *
from bleach import clean
from email.message import EmailMessage
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
ckeditor = CKEditor(app)
app.config['CKEDITOR_CONFIG'] = {'versionCheck': False}
bcrypt = Bcrypt(app)
db.init_app(app)
app_password = 'gybo zyqn psvl jazj'
email = 'ekejiubaarchimedes@gmail.com'
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    todos = relationship('Todo', back_populates='user')
    completed_todo = relationship('CompletedTodo', back_populates='user')
    current_task = relationship('CurrentTodo', back_populates='user')


class Todo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)
    img: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    completed_todo = relationship('CompletedTodo', back_populates='todos')
    user = relationship("User", back_populates='todos')
    current_task = relationship('CurrentTodo', back_populates='todos')


class CompletedTodo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    todo_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('todo.id'))
    todos = relationship('Todo', back_populates='completed_todo')
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    user = relationship("User", back_populates='completed_todo')


class CurrentTodo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    todo_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('todo.id'))
    todos = relationship('Todo', back_populates='current_task')
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    user = relationship("User", back_populates='current_task')


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user:
        return user
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    email = request.form.get('email')
    user = User.query.where(User.email == email).scalar()
    password = request.form.get('password')
    if request.method == 'POST':
        if email:
            try:
                validated_email = validate_email(email)
            except EmailNotValidError:
                flash(category='Invalid email', message="Please input a valid email")
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

                flash(category='Invalid email', message='Please this email is not registered')
                return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    email = request.form.get('email')
    user = User.query.where(User.email == email).scalar()
    password = request.form.get('password')
    name = request.form.get('name')
    if request.method == 'POST':
        if not name:
            flash('Please enter your name')
            return redirect(url_for('sign_up'))
        if email:
            try:
                validated_email = validate_email(email)
            except EmailNotValidError:
                flash(category='Invalid email', message="Please input a valid email")
                return redirect(url_for('sign_up'))
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
                        login_user(new_user)
                    return redirect(url_for('user_page'))
                else:
                    print(password)
                    flash('Invalid password')
                    return redirect(url_for('sign_up'))
    return render_template('sign-up.html')


@app.route('/my-todos')
@login_required
def todos():
    all_todos = Todo.query.all()
    print(current_user.current_task)
    return render_template('my-todos.html', all_todos=all_todos)


@app.route('/add-todo', methods=['POST', 'GET'])
@login_required
def add_todo():
    form = AddTasksForm()
    title = form.title.data
    img_url = form.img_url.data
    description = form.description.data
    duration = form.task_duration.data
    if request.method == 'POST':
        new_todo = Todo(title=title, img=img_url, description=description, time=duration, user=current_user)
        new_current_todo = CurrentTodo(user=current_user, todos=new_todo)
        with app.app_context():
            db.session.add_all([new_todo, new_current_todo])
            db.session.commit()
        return redirect(url_for('todos'))
    return render_template('add-todo.html', form=form)


@app.route('/todo/<int:todo_id>')
@login_required
def todo(todo_id):
    specific_todo = Todo.query.where(Todo.id == todo_id and Todo.user_id == current_user.id).scalar()
    return render_template('todo.html',specific_todo=specific_todo)


@app.route('/delete-todo/<int:todo_id>')
@login_required
def delete(todo_id):
    with app.app_context():
        deleted_current_todo = CurrentTodo.query.where(
            CurrentTodo.todo_id == todo_id and CurrentTodo.user_id == current_user.id).scalar()
        db.session.delete(deleted_current_todo)
        db.session.commit()
    with app.app_context():
        deleted_todo = Todo.query.where(Todo.id == todo_id).scalar()
        db.session.delete(deleted_todo)
        db.session.commit()

    return redirect(url_for('todos'))


@app.route('/edit-todo/<int:todo_id>',methods=['POST','GET'])
@login_required
def edit(todo_id):
    edited_todo = Todo.query.where(Todo.id == todo_id).scalar()
    form = EditTasksForm(title=edited_todo.title,img_url=edited_todo.img,task_duration=edited_todo.time,description=edited_todo.description)
    if form.is_submitted():
        print(form.title.data)
        edited_todo.title = form.title.data
        edited_todo.img = form.img_url.data
        edited_todo.description = form.description.data
        edited_todo.time = form.task_duration.data
        db.session.commit()
        edited_current_todo = CurrentTodo.query.where(CurrentTodo.todo_id == todo_id and CurrentTodo.user_id == current_user.id).scalar()
        edited_current_todo.title = form.title.data
        edited_current_todo.img = form.img_url.data
        edited_current_todo.description = form.description.data
        edited_current_todo.time = form.task_duration.data
        db.session.commit()
        return redirect(url_for('todos'))
    return render_template('edit-todo.html',form=form,todo_id=todo_id)


@app.route('/completed-todo/<int:todo_id>')
@login_required
def completed_todo(todo_id):
    deleted_todo = CurrentTodo.query.where(CurrentTodo.todo_id == todo_id and CurrentTodo.user_id == current_user.id).scalar()
    if deleted_todo:
        complete_todo = Todo.query.where(Todo.id == todo_id and Todo.user_id == current_user.id).scalar()
        new_completed_todo = CompletedTodo(user=current_user,todos=complete_todo)
        db.session.add(new_completed_todo)
        db.session.commit()
        db.session.delete(deleted_todo)
        db.session.commit()
    else:
        flash('This todo has already been added to the completed section')
    return redirect(url_for('todos'))


@app.route('/user-page')
@login_required
def user_page():
    return render_template('user-page.html')


@app.route('/about-page')
def about():
    return render_template('about.html')


@app.route('/contact-page', methods=['POST','GET'])
def contact():
    form = ContactForm()
    user_email = form.email.data
    message = form.msg.data
    user_name = form.name.data
    if form.validate_on_submit():
        if message:
            plain_text_msg = clean(message,tags=[],strip=True)
            with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
                connection.starttls()
                connection.login(email,app_password)
                connection.sendmail(from_addr=email,to_addrs=user_email,msg=f"Subject:{user_name}"
                                                                            f"\n\n{plain_text_msg}")
            return redirect(url_for('contact'))
        flash('Please input a message')
        return redirect(url_for('contact'))
    return render_template('contact.html',form=form)


if __name__ == "__main__":
    app.run(debug=True)
