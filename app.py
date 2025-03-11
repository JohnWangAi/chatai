"""
DeepSeek Chat Application
------------------------
A Flask-based chat application that uses DeepSeek API for intelligent responses.
"""

import os
import sys
from typing import Dict, Any
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, render_template, request, jsonify, make_response
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Flask 应用初始化
app = Flask(__name__)

# 配置 requests 会话
session = requests.Session()
retry_strategy = Retry(
    total=5,  # 增加重试次数
    backoff_factor=0.5,  # 减小退避因子使重试更快
    status_forcelist=[408, 429, 500, 502, 503, 504],  # 添加 408 超时状态码
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],  # 允许 POST 重试
    respect_retry_after_header=True
)
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=10,
    pool_maxsize=10
)
session.mount("https://", adapter)

# 手动处理 CORS
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

app.after_request(add_cors_headers)

# API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 系统提示配置
SYSTEM_PROMPT = '''你是一个专业的分析专家。请按照以下结构化格式展示你的分析和决策过程：

# 🔍 问题分析
1. **问题要点**
   - 列出关键问题点
   - 明确需求和目标

2. **背景信息**
   - 相关上下文
   - 限制条件

# 🤔 思考过程
1. **方案设计**
   ```
   方案A：...
   优点：...
   缺点：...

3. **决策推理**
   > 💡 核心决策点：...
   > 🎯 选择理由：...



2. **注意事项**
   - ⚠️ 风险点
   - 🔑 关键成功因素
   - 📊 评估指标

# 💡 扩展思考
- 可能的优化方向
- 长期发展建议
- 替代方案

请确保每个环节都清晰可见，帮助用户理解完整的分析和决策过程。'''

# API 配置
DEFAULT_MODEL_CONFIG = {
    'model': 'deepseek-reasoner',
    'temperature': 0.7,
    'max_tokens': 2000
}

def create_chat_payload(message: str) -> Dict[str, Any]:
    """
    创建发送到 DeepSeek API 的请求负载
    
    Args:
        message: 用户输入的消息
        
    Returns:
        Dict: API 请求的配置字典
    """
    return {
        **DEFAULT_MODEL_CONFIG,
        'messages': [
            {
                'role': 'system',
                'content': SYSTEM_PROMPT
            },
            {
                'role': 'user',
                'content': message
            }
        ]
    }

@app.route('/')
def home():
    """渲染主页"""
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.warning(f"Error rendering template: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """处理聊天请求"""
    if request.method == 'OPTIONS':
        response = make_response('')
        response.status_code = 204
        return response

    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        if not DEEPSEEK_API_KEY:
            return jsonify({'error': 'API 密钥未配置'}), 500

        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = create_chat_payload(user_message)

        # 添加重试逻辑
        max_retries = 3
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                response = session.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=(10, 90),  # (连接超时, 读取超时)
                    verify=True
                )
                response.raise_for_status()
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2
        
        result = response.json()
        assistant_message = result['choices'][0]['message']['content']
        
        return jsonify({
            'response': assistant_message
        })

    except requests.exceptions.SSLError as e:
        app.logger.warning(f"SSL Error: {str(e)}")
        return jsonify({'error': 'SSL 连接错误，请稍后重试'}), 503

    except requests.exceptions.ReadTimeout as e:
        app.logger.warning(f"Timeout Error: {str(e)}")
        return jsonify({'error': '请求超时，请稍后重试'}), 504

    except requests.exceptions.RequestException as e:
        app.logger.warning(f"API request error: {str(e)}")
        return jsonify({'error': f"API 请求错误: {str(e)}"}), 503
        
    except Exception as e:
        app.logger.warning(f"Server error: {str(e)}")
        return jsonify({'error': f"服务器错误: {str(e)}"}), 500

# 应用配置
app.debug = False

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 