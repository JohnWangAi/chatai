"""
DeepSeek Chat Application
------------------------
A Flask-based chat application that uses DeepSeek API for intelligent responses.
"""

import os
from typing import Dict, Any

import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Flask 应用初始化
app = Flask(__name__)

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
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    处理聊天请求
    
    Returns:
        JSON 响应，包含 AI 的回复或错误信息
    """
    try:
        # 获取并验证用户输入
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        # 准备请求数据
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 创建请求负载
        payload = create_chat_payload(user_message)

        # 发送请求到 DeepSeek API
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        assistant_message = result['choices'][0]['message']['content']
        
        return jsonify({
            'response': assistant_message
        })

    except requests.exceptions.RequestException as e:
        # 处理 API 请求错误
        error_message = f"API 请求错误: {str(e)}"
        return jsonify({'error': error_message}), 503
        
    except Exception as e:
        # 处理其他未预期的错误
        error_message = f"服务器错误: {str(e)}"
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    # 确保 API 密钥已设置
    if not DEEPSEEK_API_KEY:
        raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
        
    # 启动应用
    app.run(debug=True) 