[English](README.md) | [中文](README_zh.md)

# Wuthering Waves Red-Black List 🎮

![GitHub](https://img.shields.io/github/license/MoonShadow1976/WutheringWaves_Character_Selection?color=blue&style=for-the-badge)  ![GitHub last commit](https://img.shields.io/github/last-commit/MoonShadow1976/WutheringWaves_Character_Selection?style=for-the-badge)  ![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-brightgreen?style=for-the-badge)

An interactive web application that allows fans of the popular game “Wuthering Waves” to create and share personalized character selection cards. 🌊✨

## ✨ Features

- **Interactive Grid Interface** – A 3×4 grid with customizable Wuthering Waves character preferences
- **Image Generation** – Converts user selections into a shareable image using html2canvas
- **Multi-language Support** – Supports both Chinese and English interfaces
- **Responsive Design** – Works seamlessly on both desktop and mobile devices
- **Customizable Titles** – Allows users to temporarily edit grid titles for personalized cards
- **QR Code Integration** – Includes a QR code linking to the GitHub repository

## 🚀 Quick Start

1.  **Visit the Website**
    - Go to [GitHub Pages URL](https://moonshadow1976.github.io/WutheringWaves_Character_Selection/)
2.  **Select Characters**
    - Click on any grid cell to choose a character
3.  **Customize Titles (Optional)**
    - Click on any title to edit it
4.  **Generate Image**
    - Click the “Generate Image” button to create your character selection card
5.  **Download & Share**
    - Download your customized card and share it with the community!

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Libraries**: html2canvas, QRCode.js
- **Deployment**: GitHub Pages
- **Automation**: GitHub Actions

## 🔧 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/MoonShadow1976/WutheringWaves_Character_Selection.git
    ```
2.  **Add Character Images**
    - Place character PNG files in the `src/role/` directory with naming convention `role_pile_{id}.png`
3.  **Update Character Data**
    - Edit `id2role.json` and `role.json` to add character information in multiple languages
4.  **Deploy to GitHub Pages**
    - Push to main branch and enable GitHub Pages in repository settings
5.  **Run Locally**
    - Execute the following command in the project root directory, then visit `http://localhost:8000` in your browser.
    ```bash
    python -m http.server 8000
    ```

## 🌟 Contributing

We welcome contributions to improve this project! 🤝

1.  Fork the repository
2.  Create a feature branch
3.  Commit your changes
4.  Push to the branch
5.  Open a Pull Request

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

⭐ **Don’t forget to star this repository if you find it useful!** ⭐