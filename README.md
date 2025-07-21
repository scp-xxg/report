# 🤖 多智能体报告生成系统
> 🚀 基于多智能体协作的智能报告生成系统，支持 Web 界面、API 接口和多模型部署

## 📝 项目简介

这是一个基于多智能体协作的自动化报告生成系统，通过不同功能的智能体协作完成报告的撰写工作。系统提供了命令行接口、Web界面和API接口，支持多种使用场景。

## ✨ 核心特性

- 🎯 **智能大纲生成**：自动分析主题并生成逻辑结构
- ✍️ **多智能体协作**：4个专业智能体分工合作
- 📊 **图表自动生成**：根据内容生成相关可视化图表
- 🎨 **内容智能润色**：自动优化语言表达和逻辑结构
- 📄 **多格式输出**：支持Markdown、Word、PDF、JSON等格式
- 🌐 **Web用户界面**：直观的Web界面，易于使用
- 🔌 **API接口**：完整的REST API，便于集成
- ⚙️ **灵活配置**：支持多种模型和自定义参数
- 🚀 **一键部署**：支持本地模型和云端API
- 🔧 **易于扩展**：模块化设计，便于二次开发

## 🎬 演示

### 📊 生成效果展示
系统可以生成包含以下要素的专业报告：
- 📋 结构化大纲（自动生成逻辑层次）
- 📝 详细内容（多智能体协作撰写）  
- 📊 数据图表（自动生成可视化）
- 🎨 专业排版（多格式输出支持）

### 🌐 Web 界面预览
- **现代化设计**：渐变色彩 + 响应式布局
- **步骤引导**：4步完成报告生成
- **实时反馈**：智能体工作状态可视化
- **多端适配**：支持桌面和移动设备

## 🏗️ 系统架构

### 🤖 核心智能体
- **大纲生成智能体** (`outline_agent.py`): 负责根据主题生成报告大纲
- **内容生成智能体** (`content_agent.py`): 负责撰写各章节具体内容
- **润色智能体** (`polish_agent.py`): 负责对内容进行语言优化
- **图表生成智能体** (`chart_agent.py`): 负责生成数据可视化图表

### 🔄 协调系统
- **协调智能体** (`coordinator.py`): 负责整个工作流程的调度和管理

### 🛠️ 工具模块
- **LLM客户端** (`utils/llm_client.py`): 统一的大模型接口
- **报告格式化** (`utils/report_formatter.py`): 多格式报告输出

## 🚀 快速开始

### � 一键安装

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/multi-agent-report-generator.git
cd multi-agent-report-generator

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env

# 配置大模型（可选择 OpenAI API 或本地模型）
python configure_llm.py
```

### ⚡ 10秒体验

```bash
# 快速演示（使用演示模式，无需配置）
python quick_start.py

# 启动Web界面
python web_server.py
# 访问 http://localhost:8080
```

### �🖥️ Web界面使用（推荐）

1. **启动Web服务**
   ```bash
   cd /home/scp/report
   python web_server.py
   ```

2. **打开浏览器**
   访问 http://localhost:8080

3. **按步骤操作**
   - 输入研究主题
   - 选择研究角度
   - 配置报告参数
   - 生成并下载报告

### ⚡ 命令行快速体验

```bash
# 快速演示
python quick_start.py

# 运行测试
python test.py

# 完整示例
python examples/demo.py
```

## 🔧 配置大模型

本系统支持多种大模型接口，包括OpenAI API、本地vLLM等。

### 方法一：自动配置（推荐）
```bash
python configure_llm.py
```

### 方法二：手动配置

#### OpenAI API配置
1. 获取OpenAI API密钥
2. 编辑 `.env` 文件：
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL_TYPE=openai
DEFAULT_MODEL_NAME=gpt-3.5-turbo
```

#### 本地vLLM配置

vLLM是高性能的本地大模型推理引擎，支持多种开源模型。

**快速配置vLLM：**
```bash
# 一键安装和配置
./setup_vllm.sh

# 启动vLLM服务
./start_vllm.sh

# 测试性能
python test_vllm_performance.py
```

**手动配置vLLM：**

1. 安装vLLM：
```bash
pip install vllm
```

2. 下载模型（推荐Qwen2-7B）：
```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen2-7B-Instruct')
"
```

3. 启动vLLM服务：
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000
```

4. 配置项目：
```bash
# 编辑 .env 文件
VLLM_BASE_URL=http://localhost:8000
DEFAULT_MODEL_TYPE=vllm
DEFAULT_MODEL_NAME=Qwen/Qwen2-7B-Instruct
```

**推荐模型列表：**
- `Qwen/Qwen2-1.5B-Instruct` - 轻量级（4GB显存）
- `Qwen/Qwen2-7B-Instruct` - 均衡版（8GB显存）
- `THUDM/chatglm3-6b` - 中文优化（8GB显存）

详细配置指南请查看：[VLLM_SETUP_GUIDE.md](VLLM_SETUP_GUIDE.md)

#### 演示模式（无需API）
```bash
# 使用演示模式体验完整功能
DEFAULT_MODEL_TYPE=demo
DEFAULT_MODEL_NAME=demo-model
```

## 📦 安装配置

### 1️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 2️⃣ 环境配置
```bash
# 复制配置模板
cp .env.example .env

# 使用配置工具
python configure_llm.py

# 或手动编辑配置文件
nano .env
```

### 3️⃣ 验证配置
```bash
# 测试配置
python configure_llm.py

# 选择选项4进行测试
```

## 💻 使用方式

### 🌐 Web界面
```bash
python web_server.py
# 访问 http://localhost:8080
```

### ⚡ 命令行快速体验

```bash
# 快速演示
python quick_start.py

# 运行测试
python test.py

# 完整示例
python examples/demo.py

# 性能测试（vLLM）
python test_vllm_performance.py
```

## 📁 项目结构

```
report/
├── 📄 README.md                # 项目说明
├── 🔧 requirements.txt         # 依赖清单
├── ⚙️ config.json             # 系统配置
├── 🌐 web_server.py           # Web服务器
├── 🎯 coordinator.py          # 协调智能体
├── 🤖 agents/                 # 智能体模块
│   ├── outline_agent.py       # 大纲生成智能体
│   ├── content_agent.py       # 内容生成智能体
│   ├── polish_agent.py        # 润色智能体
│   └── chart_agent.py         # 图表生成智能体
├── 🛠️ utils/                  # 工具模块
│   ├── llm_client.py          # 大模型客户端
│   └── report_formatter.py    # 报告格式化
├── 🌐 web/                    # Web前端
│   ├── index.html             # 主页面
│   ├── style.css              # 样式文件
│   └── script.js              # 交互脚本
├── 📝 examples/               # 使用示例
│   └── demo.py                # 完整示例
├── 📊 output/                 # 输出目录
├── 🌐 web_output/            # Web输出目录
└── 📚 docs/                  # 文档目录
    ├── USAGE_GUIDE.md         # 使用教程
    ├── WEB_GUIDE.md           # Web界面指南
    └── PROJECT_SUMMARY.md     # 项目总结
```

## 🎯 功能特性

### 📋 报告类型
- **研究报告**：学术研究导向，深度分析
- **分析报告**：数据分析导向，客观评估
- **技术文档**：技术说明导向，详细阐述
- **商业计划**：商业规划导向，实用性强

### 📊 输出格式
- **Markdown**：便于编辑和版本控制
- **Word文档**：商务场景常用格式
- **PDF**：正式发布和打印格式
- **JSON数据**：程序化处理和集成

### 🔧 配置选项
- **模型选择**：OpenAI、vLLM、演示模式
- **报告长度**：简要版、标准版、详细版
- **启用功能**：图表生成、内容润色
- **自定义参数**：写作风格、章节数量等

## 🌟 界面展示

### 🖥️ Web界面特色
- **渐进式体验**：步骤式引导，简化操作流程
- **实时反馈**：智能体工作状态实时显示
- **响应式设计**：支持桌面端和移动端访问
- **现代化UI**：美观的渐变设计和动画效果

### 📱 主要功能区域
1. **研究方向**：主题输入和文档上传
2. **想法提出**：研究角度选择和自定义
3. **信息搜集**：数据源选择和搜集进度
4. **报告整理**：参数配置和生成过程

## 🔧 开发说明

### 🛠️ 技术栈
- **后端**: Python + Flask + LangChain
- **前端**: HTML5 + CSS3 + JavaScript ES6+
- **AI**: OpenAI GPT / 本地LLM
- **可视化**: Matplotlib + Plotly

### 📦 扩展开发
- 支持新的智能体模块
- 集成更多输出格式
- 添加更多模型支持
- 自定义界面主题

## 📊 使用统计

### ✅ 已完成功能
- ✅ 多智能体协作系统
- ✅ Web用户界面
- ✅ REST API接口
- ✅ 多格式输出
- ✅ 配置管理系统
- ✅ 完整文档和示例

### 🚀 未来计划
- 🔄 增加更多智能体类型
- 🌍 支持多语言界面
- 📱 移动端专用界面
- 🔐 用户认证和权限管理
- 📈 使用统计和分析

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

### 🌟 贡献者

感谢所有为这个项目做出贡献的开发者！

### 🐛 问题反馈

如果您发现任何问题或有功能建议，请：
- 📝 [创建 Issue](https://github.com/YOUR_USERNAME/multi-agent-report-generator/issues)
- 💬 参与 [讨论](https://github.com/YOUR_USERNAME/multi-agent-report-generator/discussions)

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 查看 LICENSE 文件了解详情。

## 🙏 致谢

- [LangChain](https://langchain.com/) - 强大的AI应用开发框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [vLLM](https://github.com/vllm-project/vllm) - 高性能模型推理引擎
- 所有开源大模型项目的贡献者

## 📞 联系方式

- 📧 邮箱：[创建 Issue](https://github.com/YOUR_USERNAME/multi-agent-report-generator/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/YOUR_USERNAME/multi-agent-report-generator/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个星星！
