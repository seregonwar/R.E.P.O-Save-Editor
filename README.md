# <img src="https://github.com/seregonwar/R.E.P.O-Save-Editor/blob/main/src/assets/icons/reposaveeditor.png" alt="Icon" width="40" style="vertical-align: middle;"> R.E.P.O Save Editor

<div align="center">

![GitHub release](https://img.shields.io/badge/version-3.0.0-E69F00.svg?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Windows_|_Linux_|_macOS-232323.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-E69F00.svg?style=for-the-badge&logo=python&logoColor=white)
![Github All Releases](https://img.shields.io/github/downloads/seregonwar/R.E.P.O-Save-Editor/total+-E69F00.svg?style=for-the-badge&logoColor=white)

**A powerful editor for R.E.P.O save files**

<img src="https://github.com/seregonwar/R.E.P.O-Save-Editor/blob/main/src/assets/icons/reposaveeditor.png" alt="R.E.P.O Save Editor logo" width="512">

</div>

---
> ⚠️ **Warning**  
> Versions **1.0.0** and **2.0.0** have a critical issue when saving files.  
> Please use **only the latest available version** to avoid problems!

## 🚀 Overview

**R.E.P.O Save Editor** is an advanced graphical interface tool designed to modify save files for the **R.E.P.O** game. With this application you can:

- Decrypt and modify `.es3` files
- Customize player statistics and inventory
- Complete quests and upgrade skills
- Save your changes while maintaining game compatibility

The application has been designed with a modern, intuitive, and elegant interface that allows you to focus on modifications without complications.

## ✨ Key Features

<table>
  <tr>
    <td>
      <h3>🔐 Advanced Save Management</h3>
      <ul>
        <li>Open and decode <code>.es3</code> files</li>
        <li>Encrypt and save files in the original format</li>
        <li>Export/import in JSON format for advanced editing</li>
      </ul>
    </td>
    <td>
      <h3>👤 Character Editing</h3>
      <ul>
        <li>Player statistics</li>
        <li>Inventory and items</li>
        <li>Money and resources</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>

</table>

## 🖥️ Screenshot

<img src="https://github.com/user-attachments/assets/ee44a600-bc5c-46fa-a5ad-3b829ba3e3ef">


## 🔧 Installation

### Direct Download

1. Download the latest version from the [Releases page](https://github.com/seregonwar/R.E.P.O-Save-Editor/releases)
2. Extract the ZIP file to a folder of your choice
3. Run the `REPO Save Editor.exe` file

### Installation from Source

```bash
# Clone the repository
git clone https://github.com/user/R.E.P.O-Save-Editor.git
cd R.E.P.O-Save-Editor

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the application
python src/main.py
```

## 📖 User Guide

1. **Open a save file**
   - Click on `File > Open Save`
   - Select the `.es3` file to edit

2. **Edit the data**
   - Use the different tabs to modify player, inventory, quests, and skills
   - All editable fields are highlighted

3. **Save your changes**
   - Click on `File > Save` to overwrite the original file
   - Or use `File > Save As` to create a new file

4. **Advanced features**
   - Export to JSON: `File > Export > Export to JSON` 
   - Import from JSON: `File > Import > Import from JSON`
   - Steam profile integration: The app can retrieve your Steam profile picture and display it next to your character name. If no Steam profile is found, the app icon will be used as default.

## 🛠️ For Developers

The application is written in Python using PyQt6. The project structure is:

```
R.E.P.O-Save-Editor/
├── assets/               # Graphic resources
├── src/                  # Source code
│   ├── core/             # Core logic
│   ├── ui/               # User interface
│   └── main.py           # Entry point
├── build_app.py          # Script for creating the executable
└── requirements.txt      # Dependencies
```

### Building from Source

To create a standalone executable:

```bash
python build_app.py
```

## ❤️ Support the Developer

If you find this tool useful, please consider supporting the developer:

<div align="center">
  <a href="https://ko-fi.com/seregon" target="_blank"><img src="https://img.shields.io/badge/Ko--fi-Support%20Me-E69F00?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi"></a>
  <a href="https://paypal.me/seregonwar" target="_blank"><img src="https://img.shields.io/badge/PayPal-Donate-232323?style=for-the-badge&logo=paypal&logoColor=white" alt="PayPal"></a>
  <a href="https://x.com/SeregonWar" target="_blank"><img src="https://img.shields.io/badge/Twitter-Follow-E69F00?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter"></a>
</div>

## 📄 License

This project is released under the MIT License. See the `LICENSE` file for details.

---

<div align="center">
  <p>Created with ❤️ by SeregonWar</p>
</div>
