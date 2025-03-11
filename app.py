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
                    'content': '''你是一个专业的分析专家。请按照以下结构化格式展示你的分析和决策过程：

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