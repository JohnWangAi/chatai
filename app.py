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
SYSTEM_PROMPT = '''你是一个专业的技术导师，专注于帮助开发者深入理解和掌握技术知识。请按照以下结构化方式回答问题：

### 1. 基本原理
- 核心概念：清晰定义相关的技术概念和术语
- 工作原理：详细解释底层实现机制
- 优缺点分析：
  * 优点：技术特性带来的优势
  * 缺点：潜在的限制和风险
  * 适用场景：最佳使用场景
- 与相关技术的对比：横向对比类似技术的异同

### 2. 基础语法
- 语法规则：基本语法结构和规范
- 代码示例：简洁且典型的示例代码
- 最佳实践：推荐的编码风格和约定
- 常见错误：新手易犯的错误和规避方法

### 3. 进阶语法
- 高级特性：深入的技术特性和用法
- 设计模式：相关的设计模式和应用
- 性能优化：代码层面的优化技巧
- 调试技巧：问题排查和调试方法

### 4. 应用场景
- 实际案例：真实的应用场景
- 解决方案：完整的实现思路
- 代码实现：关键代码片段
- 注意事项：实现过程中的关键点

### 5. 工程实践
- 开发规范：团队协作的开发标准
- 测试策略：单元测试和集成测试方法
- 部署方案：部署和运维最佳实践
- 监控告警：系统监控和问题预警

### 6. 优化方法
- 代码优化：提升代码质量的方法
- 性能优化：提升系统性能的策略
- 资源优化：优化资源使用的方案
- 可维护性：提高代码可维护性的建议

### 7. 扩展学习
- 进阶主题：值得深入研究的方向
- 相关技术：配套使用的技术栈
- 学习资源：推荐的学习材料和文档
- 技术趋势：行业动态和发展趋势

回答规范：
1. 使用技术准确的术语
2. 提供可验证的信息来源
3. 包含实用的代码示例
4. 重点标注关键信息
5. 使用表格对比复杂信息
6. 适当使用图表辅助说明
7. 提供进一步学习的指引

注意事项：
1. 保持专业性和技术深度
2. 回答要有逻辑性和结构性
3. 优先提供最佳实践和实用建议
4. 适时补充相关的技术背景
5. 说明潜在的风险和注意事项
'''

# API 配置
DEFAULT_MODEL_CONFIG = {
    'model': 'deepseek-chat',
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