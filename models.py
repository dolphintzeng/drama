# models.py
# 建立 SQLAlchemy models 資料表物件
from extensions import db

# 會員資料表物件
class User_info(db.Model): #若有進行參數前處理或是要使用位置對應法，需自定義__init__
    user_id = db.Column(db.String(100), primary_key=True, index=True)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.Integer, nullable=True)
    verified = db.Column(db.Boolean, default=False)

class Search_result(db.Model): 
    key = db.Column(db.String(50), primary_key=True, index=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(300), nullable=False)
    pic_url = db.Column(db.String(200), nullable=False, unique=True)
    yt = db.Column(db.String(200), nullable=True)
    
    
class Url_resource(db.Model): 
    key = db.Column(db.String(50), primary_key=True, index=True)
    gimy = db.Column(db.String(200), nullable=False)
    friday = db.Column(db.String(200), nullable=False)
    duck = db.Column(db.String(200), nullable=False, unique=True)
    netflix = db.Column(db.String(200), nullable=True)
