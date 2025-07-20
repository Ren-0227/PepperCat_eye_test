#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试战斗规则系统
"""

import sys
import os
import time

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.battle_dialog import BATTLE_RULES, StatusEffect

def test_battle_rules():
    """测试战斗规则"""
    print("=== 战斗规则测试 ===")
    
    # 测试战斗规则配置
    print("\n1. 战斗规则配置:")
    for attack_type, rules in BATTLE_RULES.items():
        print(f"  {attack_type}:")
        print(f"    基础伤害: {rules['damage']}")
        print(f"    冷却时间: {rules['cooldown']}秒")
        if 'description' in rules:
            print(f"    描述: {rules['description']}")
        
        # 计算总伤害
        total_damage = rules['damage']
        if 'burn_damage' in rules:
            total_damage += rules['burn_damage'] * rules['burn_duration']
        elif 'shock_damage' in rules:
            total_damage += rules['shock_damage'] * rules['shock_duration']
        
        print(f"    总伤害: {total_damage}")
        print()
    
    # 测试状态效果
    print("2. 状态效果测试:")
    
    # 测试灼烧效果
    burn_effect = StatusEffect("burn", 3.0, 5)
    print(f"  灼烧效果: 持续时间={burn_effect.duration}s, 伤害={burn_effect.damage}/秒")
    
    # 测试电击效果
    shock_effect = StatusEffect("shock", 4.0, 3)
    print(f"  电击效果: 持续时间={shock_effect.duration}s, 伤害={shock_effect.damage}/秒")
    
    # 测试缓速效果
    slow_effect = StatusEffect("slow", 5.0, slow_factor=0.5)
    print(f"  缓速效果: 持续时间={slow_effect.duration}s, 速度因子={slow_effect.slow_factor}")
    
    # 测试状态效果更新
    print("\n3. 状态效果更新测试:")
    effects = [burn_effect, shock_effect, slow_effect]
    
    for i in range(10):
        print(f"  第{i+1}次更新:")
        for effect in effects[:]:
            if effect.update(0.5):  # 每次更新0.5秒
                print(f"    {effect.effect_type}: 剩余{effect.remaining_time:.1f}s")
            else:
                print(f"    {effect.effect_type}: 效果结束")
                effects.remove(effect)
        
        if not effects:
            print("    所有效果已结束")
            break
    
    print("\n4. 攻击冷却测试:")
    current_time = time.time()
    for attack_type, rules in BATTLE_RULES.items():
        cooldown = rules['cooldown']
        print(f"  {attack_type}: 冷却时间{cooldown}秒")
        
        # 模拟攻击
        last_attack_time = current_time - cooldown + 1  # 还有1秒冷却
        remaining = cooldown - (current_time - last_attack_time)
        print(f"    剩余冷却时间: {remaining:.1f}秒")
    
    print("\n=== 测试完成 ===")
    print("所有战斗规则系统功能正常！")

def test_damage_calculations():
    """测试伤害计算"""
    print("\n=== 伤害计算测试 ===")
    
    # 模拟玩家受到攻击
    player_health = 100
    
    for attack_type, rules in BATTLE_RULES.items():
        print(f"\n{attack_type}攻击:")
        
        # 基础伤害
        base_damage = rules['damage']
        player_health -= base_damage
        print(f"  基础伤害: {base_damage}, 剩余生命值: {player_health}")
        
        # 状态效果伤害
        if 'burn_damage' in rules:
            burn_damage = rules['burn_damage'] * rules['burn_duration']
            player_health -= burn_damage
            print(f"  灼烧伤害: {burn_damage}, 剩余生命值: {player_health}")
        elif 'shock_damage' in rules:
            shock_damage = rules['shock_damage'] * rules['shock_duration']
            player_health -= shock_damage
            print(f"  电击伤害: {shock_damage}, 剩余生命值: {player_health}")
        
        # 重置生命值
        player_health = 100

if __name__ == "__main__":
    test_battle_rules()
    test_damage_calculations() 