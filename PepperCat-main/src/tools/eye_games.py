import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from typing import Optional, Dict, Any
from src.openmanus_agent.tool_base import BaseTool

class EyeGameWindow:
    """眼部游戏窗口基类"""
    
    def __init__(self, title: str, game_type: str):
        self.title = title
        self.game_type = game_type
        self.window = None
        self.score = 0
        self.running = False
        
    def create_window(self):
        """创建游戏窗口"""
        self.window = tk.Toplevel()
        self.window.title(f"眼部健康 - {self.title}")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # 设置窗口样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 主容器
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text=self.title, font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 信息标签
        self.info_label = ttk.Label(main_frame, text="点击开始游戏按钮开始训练", font=('Arial', 10))
        self.info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # 游戏画布
        self.canvas = tk.Canvas(main_frame, width=300, height=300, bg='#f0f0f0', relief='raised', bd=2)
        self.canvas.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # 开始按钮
        self.start_btn = ttk.Button(button_frame, text="开始游戏", command=self.start_game)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 重新开始按钮
        self.restart_btn = ttk.Button(button_frame, text="再来一次", command=self.start_game, state='disabled')
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        
        # 关闭按钮
        close_btn = ttk.Button(button_frame, text="关闭", command=self.close_window)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        self.result_label = ttk.Label(main_frame, text="", font=('Arial', 12))
        self.result_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # 初始化游戏
        self.init_game()
        
        # 非阻塞方式启动窗口（关键修复）
        self.window.update()
        self.window.deiconify()  # 确保窗口可见
        
    def init_game(self):
        """初始化游戏 - 子类重写"""
        pass
        
    def start_game(self):
        """开始游戏 - 子类重写"""
        pass
        
    def close_window(self):
        """关闭窗口"""
        self.running = False
        if self.window:
            self.window.destroy()
            self.window = None


class MemoryGame(EyeGameWindow):
    """记忆训练游戏"""
    
    def __init__(self):
        super().__init__("记忆训练游戏", "memory")
        self.sequence = []
        self.user_input = []
        self.round_num = 0
        self.max_rounds = 8
        self.colors = ['#ff0000', '#00cc00', '#0099ff', '#ffff00']
        self.showing = False
        
    def init_game(self):
        """初始化游戏"""
        self.draw_colors()
        
    def draw_colors(self, highlight_idx=-1):
        """绘制颜色圆圈"""
        self.canvas.delete("all")
        self.color_positions = []
        
        for i in range(4):
            x = 40 + i * 55
            y = 120
            color = self.colors[i]
            
            # 绘制圆圈
            if i == highlight_idx:
                # 高亮显示
                self.canvas.create_oval(x, y, x+50, y+50, fill='white', outline=color, width=3)
            else:
                self.canvas.create_oval(x, y, x+50, y+50, fill=color, outline='#999999', width=2)
            
            self.color_positions.append((x, y, color))
            
    def start_game(self):
        """开始游戏"""
        self.running = True
        self.round_num = 0
        self.sequence = []
        self.user_input = []
        self.score = 0
        self.result_label.config(text="")
        self.start_btn.config(state='disabled')
        self.restart_btn.config(state='disabled')
        self.next_round()
        
    def next_round(self):
        """下一轮"""
        if self.round_num >= self.max_rounds:
            self.end_game()
            return
            
        self.round_num += 1
        self.user_input = []
        self.sequence.append(random.randint(0, 3))
        self.info_label.config(text=f"记住颜色顺序（第{self.round_num}轮）...")
        
        # 显示序列
        self.show_sequence()
        
    def show_sequence(self):
        """显示颜色序列"""
        self.showing = True
        self.show_sequence_step(0)
        
    def show_sequence_step(self, step):
        """显示序列的每一步"""
        if step >= len(self.sequence) or not self.running:
            self.showing = False
            self.info_label.config(text=f"请按顺序点击颜色球（第{self.round_num}轮）")
            return
            
        # 高亮当前颜色
        self.draw_colors(self.sequence[step])
        
        # 600ms后恢复
        self.window.after(600, lambda: self.show_sequence_step_clear(step))
        
    def show_sequence_step_clear(self, step):
        """清除高亮"""
        if not self.running:
            return
        self.draw_colors()
        
        # 200ms后显示下一步
        self.window.after(200, lambda: self.show_sequence_step(step + 1))
        
    def check_input(self):
        """检查用户输入"""
        for i in range(len(self.sequence)):
            if self.user_input[i] != self.sequence[i]:
                self.end_game()
                return
                
        self.score += 1
        self.window.after(500, self.next_round)
        
    def on_canvas_click(self, event):
        """画布点击事件"""
        if not self.running or self.showing:
            return
            
        x, y = event.x, event.y
        
        # 检查点击了哪个颜色
        for i, (cx, cy, color) in enumerate(self.color_positions):
            center_x = cx + 25
            center_y = cy + 25
            if ((x - center_x) ** 2 + (y - center_y) ** 2) <= 625:  # 25^2
                self.user_input.append(i)
                self.draw_colors(i)
                
                # 200ms后恢复
                self.window.after(200, self.draw_colors)
                
                if len(self.user_input) == len(self.sequence):
                    self.check_input()
                break
                
    def end_game(self):
        """结束游戏"""
        self.running = False
        self.info_label.config(text="游戏结束！")
        self.result_label.config(text=f"成绩：成功记忆{self.score}轮")
        self.start_btn.config(state='normal')
        self.restart_btn.config(state='normal')
        
    def create_window(self):
        """创建窗口并绑定事件"""
        super().create_window()
        self.canvas.bind("<Button-1>", self.on_canvas_click)


class FocusGame(EyeGameWindow):
    """专注力训练游戏"""
    
    def __init__(self):
        super().__init__("专注力训练游戏", "focus")
        self.numbers = []
        self.target = 1
        self.grid_size = 3
        self.cell_size = 100
        self.hits = 0
        self.misses = 0
        self.round_num = 0
        self.max_rounds = 10
        self.start_time = 0
        self.total_time = 0
        
    def init_game(self):
        """初始化游戏"""
        self.draw_grid()
        
    def draw_grid(self):
        """绘制网格"""
        self.canvas.delete("all")
        
        # 绘制网格线
        for i in range(1, self.grid_size):
            # 垂直线
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, 300, fill='#999999')
            # 水平线
            self.canvas.create_line(0, i * self.cell_size, 300, i * self.cell_size, fill='#999999')
            
        # 绘制数字
        for i, num in enumerate(self.numbers):
            row = i // self.grid_size
            col = i % self.grid_size
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            
            color = '#667eea' if num == self.target else '#333333'
            self.canvas.create_text(x, y, text=str(num), font=('Arial', 32), fill=color)
            
    def shuffle_numbers(self):
        """打乱数字"""
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        return numbers
        
    def next_round(self):
        """下一轮"""
        if self.round_num >= self.max_rounds:
            self.end_game()
            return
            
        self.round_num += 1
        self.numbers = self.shuffle_numbers()
        
        # 选择目标数字（不是1的数字）
        possible_targets = [n for n in self.numbers if n != self.target]
        self.target = random.choice(possible_targets)
        
        self.info_label.config(text=f"第{self.round_num}轮：请点击数字 {self.target}")
        self.draw_grid()
        
    def get_cell_from_xy(self, x, y):
        """从坐标获取单元格索引"""
        col = x // self.cell_size
        row = y // self.cell_size
        return row * self.grid_size + col
        
    def on_canvas_click(self, event):
        """画布点击事件"""
        if not self.running:
            return
            
        x, y = event.x, event.y
        idx = self.get_cell_from_xy(x, y)
        
        if idx < len(self.numbers) and self.numbers[idx] == self.target:
            self.hits += 1
            self.next_round()
        else:
            self.misses += 1
            self.info_label.config(text=f"点错了！请点击数字 {self.target}")
            
    def start_game(self):
        """开始游戏"""
        self.running = True
        self.hits = 0
        self.misses = 0
        self.round_num = 0
        self.total_time = 0
        self.result_label.config(text="")
        self.start_btn.config(state='disabled')
        self.restart_btn.config(state='disabled')
        self.start_time = time.time()
        self.next_round()
        
    def end_game(self):
        """结束游戏"""
        self.running = False
        self.total_time = round(time.time() - self.start_time)
        self.info_label.config(text="游戏结束！")
        self.result_label.config(text=f"成绩：正确{self.hits}次，失误{self.misses}次，总用时{self.total_time}秒")
        self.start_btn.config(state='normal')
        self.restart_btn.config(state='normal')
        
    def create_window(self):
        """创建窗口并绑定事件"""
        super().create_window()
        self.canvas.bind("<Button-1>", self.on_canvas_click)


class ReactionGame(EyeGameWindow):
    """反应速度训练游戏"""
    
    def __init__(self):
        super().__init__("反应速度训练游戏", "reaction")
        self.box = {'x': 0, 'y': 0, 'size': 60, 'color': '#ff0000'}
        self.colors = ['#ff0000', '#00cc00', '#0099ff', '#ffff00', '#ff00ff', '#00ffff', '#ffaa00', '#00aaff']
        self.round_num = 0
        self.max_rounds = 15
        self.start_time = 0
        self.total_time = 0
        
    def init_game(self):
        """初始化游戏"""
        self.draw_box()
        
    def draw_box(self):
        """绘制方块"""
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            self.box['x'], self.box['y'],
            self.box['x'] + self.box['size'], self.box['y'] + self.box['size'],
            fill=self.box['color'], outline='#333333', width=2
        )
        
    def random_box(self):
        """随机生成方块位置和颜色"""
        self.box['size'] = 60
        self.box['x'] = random.randint(0, 300 - self.box['size'])
        self.box['y'] = random.randint(0, 300 - self.box['size'])
        self.box['color'] = random.choice(self.colors)
        
    def on_canvas_click(self, event):
        """画布点击事件"""
        if not self.running:
            return
            
        x, y = event.x, event.y
        
        if (x >= self.box['x'] and x <= self.box['x'] + self.box['size'] and
            y >= self.box['y'] and y <= self.box['y'] + self.box['size']):
            self.score += 1
            self.next_round()
            
    def next_round(self):
        """下一轮"""
        if self.round_num >= self.max_rounds:
            self.end_game()
            return
            
        self.round_num += 1
        self.info_label.config(text=f"第{self.round_num}轮：请点击彩色方块")
        self.random_box()
        self.draw_box()
        
    def start_game(self):
        """开始游戏"""
        self.running = True
        self.score = 0
        self.round_num = 0
        self.total_time = 0
        self.result_label.config(text="")
        self.start_btn.config(state='disabled')
        self.restart_btn.config(state='disabled')
        self.start_time = time.time()
        self.next_round()
        
    def end_game(self):
        """结束游戏"""
        self.running = False
        self.total_time = round(time.time() - self.start_time)
        self.info_label.config(text="游戏结束！")
        self.result_label.config(text=f"成绩：正确{self.score}次，总用时{self.total_time}秒")
        self.start_btn.config(state='normal')
        self.restart_btn.config(state='normal')
        
    def create_window(self):
        """创建窗口并绑定事件"""
        super().create_window()
        self.canvas.bind("<Button-1>", self.on_canvas_click)


class EyeGamesTool(BaseTool):
    """眼部健康游戏工具"""
    
    name: str = "eye_games"
    description: str = "启动眼部健康训练游戏，包括记忆训练、专注力训练和反应速度训练"
    game_windows: Dict[str, Any] = {}
    
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "game_type": {
                "type": "string",
                "enum": ["memory", "focus", "reaction", "all"],
                "description": "游戏类型：memory(记忆训练)、focus(专注力训练)、reaction(反应速度训练)、all(所有游戏)"
            }
        },
        "required": ["game_type"]
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
        
    async def execute(self, game_type: str = "all", **kwargs) -> str:
        """执行游戏"""
        try:
            # 确保tkinter线程已启动
            if self.tkinter_thread and not self.tkinter_thread.is_alive():
                self._start_tkinter_thread()
                await asyncio.sleep(0.5)  # 等待线程启动
            
            if game_type == "memory":
                return await self._start_memory_game()
            elif game_type == "focus":
                return await self._start_focus_game()
            elif game_type == "reaction":
                return await self._start_reaction_game()
            elif game_type == "all":
                return await self._start_all_games()
            else:
                return f"未知的游戏类型：{game_type}"
        except Exception as e:
            return f"启动游戏失败：{str(e)}"
            
    async def _start_memory_game(self) -> str:
        """启动记忆训练游戏"""
        try:
            game = MemoryGame()
            game.create_window()
            self.game_windows['memory'] = game
            return "已启动记忆训练游戏，请在新窗口中开始训练！"
        except Exception as e:
            return f"启动记忆游戏失败：{str(e)}"
        
    async def _start_focus_game(self) -> str:
        """启动专注力训练游戏"""
        try:
            game = FocusGame()
            game.create_window()
            self.game_windows['focus'] = game
            return "已启动专注力训练游戏，请在新窗口中开始训练！"
        except Exception as e:
            return f"启动专注力游戏失败：{str(e)}"
        
    async def _start_reaction_game(self) -> str:
        """启动反应速度训练游戏"""
        try:
            game = ReactionGame()
            game.create_window()
            self.game_windows['reaction'] = game
            return "已启动反应速度训练游戏，请在新窗口中开始训练！"
        except Exception as e:
            return f"启动反应速度游戏失败：{str(e)}"
        
    async def _start_all_games(self) -> str:
        """启动所有游戏"""
        try:
            results = []
            results.append(await self._start_memory_game())
            results.append(await self._start_focus_game())
            results.append(await self._start_reaction_game())
            return "已启动所有眼部健康训练游戏，请在新窗口中开始训练！"
        except Exception as e:
            return f"启动所有游戏失败：{str(e)}"
    
    def cleanup(self):
        """清理资源"""
        try:
            # 关闭所有游戏窗口
            for game in self.game_windows.values():
                if hasattr(game, 'close_window'):
                    game.close_window()
            self.game_windows.clear()
            
            # 关闭tkinter主循环
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"清理游戏资源失败：{e}") 