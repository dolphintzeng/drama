# forms.py
# Flask-WTF 表單定義
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators

# 登入表單物件
class LoginForm(FlaskForm):
    user_id = StringField("帳號", validators=[validators.DataRequired("請輸入帳號")])
    password = PasswordField("密碼", validators=[validators.DataRequired("請輸入密碼")])
    submit = SubmitField("提交")

#註冊表單物件
class RegisterForm(FlaskForm):
    user_id = StringField("帳號", validators=[validators.DataRequired("請輸入帳號")])
    password = PasswordField("密碼", validators=[validators.DataRequired("請輸入密碼")])
    name = StringField("姓名", validators=[validators.DataRequired("請輸入姓名")])
    email = StringField("Email", validators=[validators.DataRequired("請輸入Email"), validators.Email("請輸入正確格式")])
    submit = SubmitField("提交")