#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件发送模块 - 通过 QQ 邮箱 SMTP 发送要闻
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import markdown
from datetime import datetime

def convert_md_to_html(md_path):
    """将 Markdown 文件转换为 HTML"""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 使用 markdown 库转换
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'nl2br', 'sane_lists']
    )
    
    # 添加简单的 CSS 样式
    styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>能源电力要闻</title>
    <style>
        body {{ font-family: "Microsoft YaHei", Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }}
        h2 {{ color: #34a853; margin-top: 30px; }}
        h3 {{ color: #ea4335; margin-top: 20px; }}
        a {{ color: #1a73e8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    return styled_html

def send_email(md_path, recipients=None, cc=None):
    """
    发送邮件
    
    Args:
        md_path: Markdown 文件路径
        recipients: 收件人列表，默认 ["67340337@qq.com"]
        cc: 抄送列表，默认 ["451243711@qq.com"]
    """
    if recipients is None:
        recipients = ["67340337@qq.com"]
    if cc is None:
        cc = ["451243711@qq.com"]
    
    # 读取环境变量
    email_account = os.environ.get("QQ_EMAIL_ACCOUNT", "67340337@qq.com")
    email_password = os.environ.get("QQ_EMAIL_AUTH_CODE")
    
    if not email_password:
        raise ValueError("❌ 未设置 QQ_EMAIL_AUTH_CODE 环境变量")
    
    # 转换 Markdown 为 HTML
    html_content = convert_md_to_html(md_path)
    
    # 构建邮件
    today = datetime.now().strftime("%Y年%m月%d日")
    subject = f"能源电力要闻 {today}"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = email_account
    msg['To'] = ", ".join(recipients)
    if cc:
        msg['Cc'] = ", ".join(cc)
    
    # HTML 内容
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # 纯文本版本（备用）
    with open(md_path, 'r', encoding='utf-8') as f:
        text_content = f.read()
    text_part = MIMEText(text_content, 'plain', 'utf-8')
    msg.attach(text_part)
    
    # 发送邮件
    print(f"📧 正在发送邮件到 {recipients}...")
    
    try:
        # QQ 邮箱 SMTP 配置
        smtp_server = "smtp.qq.com"
        smtp_port = 465
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_account, email_password)
            server.send_message(msg)
        
        print("✅ 邮件发送成功")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

if __name__ == "__main__":
    # 测试（需要先创建一个测试 Markdown 文件）
    test_md = "output/test.md"
    if os.path.exists(test_md):
        send_email(test_md)
    else:
        print("⚠️ 请先创建测试 Markdown 文件")
