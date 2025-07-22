# config.py
# 所有設定(環境變數、DB連線、Mail設定)
import os
from dotenv import load_dotenv

load_dotenv() # 自動載入 .env 檔案

class Config: # 補上預設值避免 .env 遺失時錯誤
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "default@example.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True