# 图片去水印工具

## 功能说明

支持 JPG/PNG/BMP/WEBP 格式图片的水印区域选择与去除，提供可视化操作界面。

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行工具

```bash
python remove_watermark.py
```

## 打包成 EXE（Windows）

### 1. 安装打包工具

```bash
pip install pyinstaller
```

### 2. 执行打包命令（推荐使用脚本）

你可以直接运行打包脚本 `build_exe.bat` 来简化操作：

1. 双击 `build_exe.bat` 文件；
2. 等待命令窗口完成执行；
3. 脚本会自动完成打包并提示完成。

若需手动执行，命令如下（已包含隐藏控制台参数）：

```bash
pyinstaller --noconsole --onefile -n "图片去水印工具" remove_watermark.py
```

### 3. 找到生成的 EXE 文件

打包完成后，可执行文件位于`dist/图片去水印工具.exe`目录下。
