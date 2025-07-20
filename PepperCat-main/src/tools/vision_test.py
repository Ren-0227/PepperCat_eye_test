import cv2
import numpy as np
import mediapipe as mp
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from src.openmanus_agent.tool_base import BaseTool
import os
import asyncio

class VisionTestWindow:
    """视力检测窗口"""
    
    def __init__(self):
        self.window = None
        self.cap = None
        self.face_mesh = None
        self.hands = None
        self.testing = False
        self.result = None
        
        # 测试参数
        self.current_size = 0.5
        self.current_direction = 0  # 0:右, 90:下, 180:左, 270:上
        self.correct_count = 0
        self.total_count = 0
        self.distance = 60
        self.test_start_time = None
        
        # 视力标准对照表
        self.VISION_STANDARD = {
            0.1: 4.0, 0.15: 4.2, 0.2: 4.4,
            0.25: 4.6, 0.3: 4.8, 0.4: 5.0,
            0.5: 5.2, 0.6: 5.4, 0.8: 5.6,
            1.0: 5.8
        }
    
    def create_window(self):
        """创建视力检测窗口"""
        self.window = tk.Toplevel()
        self.window.title("视力检测")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        
        # 设置窗口样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 主容器
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="视力检测", font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 说明文字
        instruction_label = ttk.Label(main_frame, 
            text="请保持距离屏幕60厘米，用手势指示E字开口方向\n"
                 "手势说明：\n"
                 "👆 食指向上 = 向上\n"
                 "👇 食指向下 = 向下\n"
                 "👈 食指向左 = 向左\n"
                 "👉 食指向右 = 向右",
            font=('Arial', 12), justify=tk.LEFT)
        instruction_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # 摄像头显示区域
        self.camera_label = ttk.Label(main_frame, text="正在启动摄像头...", 
                                     font=('Arial', 14))
        self.camera_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # 状态信息
        self.status_label = ttk.Label(main_frame, text="准备开始检测", 
                                     font=('Arial', 12))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20))
        
        # 开始按钮
        self.start_btn = ttk.Button(button_frame, text="开始检测", 
                                   command=self.start_test)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_btn = ttk.Button(button_frame, text="停止检测", 
                                  command=self.stop_test, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 关闭按钮
        close_btn = ttk.Button(button_frame, text="关闭", 
                              command=self.close_window)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        self.result_label = ttk.Label(main_frame, text="", 
                                     font=('Arial', 14, 'bold'))
        self.result_label.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # 初始化摄像头
        self.init_camera()
    
    def init_camera(self):
        """初始化摄像头和检测模型"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("无法打开摄像头")
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # 初始化MediaPipe
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1, refine_landmarks=True,
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
            self.hands = mp.solutions.hands.Hands(
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
            
            self.status_label.config(text="摄像头已就绪，点击开始检测")
            
        except Exception as e:
            self.status_label.config(text=f"摄像头初始化失败: {str(e)}")
    
    def start_test(self):
        """开始视力检测"""
        if not self.cap or not self.cap.isOpened():
            messagebox.showerror("错误", "摄像头未就绪")
            return
        
        self.testing = True
        self.test_start_time = time.time()
        self.correct_count = 0
        self.total_count = 0
        self.current_size = 0.5
        
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="检测进行中...")
        
        # 启动检测线程
        self.test_thread = threading.Thread(target=self.run_test_loop, daemon=True)
        self.test_thread.start()
    
    def stop_test(self):
        """停止视力检测"""
        self.testing = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        if self.total_count > 0:
            self.calculate_result()
    
    def run_test_loop(self):
        """运行检测循环"""
        last_change_time = time.time()
        display_duration = 2.0  # E字显示时长
        
        while self.testing and self.total_count < 10:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # 处理帧
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 检测面部距离
            face_results = self.face_mesh.process(rgb_frame)
            if face_results.multi_face_landmarks:
                self.distance = self.calculate_face_distance(
                    face_results.multi_face_landmarks[0]
                )
            
            # 检测手势
            hand_direction = None
            hand_results = self.hands.process(rgb_frame)
            if hand_results.multi_hand_landmarks:
                hand_direction = self.detect_hand_direction(
                    hand_results.multi_hand_landmarks[0]
                )
            
            # 更新显示
            self.update_display(frame)
            
            # 检查是否需要处理手势响应
            if time.time() - last_change_time >= display_duration:
                if hand_direction is not None:
                    self.process_response(hand_direction)
                
                # 更新E字参数
                self.update_e_parameters()
                last_change_time = time.time()
            
            # 检查退出条件
            if self.total_count >= 10 or self.correct_count >= 8:
                break
        
        # 检测结束
        self.window.after(0, self.stop_test)
    
    def calculate_face_distance(self, landmarks):
        """计算面部距离"""
        # 使用面部关键点计算距离
        nose = landmarks.landmark[1]  # 鼻尖
        left_eye = landmarks.landmark[33]  # 左眼
        right_eye = landmarks.landmark[263]  # 右眼
        
        # 计算眼间距
        eye_distance = np.sqrt(
            (left_eye.x - right_eye.x)**2 + 
            (left_eye.y - right_eye.y)**2
        )
        
        # 根据眼间距估算距离（经验公式）
        distance = 60 / eye_distance if eye_distance > 0 else 60
        return max(30, min(100, distance))  # 限制在30-100cm范围内
    
    def detect_hand_direction(self, landmarks):
        """检测手势方向"""
        # 获取食指关键点
        index_tip = landmarks.landmark[8]  # 食指尖
        index_pip = landmarks.landmark[6]  # 食指第二关节
        middle_tip = landmarks.landmark[12]  # 中指尖
        
        # 计算食指方向
        dx = index_tip.x - index_pip.x
        dy = index_tip.y - index_pip.y
        
        # 判断方向
        if abs(dx) > abs(dy):
            if dx > 0:
                return 0  # 右
            else:
                return 180  # 左
        else:
            if dy > 0:
                return 90  # 下
            else:
                return 270  # 上
    
    def process_response(self, detected_direction):
        """处理手势响应"""
        self.total_count += 1
        if detected_direction == self.current_direction:
            self.correct_count += 1
        
        # 更新状态
        accuracy = self.correct_count / self.total_count
        self.window.after(0, lambda: self.status_label.config(
            text=f"准确率: {accuracy:.1%} ({self.correct_count}/{self.total_count})"
        ))
    
    def update_e_parameters(self):
        """更新E字参数"""
        # 根据准确率调整大小
        if self.total_count > 0:
            accuracy = self.correct_count / self.total_count
            if accuracy > 0.8:
                self.current_size = max(0.1, self.current_size * 0.9)
            elif accuracy < 0.6:
                self.current_size = min(1.0, self.current_size * 1.1)
        
        # 随机改变方向
        self.current_direction = (self.current_direction + 90) % 360
    
    def update_display(self, frame):
        """更新显示内容"""
        # 生成E字图像
        e_image = self.create_e_image()
        
        # 调整大小
        height, width = e_image.shape[:2]
        new_width = int(width * self.current_size)
        new_height = int(height * self.current_size)
        resized_e = cv2.resize(e_image, (new_width, new_height))
        
        # 旋转E字
        rotated_e = self.rotate_image(resized_e, self.current_direction)
        
        # 合并到画面中央
        h, w = frame.shape[:2]
        e_h, e_w = rotated_e.shape[:2]
        x_offset = (w - e_w) // 2
        y_offset = (h - e_h) // 2
        
        # 确保不越界
        if x_offset >= 0 and y_offset >= 0:
            for c in range(3):
                frame[y_offset:y_offset+e_h, x_offset:x_offset+e_w, c] = \
                    rotated_e[:, :, c] * (rotated_e[:, :, 3]/255.0) + \
                    frame[y_offset:y_offset+e_h, x_offset:x_offset+e_w, c] * (1.0 - rotated_e[:, :, 3]/255.0)
        
        # 添加信息叠加
        info_lines = [
            f"视力: {self.calculate_vision_level():.1f}",
            f"距离: {self.distance:.0f}cm",
            f"准确率: {self.correct_count}/{self.total_count}",
            f"当前方向: {['右', '下', '左', '上'][self.current_direction // 90]}"
        ]
        
        for i, text in enumerate(info_lines):
            cv2.putText(frame, text, (10, 30 + 30*i),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                       (0, 0, 255) if i == 0 else (255, 255, 255), 2)
        
        # 转换为Tkinter可显示的格式
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        
        # 更新显示
        try:
            from PIL import Image, ImageTk
            pil_image = Image.fromarray(frame_rgb)
            pil_image = pil_image.resize((400, 300), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            self.window.after(0, lambda: self.camera_label.config(image=tk_image))
            self.window.after(0, lambda: setattr(self.camera_label, 'image', tk_image))
        except ImportError:
            # 如果没有PIL，显示文字
            self.window.after(0, lambda: self.camera_label.config(
                text=f"摄像头运行中 - 视力: {self.calculate_vision_level():.1f}"
            ))
    
    def create_e_image(self):
        """创建E字图像"""
        # 创建透明背景
        img = np.zeros((200, 200, 4), dtype=np.uint8)
        img[:, :, 3] = 0  # 透明通道
        
        # 绘制E字
        color = (255, 255, 255, 255)  # 白色
        thickness = 8
        
        # E字的三个横线
        cv2.line(img, (50, 50), (150, 50), color, thickness)   # 上横线
        cv2.line(img, (50, 100), (150, 100), color, thickness) # 中横线
        cv2.line(img, (50, 150), (150, 150), color, thickness) # 下横线
        cv2.line(img, (50, 50), (50, 150), color, thickness)   # 竖线
        
        return img
    
    def rotate_image(self, image, angle):
        """旋转图像"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # 获取旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 执行旋转
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
        return rotated
    
    def calculate_vision_level(self):
        """计算视力水平"""
        if self.total_count == 0:
            return 5.0
        
        accuracy = self.correct_count / self.total_count
        size_ratio = self.current_size
        
        # 根据准确率和大小估算视力
        if accuracy > 0.8:
            if size_ratio < 0.2:
                return 5.8
            elif size_ratio < 0.3:
                return 5.6
            elif size_ratio < 0.4:
                return 5.4
            elif size_ratio < 0.5:
                return 5.2
            else:
                return 5.0
        elif accuracy > 0.6:
            return 4.8
        else:
            return 4.5
    
    def calculate_result(self):
        """计算最终结果"""
        if self.total_count == 0:
            return
        
        accuracy = self.correct_count / self.total_count
        vision_level = self.calculate_vision_level()
        
        # 生成结果文本
        result_text = f"检测完成！\n"
        result_text += f"视力水平: {vision_level:.1f}\n"
        result_text += f"准确率: {accuracy:.1%}\n"
        result_text += f"测试次数: {self.total_count}\n"
        result_text += f"平均距离: {self.distance:.0f}cm"
        
        # 评估视力状况
        if vision_level >= 5.0:
            result_text += "\n\n视力状况: 优秀"
        elif vision_level >= 4.5:
            result_text += "\n\n视力状况: 良好"
        elif vision_level >= 4.0:
            result_text += "\n\n视力状况: 一般"
        else:
            result_text += "\n\n视力状况: 需要关注"
        
        self.result_label.config(text=result_text)
        self.result = {
            'vision_level': vision_level,
            'accuracy': accuracy,
            'total_count': self.total_count,
            'distance': self.distance,
            'timestamp': time.time()
        }
    
    def close_window(self):
        """关闭窗口"""
        self.testing = False
        if self.cap:
            self.cap.release()
        if self.face_mesh:
            self.face_mesh.close()
        if self.hands:
            self.hands.close()
        if self.window:
            self.window.destroy()


class VisionTestTool(BaseTool):
    """视力检测工具"""
    
    name: str = "vision_test"
    description: str = "进行基础视力检测，使用E字表测试视力水平"
    test_window: Optional[VisionTestWindow] = None
    
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    def __init__(self):
        super().__init__()
        self.tkinter_thread = None
        self.root = None
        # 延迟启动tkinter主循环线程
        self._start_tkinter_thread()
    
    def _start_tkinter_thread(self):
        """在后台线程中启动tkinter主循环"""
        import threading
        
        def tkinter_mainloop():
            try:
                # 创建隐藏的根窗口
                self.root = tk.Tk()
                self.root.withdraw()  # 隐藏根窗口
                self.root.mainloop()
            except Exception as e:
                print(f"Tkinter主循环启动失败: {e}")
        
        # 启动tkinter线程
        self.tkinter_thread = threading.Thread(target=tkinter_mainloop, daemon=True)
        self.tkinter_thread.start()
    
    async def execute(self, **kwargs) -> str:
        """执行视力检测"""
        try:
            # 确保tkinter线程已启动
            if self.tkinter_thread and not self.tkinter_thread.is_alive():
                self._start_tkinter_thread()
                await asyncio.sleep(0.5)  # 等待线程启动
            
            # 创建检测窗口
            self.test_window = VisionTestWindow()
            self.test_window.create_window()
            
            # 等待检测完成
            while self.test_window.window and self.test_window.window.winfo_exists():
                await asyncio.sleep(0.1)
            
            # 返回结果
            if self.test_window.result:
                result = self.test_window.result
                return f"视力检测完成！\n视力水平: {result['vision_level']:.1f}\n准确率: {result['accuracy']:.1%}\n测试次数: {result['total_count']}"
            else:
                return "视力检测未完成"
                
        except Exception as e:
            return f"视力检测出错: {str(e)}"
        finally:
            if self.test_window:
                self.test_window = None
    
    def cleanup(self):
        """清理资源"""
        try:
            # 关闭检测窗口
            if self.test_window:
                self.test_window.close_window()
                self.test_window = None
            
            # 关闭tkinter主循环
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"清理视力检测资源失败：{e}") 