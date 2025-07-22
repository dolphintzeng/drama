# routes/__init__.py
# 建立 Blueprint 並註冊，Blueprint 讓每一組路由與處理邏輯可以「獨立註冊」到主程式中(將原本所以route集中在單一入口分開)
from flask import Blueprint

from .auth import auth_bp
from .main import main_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/") # url_prefix 表示透過此設定route前綴會添加"/"
    app.register_blueprint(main_bp, url_prefix="/")