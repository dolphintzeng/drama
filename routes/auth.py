# routes/auth.py
# 登入、註冊、驗證、登出邏輯
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensions import db, login_manager
from models import User_info
from forms import LoginForm, RegisterForm
from utils.user_helper import generate_token, current_timestamp, send_mail

auth_bp = Blueprint("auth", __name__) #表示 Blueprint名 為"auth"

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(user_id):
    user = User_info.query.filter_by(user_id=user_id).first()
    if user:
        user_obj = User()
        user_obj.id = user.user_id
        return user_obj
    return None

def clean_pending_users():
    current_time = current_timestamp()
    expired_users = User_info.query.filter(User_info.created_at < current_time - 600).all()
    for user in expired_users:
        db.session.delete(user)
    db.session.commit()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User_info.query.filter_by(user_id=form.user_id.data).first()
        if not user:
            flash("帳號錯誤")
        elif not check_password_hash(user.password, form.password.data):
            flash("密碼錯誤")
        elif not user.verified:
            flash("帳號尚未驗證，請先完成Email驗證")
            session["pending_user"] = user.user_id
            return redirect(url_for("auth.message")) # 要呼叫function需要以"Blueprint名.view_function名"
        else:
            user_obj = User()
            user_obj.id = user.user_id
            login_user(user_obj)
            flash(f"{user.user_id}您好，歡迎登入！")
            return redirect(url_for("main.search"))
        form.password.data = ""
    return render_template("login.html", form=form)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        clean_pending_users()
        user = User_info.query.filter_by(user_id=form.user_id.data).first()
        if user:
            if user.verified:
                flash("帳號已註冊，請直接登入")
            else:
                flash("此帳號尚未完成驗證，我們已重新發送驗證信")
                user.token = generate_token()
                user.created_at = current_timestamp()
                db.session.commit()
                send_mail(
                    subject="重新發送驗證信",
                    sender="tom1835566@gmail.com",
                    recipients=[user.email],
                    template="verification_email",
                    user_name=user.name,
                    verify_url=url_for("auth.verify", token=user.token, _external=True)
                )
                session["pending_user"] = user.user_id
                return redirect(url_for("auth.message"))
            return render_template("register.html", form=form)

        try:
            new_user = User_info(
                user_id=form.user_id.data,
                password=generate_password_hash(form.password.data),
                name=form.name.data,
                email=form.email.data,
                token=generate_token(),
                created_at=current_timestamp()
            )
            db.session.add(new_user)
            db.session.commit()

            mail_result = send_mail(
                subject="註冊驗證信",
                sender="tom1835566@gmail.com",
                recipients=[form.email.data],
                template="verification_email",
                user_name=form.name.data,
                verify_url=url_for("auth.verify", token=new_user.token, _external=True)
            )
            if not mail_result["success"]:
                db.session.rollback()
                flash("無法發送驗證信，請檢查您的Email地址是否正確")
                return render_template("register.html", form=form)

            session["pending_user"] = form.user_id.data
            flash("驗證信已發送，請在10分鐘內完成註冊！")
            return redirect(url_for("auth.message"))
        except IntegrityError:
            db.session.rollback()
            flash("帳號或Email已存在，請選擇其他帳號！")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"資料庫錯誤，請稍後再試：{str(e)}")
    return render_template("register.html", form=form)

@auth_bp.route("/message")
def message():
    if "pending_user" not in session:
        flash("請先註冊！")
        return redirect(url_for("auth.register"))
    user = User_info.query.filter_by(user_id=session["pending_user"]).first()
    return render_template("message.html", email=user.email if user else None)

@auth_bp.route("/verify/<token>")
def verify(token):
    pending_user = User_info.query.filter_by(token=token).first()
    if not pending_user:
        flash("驗證連結無效或已過期，請重新註冊")
        return redirect(url_for("auth.register"))

    if current_timestamp() - pending_user.created_at > 600:
        db.session.delete(pending_user)
        db.session.commit()
        flash("驗證連結已過期，請重新註冊")
        return redirect(url_for("auth.register"))

    pending_user.verified = True
    pending_user.token = None
    pending_user.created_at = None
    db.session.commit()
    flash("註冊成功，請登入！")
    session.pop("pending_user", None)
    return redirect(url_for("auth.login"))

@auth_bp.route("/logout")
@login_required
def logout():
    user_id = current_user.get_id()
    logout_user()
    session.pop("pending_user", None)
    flash(f"{user_id}，下次再見！")
    return redirect(url_for("auth.login"))