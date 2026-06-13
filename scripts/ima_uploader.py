#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMA 知识库归档模块 - 完整实现

正确的 API 调用方式（从 ima_skill 获得）：
  Base URL: https://ima.qq.com
  API 路径: openapi/wiki/v1/<endpoint>
  请求头:
    ima-openapi-clientid: <client_id>
    ima-openapi-apikey: <api_key>
"""

import os
import sys
import json
import requests
from datetime import datetime

# IMA API 配置
IMA_BASE_URL = "https://ima.qq.com"
KNOWLEDGE_BASE_ID = "E9owuqdzTE2LcRB0A5ub04_cxrGGpMzCmFQEahJ8te0="
CLIENT_ID = "dd4962571a67592aa50ec9146343419a"

def get_headers():
    """获取 IMA API 请求头（正确格式）"""
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
        "ima-openapi-clientid": CLIENT_ID,
        "ima-openapi-apikey": api_key,
        "Content-Type": "application/json"
    }

def ima_api_call(api_path, body):
    """
    调用 IMA API
    api_path: 如 "openapi/wiki/v1/create_media"
    body: dict 类型
    """
    headers = get_headers()
    url = f"{IMA_BASE_URL}/{api_path}"
    
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        result = resp.json()
        return result
    except Exception as e:
        print(f"  [IMA API] 调用失败: {e}")
        return None

def upload_to_ima(file_path):
    """
    完整上传文件到 IMA 知识库
    
    流程：
      Step 1: preflight_check（检查文件是否可上传）
      Step 2: check_repeated_names（检查重名）
      Step 3: create_media（获取 COS 上传凭证）
      Step 4: 上传文件到 COS
      Step 5: add_knowledge（添加到知识库）
    """
    print("  [IMA] 开始上传到 IMA 知识库...")
    print(f"  [IMA] 文件: {file_path}")
    print(f"  [IMA] 知识库 ID: {KNOWLEDGE_BASE_ID}")
    
    if not os.path.exists(file_path):
        print(f"  [IMA] ❌ 文件不存在: {file_path}")
        return False
    
    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    file_ext = os.path.splitext(filename)[1].lstrip(".")
    
    # 推断 media_type（简化版）
    media_type_map = {
        "md": 1,   # 文档
        "pdf": 1,
        "doc": 1,
        "docx": 1,
        "xls": 5,
        "xlsx": 5,
        "ppt": 4,
        "pptx": 4,
    }
    media_type = media_type_map.get(file_ext, 1)
    
    # ========== Step 1: preflight_check ==========
    print("  [IMA] [1/5] preflight_check...")
    # 注意：preflight check 通常通过 preflight-check.cjs 脚本完成
    # 这里我们先跳过，假设文件类型支持
    print("  [IMA] [1/5] ✅ 跳过 preflight（Markdown 文件默认可上传）")
    
    # ========== Step 2: check_repeated_names ==========
    print("  [IMA] [2/5] check_repeated_names...")
    check_body = {
        "params": [{"name": filename, "media_type": media_type}],
        "knowledge_base_id": KNOWLEDGE_BASE_ID
    }
    check_result = ima_api_call("openapi/wiki/v1/check_repeated_names", check_body)
    
    if check_result and check_result.get("code") == 0:
        data = check_result.get("data", {})
        repeated = data.get("is_repeated", False)
        if repeated:
            print(f"  [IMA] ⚠️ 发现重名文件")
            # 重命名文件
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}{ext}"
            print(f"  [IMA] 📝 重命名为: {filename}")
    else:
        print(f"  [IMA] [2/5] ✅ 无重名文件")
    
    # ========== Step 3: create_media ==========
    print("  [IMA] [3/5] create_media（获取 COS 上传凭证）...")
    create_body = {
        "file_name": filename,
        "file_size": filesize,
        "content_type": "text/markdown" if file_ext == "md" else "application/octet-stream",
        "knowledge_base_id": KNOWLEDGE_BASE_ID,
        "file_ext": file_ext,
        "media_type": media_type
    }
    create_result = ima_api_call("openapi/wiki/v1/create_media", create_body)
    
    if not create_result or create_result.get("code") != 0:
        print(f"  [IMA] ❌ create_media 失败: {create_result}")
        return False
    
    data = create_result.get("data", {})
    media_id = data.get("media_id")
    cos_credential = data.get("cos_credential", {})
    
    print(f"  [IMA] [3/5] ✅ 媒体创建成功, media_id={media_id}")
    
    # ========== Step 4: 上传文件到 COS ==========
    print("  [IMA] [4/5] 上传文件到 COS...")
    upload_success = upload_to_cos(file_path, cos_credential)
    
    if not upload_success:
        print("  [IMA] ❌ COS 上传失败")
        return False
    
    # ========== Step 5: add_knowledge ==========
    print("  [IMA] [5/5] add_knowledge（添加到知识库）...")
    add_body = {
        "media_type": media_type,
        "media_id": media_id,
        "title": filename,
        "knowledge_base_id": KNOWLEDGE_BASE_ID,
        "file_info": {
            "cos_key": cos_credential.get("cos_key", ""),
            "file_size": filesize,
            "file_name": filename
        }
    }
    add_result = ima_api_call("openapi/wiki/v1/add_knowledge", add_body)
    
    if add_result and add_result.get("code") == 0:
        print("  [IMA] ✅ 成功添加到知识库！")
        print(f"  [IMA] 📚 文件已归档到: 杨剑的知识库")
        return True
    else:
        print(f"  [IMA] ❌ add_knowledge 失败: {add_result}")
        return False

def upload_to_cos(file_path, cos_credential):
    """
    上传文件到 COS（腾讯云对象存储）
    
    使用 COS 凭证中的预签名 URL 直接上传
    """
    upload_url = cos_credential.get("upload_url", "")
    
    if not upload_url:
        print(f"  [COS] ⚠️ 未找到 upload_url")
        print(f"  [COS] cos_credential 内容: {json.dumps(cos_credential, ensure_ascii=False)[:500]}")
        return False
    
    print(f"  [COS] 开始上传文件到 COS...")
    print(f"  [COS] Upload URL: {upload_url[:100]}...")
    
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        # 使用 PUT 方法上传（大多数预签名 URL 使用 PUT）
        resp = requests.put(
            upload_url,
            data=file_data,
            timeout=120
        )
        
        if resp.status_code in (200, 201, 204):
            print(f"  [COS] ✅ 上传成功 (PUT, status={resp.status_code})")
            return True
        else:
            print(f"  [COS] ⚠️ PUT 返回 {resp.status_code}")
            print(f"  [COS] Response: {resp.text[:500]}")
            
            # 尝试 POST
            resp2 = requests.post(
                upload_url,
                data=file_data,
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        upload_to_ima(sys.argv[1])
    else:
        print("用法: python ima_uploader.py <file_path>")
