# routes/main.py
# 首頁、搜尋、結果頁邏輯
from flask import Blueprint, render_template, request, redirect,url_for,flash
from utils.site_crawler import gimyWeb, gimyNextWeb, duckWeb, fridayWeb, fridayNextWeb, youtubWeb,storeTodb,checkDB
from flask_login import login_required, current_user
from utils.netflix import netflixWeb
# 引用使用者資料
from models import Comment, User_info
from extensions import db

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
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
                friday = friday_result[0]["url"] if friday_result else None

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
            storeTodb(target,result_data,url_sources)
        else:
            result_data, url_sources=checkDB(target)
        return render_template("search_result.html", result=result_data, url=url_sources)
    return redirect(url_for("main.search"))

@main_bp.route("/comment", methods=["POST"])
@login_required
def comment():
    movie = request.form.get("movie")
    content = request.form.get("content")
    url = request.form.get("url")
    pic = request.form.get("pic")

    if not content.strip():
        flash("留言不得為空")
        return redirect(url_for("main.search_result", title=movie, url=url, pic=pic))

    # 根據 current_user.id 取得 User_info
    user = User_info.query.filter_by(user_id=current_user.get_id()).first()

    if not user:
        flash("使用者資料錯誤")
        return redirect(url_for("main.search_result", title=movie, url=url, pic=pic))

    new_comment = Comment(movie=movie, content=content, author=user)
    db.session.add(new_comment)
    db.session.commit()

    flash("留言成功")
    return redirect(url_for("main.search_result", title=movie, url=url, pic=pic))
