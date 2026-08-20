<div align="center">
	<img src="assets/icon.ico" width="190">
	<h1>Win Virtual Desktops Tools</h1>
	<p>Improves your experience with Windows virtual desktops</p>
</div>

<div align="center">

[![GitHub All Releases](https://img.shields.io/github/downloads/henriqueclaranhan/win-virtual-desktops-tools/total?style=for-the-badge)](https://github.com/henriqueclaranhan/win-virtual-desktops-tools/releases)
[![License](https://img.shields.io/github/license/henriqueclaranhan/win-virtual-desktops-tools?style=for-the-badge)](https://github.com/henriqueclaranhan/win-virtual-desktops-tools/blob/main/LICENSE)

</div>

## ⭐ Features

-   Switch between desktops when scrolling in the taskbar
-   Switch between desktops when scrolling in the Task View
-   Hot corner in the top left corner (or customized per-monitor) to open Task View
-   Keep secondary monitor windows pinned across virtual desktop switches

![WVDT](https://user-images.githubusercontent.com/58452863/236719035-1e797fe2-ebf0-415d-968f-f73c737f196f.gif)

## 🪟 Supported Systems

| Windows 10 | Windows 11 |
| :--------: | :--------: |
|     ✅     |     ✅     |

## 🛠️ Building from Source

### Prerequisites

- Python 3.10+
- Windows OS (x64)

### 1. Install Dependencies

```bash
pip install -r requirements/common.txt
pip install -r requirements/build.txt
```

### 2. Build with PyInstaller

Use the included `main.spec` configuration to generate an optimized, standalone executable:

```bash
pyinstaller main.spec
```

The resulting executable will be created in the `dist/` directory (e.g., `dist/win-virtual-desktops-tools-standalone-v1-5-0.exe`).

## 🧪 Running Tests

To run the automated unit test suite:

```bash
python -m unittest discover -s tests
```

## 🙏 Acknowledgments & Credits

- Windows Virtual Desktop DLL: Special thanks to [Ciantic](https://github.com/Ciantic) for the [VirtualDesktopAccessor](https://github.com/Ciantic/VirtualDesktopAccessor) library (`VirtualDesktopAccessor.dll`), which provides the underlying Windows Virtual Desktop API wrapper.

## 📝 License

Licensed under the <a href="https://github.com/henriqueclaranhan/win-virtual-desktops-tools/blob/main/LICENSE">MIT License</a>.
