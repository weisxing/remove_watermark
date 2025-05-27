import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

class WatermarkRemover:
    def __init__(self, root):
        self.root = root
        self.root.title('图片去水印工具')

        # 初始化变量
        self.img = None
        self.original_img = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.mask_area = None

        # 创建GUI组件
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(pady=10)

        # 使用grid布局优化按钮排列
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=5)

        self.btn_open = tk.Button(self.btn_frame, text='打开图片', command=self.open_image, width=10)
        self.btn_open.grid(row=0, column=0, padx=10)

        self.btn_remove = tk.Button(self.btn_frame, text='去除水印', command=self.remove_watermark, width=10)
        self.btn_remove.grid(row=0, column=1, padx=10)

        self.btn_save = tk.Button(self.btn_frame, text='保存结果', command=self.save_image, width=10)
        self.btn_save.grid(row=0, column=2, padx=10)

        # 绑定鼠标事件
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

    def open_image(self):
        # 选择图片文件（支持中文路径）
        file_path = filedialog.askopenfilename(filetypes=[('图片文件', '*.jpg;*.jpeg;*.png;*.webp'), ('JPG图片', '*.jpg;*.jpeg'), ('PNG图片', '*.png'), ('WEBP图片', '*.webp')])
        if not file_path:
            return

        # 使用PIL读取解决中文路径问题
        try:
            pil_img = Image.open(file_path)
            self.original_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            messagebox.showerror('错误', f'无法读取图片：{str(e)}')
            return

        # 读取成功后初始化变量
        self.img = self.original_img.copy()
        self.show_image()

    def show_image(self):
        # 计算缩放比例（保持宽高比，最大800x600）
        img_rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        original_width, original_height = pil_img.size

        # 计算缩放因子
        max_width = 800
        max_height = 600
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        scale_factor = min(width_ratio, height_ratio)

        # 缩放图片
        scaled_width = int(original_width * scale_factor)
        scaled_height = int(original_height * scale_factor)
        scaled_img = pil_img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

        # 保存缩放信息（用于坐标转换）
        self.scale_factor = scale_factor
        self.scaled_width = scaled_width
        self.scaled_height = scaled_height

        # 显示缩放后的图片
        self.tk_img = ImageTk.PhotoImage(scaled_img)
        self.canvas.config(width=scaled_width, height=scaled_height)
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_img)

    def on_press(self, event):
        # 记录鼠标按下位置
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_drag(self, event):
        # 更新矩形框位置
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        # 记录缩放后的选择区域，并转换为原图坐标
        x1_scaled = min(self.start_x, event.x)
        y1_scaled = min(self.start_y, event.y)
        x2_scaled = max(self.start_x, event.x)
        y2_scaled = max(self.start_y, event.y)

        # 转换为原图实际坐标（除以缩放因子）
        if hasattr(self, 'scale_factor') and self.scale_factor != 0:
            x1 = int(x1_scaled / self.scale_factor)
            y1 = int(y1_scaled / self.scale_factor)
            x2 = int(x2_scaled / self.scale_factor)
            y2 = int(y2_scaled / self.scale_factor)
            self.mask_area = (x1, y1, x2, y2)
        else:
            messagebox.showwarning('提示', '图片未正确加载，无法选择区域')
            self.mask_area = None

    def remove_watermark(self):
        if self.mask_area is None or self.original_img is None:
            messagebox.showwarning('提示', '请先选择水印区域并打开图片')
            return

        # 创建掩膜
        h, w = self.original_img.shape[:2]
        mask = np.zeros((h, w), np.uint8)
        x1, y1, x2, y2 = self.mask_area
        mask[y1:y2, x1:x2] = 255

        # 去水印处理
        self.img = cv2.inpaint(self.original_img, mask, 3, cv2.INPAINT_TELEA)
        self.show_image()  # 实时预览
        messagebox.showinfo('提示', '水印去除完成！')

    def save_image(self):
        if self.img is None:
            messagebox.showwarning('提示', '没有可保存的图片')
            return

        # 支持更多图片格式并获取保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension='.webp',
            filetypes=[('WEBP图片', '*.webp'), ('JPG图片', '*.jpg'), ('PNG图片', '*.png'), ('BMP图片', '*.bmp')]
        )
        if not file_path:
            return

        # 使用PIL保存支持中文路径并添加错误处理
        try:
            # 转换OpenCV的BGR格式为PIL的RGB格式
            pil_img = Image.fromarray(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
            pil_img.save(file_path)
            messagebox.showinfo('提示', f'图片已成功保存至：{file_path}')
        except Exception as e:
            messagebox.showerror('保存失败', f'保存图片时发生错误：{str(e)}')

if __name__ == '__main__':
    root = tk.Tk()
    app = WatermarkRemover(root)
    root.mainloop()