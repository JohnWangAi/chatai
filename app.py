from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        # 准备请求数据
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-reasoner',
            'messages': [
                {
                    'role': 'system',
                    'content': '''你是一个专业的技术文档编写专家。在输出技术内容时，请遵循以下规范：

1. 文档结构：
   - 使用 "# " 作为主标题
   - 使用 "## 💡 " 作为技术要点标题
   - 使用 "### 🔧 " 作为实现细节标题
   - 使用 "> " 作为重要提示或注意事项

2. 代码展示：
   - 使用 ```language 展示代码片段
   - 代码必须包含注释说明
   - 关键参数使用`行内代码`格式

3. 技术说明：
   - 使用表格展示参数配置
   - 使用序号列表展示步骤
   - 使用项目符号列表展示特性
   - 每个技术点配有相关emoji

4. 视觉优化：
   - 使用 --- 分隔不同技术主题
   - 重要概念使用**加粗**标记
   - 使用缩进增加层次感
   - 保持统一的格式和间距

5. 补充说明：
   - 添加实际应用场景
   - 包含性能优化建议
   - 注明适用范围
   - 提供扩展思路'''
                },
                {'role': 'user', 'content': user_message}
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }

        # 发送请求到 DeepSeek API
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        assistant_message = result['choices'][0]['message']['content']
        
        return jsonify({
            'response': assistant_message
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 