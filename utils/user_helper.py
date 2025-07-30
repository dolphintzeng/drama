# utils.py
# 常用函式 - 將部分動作以函式封裝，此封裝為了防止邏輯被拆解後惡意爆破，進而整合到使用者資料表中作為狀態管理欄位
import uuid
import time
from flask import render_template
from flask_mail import Message
from extensions import mail

import logging
logger = logging.getLogger(__name__)

def generate_token():
    return str(uuid.uuid4())

def current_timestamp():
    return int(time.time())

def send_mail(subject, sender, recipients, template, **kwargs):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = render_template(template + ".html", **kwargs)
    try:
        mail.send(msg)
        return {"success": True, "error": None}
    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True) # 將錯誤訊息記錄起來
        return {"success": False, "error": str(e)}