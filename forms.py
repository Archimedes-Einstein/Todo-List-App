from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,URLField,TimeField
from flask_ckeditor import CKEditorField
from wtforms.validators import Length,DataRequired


class AddTasksForm(FlaskForm):
    title = StringField("Task Title:",[DataRequired()])
    img_url = URLField('Image URL:',[DataRequired()])
    task_duration = StringField('Duration:',[DataRequired()])
    description = CKEditorField('Task Description:',[DataRequired()])
    submit = SubmitField('Add Task!')