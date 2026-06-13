#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通义千问 API 调用模块 - 生成能源电力要闻汇总
（已适配阿里云百炼平台，国内可直接访问）
"""

import os
import requests
import json
from datetime import datetime

# 通义千问 API 配置（兼容 OpenAI 格式）
QWEN_API_URL = "https://bailian.console.aliyuncs.com/compatible-mode/v1/chat/completions"

def generate_energy_news(articles, history_titles):
    """
    使用通义千问 API 生成能源电力要闻汇总
    
    Args:
        articles: 新闻列表
        history_titles: 历史标题集合（用于去重）
    
    Returns:
        str: 生成的 Markdown 内容
    """
    api_key = os.environ.get("QWEN_API_KEY")
    if not api_key:
        raise ValueError("❌ 未设置 QWEN_API_KEY 环境变量")
    
    # 过滤掉历史中已经出现过的标题
    new_articles = [a for a in articles if a["title"] not in history_titles]
    
    if not new_articles:
        print("⚠️ 所有新闻都是历史重复，使用备用方案")
        new_articles = articles[:8]  # 取前 8 条作为备用
    
    # 构建 prompt
    today = datetime.now().strftime("%Y年%m月%d日")
    
    news_text = "\n".join([
        f"【{a['source']}】{a['title']}"
        for a in new_articles[:20]  # 最多使用 20 条新闻作为输入
    ])
    
    prompt = f"""你是能源电力行业的专业分析师。以下是今天({today})收集的能源电力相关新闻：

{news_text}

请从中筛选出8条最重要、最有价值的新闻，涵盖以下7个主题（每个主题至少1条）：
1. 三新建设（新型电力系统、新能源、新基建）
2. 电力市场（电价、交易、政策）
3. AI+能源（人工智能在能源领域的应用）
4. 电碳算协同（电力、碳交易、算力协同）
5. 科技创新（新技术、新装备）
6. 产业发展（产业链、市场规模）
7. 央企动态（国家能源、国家电网、南方电网等央企）

输出格式（Markdown）：
# 能源电力要闻 {today}

## 今日概览
（2-3句话概括今日要闻特点）

## 详细要闻

### 1. [新闻标题]
**来源**：XXX | **日期**：XXX
**摘要**：XXX
**分析**：XXX

（共8条，格式相同）

## 风险提示
（如有需要）

注意：
- 只输出Markdown内容，不要解释
- 新闻必须真实，基于提供的新闻列表
- 如果某主题没有合适新闻，可以选择其他主题补充
"""

    # 调用通义千问 API（兼容 OpenAI 格式）
    print("🤖 正在调用通义千问 API 生成要闻汇总...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "qwen-turbo",  # 免费额度模型，可选 qwen-plus（更强）
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(QWEN_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result["choices"][0]["message"]["content"]
        
        print("✅ 通义千问生成完成")
        return generated_text
        
    except Exception as e:
        print(f"❌ 通义千问 API 调用失败: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"   错误详情: {e.response.text}")
        # 返回简单的备用内容
        return generate_fallback_news(new_articles[:8], today)

def generate_fallback_news(articles, today):
    """备用方案：如果 API 失败，生成简单列表"""
    lines = [f"# 能源电力要闻 {today}\n"]
    lines.append("## 今日要闻\n")
    
    for i, article in enumerate(articles[:8], 1):
        lines.append(f"### {i}. {article['title']}")
        lines.append(f"**来源**：{article['source']} | **链接**：{article['link']}")
        lines.append(f"**摘要**：{article.get('summary', '暂无摘要')}\n")
    
    return "\n".join(lines)

def save_markdown(content, output_dir="output"):
    """保存 Markdown 文件"""
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(output_dir, f"{today}.md")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Markdown 已保存: {filepath}")
    return filepath

if __name__ == "__main__":
    # 测试
    test_articles = [
        {"title": "测试新闻1", "source": "国家能源局", "link": "http://example.com/1", "summary": "摘要1"},
        {"title": "测试新闻2", "source": "国家电网", "link": "http://example.com/2", "summary": "摘要2"},
    ]
    
    # 需要设置环境变量 QWEN_API_KEY 才能测试
    if os.environ.get("QWEN_API_KEY"):
        result = generate_energy_news(test_articles, set())
        print(result[:500])  # 打印前 500 字符
    else:
        print("⚠️ 请先设置 QWEN_API_KEY 环境变量")
