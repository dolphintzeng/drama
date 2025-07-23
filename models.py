# models.py
# 建立 SQLAlchemy models 資料表物件
from extensions import db
from datetime import datetime

# 會員資料表物件
class User_info(db.Model): #若有進行參數前處理或是要使用位置對應法，需自定義__init__
    user_id = db.Column(db.String(100), primary_key=True, index=True)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.Integer, nullable=True)
    verified = db.Column(db.Boolean, default=False)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now)

    author_id = db.Column(db.String(100), db.ForeignKey("user_info.user_id"), nullable=False)

    author = db.relationship("User_info", backref="comments")

class Search_result(db.Model): 
    keyword = db.Column(db.String(50), primary_key=True, index=True, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(300), nullable=True)
    pic_url = db.Column(db.String(200), nullable=True, unique=True)
    yt = db.Column(db.String(200), nullable=True, unique=True)
    
    
class Url_resource(db.Model): 
    keyword = db.Column(db.String(50), primary_key=True, index=True)
    gimy = db.Column(db.String(200), nullable=True, unique=True)
    friday = db.Column(db.String(200), nullable=True, unique=True)
    duck = db.Column(db.String(200), nullable=True, unique=True)
    netflix = db.Column(db.String(200), nullable=True)
