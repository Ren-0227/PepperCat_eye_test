# 🏥 眼部健康智能系统 (Eye Health AI Suite)



## 📖 项目简介

这是一个集成了**Web端眼部健康管理**和**智能桌宠PepperCat**的综合性AI健康系统。系统采用本地大模型推理，支持自然语言命令、OCT图片分析、数据可视化、视力检测、健康训练、AI对话等多模态交互，适合个人和家庭日常眼部健康管理。

---

## 🌟 主要亮点
- **本地AI大模型**：支持DeepSeek/Ollama，隐私安全
- **OCT图片智能分析**：自动识别OCT图片，生成AI健康报告
- **自然语言命令**：一句话调用任意健康工具，自动规划多步任务
- **多工具链集成**：Web搜索、文件操作、数据可视化、AI分析、健康游戏
- **桌宠智能陪伴**：PepperCat桌宠拟人化互动，支持语音/文本/游戏/对战
- **Web+桌宠双端体验**：Web端专业管理，桌宠端趣味陪伴
- **极致Prompt设计**：LLM自动选择最合适工具，OCT分析/图片分析/视力检测不混淆

---

## 📋 目录
- [系统架构](#系统架构)
- [功能总览](#功能总览)
- [快速开始](#快速开始)
- [AI工具链与自然语言命令](#ai工具链与自然语言命令)
- [OCT图片分析与健康报告](#oct图片分析与健康报告)
- [数据可视化与趋势分析](#数据可视化与趋势分析)
- [常见问题](#常见问题)
- [开发指南](#开发指南)

---

## 🏗️ 系统架构
```
Eye Health AI Suite
├── 🌐 Web端 (Flask)
│   ├── 智能对话/健康管理/数据分析
│   └── 视力检测/训练/报告
└── 🐱 桌宠端 (PyQt6)
    ├── 智能桌宠PepperCat
    ├── AI工具链/自然语言命令
    ├── OCT/图片分析/健康游戏
    └── 网络对战/多模态交互
```

---

## 🚀 功能总览

### 🌐 Web端
- 智能对话与健康咨询
- 视力检测（E字表/色觉/对比度/眼动追踪）
- 训练游戏（记忆/专注/反应/眼动）
- 数据分析与趋势可视化
- 个性化健康报告

### 🐱 桌宠端
- 拟人化桌宠PepperCat，情感/记忆/动画
- 眼部健康游戏（记忆/专注/反应）
- AI工具链：Web搜索、文件、可视化、AI分析
- OCT图片分析与AI健康报告
- 网络对战/多玩家互动
- 语音/文本/自然语言命令

---

## ⚡ 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
cd PepperCat-main
pip install -r requirements.txt
```

### 2. 部署大模型
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull deepseek-chat
ollama serve
```

### 3. 启动系统
- Web端：`python start_web_app.py` 访问 http://localhost:5000
- 桌宠端：`cd PepperCat-main && python main.py`
- 一键启动：`python start_all.py`

---

## 🤖 AI工具链与自然语言命令

### 智能Prompt设计（核心）
- **oct_analysis**：只要命令中有“OCT”、“光学相干断层扫描”、“OCT图片”，必须用oct_analysis，不能用image_analysis或vision_test。
- **image_analysis**：仅分析普通照片，不能分析OCT图片。
- **vision_test**：仅做视力表/E字表测试，不能分析图片。
- **visualize**：数据可视化，支持csv/json/趋势分析。
- **eye_games**：健康训练游戏。

#### 示例命令
- “分析我的OCT图片pictures/eyes.png” → oct_analysis
- “分析自拍眼部照片” → image_analysis
- “做一次视力检测” → vision_test
- “画出视力趋势图” → visualize
- “我想玩记忆训练游戏” → eye_games

#### 多步任务自动规划
- “查找北京天气并保存为csv并画趋势图”
- “读取eyes_test.csv并分析”
- “分析图片并生成健康报告”

---

## 🩺 OCT图片分析与健康报告

- 支持OCT图片（光学相干断层扫描）智能分析，自动识别青光眼、黄斑变性、糖尿病视网膜病变等
- 一句话命令即可分析本地/桌面/pictures目录下的OCT图片
- 自动生成AI健康报告（含检测结果、置信度、健康建议、就医建议等）
- 完全本地推理，隐私安全

#### 命令示例
- “分析桌面上的eyes.png OCT图片”
- “分析图片pictures/glaucoma_classification_1.png”
- “请帮我分析这张OCT检查图片”

---

## 📊 数据可视化与趋势分析

- 支持csv/json数据的折线图、柱状图、散点图、热力图、箱线图、相关性分析等
- 一句话命令自动生成趋势图/统计图/综合分析
- 支持Web端和桌宠端可视化，图片自动保存到visualization_outputs/

#### 命令示例
- “读取eyes_test.csv并画出视力趋势图”
- “分析csv文件并生成相关性热力图”
- “生成视力变化折线图”

---

## 🐱 桌宠端特色
- 多种心情/动画/状态，情感系统
- 记忆系统，个性化互动
- 健康训练游戏，语音/文本命令启动
- 网络对战/多玩家同步
- 支持AI工具链所有功能

---

## 🛠️ 技术架构
- Python 3.8+ / Flask / PyQt6 / OpenManus / Ollama / DeepSeek
- OpenCV / MediaPipe / PyTorch / NumPy / Pandas
- HTML5 / Bootstrap / Chart.js
- JSON/SQLite/本地文件系统

---

## 📦 安装与开发指南
- 见上文“快速开始”与“开发指南”章节
- 支持虚拟环境、分支开发、自动化测试、代码格式化

---

## ❓ 常见问题
- **OCT分析报错**：请确认oct_scripted.pt/best_model.pth已放在根目录
- **AI对话无响应**：请确认Ollama和DeepSeek已启动
- **图片路径问题**：请将图片放到pictures/目录或用绝对路径
- **Web端/桌宠端无法启动**：请检查依赖和Python版本

---

## 📄 许可证
MIT License

---

## 🙏 致谢
- OpenManus/DeepSeek/Ollama团队
- 所有开源贡献者

---

*让AI守护你的眼健康，体验智能与温度并存的健康管理！*

