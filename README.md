
# 📚 TOEFL Word Reviewer (托福词汇闪卡复习工具)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![Vercel](https://img.shields.io/badge/Deployment-Vercel-black)
![License](https://img.shields.io/badge/license-MIT-grey)

一个基于 Python Flask 的轻量级在线背单词工具。专为托福词汇复习设计，支持自定义词汇表导入、闪卡（Flashcard）模式复习、错题实时记录以及导出功能。

本项目已针对 **Vercel Serverless** 环境进行了深度适配，并采用 **SPA (单页面应用)** 架构优化了前端交互体验。

---

## ✨ 功能特性 (Features)

* **📂 自定义导入**: 支持 `.csv` 和 `.xlsx` 格式的词汇表上传（适配王玉梅托福词汇表格式）。
* **🔀 多种复习模式**:
    * **按 List 复习**: 选择特定的 Word List 进行针对性训练。
    * **随机抽查**: 打乱所有上传的词汇进行综合测试。
* **🃏 交互式闪卡**:
    * 前端采用 CSS 3D 翻转动画。
    * **SPA 架构**: 点击“记住了/没记住”无需刷新页面，体验丝滑流畅，无网络延时感。
* **📝 实时错题本**:
    * 复习过程中，点击“没记住”的单词会实时添加到侧边栏（Sidebar）。
    * 支持随时展开/收起侧边栏查看当前未掌握的词汇。
* **💾 数据导出**: 支持将“没记住”的单词一键导出为 Excel 文件 (`.xlsx`)，方便二次复习。
* **☁️ 云端适配**: 代码已针对 Vercel 的只读文件系统和冷启动特性进行了优化（使用 `/tmp` 目录和内存流）。

---

## 🛠️ 技术栈 (Tech Stack)

* **后端**: Python, Flask, Pandas, Flask-Session
* **前端**: HTML5, CSS3 (Flexbox/Grid/Animations), JavaScript (Fetch API, ES6+)
* **部署**: Vercel (Serverless Function)

---

## 🚀 快速开始 (本地运行)

### 1. 克隆项目
```
git clone [https://github.com/你的用户名/word_learning.git](https://github.com/你的用户名/word_learning.git)
cd word_learning
```
2. 创建并激活虚拟环境 (推荐)
```Bash
# 使用 Conda
conda create -n word-app python=3.9
conda activate word-app
# 或者使用 venv
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```
3. 安装依赖
```
Bash
pip install -r requirements.txt
```
5. 运行应用
```
Bash
python app.py
```
7. 访问
打开浏览器访问: http://127.0.0.1:5000

提示: 如果想在局域网内（手机端）访问，请确保电脑和手机连接同一 WiFi，并查看终端输出的 IP 地址（如 http://192.168.x.x:5000）。

☁️ 部署到 Vercel
本项目已包含 vercel.json 配置文件，可直接一键部署。
将代码推送到 GitHub。
登录 Vercel 并连接你的 GitHub 账号。
点击 "Add New Project" 并导入该仓库。
Vercel 会自动识别 Python 环境，点击 "Deploy" 即可。
注意: 本项目使用了 Flask-Session 的文件系统模式。在 Vercel 环境下，代码会自动检测并将 Session 存储路径指向 /tmp 临时目录，以适应 Serverless 环境的只读限制。

📂 项目结构
```
Plaintext
word_learning/
├── app.py              # Flask 主程序 (包含后端逻辑与路由)
├── requirements.txt    # Python 依赖列表
├── vercel.json         # Vercel 部署配置文件
├── .gitignore          # Git 忽略配置
└── templates/          # 前端 HTML 模板
    ├── index.html      # 首页 (上传与模式选择)
    ├── review.html     # 复习页 (核心 SPA 页面)
    └── results.html    # 结果页 (统计与下载)
```
📄 词汇表格式说明
程序默认解析如下格式的 CSV/Excel 文件：
```
Col A (ID)	Col B (Word)	Col C (POS)	Col D (Def)	Col E (Syn)
Word List 1				
1	abandon	v.	放弃，遗弃	give up
2	abbreviate	v.	缩写	shorten
```
必须包含 以 "Word List" 开头的行作为列表分隔符。
程序会自动识别并归类单词到对应的 List 中。
