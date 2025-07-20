#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠核心逻辑
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque, defaultdict
import pyperclip
import win32gui
import requests
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QDialog, QVBoxLayout

class PetState:
    """桌宠状态类"""
    def __init__(self):
        self.happiness = 0.5      # 心情值 (0-1)
        self.energy = 0.8         # 精力值 (0-1)
        self.hunger = 0.3         # 饥饿值 (0-1)
        self.health = 0.9         # 健康值 (0-1)
        self.last_interaction: Optional[datetime] = None  # 上次互动时间
        self.interaction_count = 0    # 互动次数
        self.favorite_foods = []      # 喜欢的食物
        self.disliked_foods = []      # 不喜欢的食物
        self.personality_traits = {   # 性格特征
            'playfulness': 0.6,       # 爱玩程度
            'curiosity': 0.7,         # 好奇心
            'laziness': 0.4,          # 懒惰程度
            'friendliness': 0.8       # 友好程度
        }

class PetAgent:
    """桌宠智能体"""
    
    def __init__(self, name: str = "小宠物"):
        self.name = name
        self.state = PetState()
        self.mood = "happy"  # happy, sad, excited, sleepy, hungry
        self.current_animation = "idle"
        self.messages = []
        self.last_update = time.time()
        # 聊天历史，最多保存20条
        self.chat_history = deque(maxlen=20)
        
        # 个性化习惯学习
        self.user_habits = {
            "favorite_apps": defaultdict(int),  # 常用软件统计
            "app_usage_time": defaultdict(list),  # 软件使用时间记录
            "daily_patterns": defaultdict(int),  # 每日活动模式
            "work_hours": {"start": 9, "end": 18},  # 工作时间（默认）
            "break_times": [],  # 休息时间记录
            "productivity_score": 0.5,  # 工作效率评分
            "last_learned": None  # 上次学习时间
        }
        
        # 情感分析
        self.emotion_analysis = {
            "current_mood": "neutral",  # 当前心情：happy, sad, stressed, relaxed, focused
            "mood_history": deque(maxlen=50),  # 心情历史
            "stress_indicators": [],  # 压力指标
            "positive_activities": [],  # 积极活动
            "last_mood_update": time.time()
        }
        
        # 主动提醒系统
        self.reminder_system = {
            "last_reminder": time.time(),
            "reminder_cooldown": 1800,  # 30分钟冷却时间
            "reminder_types": {
                "break": {"last": 0, "interval": 3600},  # 休息提醒
                "productivity": {"last": 0, "interval": 7200},  # 效率提醒
                "health": {"last": 0, "interval": 5400},  # 健康提醒
                "social": {"last": 0, "interval": 9000}  # 社交提醒
            }
        }
        
        # 活动监控
        self.current_window_title = ""
        self.last_clipboard_content = ""
        self.last_activity_check = time.time()
        self.activity_triggered = False
        
        # 初始化基础数据
        self._init_pet_data()
        self._load_user_habits()
        
        # 强化学习引擎
        self.rl_engine = None  # 将在需要时初始化

        self.stats = {
            "attack": 10, "attack_exp": 0,
            "defense": 10, "defense_exp": 0,
            "speed": 10, "speed_exp": 0,
            "hp": 100
        }
        self._load_stats()
    
    def _init_pet_data(self):
        """初始化宠物数据"""
        self.state.favorite_foods = ["苹果", "胡萝卜", "鱼", "鸡肉"]
        self.state.disliked_foods = ["辣椒", "苦瓜", "臭豆腐"]
        self.state.last_interaction = datetime.now()
    
    def update(self):
        """更新宠物状态"""
        current_time = time.time()
        time_diff = current_time - self.last_update
        
        # 每秒更新一次状态
        if time_diff >= 1.0:
            self._update_automatic_states()
            self._update_mood()
            self.last_update = current_time
    
    def _save_user_habits(self):
        """保存用户习惯数据"""
        try:
            # 转换defaultdict为普通dict以便JSON序列化
            data = {}
            for key, value in self.user_habits.items():
                if isinstance(value, defaultdict):
                    data[key] = dict(value)
                elif isinstance(value, list):
                    # 处理break_times等列表中的datetime
                    data[key] = [v.isoformat() if isinstance(v, datetime) else v for v in value]
                elif isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
            # 特殊处理last_learned
            if "last_learned" in data and isinstance(data["last_learned"], datetime):
                data["last_learned"] = data["last_learned"].isoformat()
            with open("user_habits.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户习惯数据失败: {e}")
    
    def _load_user_habits(self):
        """加载用户习惯数据"""
        try:
            if os.path.exists("user_habits.json"):
                with open("user_habits.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 转换defaultdict数据
                    for key, value in data.items():
                        if key == "favorite_apps":
                            self.user_habits[key] = defaultdict(int, value)
                        elif key == "app_usage_time":
                            self.user_habits[key] = defaultdict(list, value)
                        elif key == "daily_patterns":
                            self.user_habits[key] = defaultdict(int, value)
                        elif key == "break_times":
                            # 反序列化break_times中的datetime
                            self.user_habits[key] = [datetime.fromisoformat(v) if isinstance(v, str) and v else v for v in value]
                        elif key == "last_learned":
                            self.user_habits[key] = datetime.fromisoformat(value) if value else None
                        else:
                            self.user_habits[key] = value
        except Exception as e:
            print(f"加载用户习惯数据失败: {e}")
    
    def learn_user_habits(self):
        """学习用户习惯"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_day = current_time.strftime("%A")  # 星期几
        
        # 记录软件使用
        if self.current_window_title:
            app_name = self._extract_app_name(self.current_window_title)
            if app_name:
                self.user_habits["favorite_apps"][app_name] += 1
                self.user_habits["app_usage_time"][app_name].append({
                    "time": current_time.strftime("%H:%M"),
                    "day": current_day,
                    "duration": 1  # 每次更新算1分钟
                })
        
        # 记录每日模式
        activity_type = self._categorize_activity(self.current_window_title)
        if activity_type:
            self.user_habits["daily_patterns"][f"{current_day}_{activity_type}"] += 1
        
        # 更新工作效率评分
        self._update_productivity_score()
        
        # 每小时保存一次数据
        if not self.user_habits["last_learned"] or \
           (current_time - self.user_habits["last_learned"]).total_seconds() > 3600:
            self.user_habits["last_learned"] = current_time
            self._save_user_habits()
    
    def _extract_app_name(self, window_title: str) -> str:
        """从窗口标题提取应用名称"""
        title_lower = window_title.lower()
        
        # 浏览器
        if any(browser in title_lower for browser in ["chrome", "edge", "firefox"]):
            return "浏览器"
        
        # 办公软件
        if "word" in title_lower:
            return "Word"
        elif "excel" in title_lower:
            return "Excel"
        elif "powerpoint" in title_lower or "ppt" in title_lower:
            return "PowerPoint"
        
        # 开发工具
        if "vscode" in title_lower:
            return "VSCode"
        elif "pycharm" in title_lower:
            return "PyCharm"
        elif "visual studio" in title_lower:
            return "Visual Studio"
        elif "terminal" in title_lower or "cmd" in title_lower:
            return "终端"
        
        # 游戏
        if "steam" in title_lower:
            return "Steam"
        
        # 其他常见应用
        if "notepad" in title_lower:
            return "记事本"
        elif "explorer" in title_lower:
            return "文件管理器"
        
        return "其他"
    
    def _categorize_activity(self, window_title: str) -> str:
        """分类活动类型"""
        title_lower = window_title.lower()
        
        if any(browser in title_lower for browser in ["chrome", "edge", "firefox"]):
            if "搜索" in title_lower or "search" in title_lower:
                return "搜索"
            elif "知乎" in title_lower or "zhihu" in title_lower:
                return "学习"
            elif "bilibili" in title_lower:
                return "娱乐"
            elif "github" in title_lower:
                return "编程"
            else:
                return "浏览"
        
        if any(app in title_lower for app in ["word", "excel", "powerpoint", "ppt"]):
            return "办公"
        
        if any(ide in title_lower for ide in ["vscode", "pycharm", "visual studio"]):
            return "编程"
        
        if "steam" in title_lower:
            return "游戏"
        
        return "其他"
    
    def _update_productivity_score(self):
        """更新工作效率评分"""
        current_hour = datetime.now().hour
        current_activity = self._categorize_activity(self.current_window_title)
        
        # 工作时间内的生产性活动加分
        if self.user_habits["work_hours"]["start"] <= current_hour <= self.user_habits["work_hours"]["end"]:
            if current_activity in ["办公", "编程", "学习"]:
                self.user_habits["productivity_score"] = min(1.0, self.user_habits["productivity_score"] + 0.01)
            elif current_activity in ["游戏", "娱乐"]:
                self.user_habits["productivity_score"] = max(0.0, self.user_habits["productivity_score"] - 0.01)
        else:
            # 非工作时间，娱乐活动加分
            if current_activity in ["游戏", "娱乐"]:
                self.user_habits["productivity_score"] = min(1.0, self.user_habits["productivity_score"] + 0.005)
    
    def get_user_insights(self) -> Dict:
        """获取用户行为洞察"""
        insights = {
            "favorite_app": self._get_favorite_app(),
            "most_productive_time": self._get_most_productive_time(),
            "work_pattern": self._analyze_work_pattern(),
            "productivity_score": round(self.user_habits["productivity_score"], 2),
            "daily_summary": self._get_daily_summary()
        }
        return insights
    
    def _get_favorite_app(self) -> str:
        """获取最常用的应用"""
        if not self.user_habits["favorite_apps"]:
            return "未知"
        
        favorite = max(self.user_habits["favorite_apps"].items(), key=lambda x: x[1])
        return favorite[0]
    
    def _get_most_productive_time(self) -> str:
        """获取最有效率的时间段"""
        time_stats = defaultdict(int)
        for app, times in self.user_habits["app_usage_time"].items():
            for time_record in times:
                hour = int(time_record["time"].split(":")[0])
                if app in ["Word", "Excel", "VSCode", "PyCharm"]:
                    time_stats[hour] += 1
        
        if time_stats:
            most_productive_hour = max(time_stats.items(), key=lambda x: x[1])[0]
            return f"{most_productive_hour}:00-{most_productive_hour+1}:00"
        return "未知"
    
    def _analyze_work_pattern(self) -> str:
        """分析工作模式"""
        work_count = sum(1 for pattern, count in self.user_habits["daily_patterns"].items() 
                        if "办公" in pattern or "编程" in pattern)
        total_count = sum(self.user_habits["daily_patterns"].values())
        
        if total_count == 0:
            return "数据不足"
        
        work_ratio = work_count / total_count
        if work_ratio > 0.7:
            return "工作狂"
        elif work_ratio > 0.5:
            return "平衡型"
        else:
            return "休闲型"
    
    def _get_daily_summary(self) -> str:
        """获取今日活动总结"""
        today = datetime.now().strftime("%A")
        today_patterns = {k: v for k, v in self.user_habits["daily_patterns"].items() 
                         if today in k}
        
        if not today_patterns:
            return "今天还没有活动记录"
        
        activities = []
        for pattern, count in today_patterns.items():
            activity = pattern.split("_")[1] if "_" in pattern else pattern
            activities.append(f"{activity}({count}次)")
        
        return "、".join(activities)
    
    def update_activity_info(self):
        """更新当前活动窗口标题和剪贴板内容"""
        # 获取活动窗口标题
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            self.current_window_title = window_title
        except Exception:
            self.current_window_title = ""
        # 获取剪贴板内容
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content != self.last_clipboard_content:
                self.last_clipboard_content = clipboard_content
        except Exception:
            pass
        
        # 学习用户习惯
        self.learn_user_habits()
        
        # 分析情感状态
        self.analyze_emotion()
    
    def analyze_emotion(self):
        """分析用户情感状态"""
        current_time = time.time()
        if current_time - self.emotion_analysis["last_mood_update"] < 60:  # 每分钟分析一次
            return
        
        self.emotion_analysis["last_mood_update"] = current_time
        current_hour = datetime.now().hour
        current_activity = self._categorize_activity(self.current_window_title)
        
        # 基于活动类型判断心情
        mood_score = 0
        mood_indicators = []
        
        # 积极活动加分
        if current_activity in ["学习", "编程"]:
            mood_score += 2
            mood_indicators.append("专注学习")
        elif current_activity == "娱乐":
            mood_score += 1
            mood_indicators.append("放松娱乐")
        elif current_activity == "游戏":
            mood_score += 1.5
            mood_indicators.append("游戏放松")
        
        # 工作时间压力分析
        if self.user_habits["work_hours"]["start"] <= current_hour <= self.user_habits["work_hours"]["end"]:
            if current_activity in ["办公", "编程"]:
                # 工作时间内的生产性活动，压力适中
                mood_score += 0.5
                mood_indicators.append("工作专注")
            elif current_activity in ["游戏", "娱乐"]:
                # 工作时间娱乐，可能有逃避心理
                mood_score -= 1
                mood_indicators.append("工作分心")
        else:
            # 非工作时间，娱乐活动更积极
            if current_activity in ["游戏", "娱乐"]:
                mood_score += 1.5
                mood_indicators.append("休闲时光")
        
        # 基于效率评分调整心情
        if self.user_habits["productivity_score"] > 0.7:
            mood_score += 1
            mood_indicators.append("效率很高")
        elif self.user_habits["productivity_score"] < 0.3:
            mood_score -= 1
            mood_indicators.append("效率较低")
        
        # 基于互动频率判断孤独感
        if self.state.interaction_count > 0 and self.state.last_interaction:
            time_since_interaction = (datetime.now() - self.state.last_interaction).total_seconds()
            if time_since_interaction > 1800:  # 30分钟无互动
                mood_score -= 0.5
                mood_indicators.append("缺少互动")
        
        # 确定心情状态
        if mood_score >= 3:
            mood = "happy"
        elif mood_score >= 1:
            mood = "relaxed"
        elif mood_score >= -1:
            mood = "neutral"
        elif mood_score >= -3:
            mood = "stressed"
        else:
            mood = "sad"
        
        # 更新心情历史
        self.emotion_analysis["current_mood"] = mood
        self.emotion_analysis["mood_history"].append({
            "time": datetime.now().strftime("%H:%M"),
            "mood": mood,
            "score": mood_score,
            "indicators": mood_indicators,
            "activity": current_activity
        })
        
        # 记录压力指标
        if mood in ["stressed", "sad"]:
            self.emotion_analysis["stress_indicators"].append({
                "time": datetime.now(),
                "activity": current_activity,
                "reason": "、".join(mood_indicators)
            })
        
        # 记录积极活动
        if mood in ["happy", "relaxed"]:
            self.emotion_analysis["positive_activities"].append({
                "time": datetime.now(),
                "activity": current_activity,
                "reason": "、".join(mood_indicators)
            })
    
    def check_reminders(self) -> str:
        """检查是否需要主动提醒"""
        current_time = time.time()
        
        # 检查冷却时间
        if current_time - self.reminder_system["last_reminder"] < self.reminder_system["reminder_cooldown"]:
            return ""
        
        current_hour = datetime.now().hour
        current_activity = self._categorize_activity(self.current_window_title)
        insights = self.get_user_insights()
        
        # 休息提醒
        if current_time - self.reminder_system["reminder_types"]["break"]["last"] > self.reminder_system["reminder_types"]["break"]["interval"]:
            if current_activity in ["办公", "编程"] and current_hour >= 10:
                # 工作2小时后提醒休息
                self.reminder_system["reminder_types"]["break"]["last"] = current_time
                self.reminder_system["last_reminder"] = current_time
                return f"工作辛苦了！建议休息一下，喝杯水，活动活动身体~"
        
        # 效率提醒
        if current_time - self.reminder_system["reminder_types"]["productivity"]["last"] > self.reminder_system["reminder_types"]["productivity"]["interval"]:
            if self.user_habits["productivity_score"] < 0.4 and current_hour in [9, 10, 14, 15]:
                self.reminder_system["reminder_types"]["productivity"]["last"] = current_time
                self.reminder_system["last_reminder"] = current_time
                return f"现在是{insights['most_productive_time']}，是你最有效率的时间，建议专注工作哦~"
        
        # 健康提醒
        if current_time - self.reminder_system["reminder_types"]["health"]["last"] > self.reminder_system["reminder_types"]["health"]["interval"]:
            if current_activity in ["游戏", "娱乐"] and current_hour >= 22:
                self.reminder_system["reminder_types"]["health"]["last"] = current_time
                self.reminder_system["last_reminder"] = current_time
                return f"夜深了，早点休息对身体好哦~"
            elif current_hour in [12, 18] and current_activity in ["办公", "编程"]:
                self.reminder_system["reminder_types"]["health"]["last"] = current_time
                self.reminder_system["last_reminder"] = current_time
                return f"该吃饭了！记得按时用餐，保持健康~"
        
        # 社交提醒
        if current_time - self.reminder_system["reminder_types"]["social"]["last"] > self.reminder_system["reminder_types"]["social"]["interval"]:
            if self.emotion_analysis["current_mood"] in ["stressed", "sad"]:
                self.reminder_system["reminder_types"]["social"]["last"] = current_time
                self.reminder_system["last_reminder"] = current_time
                return f"看起来你心情不太好，要不要和我聊聊天？或者找朋友倾诉一下~"
        
        return ""
    
    def get_emotion_summary(self) -> Dict:
        """获取情感分析总结"""
        if not self.emotion_analysis["mood_history"]:
            return {"current_mood": "未知", "trend": "数据不足", "suggestion": "继续观察"}
        
        current_mood = self.emotion_analysis["current_mood"]
        
        # 分析心情趋势
        recent_moods = [record["mood"] for record in list(self.emotion_analysis["mood_history"])[-10:]]
        positive_count = sum(1 for mood in recent_moods if mood in ["happy", "relaxed"])
        negative_count = sum(1 for mood in recent_moods if mood in ["stressed", "sad"])
        
        if positive_count > negative_count:
            trend = "心情向好"
        elif negative_count > positive_count:
            trend = "心情下降"
        else:
            trend = "心情稳定"
        
        # 生成建议
        suggestions = []
        if current_mood == "stressed":
            suggestions.append("建议适当休息，听些轻松的音乐")
        elif current_mood == "sad":
            suggestions.append("建议做些喜欢的事情，或者找人聊天")
        elif current_mood == "happy":
            suggestions.append("心情不错，继续保持！")
        elif current_mood == "relaxed":
            suggestions.append("状态很放松，适合学习或工作")
        
        return {
            "current_mood": current_mood,
            "trend": trend,
            "suggestion": "、".join(suggestions) if suggestions else "继续保持当前状态"
        }
    
    def check_activity_triggers(self) -> str:
        """检查活动触发条件，返回主动互动消息"""
        current_time = time.time()
        if current_time - self.last_activity_check < 30:  # 30秒内不重复触发
            return ""
        
        self.last_activity_check = current_time
        message = ""
        
        # 检查主动提醒
        reminder_message = self.check_reminders()
        if reminder_message:
            return reminder_message
        
        # 使用强化学习选择最佳动作（如果可用）
        if self.rl_engine:
            best_action = self.rl_engine.get_best_action(self)
            if best_action:
                message = self._execute_rl_action(best_action)
                if message:
                    return message
        
        # 检查窗口标题中的关键词
        window_lower = self.current_window_title.lower()
        
        # 浏览器相关
        if any(browser in window_lower for browser in ["chrome", "edge", "firefox", "safari"]):
            if "搜索" in window_lower or "search" in window_lower:
                message = f"看起来你在搜索什么，需要我帮忙吗？"
            elif "知乎" in window_lower or "zhihu" in window_lower:
                message = f"在知乎上学习新知识呢，真棒！"
            elif "bilibili" in window_lower or "哔哩哔哩" in window_lower:
                message = f"在看B站视频吗？我也想看！"
            elif "github" in window_lower:
                message = f"在GitHub上写代码呢，好厉害！"
            elif "stack overflow" in window_lower:
                message = f"在Stack Overflow上找解决方案吗？"
        
        # 办公软件
        elif "word" in window_lower or "文档" in window_lower:
            message = f"在写文档呢，工作辛苦了！"
        elif "excel" in window_lower or "表格" in window_lower:
            message = f"在处理数据表格吗？"
        elif "powerpoint" in window_lower or "ppt" in window_lower:
            message = f"在做演示文稿呢！"
        
        # 开发工具
        elif any(ide in window_lower for ide in ["visual studio", "vscode", "pycharm", "intellij", "eclipse"]):
            message = f"在写代码呢，编程加油！"
        elif "terminal" in window_lower or "cmd" in window_lower or "powershell" in window_lower:
            message = f"在使用命令行呢，好专业！"
        
        # 游戏
        elif any(game in window_lower for game in ["steam", "游戏", "game"]):
            message = f"在玩游戏呢，玩得开心！"
        
        # 检查剪贴板内容
        if self.last_clipboard_content and len(self.last_clipboard_content) > 5:
            clipboard_lower = self.last_clipboard_content.lower()
            if "http" in clipboard_lower or "www" in clipboard_lower:
                message = f"你复制了一个链接呢，是要分享什么好东西吗？"
            elif len(clipboard_lower) > 20:
                message = f"你复制了一段文字，是在整理资料吗？"
        
        # 基于情感状态的互动
        if not message:
            emotion_summary = self.get_emotion_summary()
            if emotion_summary["current_mood"] == "stressed":
                message = f"看起来你有点压力，要不要休息一下？"
            elif emotion_summary["current_mood"] == "sad":
                message = f"心情不太好吗？和我聊聊天吧~"
            elif emotion_summary["current_mood"] == "happy":
                message = f"心情不错呢！继续保持好心情~"
        
        # 长时间无互动提醒
        if not message and self.state.interaction_count > 0 and self.state.last_interaction:
            last_interaction_time = (datetime.now() - self.state.last_interaction).total_seconds()
            if last_interaction_time > 300:  # 5分钟无互动
                if self.state.hunger > 0.7:
                    message = f"我有点饿了，能给我点吃的吗？"
                elif self.state.happiness < 0.4:
                    message = f"好久没和你聊天了，想你了~"
                elif self.state.energy < 0.3:
                    message = f"我有点累了，想休息一下..."
        
        return message
    
    def _execute_rl_action(self, action: str) -> str:
        """执行强化学习选择的动作"""
        action_responses = {
            "pet": f"{self.name}主动蹭了蹭你，表示亲昵~",
            "feed": f"{self.name}用期待的眼神看着你，好像饿了~",
            "play": f"{self.name}兴奋地跳来跳去，想和你一起玩！",
            "chat": f"{self.name}温柔地看着你，想和你聊天~",
            "sleep": f"{self.name}打了个哈欠，看起来有点累了~",
            "observe": f"{self.name}安静地观察着你，不打扰你工作~",
            "comfort": f"{self.name}用温暖的眼神安慰你，一切都会好起来的~",
            "encourage": f"{self.name}用坚定的眼神鼓励你，加油！"
        }
        
        return action_responses.get(action, "")
    
    def set_rl_engine(self, rl_engine):
        """设置强化学习引擎"""
        self.rl_engine = rl_engine
    
    def get_activity_summary(self) -> str:
        """获取当前活动的总结"""
        window_lower = self.current_window_title.lower()
        
        if any(browser in window_lower for browser in ["chrome", "edge", "firefox"]):
            if "搜索" in window_lower:
                return "正在搜索信息"
            elif "知乎" in window_lower:
                return "在知乎上学习"
            elif "bilibili" in window_lower:
                return "在看B站视频"
            elif "github" in window_lower:
                return "在GitHub上编程"
            else:
                return "在浏览网页"
        elif "word" in window_lower:
            return "在写文档"
        elif "excel" in window_lower:
            return "在处理数据"
        elif "vscode" in window_lower or "pycharm" in window_lower:
            return "在写代码"
        elif "steam" in window_lower:
            return "在玩游戏"
        else:
            return "在使用电脑"

    def _update_automatic_states(self):
        """自动更新状态"""
        # 饥饿值随时间增加
        self.state.hunger = min(1.0, self.state.hunger + 0.001)
        
        # 精力值随时间减少
        self.state.energy = max(0.0, self.state.energy - 0.0005)
        
        # 心情值受其他状态影响
        self._update_happiness()
        
        # 健康值受饥饿和心情影响
        if self.state.hunger > 0.8:
            self.state.health = max(0.0, self.state.health - 0.001)
        elif self.state.happiness > 0.7:
            self.state.health = min(1.0, self.state.health + 0.0005)
    
    def _update_happiness(self):
        """更新心情值"""
        # 基础心情衰减
        self.state.happiness = max(0.0, self.state.happiness - 0.0002)
        
        # 受其他状态影响
        if self.state.hunger > 0.7:
            self.state.happiness = max(0.0, self.state.happiness - 0.001)
        if self.state.energy < 0.3:
            self.state.happiness = max(0.0, self.state.happiness - 0.001)
        if self.state.health < 0.5:
            self.state.happiness = max(0.0, self.state.happiness - 0.002)
    
    def _update_mood(self):
        """更新情绪状态"""
        if self.state.happiness > 0.8:
            self.mood = "excited"
        elif self.state.happiness > 0.6:
            self.mood = "happy"
        elif self.state.happiness > 0.4:
            self.mood = "normal"
        elif self.state.happiness > 0.2:
            self.mood = "sad"
        else:
            self.mood = "depressed"
        
        # 特殊状态
        if self.state.hunger > 0.8:
            self.mood = "hungry"
        if self.state.energy < 0.2:
            self.mood = "sleepy"
    
    def interact(self, action, **kwargs):
        """与宠物互动"""
        self.state.last_interaction = datetime.now()
        self.state.interaction_count += 1
        
        response = ""
        
        if action == "pet":
            response = self._handle_pet()
        elif action == "feed":
            food = kwargs.get("food", "")
            response = self._handle_feed(food)
        elif action == "play":
            response = self._handle_play()
        elif action == "chat":
            message = kwargs.get("message", "")
            # 记录聊天历史
            self.chat_history.append({"role": "user", "content": message})
            response = self._handle_chat(message)
            # 记录宠物回复
            self.chat_history.append({"role": "pet", "content": response})
            self.stats["attack_exp"] += 1
            self._check_upgrade("attack")
        elif action == "sleep":
            response = self._handle_sleep()
            self.stats["defense_exp"] += 1
            self._check_upgrade("defense")
        
        self._save_stats()
        return response
    
    def _handle_pet(self) -> str:
        """处理抚摸互动"""
        self.state.happiness = min(1.0, self.state.happiness + 0.1)
        self.state.energy = min(1.0, self.state.energy + 0.05)
        
        responses = [
            f"{self.name}开心地蹭了蹭你的手！",
            f"{self.name}发出满足的呼噜声~",
            f"{self.name}用温暖的眼神看着你",
            f"{self.name}摇着尾巴表示开心！"
        ]
        return random.choice(responses)
    
    def _handle_feed(self, food: str) -> str:
        """处理喂食互动"""
        if food in self.state.favorite_foods:
            self.state.happiness = min(1.0, self.state.happiness + 0.15)
            self.state.hunger = max(0.0, self.state.hunger - 0.3)
            self.state.health = min(1.0, self.state.health + 0.05)
            responses = [
                f"{self.name}兴奋地吃掉了{food}！看起来很喜欢呢~",
                f"{self.name}狼吞虎咽地吃着{food}，眼睛都亮了！",
                f"{self.name}吃完{food}后满足地舔了舔嘴巴"
            ]
        elif food in self.state.disliked_foods:
            self.state.happiness = max(0.0, self.state.happiness - 0.1)
            self.state.hunger = max(0.0, self.state.hunger - 0.1)
            responses = [
                f"{self.name}闻了闻{food}，露出嫌弃的表情...",
                f"{self.name}勉强吃了一点{food}，但明显不喜欢",
                f"{self.name}用爪子把{food}推开了"
            ]
        else:
            self.state.happiness = min(1.0, self.state.happiness + 0.05)
            self.state.hunger = max(0.0, self.state.hunger - 0.2)
            responses = [
                f"{self.name}吃掉了{food}，看起来还不错~",
                f"{self.name}慢慢品尝着{food}",
                f"{self.name}吃完{food}后打了个饱嗝"
            ]
        
        return random.choice(responses)
    
    def _handle_play(self) -> str:
        """处理玩耍互动"""
        if self.state.energy < 0.3:
            return f"{self.name}看起来太累了，需要休息一下..."
        
        self.state.happiness = min(1.0, self.state.happiness + 0.2)
        self.state.energy = max(0.0, self.state.energy - 0.1)
        
        responses = [
            f"{self.name}兴奋地跑来跑去，玩得很开心！",
            f"{self.name}和你玩起了捉迷藏~",
            f"{self.name}跳来跳去，活力满满！",
            f"{self.name}用爪子拍着玩具，玩得不亦乐乎"
        ]
        return random.choice(responses)
    
    def _handle_chat(self, message: str) -> str:
        """处理聊天互动"""
        self.state.happiness = min(1.0, self.state.happiness + 0.05)
        
        # 检查是否包含图片分析请求
        import re
        match = re.search(r'图片.*名为[“\"]?([\w\-.]+\.png)[”\"]?', message)
        if match:
            img_name = match.group(1)
            # 桌面路径
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            img_path = os.path.join(desktop, img_name)
            if not os.path.exists(img_path):
                return f"没有在桌面找到图片 {img_name}，请确认文件名。"
            # 调用后端API
            try:
                files = {'image': open(img_path, 'rb')}
                resp = requests.post('http://localhost:5000/api/image/recognition', files=files)
                data = resp.json()
                if data.get('success'):
                    result = data.get('result', '')
                    report = data.get('report', '')
                    # 弹出Web前端分析页面
                    self.show_web_report()
                    return f"图片分析结果：{result}\nAI健康报告：{report}"
                else:
                    return f"图片分析失败：{data.get('error', '未知错误')}"
            except Exception as e:
                return f"图片分析请求失败：{e}"
        
        # 检查是否询问当前活动
        if "在干什么" in message or "做什么" in message or "在干嘛" in message:
            activity = self.get_activity_summary()
            return f"我正在看着你呢！你{activity}，看起来很有趣的样子~"
        
        # 检查是否询问搜索内容
        if "搜索" in message or "查什么" in message:
            if self.last_clipboard_content and len(self.last_clipboard_content) > 3:
                return f"我看到你最近复制了：{self.last_clipboard_content[:20]}...，是在查这个吗？"
            else:
                return f"我看到你在浏览器里，但不知道具体在查什么。你可以告诉我吗？"
        
        # 检查是否询问工作状态
        if "工作" in message or "忙" in message:
            activity = self.get_activity_summary()
            if "文档" in activity or "数据" in activity or "代码" in activity:
                return f"看起来你在工作呢！{activity}，工作辛苦了，记得休息哦~"
            else:
                return f"看起来你在{activity}，放松一下也不错呢！"
        
        # 检查是否询问用户习惯
        if "习惯" in message or "常用" in message or "喜欢" in message:
            insights = self.get_user_insights()
            if insights["favorite_app"] != "未知":
                return f"我发现你最喜欢用{insights['favorite_app']}呢！"
            else:
                return f"我还在学习你的习惯，多和我互动我就能更了解你了~"
        
        # 检查是否询问工作效率
        if "效率" in message or "工作模式" in message or "工作狂" in message:
            insights = self.get_user_insights()
            if insights["work_pattern"] == "工作狂":
                return f"你是个工作狂呢！效率评分{insights['productivity_score']}，最有效率的时间是{insights['most_productive_time']}。记得适当休息哦！"
            elif insights["work_pattern"] == "平衡型":
                return f"你的工作生活很平衡呢！效率评分{insights['productivity_score']}，继续保持这种状态~"
            else:
                return f"你比较喜欢休闲呢！效率评分{insights['productivity_score']}，偶尔也要专注工作哦~"
        
        # 检查是否询问今日活动
        if "今天" in message and ("做什么" in message or "活动" in message):
            insights = self.get_user_insights()
            return f"今天你{insights['daily_summary']}，看起来很有规律呢！"
        
        # 检查是否询问建议
        if "建议" in message or "推荐" in message:
            insights = self.get_user_insights()
            current_hour = datetime.now().hour
            
            if current_hour < 12:
                return f"早上好！建议你{insights['most_productive_time']}的时候专注工作，效率会更高哦~"
            elif current_hour < 18:
                return f"下午了，记得适当休息。你最喜欢用{insights['favorite_app']}，可以切换一下心情~"
            else:
                return f"晚上了，工作了一天辛苦了！建议你放松一下，明天再继续~"
        
        # 检查是否询问心情
        if "心情" in message or "感觉" in message or "情绪" in message:
            emotion_summary = self.get_emotion_summary()
            if emotion_summary["current_mood"] == "happy":
                return f"看起来你心情很好呢！继续保持这种好心情~"
            elif emotion_summary["current_mood"] == "relaxed":
                return f"你现在的状态很放松，很适合学习或工作~"
            elif emotion_summary["current_mood"] == "stressed":
                return f"看起来你有点压力，建议休息一下，听些轻松的音乐~"
            elif emotion_summary["current_mood"] == "sad":
                return f"心情不太好吗？要不要和我聊聊天，或者做些喜欢的事情？"
            else:
                return f"心情一般，需要一些关爱~"
        
        # 检查是否询问压力
        if "压力" in message or "累" in message or "疲惫" in message:
            emotion_summary = self.get_emotion_summary()
            if emotion_summary["current_mood"] in ["stressed", "sad"]:
                return f"确实看起来你有点压力，建议：\n1. 适当休息，活动身体\n2. 听些轻松的音乐\n3. 找人聊聊天\n4. 做些喜欢的事情"
            else:
                return f"看起来你状态还不错，继续保持~"
        
        # 检查是否询问如何改善心情
        if "改善" in message and "心情" in message or "开心" in message:
            emotion_summary = self.get_emotion_summary()
            if emotion_summary["current_mood"] in ["stressed", "sad"]:
                return f"改善心情的建议：\n1. 做些你喜欢的活动\n2. 听些欢快的音乐\n3. 和朋友聊天\n4. 适当运动\n5. 或者和我多互动~"
            else:
                return f"你心情不错，继续保持这种状态就好~"
        
        # 简单的关键词回复
        if "你好" in message or "hello" in message.lower():
            return f"{self.name}开心地向你打招呼：你好呀！"
        elif "名字" in message:
            return f"我叫{self.name}，很高兴认识你！"
        elif "饿" in message or "吃" in message:
            if self.state.hunger > 0.6:
                return f"{self.name}确实有点饿了，想要好吃的！"
            else:
                return f"{self.name}现在不饿，但还是很感谢你的关心~"
        else:
            responses = [
                f"{self.name}认真听着你说话，时不时点点头",
                f"{self.name}用温柔的眼神回应着你",
                f"{self.name}发出轻轻的叫声，好像在回应你",
                f"{self.name}歪着头看着你，很感兴趣的样子"
            ]
            return random.choice(responses)
    
    def _handle_sleep(self) -> str:
        """处理睡觉互动"""
        if self.state.energy > 0.7:
            return f"{self.name}现在精力充沛，不想睡觉~"
        
        self.state.energy = min(1.0, self.state.energy + 0.3)
        self.state.happiness = min(1.0, self.state.happiness + 0.1)
        
        responses = [
            f"{self.name}舒服地蜷缩着睡着了，发出轻微的鼾声~",
            f"{self.name}闭上眼睛，很快就进入了梦乡",
            f"{self.name}找了个舒服的地方躺下，开始休息"
        ]
        return random.choice(responses)
    
    def get_status_info(self) -> Dict:
        """获取状态信息"""
        return {
            "name": self.name,
            "mood": self.mood,
            "happiness": round(self.state.happiness, 2),
            "energy": round(self.state.energy, 2),
            "hunger": round(self.state.hunger, 2),
            "health": round(self.state.health, 2),
            "interaction_count": self.state.interaction_count,
            "last_interaction": self.state.last_interaction.strftime("%H:%M:%S") if self.state.last_interaction else "从未"
        }
    
    def get_current_animation(self) -> str:
        """获取当前动画状态"""
        if self.mood == "sleepy" or self.state.energy < 0.3:
            return "sleeping"
        elif self.mood == "excited" or self.state.happiness > 0.8:
            return "excited"
        elif self.mood == "hungry":
            return "hungry"
        elif self.mood == "sad" or self.state.happiness < 0.3:
            return "sad"
        else:
            return "idle" 

    def _check_upgrade(self, stat):
        exp = self.stats[f"{stat}_exp"]
        level = self.stats[stat]
        if exp >= level * 5:
            self.stats[stat] += 1
            self.stats[f"{stat}_exp"] = 0
            # 可加提示
    def get_stats_summary(self):
        return (
            f"攻击力: {self.stats['attack']} (经验: {self.stats['attack_exp']})\n"
            f"防御力: {self.stats['defense']} (经验: {self.stats['defense_exp']})\n"
            f"速度: {self.stats['speed']} (经验: {self.stats['speed_exp']})\n"
            f"体力: {self.stats['hp']}"
        )
    def _save_stats(self):
        import json
        try:
            with open("pet_stats.json", "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    def _load_stats(self):
        import json, os
        if os.path.exists("pet_stats.json"):
            try:
                with open("pet_stats.json", "r", encoding="utf-8") as f:
                    self.stats.update(json.load(f))
            except Exception as e:
                pass 

    def show_analysis_result(self, result, report):
        msg = QMessageBox()
        msg.setWindowTitle("眼部图片分析结果")
        msg.setText(f"识别标签：{result}\n\nAI健康报告：{report}")
        msg.exec_() 

    def show_web_report(self, url="http://localhost:5000"):
        class WebDialog(QDialog):
            def __init__(self, url, parent=None):
                super().__init__(parent)
                self.setWindowTitle("眼部健康分析报告")
                layout = QVBoxLayout(self)
                self.webview = QWebEngineView(self)
                self.webview.load(url)
                layout.addWidget(self.webview)
                self.setLayout(layout)
        dlg = WebDialog(url)
        dlg.exec_() 