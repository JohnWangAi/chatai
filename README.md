# DeepSeek 聊天助手

这是一个使用 DeepSeek API 的简单聊天应用。用户可以输入问题，系统会调用 DeepSeek API 生成回答。

## 功能特点

- 简洁美观的用户界面
- 实时对话功能
- 支持回车发送消息
- 错误处理和加载状态显示

## 安装步骤

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 创建 `.env` 文件并添加你的 DeepSeek API 密钥：
   ```
   DEEPSEEK_API_KEY=你的API密钥
   ```

## 运行应用

1. 确保已经设置好 API 密钥
2. 运行应用：
   ```bash
   python app.py
   ```
3. 在浏览器中访问 `http://localhost:8000`

## 注意事项

- 请确保你有有效的 DeepSeek API 密钥
- 不要将 API 密钥提交到版本控制系统中
- 建议在生产环境中使用更安全的配置管理方式 