#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强化学习引擎
"""

import numpy as np
import random
import json
import os
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import time

class RLState:
    """强化学习状态类"""
    def __init__(self):
        self.user_activity = ""  # 用户当前活动
        self.user_mood = ""      # 用户心情
        self.time_of_day = 0    # 一天中的时间（小时）
        self.day_of_week = 0    # 星期几
        self.pet_hunger = 0.0   # 宠物饥饿度
        self.pet_energy = 0.0   # 宠物精力
        self.pet_happiness = 0.0 # 宠物心情
        self.interaction_count = 0 # 互动次数
    
    def to_tuple(self) -> Tuple:
        """转换为元组用于哈希"""
        return (
            self.user_activity,
            self.user_mood,
            self.time_of_day,
            self.day_of_week,
            round(self.pet_hunger, 1),
            round(self.pet_energy, 1),
            round(self.pet_happiness, 1),
            min(self.interaction_count, 10)  # 限制互动次数范围
        )
    
    def from_pet_agent(self, pet_agent):
        """从宠物智能体获取状态"""
        from src.agent.pet_agent import PetAgent
        
        current_time = pet_agent.state.last_interaction or time.time()
        dt = time.localtime(current_time)
        
        self.user_activity = pet_agent._categorize_activity(pet_agent.current_window_title)
        self.user_mood = pet_agent.emotion_analysis["current_mood"]
        self.time_of_day = dt.tm_hour
        self.day_of_week = dt.tm_wday
        self.pet_hunger = pet_agent.state.hunger
        self.pet_energy = pet_agent.state.energy
        self.pet_happiness = pet_agent.state.happiness
        self.interaction_count = pet_agent.state.interaction_count

class RLEngine:
    """强化学习引擎"""
    
    def __init__(self):
        self.actions = [
            "pet", "feed", "play", "chat", "sleep", "observe", "comfort", "encourage"
        ]
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1  # 探索率
        
        # 训练相关
        self.training_data = []
        self.training_progress = 0.0
        self.is_training = False
        self.training_episodes = 0
        self.max_episodes = 1000
        
        # 加载已有的Q表
        self.load_q_table()
    
    def get_state_action_key(self, state: RLState, action: str) -> str:
        """获取状态-动作键"""
        return f"{state.to_tuple()}_{action}"
    
    def get_reward(self, state: RLState, action: str, next_state: RLState) -> float:
        """计算奖励值"""
        reward = 0.0
        
        # 基础奖励：根据用户心情
        if state.user_mood == "happy":
            reward += 2.0
        elif state.user_mood == "relaxed":
            reward += 1.5
        elif state.user_mood == "stressed":
            reward -= 1.0
        elif state.user_mood == "sad":
            reward -= 2.0
        
        # 动作特定奖励
        if action == "comfort" and state.user_mood in ["stressed", "sad"]:
            reward += 3.0  # 安慰压力大的用户
        elif action == "encourage" and state.user_mood == "neutral":
            reward += 2.0  # 鼓励一般心情的用户
        elif action == "observe" and state.user_activity in ["编程", "办公"]:
            reward += 1.0  # 观察工作中的用户
        elif action == "play" and state.user_mood == "happy":
            reward += 2.0  # 和开心的用户玩耍
        
        # 时间相关奖励
        if 9 <= state.time_of_day <= 18:  # 工作时间
            if action in ["observe", "comfort"] and state.user_activity in ["编程", "办公"]:
                reward += 1.5  # 工作时间的适当互动
            elif action == "play" and state.user_activity in ["编程", "办公"]:
                reward -= 1.0  # 工作时间玩耍可能打扰
        else:  # 非工作时间
            if action in ["play", "chat"]:
                reward += 1.0  # 非工作时间娱乐互动
        
        # 宠物状态奖励
        if state.pet_hunger > 0.7 and action == "feed":
            reward += 2.0  # 饥饿时喂食
        elif state.pet_energy < 0.3 and action == "sleep":
            reward += 2.0  # 精力不足时睡觉
        elif state.pet_happiness < 0.4 and action in ["pet", "play"]:
            reward += 1.5  # 心情不好时互动
        
        return reward
    
    def choose_action(self, state: RLState, training: bool = True) -> str:
        """选择动作（ε-贪婪策略）"""
        if training and random.random() < self.epsilon:
            return random.choice(self.actions)
        
        # 选择Q值最大的动作
        q_values = [self.q_table[state.to_tuple()][action] for action in self.actions]
        max_q = max(q_values)
        best_actions = [action for action, q in zip(self.actions, q_values) if q == max_q]
        return random.choice(best_actions)
    
    def update_q_value(self, state: RLState, action: str, reward: float, next_state: RLState):
        """更新Q值"""
        current_q = self.q_table[state.to_tuple()][action]
        
        # 计算下一状态的最大Q值
        next_q_values = [self.q_table[next_state.to_tuple()][a] for a in self.actions]
        max_next_q = max(next_q_values) if next_q_values else 0
        
        # Q-learning更新公式
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state.to_tuple()][action] = new_q
    
    def train_episode(self, pet_agent) -> float:
        """训练一个回合"""
        state = RLState()
        state.from_pet_agent(pet_agent)
        
        total_reward = 0.0
        steps = 0
        max_steps = 50
        
        while steps < max_steps:
            # 选择动作
            action = self.choose_action(state, training=True)
            
            # 执行动作（模拟）
            reward = self.simulate_action(pet_agent, action)
            
            # 获取下一状态
            next_state = RLState()
            next_state.from_pet_agent(pet_agent)
            
            # 更新Q值
            self.update_q_value(state, action, reward, next_state)
            
            total_reward += reward
            state = next_state
            steps += 1
            
            # 如果用户心情很好，可以提前结束
            if state.user_mood == "happy" and reward > 0:
                break
        
        # 强化学习回合结束后，根据reward提升属性
        if hasattr(pet_agent, 'stats'):
            if total_reward > 20:
                pet_agent.stats["attack"] += 1
            if total_reward > 15:
                pet_agent.stats["defense"] += 1
            if total_reward > 10:
                pet_agent.stats["speed"] += 1
            if total_reward > 5:
                pet_agent.stats["hp"] += 2
            if hasattr(pet_agent, '_save_stats'):
                pet_agent._save_stats()
        return total_reward
    
    def simulate_action(self, pet_agent, action: str) -> float:
        """模拟动作执行并返回奖励"""
        # 创建当前状态的副本
        current_state = RLState()
        current_state.from_pet_agent(pet_agent)
        
        # 模拟动作效果
        if action == "pet":
            pet_agent.state.happiness = min(1.0, pet_agent.state.happiness + 0.1)
        elif action == "feed":
            pet_agent.state.hunger = max(0.0, pet_agent.state.hunger - 0.3)
            pet_agent.state.happiness = min(1.0, pet_agent.state.happiness + 0.05)
        elif action == "play":
            if pet_agent.state.energy > 0.3:
                pet_agent.state.happiness = min(1.0, pet_agent.state.happiness + 0.2)
                pet_agent.state.energy = max(0.0, pet_agent.state.energy - 0.1)
        elif action == "sleep":
            pet_agent.state.energy = min(1.0, pet_agent.state.energy + 0.3)
        elif action == "comfort":
            if pet_agent.emotion_analysis["current_mood"] in ["stressed", "sad"]:
                pet_agent.emotion_analysis["current_mood"] = "relaxed"
        elif action == "encourage":
            if pet_agent.emotion_analysis["current_mood"] == "neutral":
                pet_agent.emotion_analysis["current_mood"] = "relaxed"
        
        # 计算奖励
        next_state = RLState()
        next_state.from_pet_agent(pet_agent)
        reward = self.get_reward(current_state, action, next_state)
        
        return reward
    
    def start_training(self, pet_agent) -> bool:
        """开始训练"""
        if self.is_training:
            return False
        
        self.is_training = True
        self.training_progress = 0.0
        self.training_episodes = 0
        
        # 收集训练数据
        self.collect_training_data(pet_agent)
        
        return True
    
    def collect_training_data(self, pet_agent):
        """收集训练数据"""
        # 基于用户习惯生成训练数据
        insights = pet_agent.get_user_insights()
        emotion_summary = pet_agent.get_emotion_summary()
        
        # 创建多样化的训练场景
        scenarios = []
        
        # 工作场景
        for hour in [9, 10, 14, 15, 16]:
            for activity in ["编程", "办公"]:
                for mood in ["stressed", "neutral", "relaxed"]:
                    scenarios.append({
                        "time": hour,
                        "activity": activity,
                        "mood": mood,
                        "expected_action": "observe" if mood == "stressed" else "encourage"
                    })
        
        # 休息场景
        for hour in [12, 18, 20, 22]:
            for activity in ["娱乐", "游戏"]:
                for mood in ["happy", "relaxed"]:
                    scenarios.append({
                        "time": hour,
                        "activity": activity,
                        "mood": mood,
                        "expected_action": "play"
                    })
        
        # 压力场景
        for mood in ["stressed", "sad"]:
            for activity in ["编程", "办公", "其他"]:
                scenarios.append({
                    "time": random.randint(9, 18),
                    "activity": activity,
                    "mood": mood,
                    "expected_action": "comfort"
                })
        
        self.training_data = scenarios
    
    def train_step(self, pet_agent) -> float:
        """执行一步训练"""
        if not self.is_training or self.training_episodes >= self.max_episodes:
            self.is_training = False
            return 0.0
        
        # 选择一个训练场景
        if self.training_data:
            scenario = random.choice(self.training_data)
            
            # 设置模拟状态
            pet_agent.current_window_title = f"模拟_{scenario['activity']}"
            pet_agent.emotion_analysis["current_mood"] = scenario["mood"]
            
            # 训练一个回合
            reward = self.train_episode(pet_agent)
            
            self.training_episodes += 1
            self.training_progress = self.training_episodes / self.max_episodes
            
            # 训练日志提示属性提升
            if hasattr(pet_agent, 'stats') and reward > 10:
                print(f"[RL] 属性提升: 攻击{pet_agent.stats['attack']} 防御{pet_agent.stats['defense']} 速度{pet_agent.stats['speed']} 体力{pet_agent.stats['hp']}")
            return reward
        
        return 0.0
    
    def get_best_action(self, pet_agent) -> str:
        """获取当前状态下的最佳动作"""
        state = RLState()
        state.from_pet_agent(pet_agent)
        return self.choose_action(state, training=False)
    
    def save_q_table(self):
        """保存Q表"""
        try:
            # 转换defaultdict为普通dict
            q_table_dict = {}
            for state_key, actions in self.q_table.items():
                q_table_dict[str(state_key)] = dict(actions)
            
            with open("q_table.json", "w", encoding="utf-8") as f:
                json.dump(q_table_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存Q表失败: {e}")
    
    def load_q_table(self):
        """加载Q表"""
        try:
            if os.path.exists("q_table.json"):
                with open("q_table.json", "r", encoding="utf-8") as f:
                    q_table_dict = json.load(f)
                
                for state_key_str, actions in q_table_dict.items():
                    # 解析状态键
                    state_key = eval(state_key_str)  # 注意：这里简化处理
                    self.q_table[state_key] = defaultdict(float, actions)
        except Exception as e:
            print(f"加载Q表失败: {e}")
    
    def get_training_status(self) -> Dict:
        """获取训练状态"""
        return {
            "is_training": self.is_training,
            "progress": self.training_progress,
            "episodes": self.training_episodes,
            "max_episodes": self.max_episodes,
            "q_table_size": len(self.q_table)
        } 