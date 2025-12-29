[English](README.md) | [中文](README_zh.md)

# 鸣潮角色红黑榜 🎮

![GitHub](https://img.shields.io/github/license/MoonShadow1976/WutheringWaves_Character_Selection?color=blue&style=for-the-badge)  ![GitHub last commit](https://img.shields.io/github/last-commit/MoonShadow1976/WutheringWaves_Character_Selection?style=for-the-badge)  ![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-brightgreen?style=for-the-badge)

一个交互式网络应用程序，允许《鸣潮》的粉丝创建和分享个性化的角色选择卡。🎨📱

## ✨ 主要功能

- **交互式网格界面** - 一个 3×4 的网格，可自定义鸣潮角色喜好选择
- **图像生成** - 使用 html2canvas 技术将用户选择转换为可分享的图像
- **多语言支持** - 支持中文和英文界面
- **响应式设计** - 在桌面和移动设备上均能无缝运行
- **可自定义标题** - 允许用户临时编辑网格标题，创建个性化卡片
- **二维码集成** - 包含一个链接到 GitHub 仓库的二维码

## 🚀 快速开始

1.  **访问网站**
    - 访问 [GitHub Pages URL](https://moonshadow1976.github.io/WutheringWaves_Character_Selection/)
2.  **选择角色**
    - 点击任意网格单元格选择角色
3.  **自定义标题（可选）**
    - 点击任意标题进行编辑
4.  **生成图片**
    - 点击“生成图片”按钮创建角色选择卡
5.  **下载与分享**
    - 下载您的定制卡片并与社区分享！

## 🛠️ 技术栈

- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **库**: html2canvas, QRCode.js
- **部署**: GitHub Pages
- **自动化**: GitHub Actions

## 🔧 安装与设置

1.  **克隆仓库**
    ```bash
    git clone https://github.com/MoonShadow1976/WutheringWaves_Character_Selection.git
    ```
2.  **添加角色图片**
    - 将角色PNG文件放入 `src/role/`目录，命名格式为 `role_pile_{id}.png`
3.  **更新角色数据**
    - 编辑 `id2role.json`与 `role.json`添加多语言角色信息
4.  **部署到GitHub Pages**
    - 推送到主分支并在仓库设置中启用GitHub Pages
5.  **本地运行**
    - 在项目根目录下执行命令，然后在浏览器中访问 `http://localhost:8000`。
    ```bash
    python -m http.server 8000
    ```

## 🌟 贡献

欢迎贡献代码改进这个项目！🙌

1.  Fork 本仓库
2.  创建特性分支
3.  提交更改
4.  推送到分支
5.  打开拉取请求

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

⭐ **如果您觉得这个项目有用，别忘了给它点个星！** ⭐