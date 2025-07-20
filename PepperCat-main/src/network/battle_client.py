#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对战客户端模块
处理与服务器的通信和消息发送
"""

import socket
import threading
import json
import time
import uuid
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from PyQt6.QtCore import QObject, pyqtSignal

@dataclass
class BattleMessage:
    """对战消息"""
    type: str  # 'attack', 'move', 'join', 'leave', 'heartbeat'
    player_id: str
    data: dict
    timestamp: float

class BattleClient(QObject):
    """对战客户端"""
    
    # 信号
    player_joined = pyqtSignal(str, str)  # player_id, player_name
    player_left = pyqtSignal(str)
    attack_received = pyqtSignal(str, str, dict)  # attacker_id, target_id, attack_data
    player_moved = pyqtSignal(str, tuple)  # player_id, position
    server_disconnected = pyqtSignal()
    opponent_melee_move = pyqtSignal(str, tuple)  # player_id, pos
    opponent_melee_attack = pyqtSignal(str, tuple)  # player_id, pos
    melee_hit_feedback = pyqtSignal(str, tuple)  # player_id, pos
    
    def __init__(self, player_id: str, player_name: str, pet_name: str, server_ip: str = "127.0.0.1", server_port: int = 8888):
        super().__init__()
        self.player_id = player_id
        self.player_name = player_name
        self.pet_name = pet_name
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = 8889  # 客户端监听端口
        
        self.socket = None
        self.running = False
        self.client_thread = None
        self.heartbeat_thread = None
        
        # 消息处理器
        self.message_handlers: Dict[str, Callable] = {}
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """设置消息处理器"""
        self.message_handlers = {
            'join': self._handle_player_join,
            'leave': self._handle_player_leave,
            'attack': self._handle_attack,
            'move': self._handle_player_move,
            'heartbeat': self._handle_heartbeat,
            'melee_move': self._handle_melee_move,
            'melee_attack': self._handle_melee_attack,
            'melee_hit_feedback': self._handle_melee_hit_feedback
        }
    
    def start(self) -> bool:
        """启动客户端"""
        try:
            # 创建UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('0.0.0.0', self.client_port))
            self.running = True
            
            # 启动接收线程
            self.client_thread = threading.Thread(target=self._client_loop, daemon=True)
            self.client_thread.start()
            
            # 启动心跳线程
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            
            # 发送加入消息
            self._send_join_message()
            
            print(f"[对战客户端] 启动成功，连接到 {self.server_ip}:{self.server_port}")
            return True
            
        except Exception as e:
            print(f"[对战客户端] 启动失败: {e}")
            return False
    
    def stop(self):
        """停止客户端"""
        self.running = False
        
        # 发送离开消息
        if self.socket:
            self._send_leave_message()
            self.socket.close()
        
        print("[对战客户端] 已停止")
    
    def _client_loop(self):
        """客户端主循环"""
        while self.running:
            try:
                self.socket.settimeout(1.0)
                data, addr = self.socket.recvfrom(1024)
                self._handle_message(data)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[对战客户端] 接收消息错误: {e}")
                    self.server_disconnected.emit()
                break
    
    def _handle_message(self, data: bytes):
        """处理接收到的消息"""
        try:
            message_data = json.loads(data.decode('utf-8'))
            message = BattleMessage(**message_data)
            
            # 忽略自己的消息
            if message.player_id == self.player_id:
                return
            
            # 调用对应的处理器
            handler = self.message_handlers.get(message.type)
            if handler:
                handler(message)
                
        except Exception as e:
            print(f"[对战客户端] 处理消息错误: {e}")
    
    def _handle_player_join(self, message: BattleMessage):
        """处理玩家加入"""
        player_name = message.data.get('name', '未知玩家')
        print(f"[对战客户端] 玩家加入: {player_name}")
        self.player_joined.emit(message.player_id, player_name)
    
    def _handle_player_leave(self, message: BattleMessage):
        """处理玩家离开"""
        print(f"[对战客户端] 玩家离开: {message.player_id}")
        self.player_left.emit(message.player_id)
    
    def _handle_attack(self, message: BattleMessage):
        """处理攻击消息"""
        attacker_id = message.player_id
        target_id = message.data.get('target_id')
        attack_data = message.data
        
        print(f"[对战客户端] 攻击: {attacker_id} -> {target_id}")
        self.attack_received.emit(attacker_id, target_id, attack_data)
    
    def _handle_player_move(self, message: BattleMessage):
        """处理玩家移动"""
        player_id = message.player_id
        position = tuple(message.data.get('position', (0, 0)))
        
        print(f"[对战客户端] 玩家移动: {player_id} -> {position}")
        self.player_moved.emit(player_id, position)
    
    def _handle_heartbeat(self, message: BattleMessage):
        """处理心跳消息"""
        # 心跳消息不需要特殊处理
        pass
    
    def _handle_melee_move(self, message: BattleMessage):
        player_id = message.player_id
        pos = tuple(message.data.get('pos', (0, 0)))
        self.opponent_melee_move.emit(player_id, pos)
    def _handle_melee_attack(self, message: BattleMessage):
        player_id = message.player_id
        pos = tuple(message.data.get('pos', (0, 0)))
        damage = message.data.get('damage', 20)
        is_crit = message.data.get('is_crit', False)
        self.opponent_melee_attack.emit(player_id, (pos, damage, is_crit))
    
    def _handle_melee_hit_feedback(self, message: BattleMessage):
        player_id = message.player_id
        pos = tuple(message.data.get('pos', (0, 0)))
        damage = message.data.get('damage', 20)
        is_crit = message.data.get('is_crit', False)
        self.melee_hit_feedback.emit(player_id, (pos, damage, is_crit))
    
    def _send_message(self, message_type: str, data: dict):
        """发送消息到服务器"""
        if not self.socket:
            return
        
        message = BattleMessage(
            type=message_type,
            player_id=self.player_id,
            data=data,
            timestamp=time.time()
        )
        
        try:
            message_data = json.dumps(asdict(message)).encode('utf-8')
            self.socket.sendto(message_data, (self.server_ip, self.server_port))
        except Exception as e:
            print(f"[对战客户端] 发送消息失败: {e}")
    
    def _send_join_message(self):
        """发送加入消息"""
        data = {
            'name': self.player_name,
            'pet_name': self.pet_name,
            'port': self.client_port
        }
        self._send_message('join', data)
    
    def _send_leave_message(self):
        """发送离开消息"""
        self._send_message('leave', {})
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                self._send_message('heartbeat', {})
                time.sleep(5)  # 每5秒发送一次心跳
            except Exception as e:
                print(f"[对战客户端] 心跳发送失败: {e}")
                break
    
    def send_attack(self, target_id: str, attack_type: str = "fireball", damage: int = 20, attack_data: dict = None):
        """发送攻击消息"""
        data = {
            'target_id': target_id,
            'attack_type': attack_type,
            'damage': damage,
            'position': (0, 0)  # 可以添加攻击位置
        }
        
        # 添加特殊效果数据
        if attack_data is not None:
            data.update(attack_data)
            
        self._send_message('attack', data)
    
    def send_move(self, position: tuple):
        """发送移动消息"""
        data = {
            'position': position
        }
        self._send_message('move', data) 

    def send_melee_move(self, pos: tuple):
        data = {'pos': pos}
        self._send_message('melee_move', data)
    def send_melee_attack(self, pos: tuple, damage: int = 20, is_crit: bool = False):
        data = {'pos': pos, 'damage': damage, 'is_crit': is_crit}
        self._send_message('melee_attack', data) 

    def send_melee_hit_feedback(self, target_id: str, pos: tuple, damage: int = 20, is_crit: bool = False):
        data = {'target_id': target_id, 'pos': pos, 'damage': damage, 'is_crit': is_crit}
        self._send_message('melee_hit_feedback', data) 