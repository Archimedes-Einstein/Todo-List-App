
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column
from sqlalchemy import String, Integer,Float
from datetime import datetime
from flask_bootstrap import Bootstrap5
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap5(app)
db.init_app(app)
class User(db.Model):
     id: Mapped[int] = mapped_column(Integer,primary_key=True)
     name: Mapped[str] = mapped_column(String, nullable=False)
     email: Mapped[str] = mapped_column(String, nullable=False)
class Todo(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)