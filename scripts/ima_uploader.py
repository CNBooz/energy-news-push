#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMA 知识库归档模块 - 完整实现

流程：
  Step 1: preflight_check（检查文件是否可上传）
  Step 2: check_repeated_names（检查重名）
  Step 3: create_media（获取 COS 上传凭证）
  Step 4: 上传文件到 COS
  Step 5: add_knowledge（添加到知识库）
"""

import os
import sys
import requests
import json
import base64
import hmac
import hashlib
import time
from datetime import datetime

# IMA API 配置
IMA_API_BASE = "https://ima.qq.com/openapi/v1"
KNOWLEDGE_BASE_ID = "E9owuqdzTE2LcRB0A5ub04_cxrGGpMzCmFQEahJ8te0="
CLIENT_ID = "dd4962571a67592aa50ec9146343419a"

def get_headers():
    """获取 IMA API 请求头"""
    api_key = os.environ.get("IMA_API_KEY")
    if not api_key:
        # 尝试从配置文件读取
        config_path = os.path.expanduser("~/.config/ima/api_key")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                api_key = f.read().strip()
    
    if not api_key:
        raise ValueError("未设置 IMA_API_KEY 环境变量，且 ~/.config/ima/api_key 不存在")
    
    return {
        "X-Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def cos_auth(secret_id, secret_key, token, method, path, headers, expire=3600):
    """生成 COS 上传所需的签名"""
    now = int(time.time())
    key_time = f"{now};{now + expire}"
    
    # 简化版：直接使用 requests 工具上传，让 requests 处理签名
    # 实际 COS 上传使用预签名 URL，不需要手动签名
    return {}

def upload_to_cos(file_path, cos_credentials):
    """
    上传文件到 COS（腾讯云对象存储）
    
    cos_credentials 包含：
      - upload_url: 预签名的上传 URL
      - headers: 上传时需要的请求头
    """
    upload_url = cos_credentials.get("upload_url") or cos_credentials.get("url")
    cos_headers = cos_credentials.get("headers", {})
    
    if not upload_url:
        # 尝试从完整响应中提取
        if "presigned_url" in cos_credentials:
            upload_url = cos_credentials["presigned_url"]
    
    if not upload_url:
        # 尝试构造上传 URL（某些实现会返回 bucket/region 信息）
        print(f"  [COS] ⚠️ 未找到 upload_url，尝试从凭证中提取...")
        print(f"  [COS] 凭证内容: {json.dumps(cos_credentials, ensure_ascii=False)[:500]}")
        raise ValueError("COS 上传凭证中未找到 upload_url")
    
    print(f"  [COS] 开始上传文件到 COS...")
    print(f"  [COS] Upload URL: {upload_url[:100]}...")
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    # 使用 PUT 或 POST 上传（取决于 IMA API 的设计）
    # 大多数预签名 URL 使用 PUT 方法
    try:
        # 先尝试 PUT
        resp = requests.put(
            upload_url,
            data=file_data,
            headers=cos_headers,
            timeout=120
        )
        
        if resp.status_code in (200, 201, 204):
            print(f"  [COS] ✅ 上传成功 (PUT, status={resp.status_code})")
            return True
        else:
            print(f"  [COS] ⚠️ PUT 返回 {resp.status_code}，尝试 POST...")
            print(f"  [COS] Response: {resp.text[:500]}")
            
            # 尝试 POST
            resp2 = requests.post(
                upload_url,
                data=file_data,
                headers=cos_headers,
                timeout=120
            )
            
            if resp2.status_code in (200, 201, 204):
                print(f"  [COS] ✅ 上传成功 (POST, status={resp2.status_code})")
                return True
            else:
                print(f"  [COS] ❌ POST 也失败: {resp2.status_code}")
                print(f"  [COS] Response: {resp2.text[:500]}")
                return False
                
    except Exception as e:
        print(f"  [COS] ❌ 上传异常: {e}")
        return False

def upload_to_ima(file_path):
    """
    完整上传文件到 IMA 知识库
    
    Returns:
        bool: 是否成功
    """
    print("📚 IMA 知识库归档（完整版）")
    print(f"   文件: {file_path}")
    print(f"   知识库 ID: {KNOWLEDGE_BASE_ID}")
    
    if not os.path.exists(file_path):
        print(f"  ❌ 文件不存在: {file_path}")
        return False
    
    try:
        headers = get_headers()
    except ValueError as e:
        print(f"  ❌ {e}")
        return False
    
    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    
    # ========== Step 1: preflight_check ==========
    print("  [Step 1/5] preflight_check（检查文件是否可上传）...")
    try:
        preflight_data = {
            "filename": filename,
            "filesize": filesize,
            "knowledge_base_id": KNOWLEDGE_BASE_ID
        }
        resp = requests.post(
            f"{IMA_API_BASE}/preflight-check",
            headers=headers,
            json=preflight_data,
            timeout=30
        )
        if resp.status_code == 200:
            print("    ✅ preflight 检查通过")
        else:
            print(f"    ⚠️ preflight 返回 {resp.status_code}: {resp.text[:300]}")
            # 某些实现可能没有 preflight 接口，继续执行
    except Exception as e:
        print(f"    ⚠️ preflight 调用失败（继续执行）: {e}")
    
    # ========== Step 2: check_repeated_names ==========
    print("  [Step 2/5] check_repeated_names（检查重名）...")
    try:
        check_data = {
            "knowledge_base_id": KNOWLEDGE_BASE_ID,
            "names": [filename]
        }
        resp = requests.post(
            f"{IMA_API_BASE}/check-repeated-names",
            headers=headers,
            json=check_data,
            timeout=30
        )
        if resp.status_code == 200:
            result = resp.json()
            repeated = result.get("repeated", [])
            if repeated:
                print(f"    ⚠️ 发现重名文件: {repeated}")
                # 重命名文件
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}{ext}"
                print(f"    📝 重命名为: {filename}")
            else:
                print("    ✅ 无重名文件")
        else:
            print(f"    ⚠️ check_repeated 返回 {resp.status_code}（继续执行）")
    except Exception as e:
        print(f"    ⚠️ check_repeated 调用失败（继续执行）: {e}")
    
    # ========== Step 3: create_media ==========
    print("  [Step 3/5] create_media（获取 COS 上传凭证）...")
    try:
        create_data = {
            "knowledge_base_id": KNOWLEDGE_BASE_ID,
            "filename": filename,
            "filesize": filesize,
            "mime_type": "text/markdown" if filename.endswith(".md") else "application/octet-stream"
        }
        resp = requests.post(
            f"{IMA_API_BASE}/create-media",
            headers=headers,
            json=create_data,
            timeout=30
        )
        
        if resp.status_code != 200:
            print(f"    ❌ create_media 失败: {resp.status_code}")
            print(f"    Response: {resp.text[:500]}")
            return False
        
        media_result = resp.json()
        media_id = media_result.get("media_id") or media_result.get("id")
        cos_credentials = media_result.get("cos_credentials") or media_result.get("upload_credentials") or media_result
        
        print(f"    ✅ 媒体创建成功, media_id={media_id}")
        
    except Exception as e:
        print(f"    ❌ create_media 异常: {e}")
        return False
    
    # ========== Step 4: 上传文件到 COS ==========
    print("  [Step 4/5] 上传文件到 COS...")
    cos_success = upload_to_cos(file_path, cos_credentials)
    
    if not cos_success:
        print("    ❌ COS 上传失败")
        return False
    
    # ========== Step 5: add_knowledge ==========
    print("  [Step 5/5] add_knowledge（添加到知识库）...")
    try:
        add_data = {
            "knowledge_base_id": KNOWLEDGE_BASE_ID,
            "media_id": media_id
        }
        resp = requests.post(
            f"{IMA_API_BASE}/add-knowledge",
            headers=headers,
            json=add_data,
            timeout=30
        )
        
        if resp.status_code == 200:
            print("    ✅ 成功添加到知识库！")
            print(f"    📚 文件已归档到: 杨剑的知识库")
            return True
        else:
            print(f"    ❌ add_knowledge 失败: {resp.status_code}")
            print(f"    Response: {resp.text[:500]}")
            return False
            
    except Exception as e:
        print(f"    ❌ add_knowledge 异常: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        upload_to_ima(sys.argv[1])
    else:
        print("用法: python ima_uploader.py <file_path>")
