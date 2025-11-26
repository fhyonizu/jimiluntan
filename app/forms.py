from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), 
        Length(min=3, max=80)
    ])
    email = StringField('邮箱', validators=[
        DataRequired(), 
        Email()
    ])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=6)
    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', message='密码必须匹配')
    ])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('用户名已被使用')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('邮箱已被注册')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])

class ThreadForm(FlaskForm):
    title = StringField('标题', validators=[
        DataRequired(),
        Length(min=1, max=200)
    ])
    content = TextAreaField('内容', validators=[
        DataRequired(),
        Length(min=1)
    ])
    category_id = SelectField('分类', coerce=int, validators=[DataRequired()])

class PostForm(FlaskForm):
    content = TextAreaField('回复内容', validators=[
        DataRequired(),
        Length(min=1)
    ])

class CategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    description = TextAreaField('描述')
