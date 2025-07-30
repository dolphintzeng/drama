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
    author_id = db.Column(db.String(100), db.ForeignKey("user_info.user_id"), nullable=False) #此處user_info.user_id指的是資料表名稱，預測為小寫
    author = db.relationship("User_info", backref="comments") #透過Comment.author就可以取得User_info資料，反之User_info.comments

class Search_result(db.Model):#利用SQLAlchemy ORM 的技術 建立查詢結果的資料表 
    keyword = db.Column(db.String(50), primary_key=True, index=True, nullable=False) # 這個欄位不得為空值，且設為主鍵不能重覆
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(300), nullable=True)
    pic_url = db.Column(db.String(200), nullable=True)
    yt = db.Column(db.String(200), nullable=True)
    gimy = db.Column(db.String(200), nullable=True)
    friday = db.Column(db.String(200), nullable=True)
    duck = db.Column(db.String(200), nullable=True)
    netflix = db.Column(db.String(200), nullable=True)
