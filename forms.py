from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,URLField,TimeField,EmailField
from flask_ckeditor import CKEditorField
from wtforms.validators import Length,DataRequired,Email


class AddTasksForm(FlaskForm):
    title = StringField("Task Title:",[DataRequired()])
    img_url = URLField('Image URL:',[DataRequired()])
    task_duration = StringField('Duration:',[DataRequired()])
    description = CKEditorField('Task Description:',[DataRequired()])
    submit = SubmitField('Add Task!')

class EditTasksForm(FlaskForm):
    title = StringField("Task Title:",[DataRequired()])
    img_url = URLField('Image URL:',[DataRequired()])
    task_duration = StringField('Duration:',[DataRequired()])
    description = CKEditorField('Task Description:',[DataRequired()])
    submit = SubmitField('Edit Task!')

class ContactForm(FlaskForm):
    name = StringField('Name:',[DataRequired()])
    email = EmailField('Email:',[DataRequired(),Email(message='Please input a valid email.')])
    msg = CKEditorField('Message:',[DataRequired()])
    submit = SubmitField("Send !")