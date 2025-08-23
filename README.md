# Wuthering Waves Character Selection / 鸣潮角色选择 🎮

![GitHub](https://img.shields.io/github/license/MoonShadow1976/WutheringWaves_Character_Selection?color=blue&style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/MoonShadow1976/WutheringWaves_Character_Selection?style=for-the-badge)
![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-brightgreen?style=for-the-badge)

An interactive web application that allows fans of the popular game "Wuthering Waves" to create and share personalized character selection cards. 🌊✨

一个交互式网络应用程序，允许《鸣潮》的粉丝创建和分享个性化的角色选择卡。🎨📱

## ✨ Features / 主要功能

- 🎯 **Interactive Grid Interface** - A 3×4 grid with 11 customizable categories for character selection

  - **交互式网格界面** - 一个 3×4 的网格，包含 11 个可自定义的角色选择类别
- 🖼️ **Image Generation** - Converts user selections into a shareable image using html2canvas

  - **图像生成** - 使用 html2canvas 技术将用户选择转换为可分享的图像
- 🌐 **Multi-language Support** - Supports both Chinese and English interfaces

  - **多语言支持** - 支持中文和英文界面
- 📱 **Responsive Design** - Works seamlessly on both desktop and mobile devices

  - **响应式设计** - 在桌面和移动设备上均能无缝运行
- 🎨 **Customizable Titles** - Allows users to temporarily edit grid titles for personalized cards

  - **可自定义标题** - 允许用户临时编辑网格标题，创建个性化卡片
- 🔗 **QR Code Integration** - Includes a QR code linking to the GitHub repository

  - **二维码集成** - 包含一个链接到 GitHub 仓库的二维码

## 🚀 Quick Start / 快速开始

1. **Visit the Website** / **访问网站**

   - Go to [GitHub Pages URL](https://moonshadow1976.github.io/WutheringWaves_Character_Selection/) / 访问 [GitHub Pages URL](https://moonshadow1976.github.io/WutheringWaves_Character_Selection/)
2. **Select Characters** / **选择角色**

   - Click on any grid cell (except "Join Us") to choose a character / 点击任意网格单元格（"加入我们"除外）选择角色
3. **Customize Titles (Optional)** / **自定义标题（可选）**

   - Click on any title to edit it / 点击任意标题进行编辑
4. **Generate Image** / **生成图片**

   - Click the "Generate Image" button to create your character selection card / 点击"生成图片"按钮创建角色选择卡
5. **Download & Share** / **下载与分享**

   - Download your customized card and share it with the community! / 下载您的定制卡片并与社区分享！

## 🛠️ Technology Stack / 技术栈

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Libraries**: html2canvas, QRCode.js
- **Deployment**: GitHub Pages
- **Automation**: GitHub Actions

## 📁 Project Structure / 项目结构

```
WutheringWaves_Character_Selection/
├── index.html          # Main application file / 主应用文件
├── role.json           # Character data (auto-generated) / 角色数据（自动生成）
├── id2role.json        # Character ID to name mapping / 角色ID与名称映射
├── role/               # Character images directory / 角色图片目录
│   ├── role_pile_1405.png
│   ├── role_pile_1406.png
│   └── ...
├── .github/
│   └── workflows/
│       └── update-role-json.yml  # GitHub Actions workflow / GitHub Actions工作流
└── README.md           # This file / 本文件
```

## 🔧 Installation & Setup / 安装与设置

1. **Clone the Repository** / **克隆仓库**

   ```bash
   git clone https://github.com/your-username/WutheringWaves_Character_Selection.git
   ```
2. **Add Character Images** / **添加角色图片**

   - Place character PNG files in the `role/` directory with naming convention `role_pile_{id}.png`
   - 将角色PNG文件放入 `role/`目录，命名格式为 `role_pile_{id}.png`
3. **Update Character Data** / **更新角色数据**

   - Edit `id2role.json` to add character information in multiple languages
   - 编辑 `id2role.json`添加多语言角色信息
4. **Deploy to GitHub Pages** / **部署到GitHub Pages**

   - Push to main branch and enable GitHub Pages in repository settings
   - 推送到主分支并在仓库设置中启用GitHub Pages

## 🌟 Contributing / 贡献

We welcome contributions to improve this project! 🤝

欢迎贡献代码改进这个项目！🙌

1. Fork the repository / Fork 本仓库
2. Create a feature branch / 创建特性分支
3. Commit your changes / 提交更改
4. Push to the branch / 推送到分支
5. Open a Pull Request / 打开拉取请求

## 📄 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 Contact / 联系

If you have any questions or suggestions, feel free to open an issue or contact us!

如果您有任何问题或建议，请随时提出问题或联系我们！

---

⭐ **Don't forget to star this repository if you find it useful!** / **如果您觉得这个项目有用，别忘了给它点个星！** ⭐
