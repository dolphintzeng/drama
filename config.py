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
    SQLALCHEMY_TRACK_MODIFICATIONS = False #加入這行設定以清除SQLAlchemy警告，提升效能
    
# config.py
# import os
# from dotenv import load_dotenv

# load_dotenv()

# basedir = os.path.abspath(os.path.dirname(__file__))

# class Config:
#     SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

#     raw_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")
#     if raw_uri.startswith("sqlite:///") and not raw_uri.startswith("sqlite:////"):
#         relative_path = raw_uri.replace("sqlite:///", "")
#         absolute_path = os.path.join(basedir, relative_path)
#         SQLALCHEMY_DATABASE_URI = f"sqlite:///{absolute_path}"
#     else:
#         SQLALCHEMY_DATABASE_URI = raw_uri

#     MAIL_USERNAME = os.getenv("MAIL_USERNAME", "default@example.com")
#     MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
#     MAIL_SERVER = "smtp.gmail.com"
#     MAIL_PORT = 465
#     MAIL_USE_SSL = True
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
# config.py
# import os
# from dotenv import load_dotenv
# from pathlib import Path

# load_dotenv()
# basedir = Path(__file__).resolve().parent
# db_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")

# if db_uri.startswith("sqlite:///") and not db_uri.startswith("sqlite:////"):
#     relative_path = db_uri.replace("sqlite:///", "")
#     absolute_path = basedir / relative_path
#     db_uri = f"sqlite:///{absolute_path}"

# class Config:
#     SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
#     SQLALCHEMY_DATABASE_URI = db_uri
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

