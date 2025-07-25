# routes/auth.py
# 登入、註冊、驗證、登出邏輯
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensions import db, login_manager
from models import User_info
from forms import LoginForm, RegisterForm
from utils.user_helper import generate_token, current_timestamp, send_mail

auth_bp = Blueprint("auth", __name__) #表示 Blueprint名 為"auth"

class User(UserMixin): #因登入時要在各地方顯示user.name，故調整起始函數
    def __init__(self, id, name):
        self.id = id
        self.name = name

@login_manager.user_loader
def user_loader(user_id):
    user = User_info.query.filter_by(user_id=user_id).first()
    if user:
        user_obj = User(id=user.user_id, name=user.name)
        return user_obj
    return None

def clean_pending_users():
    current_time = current_timestamp()
    User_info.query.filter(User_info.created_at < current_time - 600).delete()
    db.session.commit()

@auth_bp.route("/prelogin", methods=["POST"]) #因為直接POST跳轉到login會觸發驗證錯誤
def prelogin():
    # 接收表單參數並存入 session
    session["next"] = request.form.get("next") #有使用到session就會自動產生名為session的cookies
    session["key"] = request.form.get("key")
    session["title"] = request.form.get("title")
    session["url"] = request.form.get("url")
    session["pic"] = request.form.get("pic")
    return redirect(url_for("auth.login"))

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
            user_obj = User(id=user.user_id, name=user.name)
            login_user(user_obj)

            next_page = session.pop("next", None)
            if next_page == "search":
                key = session.pop("key", "")
                return render_template("post_redirect.html", action=url_for("main.search"), key=key) #redirect只能以GET傳參數，改成導向模板搭配JS以POST傳參數
            elif next_page == "search_result":
                title = session.pop("title", "")
                url = session.pop("url", "")
                pic = session.pop("pic", "")
                return render_template("post_redirect.html", action=url_for("main.search_result"), title=title, url=url, pic=pic)
            else:
                return redirect(url_for("main.index"))
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
                return render_template(url_for("auth.login"))
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

        user_by_email = User_info.query.filter_by(email=form.email.data).first() #主動檢查email可以提升程式效率、更好的使用者體驗
        if user_by_email:
            flash("此 Email 已註冊，請使用其他 Email！")
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
        except IntegrityError: #models有設定user_id與email有唯一性，故建立此例外處理告知使用者資料重複，但主要用於處理「異常」情況
            db.session.rollback()
            flash("帳號或Email已存在，請選擇其他帳號或Email！")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"資料庫錯誤，請稍後再試：{str(e)}")
    return render_template("register.html", form=form)

@auth_bp.route("/message") #註冊後頁面，顯示email資訊給使用者確認並提醒收信
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
    user = User_info.query.filter_by(user_id=user_id).first()
    logout_user()
    flash(f"{user.name}，下次再見！")
    return redirect(url_for("auth.login"))