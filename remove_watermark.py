import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class WatermarkRemover:    
    def __init__(self, root):
        self.root = root
        self.root.title('图片去水印工具')
        self.root.geometry('900x700')  # 设置初始窗口大小
        self.root.resizable(True, True)  # 允许窗口调整大小

        # 设置中文字体
        self.default_font = ('Microsoft YaHei UI', 10)
        self.title_font = ('Microsoft YaHei UI', 12, 'bold')

        # 初始化变量
        self.img = None
        self.original_img = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.mask_area = None

        # 创建主框架
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建标题标签
        self.title_label = tk.Label(
            self.main_frame, 
            text='图片去水印工具', 
            font=self.title_font, 
            fg='#2c3e50'
        )
        self.title_label.pack(pady=(0, 10))

        # 创建使用说明标签
        self.instruction_label = tk.Label(
            self.main_frame, 
            text='使用步骤: 1.打开图片  2.框选水印区域  3.去除水印  4.保存结果', 
            font=self.default_font, 
            fg='#555555'
        )
        self.instruction_label.pack(pady=(0, 10))

        # 创建画布框架（带滚动条）
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        self.scroll_x = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建画布
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            width=800, 
            height=500, 
            bg='#f0f0f0',
            xscrollcommand=self.scroll_x.set, 
            yscrollcommand=self.scroll_y.set,
            highlightthickness=1, 
            highlightbackground='#cccccc'
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 配置滚动条
        self.scroll_x.config(command=self.canvas.xview)
        self.scroll_y.config(command=self.canvas.yview)

        # 创建按钮框架
        self.btn_frame = tk.Frame(self.main_frame)
        self.btn_frame.pack(pady=15)

        # 创建按钮样式
        self.style = ttk.Style()
        self.style.configure('TButton', font=self.default_font, padding=8)

        # 创建按钮
        self.btn_open = ttk.Button(
            self.btn_frame, 
            text='打开图片', 
            command=self.open_image, 
            width=12
        )
        self.btn_open.grid(row=0, column=0, padx=15)

        self.btn_remove = ttk.Button(
            self.btn_frame, 
            text='去除水印', 
            command=self.remove_watermark, 
            width=12
        )
        self.btn_remove.grid(row=0, column=1, padx=15)

        self.btn_save = ttk.Button(
            self.btn_frame, 
            text='保存结果', 
            command=self.save_image, 
            width=12
        )
        self.btn_save.grid(row=0, column=2, padx=15)

        # 创建状态栏（增加高度）
        self.status_var = tk.StringVar()
        self.status_var.set('就绪: 请打开一张图片开始操作')
        self.status_bar = tk.Label(
            root, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W, 
            font=self.default_font,
            height=2  # 增加状态栏高度
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定鼠标事件
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

    def show_message(self, title, message, msg_type='info'):
        """自定义消息框，使其在主窗口居中显示"""
        # 创建顶层窗口
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry('300x150')
        top.resizable(False, False)
        top.transient(self.root)  # 设置为临时窗口
        top.grab_set()  # 模态窗口

        # 添加消息标签
        label = tk.Label(top, text=message, font=self.default_font, wraplength=280, justify='center')
        label.pack(pady=20)

        # 添加确定按钮
        btn_ok = ttk.Button(top, text='确定', command=top.destroy)
        btn_ok.pack(pady=10)

        # 计算居中位置
        x = self.root.winfo_x() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - top.winfo_height()) // 2
        top.geometry(f'+{x}+{y}')

        # 根据消息类型设置图标
        if msg_type == 'error':
            icon = 'error'
        elif msg_type == 'warning':
            icon = 'warning'
        else:
            icon = 'info'


        # 设置图标
        # 尝试设置图标，兼容不同系统
        try:
            if icon in tk.image_types():
                top.iconbitmap(default=tk.image_types()[icon])
        except:
            # 忽略图标设置失败的情况
            pass

        # 等待窗口关闭
        self.root.wait_window(top)

    def open_image(self):
        self.status_var.set('正在打开图片...')
        self.root.update_idletasks()

        # 选择图片文件（支持中文路径）
        file_path = filedialog.askopenfilename(filetypes=[('图片文件', ('*.jpg', '*.jpeg', '*.png', '*.webp')), ('JPG图片', ('*.jpg', '*.jpeg')), ('PNG图片', '*.png'), ('WEBP图片', '*.webp')])
        if not file_path:
            self.status_var.set('就绪: 请打开一张图片开始操作')
            return

        # 使用PIL读取解决中文路径问题
        try:
            pil_img = Image.open(file_path)
            self.original_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            self.status_var.set(f'已加载图片: {file_path.split("/")[-1]}')
        except Exception as e:
            self.show_message('错误', f'无法读取图片：{str(e)}', 'error')
            self.status_var.set('就绪: 请打开一张有效的图片')
            return

        # 读取成功后初始化变量
        self.img = self.original_img.copy()
        self.show_image()

    def show_image(self):
        # 计算缩放比例（保持宽高比）
        img_rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        original_width, original_height = pil_img.size

        # 获取画布可用空间
        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 800
        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 500

        # 计算缩放因子
        width_ratio = canvas_width / original_width
        height_ratio = canvas_height / original_height
        scale_factor = min(width_ratio, height_ratio, 1.0)  # 不放大图片

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
        self.canvas.delete('all')  # 清除画布
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_img)
        # 设置滚动区域
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_press(self, event):
        # 记录鼠标按下位置
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#e74c3c', width=2, dash=(4, 2)
        )
        self.status_var.set('正在选择水印区域...')

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
            self.status_var.set(f'已选择水印区域: 位置({x1}, {y1}) 大小({x2-x1}x{y2-y1})')
        else:
            self.show_message('提示', '图片未正确加载，无法选择区域', 'warning')
            self.mask_area = None
            self.status_var.set('就绪: 请先打开图片')

    def remove_watermark(self):
        if self.mask_area is None or self.original_img is None:
            self.show_message('提示', '请先选择水印区域并打开图片', 'warning')
            return

        self.status_var.set('正在去除水印...')
        self.root.update_idletasks()

        # 创建掩膜
        h, w = self.original_img.shape[:2]
        mask = np.zeros((h, w), np.uint8)
        x1, y1, x2, y2 = self.mask_area
        mask[y1:y2, x1:x2] = 255

        # 去水印处理
        self.img = cv2.inpaint(self.original_img, mask, 3, cv2.INPAINT_TELEA)
        self.show_image()  # 实时预览
        self.status_var.set('水印去除完成！请保存结果')
        self.show_message('提示', '水印去除完成！')

    def save_image(self):
        if self.img is None:
            self.show_message('提示', '没有可保存的图片', 'warning')
            return

        self.status_var.set('正在保存图片...')
        self.root.update_idletasks()

        # 支持更多图片格式并获取保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension='.webp',
            filetypes=[('WEBP图片', '*.webp'), ('JPG图片', '*.jpg'), ('PNG图片', '*.png'), ('BMP图片', '*.bmp')]
        )
        if not file_path:
            self.status_var.set('保存已取消')
            return

        # 使用PIL保存支持中文路径并添加错误处理
        try:
            # 转换OpenCV的BGR格式为PIL的RGB格式
            pil_img = Image.fromarray(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
            pil_img.save(file_path)
            self.status_var.set(f'图片已保存至: {file_path}')
            self.show_message('提示', f'图片已成功保存至：{file_path}')
        except Exception as e:
            self.show_message('保存失败', f'保存图片时发生错误：{str(e)}', 'error')
            self.status_var.set('保存失败，请重试')

if __name__ == '__main__':
    root = tk.Tk()
    app = WatermarkRemover(root)
    root.mainloop()