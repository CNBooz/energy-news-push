#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能源电力要闻 - 主脚本

流程：
1. 抓取新闻（RSS/网页）
2. 调用 Gemini 生成要闻汇总
3. 发送邮件
4. 归档到 IMA 知识库（可选）
"""

import sys
import os
from datetime import datetime

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from rss_fetcher import fetch_all_news, load_history
from gemini_generator import generate_energy_news, save_markdown
from email_sender import send_email
from ima_uploader import upload_to_ima

def main():
    print("=" * 60)
    print("🚀 能源电力要闻自动化开始")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: 抓取新闻
    print("\n📡 Step 1: 抓取新闻")
    articles = fetch_all_news()
    
    if not articles:
        print("❌ 未获取到任何新闻，退出")
        return
    
    # Step 2: 加载历史记录（去重）
    print("\n📚 Step 2: 加载历史记录")
    history_titles = load_history("../history")
    print(f"   历史记录中有 {len(history_titles)} 条标题")
    
    # Step 3: 调用 Gemini 生成要闻
    print("\n🤖 Step 3: 调用 Gemini 生成要闻汇总")
    try:
        markdown_content = generate_energy_news(articles, history_titles)
    except Exception as e:
        print(f"❌ Gemini 生成失败: {e}")
        print("   使用备用方案（简单列表）")
        from gemini_generator import generate_fallback_news
        markdown_content = generate_fallback_news(articles, datetime.now().strftime("%Y年%m月%d日"))
    
    # Step 4: 保存 Markdown
    print("\n💾 Step 4: 保存 Markdown")
    md_path = save_markdown(markdown_content, "../output")
    
    # Step 5: 发送邮件
    print("\n📧 Step 5: 发送邮件")
    try:
        send_email(md_path)
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
    
    # Step 6: 归档到 IMA 知识库（可选）
    print("\n📚 Step 6: IMA 知识库归档（可选）")
    if os.environ.get("IMA_API_KEY"):
        try:
            upload_to_ima(md_path)
        except Exception as e:
            print(f"⚠️ IMA 归档失败（非关键）: {e}")
    else:
        print("⚠️ 未配置 IMA_API_KEY，跳过归档")
    
    print("\n" + "=" * 60)
    print("✅ 能源电力要闻自动化完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
