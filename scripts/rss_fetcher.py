#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS 抓取模块 - 从能源电力相关网站抓取新闻
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

# 新闻源配置（移除南方电网，按用户要求）
RSS_SOURCES = [
    {"name": "国家能源局", "url": "http://www.nea.gov.cn/", "type": "rss", "rss": "http://www.nea.gov.cn/zfxxgk/fdzdgknr/tzgg/index.xml"},
    {"name": "国家电网", "url": "https://www.sgcc.com.cn/", "type": "web"},
    {"name": "能源杂志", "url": "http://www.cnenergy.org/", "type": "web"},
    {"name": "中国电力新闻网", "url": "https://www.cpnn.com.cn/", "type": "web"},
    {"name": "国家能源集团", "url": "https://www.ceic.com/", "type": "web"},
    {"name": "中电联", "url": "https://www.cec.org.cn/", "type": "web"},
    {"name": "澎湃新闻·能源", "url": "https://www.thepaper.cn/", "type": "rss", "rss": "https://www.thepaper.cn/rss.jsp"},
]

def fetch_rss(rss_url, source_name):
    """抓取 RSS 源"""
    try:
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries[:10]:  # 每个源取最新 10 条
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "source": source_name
            })
        return articles
    except Exception as e:
        print(f"❌ RSS 抓取失败 ({source_name}): {e}")
        return []

def fetch_web(url, source_name):
    """简单网页抓取（备用方案）"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 简单提取标题（不同网站需定制）
        titles = soup.find_all(['h1', 'h2', 'h3', 'h4'], limit=10)
        articles = []
        for t in titles:
            text = t.get_text(strip=True)
            if text and len(text) > 10:
                articles.append({
                    "title": text,
                    "link": url,
                    "summary": "",
                    "published": "",
                    "source": source_name
                })
        return articles
    except Exception as e:
        print(f"❌ 网页抓取失败 ({source_name}): {e}")
        return []

def fetch_all_news():
    """抓取所有来源的新闻"""
    all_articles = []
    
    for source in RSS_SOURCES:
        print(f"📡 正在抓取: {source['name']}")
        
        if source.get("type") == "rss" and source.get("rss"):
            articles = fetch_rss(source["rss"], source["name"])
        else:
            articles = fetch_web(source["url"], source["name"])
        
        all_articles.extend(articles)
        print(f"   ✓ 获取到 {len(articles)} 条")
    
    # 去重（基于标题）
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title = article["title"]
        if title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    print(f"\n📊 总计获取 {len(unique_articles)} 条新闻（去重后）")
    return unique_articles

def load_history(history_dir="history"):
    """加载历史记录用于去重"""
    history_titles = set()
    
    if not os.path.exists(history_dir):
        return history_titles
    
    # 读取最近 3 天的历史
    for filename in os.listdir(history_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(history_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单提取标题（### 开头的行）
                    for line in content.split('\n'):
                        if line.startswith('###'):
                            title = line.replace('###', '').strip()
                            history_titles.add(title)
            except Exception as e:
                print(f"⚠️ 读取历史文件失败 ({filename}): {e}")
    
    return history_titles

if __name__ == "__main__":
    articles = fetch_all_news()
    print(f"\n获取到的新闻：")
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article['title']} ({article['source']})")
