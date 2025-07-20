#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对战服务器模块
处理局域网内的玩家连接和消息广播
"""

import socket
import threading
import json
import time
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from PyQt6.QtCore import QObject, pyqtSignal

@dataclass
class Player:
    """玩家信息"""
    id: str
    name: str
    ip: str
    port: int
    pet_name: str
    health: int = 100
    position: tuple = (0, 0)
    last_seen: float = 0

@dataclass
class BattleMessage:
    """对战消息"""
    type: str  # 'attack', 'move', 'join', 'leave', 'heartbeat'
    player_id: str
    data: dict
    timestamp: float

class BattleServer(QObject):
    """对战服务器"""
    
    # 信号
    player_joined = pyqtSignal(str, str)  # player_id, player_name
    player_left = pyqtSignal(str)
    attack_received = pyqtSignal(str, str, dict)  # attacker_id, target_id, attack_data
    player_moved = pyqtSignal(str, tuple)  # player_id, position
    
    def __init__(self, port=8888):
        super().__init__()
        self.port = port
        self.host = '0.0.0.0'
        self.players: Dict[str, Player] = {}
        self.server_socket = None
        self.running = False
        self.server_thread = None
        
    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.host, self.port))
            self.running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            print(f"[对战服务器] 启动成功，监听端口 {self.port}")
            return True
        except Exception as e:
            print(f"[对战服务器] 启动失败: {e}")
            return False
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("[对战服务器] 已停止")
    
    def _server_loop(self):
        """服务器主循环"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                data, addr = self.server_socket.recvfrom(1024)
                self._handle_message(data, addr)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[对战服务器] 接收消息错误: {e}")
        
        # 清理超时的玩家
        self._cleanup_timeout_players()
    
    def _handle_message(self, data: bytes, addr: tuple):
        """处理接收到的消息"""
        try:
            message_data = json.loads(data.decode('utf-8'))
            message = BattleMessage(**message_data)
            
            if message.type == 'join':
                self._handle_player_join(message, addr)
            elif message.type == 'leave':
                self._handle_player_leave(message)
            elif message.type == 'attack':
                self._handle_attack(message)
            elif message.type == 'move':
                self._handle_player_move(message)
            elif message.type == 'heartbeat':
                self._handle_heartbeat(message)
                
        except Exception as e:
            print(f"[对战服务器] 处理消息错误: {e}")
    
    def _handle_player_join(self, message: BattleMessage, addr: tuple):
        """处理玩家加入"""
        player = Player(
            id=message.player_id,
            name=message.data.get('name', '未知玩家'),
            ip=addr[0],
            port=message.data.get('port', 8889),
            pet_name=message.data.get('pet_name', '小宠物'),
            last_seen=time.time()
        )
        self.players[player.id] = player
        print(f"[对战服务器] 玩家加入: {player.name} ({player.id})")
        self.player_joined.emit(player.id, player.name)
        
        # 广播新玩家加入消息
        self._broadcast_message(message)
    
    def _handle_player_leave(self, message: BattleMessage):
        """处理玩家离开"""
        player_id = message.player_id
        if player_id in self.players:
            player_name = self.players[player_id].name
            del self.players[player_id]
            print(f"[对战服务器] 玩家离开: {player_name} ({player_id})")
            self.player_left.emit(player_id)
            
            # 广播玩家离开消息
            self._broadcast_message(message)
    
    def _handle_attack(self, message: BattleMessage):
        """处理攻击消息"""
        attacker_id = message.player_id
        target_id = message.data.get('target_id')
        
        if attacker_id in self.players and target_id in self.players:
            print(f"[对战服务器] 攻击: {self.players[attacker_id].name} -> {self.players[target_id].name}")
            self.attack_received.emit(attacker_id, target_id, message.data)
            
            # 广播攻击消息
            self._broadcast_message(message)
    
    def _handle_player_move(self, message: BattleMessage):
        """处理玩家移动"""
        player_id = message.player_id
        position = tuple(message.data.get('position', (0, 0)))
        
        if player_id in self.players:
            self.players[player_id].position = position
            self.players[player_id].last_seen = time.time()
            self.player_moved.emit(player_id, position)
            
            # 广播移动消息
            self._broadcast_message(message)
    
    def _handle_heartbeat(self, message: BattleMessage):
        """处理心跳消息"""
        player_id = message.player_id
        if player_id in self.players:
            self.players[player_id].last_seen = time.time()
    
    def _broadcast_message(self, message: BattleMessage):
        """广播消息给所有玩家"""
        message_data = json.dumps(asdict(message)).encode('utf-8')
        for player in self.players.values():
            try:
                self.server_socket.sendto(message_data, (player.ip, player.port))
            except Exception as e:
                print(f"[对战服务器] 广播消息失败: {e}")
    
    def _cleanup_timeout_players(self):
        """清理超时的玩家"""
        current_time = time.time()
        timeout_players = []
        
        for player_id, player in self.players.items():
            if current_time - player.last_seen > 10.0:  # 10秒超时
                timeout_players.append(player_id)
        
        for player_id in timeout_players:
            player_name = self.players[player_id].name
            del self.players[player_id]
            print(f"[对战服务器] 玩家超时离开: {player_name} ({player_id})")
            self.player_left.emit(player_id)
    
    def get_players(self) -> List[Player]:
        """获取所有在线玩家"""
        return list(self.players.values())
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """获取指定玩家"""
        return self.players.get(player_id) 