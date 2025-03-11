"""
DeepSeek Chat Application
------------------------
A Flask-based chat application that uses DeepSeek API for intelligent responses.
"""

import os
import sys
from typing import Dict, Any

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
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# 手动处理 CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
   
   方案B：...
   优点：...
   缺点：...
   ```

2. **评估标准**
   | 评估维度 | 权重 | 说明 |
   |---------|------|-----|
   | 可行性   | 高   | ... |
   | 成本     | 中   | ... |
   | 效果     | 高   | ... |

3. **决策推理**
   > 💡 核心决策点：...
   > 🎯 选择理由：...

# 📝 最终方案
1. **具体实施步骤**
   1. 第一步：...
   2. 第二步：...
   3. 第三步：...

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
        app.logger.error(f"Error rendering template: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """处理聊天请求"""
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        data = request.get_json()
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

        response = session.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
            verify=True
        )
        response.raise_for_status()
        
        result = response.json()
        assistant_message = result['choices'][0]['message']['content']
        
        return jsonify({
            'response': assistant_message
        })

    except requests.exceptions.SSLError as e:
        app.logger.error(f"SSL Error: {str(e)}")
        return jsonify({'error': 'SSL 连接错误，请稍后重试'}), 503

    except requests.exceptions.RequestException as e:
        app.logger.error(f"API request error: {str(e)}")
        return jsonify({'error': f"API 请求错误: {str(e)}"}), 503
        
    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({'error': f"服务器错误: {str(e)}"}), 500

# 应用配置
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 