from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import Required, Email, Length


class UpdateProfile(FlaskForm):
    bio = TextAreaField('Tell Us About Yourself...',validators = [Required()])
    submit = SubmitField('Submit')

class UpdateProfileForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(1, 64)])
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    bio = TextAreaField('About...', validators=[Required(), Length(1, 100)])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post_title = StringField('Post title', validators=[Required()])
    post_category = SelectField('Post category',choices=[('Select a category','Select a category'),('Rift Valley', 'Rift Valley'),('Tsavo','Tsavo'),('Maasai Mara','Maasai Mara'),('Pwani','Pwani')], validators=[Required()])
    post_content = StringField('What is in your mind?')
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment = TextAreaField('Body', validators=[Required()])
    submit = SubmitField('Submit')