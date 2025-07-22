# app.py (主程式)
from flask import Flask
from config import Config
from extensions import db, mail, login_manager
from routes import register_blueprints

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