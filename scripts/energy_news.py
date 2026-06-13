#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
能源电力要闻 - 主脚本

流程：
1. 抓取新闻（RSS/网页）
2. 调用 DeepSeek 生成要闻汇总
3. 保存为 Markdown
4. 发送邮件
5. （可选）IMA 归档 - 由 GitHub Actions workflow 中的 Node.js 步骤完成
"""

import sys
import os
from datetime import datetime

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from rss_fetcher import fetch_all_news, load_history
from gemini_generator import generate_energy_news, save_markdown
from email_sender import send_email

def main():
    print("=" * 60)
    print("能源电力要闻自动化开始")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: 抓取新闻
    print("\n[Step 1/4] 抓取新闻")
    articles = fetch_all_news()
    
    if not articles:
        print("错误: 未获取到任何新闻，退出")
        return
    
    print(f"  获取到 {len(articles)} 条新闻")
    
    # Step 2: 加载历史记录（去重）
    print("\n[Step 2/4] 加载历史记录")
    history_titles = load_history("../history")
    print(f"  历史记录中有 {len(history_titles)} 条标题")
    
    # Step 3: 调用 DeepSeek 生成要闻
    print("\n[Step 3/4] 调用 DeepSeek 生成要闻汇总")
    try:
        markdown_content = generate_energy_news(articles, history_titles)
        print("  DeepSeek 生成成功")
    except Exception as e:
        print(f"  错误: DeepSeek 生成失败: {e}")
        print("  使用备用方案（简单列表）")
        from gemini_generator import generate_fallback_news
        markdown_content = generate_fallback_news(articles, datetime.now().strftime("%Y年%m月%d日"))
    
    # Step 4: 保存 Markdown（供存档 + IMA 归档）
    print("\n[Step 4/4] 保存 Markdown")
    md_path = save_markdown(markdown_content, "../output")
    print(f"  存档保存到: {md_path}")
    
    # 保存到 scripts/ 目录（供 IMA 步骤上传，IMA 只接受 .md 文件）
    ima_md_path = os.path.join(os.path.dirname(__file__), "energy_news.md")
    with open(ima_md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"  IMA 文件保存到: {ima_md_path}")
    print(f"  ✅ 文件已保存，等待 workflow 中的 Python 步骤完成 IMA 归档")
    
    # Step 5: 发送邮件
    print("\n[Step 5/4] 发送邮件")
    try:
        send_email(md_path)
        print("  邮件发送成功")
    except Exception as e:
        print(f"  错误: 邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 注意：IMA 归档已在 GitHub Actions workflow 中作为独立步骤完成
    # 该步骤在 Python 脚本运行后执行，使用 Node.js 脚本调用 IMA API
    
    print("\n" + "=" * 60)
    print("能源电力要闻自动化完成（IMA 归档由 workflow 后续步骤完成）")
    print("=" * 60)

if __name__ == "__main__":
    main()
