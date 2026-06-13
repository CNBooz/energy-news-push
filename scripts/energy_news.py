#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能源电力要闻 - 主脚本

流程：
1. 抓取新闻（RSS/网页）
2. 调用 DeepSeek 生成要闻汇总
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
    print("能源电力要闻自动化开始")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: 抓取新闻
    print("\n[Step 1/6] 抓取新闻")
    articles = fetch_all_news()
    
    if not articles:
        print("错误: 未获取到任何新闻，退出")
        return
    
    print(f"  获取到 {len(articles)} 条新闻")
    
    # Step 2: 加载历史记录（去重）
    print("\n[Step 2/6] 加载历史记录")
    history_titles = load_history("../history")
    print(f"  历史记录中有 {len(history_titles)} 条标题")
    
    # Step 3: 调用 DeepSeek 生成要闻
    print("\n[Step 3/6] 调用 DeepSeek 生成要闻汇总")
    try:
        markdown_content = generate_energy_news(articles, history_titles)
        print("  DeepSeek 生成成功")
    except Exception as e:
        print(f"  错误: DeepSeek 生成失败: {e}")
        print("  使用备用方案（简单列表）")
        from gemini_generator import generate_fallback_news
        markdown_content = generate_fallback_news(articles, datetime.now().strftime("%Y年%m月%d日"))
    
    # Step 4: 保存 Markdown
    print("\n[Step 4/6] 保存 Markdown")
    md_path = save_markdown(markdown_content, "../output")
    print(f"  保存到: {md_path}")
    
    # Step 5: 发送邮件
    print("\n[Step 5/6] 发送邮件")
    try:
        send_email(md_path)
        print("  邮件发送成功")
    except Exception as e:
        print(f"  错误: 邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 6: 归档到 IMA 知识库（可选）
    print("\n[Step 6/6] IMA 知识库归档")
    
    ima_api_key = os.environ.get("IMA_API_KEY")
    print(f"  IMA_API_KEY 环境变量: {'已设置' if ima_api_key else '未设置'}")
    
    if ima_api_key:
        try:
            print("  开始上传到 IMA 知识库...")
            result = upload_to_ima(md_path)
            if result:
                print("  IMA 归档成功")
            else:
                print("  IMA 归档失败（返回 False）")
        except Exception as e:
            print(f"  错误: IMA 归档失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("  未配置 IMA_API_KEY，跳过归档")
    
    print("\n" + "=" * 60)
    print("能源电力要闻自动化完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
