# routes/main.py
# 首頁、搜尋、結果頁邏輯
from flask import Blueprint, render_template, request, redirect,url_for,flash, session
from utils.site_crawler import gimyWeb, gimyNextWeb, duckWeb, fridayWeb, fridayNextWeb, youtubWeb,storeTodb,checkDB
from flask_login import login_required, current_user
from utils.netflix import netflixWeb
# 引用使用者資料
from models import Comment, User_info
from extensions import db
from sqlalchemy.exc import SQLAlchemyError

import logging
logger = logging.getLogger(__name__) #記錄出錯的程式檔名

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["POST", "GET"])
def index():
    return render_template("home.html")

@main_bp.route("/search/",methods=['POST','GET'])
def search():
    if request.method == 'POST':
        search_key = request.form.get('key')
        searchList = gimyWeb(search_key)
        if not searchList:
            searchList = fridayWeb(search_key, 2)
        return render_template("search.html", searchList=searchList, key=search_key)
    return redirect(url_for("main.index"))

@main_bp.route("/search/result/",methods=['POST','GET'])
def search_result():
    if request.method == 'POST':
        url = request.form.get('url')
        pic_url = request.form.get("pic")
        target = request.form.get("title")

        title = content = ''
        gimy = friday = None
        if not checkDB(target):
            print("DB裡沒有要從網頁搜尋")
            if "gimy" in url:
                result = gimyNextWeb(url)
                if result:
                    title, content = result
                gimy = url
                friday_result = fridayWeb(target)
                friday = friday_result[0]["url"] if friday_result else ""

            elif "friday" in url:
                result = fridayNextWeb(url)
                if result:
                    title, content = result
                friday = url

            yt = youtubWeb(target)
            result_data = {
                "title": title,
                "content": content,
                "pic": pic_url,
                "yt": yt
            }
            netflix_url = netflixWeb(target)
            url_sources = {
                "gimy": gimy,
                "friday": friday,
                "duck": duckWeb(target),
                "netflix": netflix_url
            }
            error=storeTodb(target,result_data,url_sources)
            if error !='success':
                print(error)
        else:
            result_data, url_sources=checkDB(target)

        # 加入留言資料查詢
        comments = Comment.query.filter_by(movie=target.strip()).order_by(Comment.time.desc()).all()

        return render_template("search_result.html", result=result_data, url=url_sources, comments=comments)
    return redirect(url_for("main.search"))

@main_bp.route("/comment", methods=["POST"])
def comment():
    title = request.form.get("title")
    url = request.form.get("url")
    pic = request.form.get("pic")
    content = request.form.get("content")

    if not current_user.is_authenticated:
        session["next"] = request.form.get("next")
        session["title"] = title
        session["url"] = url
        session["pic"] = pic
        session["content"] = content
        return redirect(url_for("auth.login"))

    try:
        # 加入留言資料表
        new_comment = Comment(movie=title, content=content, author_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
    except SQLAlchemyError as e:
        flash(f"資料庫錯誤，請稍後再試：{str(e)}")
        logger.error(f"資料庫操作錯誤: {str(e)}", exc_info=True)
    return render_template("post_redirect.html", action=url_for("main.search_result"), title=title, url=url, pic=pic)
