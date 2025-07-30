# app.py (主程式)
from flask import Flask
from extensions import db, mail, login_manager
from routes import register_blueprints

import logging # 可透過查看log了解明確的錯誤訊息，命令列輸入heroku logs --tail

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# 所有設定(環境變數、DB連線、Mail設定)
import os
from dotenv import load_dotenv

load_dotenv() # 自動載入 .env 檔案

class Config: # 補上預設值避免 .env 遺失時錯誤
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 取得專案根目錄
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}" #統一連線到instance的db
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "default@example.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False #加入這行設定以清除SQLAlchemy警告，提升效能

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化擴充套件
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 註冊 Blueprint
    register_blueprints(app)

    # 建立資料表
    with app.app_context():
        db.create_all()

    return app

# 執行伺服器
if __name__ == '__main__':
    app = create_app()
    app.run()