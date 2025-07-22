# routes/main.py
# 首頁、搜尋、結果頁邏輯
from flask import Blueprint, render_template, request, redirect,url_for
from utils.site_crawler import gimyWeb, gimyNextWeb, duckWeb, fridayWeb, fridayNextWeb, youtubWeb

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
        url_sources = {
            "gimy": gimy,
            "friday": friday,
            "duck": duckWeb(target),
            "netflix": "https://www.netflix.com/tw/title/81040344"
        }

        return render_template("search_result.html", result=result_data, url=url_sources)
    return redirect(url_for("main.search"))