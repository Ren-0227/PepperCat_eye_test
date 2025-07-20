# vision_training_game.py
import cv2
import numpy as np
import mediapipe as mp
import time
import random
import json
import os
from typing import Dict, List, Tuple, Optional
from enum import Enum

class GameType(Enum):
    EYE_TRACKING = "eye_tracking"      # 眼动追踪游戏
    FOCUS_TRAINING = "focus_training"  # 专注力训练
    REACTION_SPEED = "reaction_speed"  # 反应速度训练
    MEMORY_GAME = "memory_game"        # 记忆游戏
    COLOR_MATCHING = "color_matching"  # 颜色匹配游戏

class VisionTrainingGame:
    """视力训练游戏系统"""
    
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.hands = mp.solutions.hands.Hands(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        
        # 游戏状态
        self.current_game = None
        self.game_score = 0
        self.game_level = 1
        self.game_duration = 60  # 默认60秒
        
        # 游戏数据
        self.game_history = []
        self.performance_stats = {}
        
        # 初始化游戏参数
        self._init_game_parameters()
    
    def _init_game_parameters(self):
        """初始化游戏参数"""
        self.target_positions = []
        self.current_target = None
        self.game_start_time = None
        self.hits = 0
        self.misses = 0
        self.reaction_times = []
    
    def start_game_menu(self):
        """启动游戏菜单"""
        print("=== 视力训练游戏 ===")
        print("1. 眼动追踪游戏")
        print("2. 专注力训练")
        print("3. 反应速度训练")
        print("4. 记忆游戏")
        print("5. 颜色匹配游戏")
        print("6. 查看历史成绩")
        print("0. 退出")
        
        while True:
            choice = input("\n请选择游戏 (0-6): ").strip()
            
            if choice == '0':
                print("感谢使用视力训练游戏！")
                break
            elif choice == '6':
                self._show_game_history()
                continue
            elif choice in ['1', '2', '3', '4', '5']:
                game_type = self._get_game_type(choice)
                self._start_game(game_type)
            else:
                print("无效选择，请重新输入")
    
    def _get_game_type(self, choice: str) -> GameType:
        """根据选择获取游戏类型"""
        game_map = {
            '1': GameType.EYE_TRACKING,
            '2': GameType.FOCUS_TRAINING,
            '3': GameType.REACTION_SPEED,
            '4': GameType.MEMORY_GAME,
            '5': GameType.COLOR_MATCHING
        }
        return game_map.get(choice, GameType.EYE_TRACKING)
    
    def _start_game(self, game_type: GameType):
        """开始指定游戏"""
        print(f"\n开始 {game_type.value} 游戏...")
        print("游戏说明:")
        
        if game_type == GameType.EYE_TRACKING:
            print("- 跟随移动的目标点")
            print("- 保持眼睛在目标中心")
        elif game_type == GameType.FOCUS_TRAINING:
            print("- 找到并点击指定的数字")
            print("- 提高专注力和视觉搜索能力")
        elif game_type == GameType.REACTION_SPEED:
            print("- 快速识别并点击出现的颜色")
            print("- 训练反应速度和视觉处理")
        elif game_type == GameType.MEMORY_GAME:
            print("- 记住颜色序列并重复")
            print("- 训练视觉记忆能力")
        elif game_type == GameType.COLOR_MATCHING:
            print("- 匹配相同颜色的方块")
            print("- 训练颜色识别和匹配能力")
        
        input("按回车键开始游戏...")
        
        self.current_game = game_type
        self._init_game_parameters()
        self.game_start_time = time.time()
        
        if game_type == GameType.EYE_TRACKING:
            self._play_eye_tracking_game()
        elif game_type == GameType.FOCUS_TRAINING:
            self._play_focus_training_game()
        elif game_type == GameType.REACTION_SPEED:
            self._play_reaction_speed_game()
        elif game_type == GameType.MEMORY_GAME:
            self._play_memory_game()
        elif game_type == GameType.COLOR_MATCHING:
            self._play_color_matching_game()
        
        self._end_game()
    
    def _play_eye_tracking_game(self):
        """眼动追踪游戏"""
        print("眼动追踪游戏开始！跟随移动的目标点...")
        
        target_pos = (320, 240)  # 屏幕中心
        target_radius = 20
        move_speed = 2
        
        while time.time() - self.game_start_time < self.game_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            # 更新目标位置（随机移动）
            if random.random() < 0.02:  # 2%概率改变方向
                target_pos = (
                    random.randint(50, 590),
                    random.randint(50, 430)
                )
            
            # 绘制目标点
            cv2.circle(frame, target_pos, target_radius, (0, 255, 0), -1)
            cv2.circle(frame, target_pos, target_radius + 5, (255, 255, 255), 2)
            
            # 检测眼动
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = self.face_mesh.process(rgb_frame)
            
            if face_results.multi_face_landmarks:
                eye_center = self._get_eye_center(face_results.multi_face_landmarks[0])
                eye_pos = (int(eye_center[0] * frame.shape[1]), int(eye_center[1] * frame.shape[0]))
                
                # 计算眼动距离
                distance = np.sqrt((eye_pos[0] - target_pos[0])**2 + (eye_pos[1] - target_pos[1])**2)
                
                if distance < target_radius + 30:  # 在目标附近
                    self.hits += 1
                    cv2.circle(frame, eye_pos, 10, (0, 255, 0), -1)
                else:
                    self.misses += 1
                    cv2.circle(frame, eye_pos, 10, (0, 0, 255), -1)
                
                # 绘制眼动轨迹
                cv2.line(frame, eye_pos, target_pos, (255, 255, 0), 2)
            
            # 显示游戏信息
            self._display_game_info(frame)
            cv2.imshow('Eye Tracking Game', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def _play_focus_training_game(self):
        """专注力训练游戏"""
        print("专注力训练游戏开始！找到并点击指定的数字...")
        
        numbers = list(range(1, 10))
        current_target = random.choice(numbers)
        grid_size = 3
        cell_size = 100
        
        while time.time() - self.game_start_time < self.game_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            # 创建数字网格
            grid_frame = np.ones((300, 300, 3), dtype=np.uint8) * 255
            
            # 随机排列数字
            random.shuffle(numbers)
            for i, num in enumerate(numbers):
                row = i // grid_size
                col = i % grid_size
                x = col * cell_size + cell_size // 2
                y = row * cell_size + cell_size // 2
                
                color = (0, 0, 255) if num == current_target else (0, 0, 0)
                cv2.putText(grid_frame, str(num), (x-20, y+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
                
                # 绘制网格线
                cv2.rectangle(grid_frame, (col*cell_size, row*cell_size), 
                             ((col+1)*cell_size, (row+1)*cell_size), (128, 128, 128), 2)
            
            # 显示目标数字
            cv2.putText(frame, f"找到数字: {current_target}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # 将网格添加到主画面
            x_offset = (frame.shape[1] - grid_frame.shape[1]) // 2
            y_offset = (frame.shape[0] - grid_frame.shape[0]) // 2
            frame[y_offset:y_offset+grid_frame.shape[0], 
                 x_offset:x_offset+grid_frame.shape[1]] = grid_frame
            
            # 检测手势点击
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = self.hands.process(rgb_frame)
            
            if hand_results.multi_hand_landmarks:
                hand_pos = self._get_hand_position(hand_results.multi_hand_landmarks[0])
                
                # 检查是否点击了目标数字
                if self._check_grid_click(hand_pos, x_offset, y_offset, grid_size, cell_size, numbers, current_target):
                    self.hits += 1
                    current_target = random.choice([n for n in numbers if n != current_target])
                else:
                    self.misses += 1
            
            self._display_game_info(frame)
            cv2.imshow('Focus Training Game', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def _play_reaction_speed_game(self):
        """反应速度训练游戏"""
        print("反应速度训练游戏开始！快速识别并点击出现的颜色...")
        
        colors = ['red', 'green', 'blue', 'yellow']
        color_map = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255)
        }
        
        current_color = random.choice(colors)
        color_start_time = time.time()
        
        while time.time() - self.game_start_time < self.game_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            # 显示当前颜色
            color_circle = np.ones((200, 200, 3), dtype=np.uint8) * 255
            cv2.circle(color_circle, (100, 100), 80, color_map[current_color], -1)
            
            # 将颜色圆圈添加到主画面
            x_offset = (frame.shape[1] - color_circle.shape[1]) // 2
            y_offset = (frame.shape[0] - color_circle.shape[0]) // 2
            frame[y_offset:y_offset+color_circle.shape[0], 
                 x_offset:x_offset+color_circle.shape[1]] = color_circle
            
            # 检测手势响应
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = self.hands.process(rgb_frame)
            
            if hand_results.multi_hand_landmarks:
                self.hits += 1
                reaction_time = time.time() - color_start_time
                self.reaction_times.append(reaction_time)
                
                # 更换颜色
                current_color = random.choice([c for c in colors if c != current_color])
                color_start_time = time.time()
            
            # 检查颜色显示时间
            if time.time() - color_start_time > 3:  # 3秒超时
                self.misses += 1
                current_color = random.choice([c for c in colors if c != current_color])
                color_start_time = time.time()
            
            self._display_game_info(frame)
            cv2.imshow('Reaction Speed Game', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def _play_memory_game(self):
        """记忆游戏"""
        print("记忆游戏开始！记住颜色序列并重复...")
        
        colors = ['red', 'green', 'blue', 'yellow']
        sequence = []
        sequence_length = 3
        current_step = 0
        showing_sequence = True
        sequence_start_time = time.time()
        
        while time.time() - self.game_start_time < self.game_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            if showing_sequence:
                # 显示序列
                if current_step < len(sequence):
                    current_color = sequence[current_step]
                    if time.time() - sequence_start_time > 1:  # 每个颜色显示1秒
                        current_step += 1
                        sequence_start_time = time.time()
                else:
                    showing_sequence = False
                    current_step = 0
                    sequence_start_time = time.time()
            else:
                # 等待用户输入
                if current_step < len(sequence):
                    expected_color = sequence[current_step]
                    
                    # 检测手势响应
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    hand_results = self.hands.process(rgb_frame)
                    
                    if hand_results.multi_hand_landmarks:
                        # 简化的颜色检测（实际应用中需要更复杂的检测）
                        if random.random() < 0.8:  # 80%正确率模拟
                            self.hits += 1
                        else:
                            self.misses += 1
                        
                        current_step += 1
                
                if current_step >= len(sequence):
                    # 序列完成，生成新序列
                    sequence = [random.choice(colors) for _ in range(sequence_length)]
                    sequence_length = min(sequence_length + 1, 8)  # 逐渐增加难度
                    current_step = 0
                    showing_sequence = True
                    sequence_start_time = time.time()
            
            # 显示当前颜色
            if showing_sequence and current_step < len(sequence):
                current_color = sequence[current_step]
                color_circle = np.ones((200, 200, 3), dtype=np.uint8) * 255
                color_map = {'red': (0, 0, 255), 'green': (0, 255, 0), 
                           'blue': (255, 0, 0), 'yellow': (0, 255, 255)}
                cv2.circle(color_circle, (100, 100), 80, color_map[current_color], -1)
                
                x_offset = (frame.shape[1] - color_circle.shape[1]) // 2
                y_offset = (frame.shape[0] - color_circle.shape[0]) // 2
                frame[y_offset:y_offset+color_circle.shape[0], 
                     x_offset:x_offset+color_circle.shape[1]] = color_circle
            
            self._display_game_info(frame)
            cv2.imshow('Memory Game', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def _play_color_matching_game(self):
        """颜色匹配游戏"""
        print("颜色匹配游戏开始！匹配相同颜色的方块...")
        
        grid_size = 4
        cell_size = 80
        colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'cyan']
        color_map = {
            'red': (0, 0, 255), 'green': (0, 255, 0), 'blue': (255, 0, 0),
            'yellow': (0, 255, 255), 'purple': (255, 0, 255), 'orange': (0, 165, 255),
            'pink': (147, 20, 255), 'cyan': (255, 255, 0)
        }
        
        # 创建颜色网格
        grid_colors = []
        for i in range(grid_size * grid_size // 2):
            color = random.choice(colors)
            grid_colors.extend([color, color])
        random.shuffle(grid_colors)
        
        revealed = [False] * len(grid_colors)
        selected = None
        
        while time.time() - self.game_start_time < self.game_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            # 创建颜色网格
            grid_frame = np.ones((grid_size * cell_size, grid_size * cell_size, 3), dtype=np.uint8) * 255
            
            for i, color in enumerate(grid_colors):
                row = i // grid_size
                col = i % grid_size
                x = col * cell_size
                y = row * cell_size
                
                if revealed[i]:
                    cv2.rectangle(grid_frame, (x, y), (x + cell_size, y + cell_size), 
                                 color_map[color], -1)
                else:
                    cv2.rectangle(grid_frame, (x, y), (x + cell_size, y + cell_size), 
                                 (128, 128, 128), -1)
                
                cv2.rectangle(grid_frame, (x, y), (x + cell_size, y + cell_size), 
                             (0, 0, 0), 2)
            
            # 将网格添加到主画面
            x_offset = (frame.shape[1] - grid_frame.shape[1]) // 2
            y_offset = (frame.shape[0] - grid_frame.shape[0]) // 2
            frame[y_offset:y_offset+grid_frame.shape[0], 
                 x_offset:x_offset+grid_frame.shape[1]] = grid_frame
            
            # 检测手势点击
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = self.hands.process(rgb_frame)
            
            if hand_results.multi_hand_landmarks:
                hand_pos = self._get_hand_position(hand_results.multi_hand_landmarks[0])
                clicked_index = self._get_grid_index(hand_pos, x_offset, y_offset, grid_size, cell_size)
                
                if clicked_index is not None and not revealed[clicked_index]:
                    if selected is None:
                        selected = clicked_index
                        revealed[clicked_index] = True
                    else:
                        revealed[clicked_index] = True
                        
                        if grid_colors[selected] == grid_colors[clicked_index]:
                            self.hits += 1
                        else:
                            self.misses += 1
                            # 隐藏不匹配的方块
                            revealed[selected] = False
                            revealed[clicked_index] = False
                        
                        selected = None
            
            self._display_game_info(frame)
            cv2.imshow('Color Matching Game', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def _end_game(self):
        """结束游戏"""
        game_duration = time.time() - self.game_start_time
        accuracy = self.hits / max(self.hits + self.misses, 1)
        avg_reaction_time = np.mean(self.reaction_times) if self.reaction_times else 0
        
        # 计算游戏分数
        score = int(self.hits * 100 * accuracy)
        
        # 保存游戏结果
        game_result = {
            'game_type': self.current_game.value,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': game_duration,
            'hits': self.hits,
            'misses': self.misses,
            'accuracy': accuracy,
            'score': score,
            'avg_reaction_time': avg_reaction_time
        }
        
        self.game_history.append(game_result)
        self._save_game_history()
        
        # 显示游戏结果
        print(f"\n=== 游戏结束 ===")
        print(f"游戏类型: {self.current_game.value}")
        print(f"游戏时长: {game_duration:.1f}秒")
        print(f"命中次数: {self.hits}")
        print(f"失误次数: {self.misses}")
        print(f"准确率: {accuracy:.2%}")
        print(f"游戏分数: {score}")
        if avg_reaction_time > 0:
            print(f"平均反应时间: {avg_reaction_time:.3f}秒")
        
        # 给出评价
        if accuracy >= 0.9:
            print("评价: 优秀！继续保持！")
        elif accuracy >= 0.7:
            print("评价: 良好！还有提升空间。")
        elif accuracy >= 0.5:
            print("评价: 一般，需要多加练习。")
        else:
            print("评价: 需要更多练习来提高准确率。")
    
    def _show_game_history(self):
        """显示游戏历史"""
        if not self.game_history:
            print("暂无游戏历史记录")
            return
        
        print("\n=== 游戏历史记录 ===")
        for i, result in enumerate(self.game_history[-10:], 1):  # 显示最近10条记录
            print(f"{i}. {result['game_type']} - 分数: {result['score']} - 准确率: {result['accuracy']:.2%} - {result['timestamp']}")
    
    def _save_game_history(self):
        """保存游戏历史"""
        history_file = "game_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.game_history, f, ensure_ascii=False, indent=2)
    
    # 辅助方法
    def _get_eye_center(self, landmarks) -> Tuple[float, float]:
        """获取眼睛中心点"""
        left_eye = landmarks.landmark[159]
        right_eye = landmarks.landmark[386]
        return ((left_eye.x + right_eye.x) / 2, (left_eye.y + right_eye.y) / 2)
    
    def _get_hand_position(self, hand_landmarks) -> Tuple[int, int]:
        """获取手势位置"""
        index_tip = hand_landmarks.landmark[8]
        return (int(index_tip.x * 640), int(index_tip.y * 480))
    
    def _check_grid_click(self, hand_pos: Tuple[int, int], x_offset: int, y_offset: int, 
                          grid_size: int, cell_size: int, numbers: List[int], target: int) -> bool:
        """检查是否点击了目标数字"""
        if x_offset <= hand_pos[0] <= x_offset + grid_size * cell_size and \
           y_offset <= hand_pos[1] <= y_offset + grid_size * cell_size:
            col = (hand_pos[0] - x_offset) // cell_size
            row = (hand_pos[1] - y_offset) // cell_size
            index = row * grid_size + col
            return numbers[index] == target
        return False
    
    def _get_grid_index(self, hand_pos: Tuple[int, int], x_offset: int, y_offset: int, 
                        grid_size: int, cell_size: int) -> Optional[int]:
        """获取网格索引"""
        if x_offset <= hand_pos[0] <= x_offset + grid_size * cell_size and \
           y_offset <= hand_pos[1] <= y_offset + grid_size * cell_size:
            col = (hand_pos[0] - x_offset) // cell_size
            row = (hand_pos[1] - y_offset) // cell_size
            return row * grid_size + col
        return None
    
    def _display_game_info(self, frame: np.ndarray):
        """显示游戏信息"""
        info_text = [
            f"游戏: {self.current_game.value}",
            f"分数: {self.game_score}",
            f"命中: {self.hits}",
            f"失误: {self.misses}",
            f"时间: {int(time.time() - self.game_start_time)}s"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, 30 + 30*i),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def cleanup(self):
        """清理资源"""
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_mesh.close()
        self.hands.close()

# 使用示例
if __name__ == "__main__":
    try:
        game = VisionTrainingGame()
        game.start_game_menu()
    except Exception as e:
        print(f"游戏启动失败: {str(e)}")
    finally:
        if 'game' in locals():
            game.cleanup() 