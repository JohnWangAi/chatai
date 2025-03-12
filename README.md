这是一个使用 DeepSeek API 的简单聊天应用。用户可以输入问题，系统会调用 DeepSeek API 生成回答。

## 功能特点

- 简洁美观的用户界面
- 实时对话功能
- 支持回车发送消息
- 错误处理和加载状态显示

## 本地安装运行

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 创建 `.env` 文件并添加你的 DeepSeek API 密钥：
   ```
   DEEPSEEK_API_KEY=你的API密钥
   ```
4. 运行应用：
   ```bash
   python app.py
   ```
5. 在浏览器中访问 `http://localhost:8000`

## Docker 部署

### 1. 构建镜像

在项目根目录执行以下命令构建 Docker 镜像：

```bash
docker build -t deepseek-chat-app .
```

### 2. 运行容器

使用以下命令运行容器（将 YOUR_API_KEY 替换为你的实际 API 密钥）：

```bash
docker run -d -p 8000:8000 -e DEEPSEEK_API_KEY=YOUR_API_KEY deepseek-chat-app
```

命令说明：
- `-d`: 在后台运行容器
- `-p 8000:8000`: 将容器的 8000 端口映射到主机的 8000 端口
- `-e DEEPSEEK_API_KEY=YOUR_API_KEY`: 设置环境变量

### 3. 访问应用
http://YOUR_IP:8000/