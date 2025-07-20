#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
眼部健康大模型Web应用
提供现代化的前端界面，整合所有眼部健康功能
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入眼部健康模块
try:
    from eye_health_agent_integrated import EyeHealthSystem
    from openmanus_core.logger import logger
    from vision_test import VisionTester
    from advanced_vision_test import AdvancedVisionTest
    from vision_training_game import VisionTrainingGame, GameType
    from vision_analytics import VisionAnalytics
    from api_integration import DeepseekAPI
    from image_processing import analyze_image
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖已正确安装")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'eye_health_secret_key_2024'
CORS(app)

# 全局系统实例
eye_health_system = None
chat_history = []

class WebEyeHealthSystem:
    """Web版本的眼部健康系统"""
    
    def __init__(self):
        self.system = None
        self.is_initialized = False
        self.stats = {
            'total_tests': 0,
            'total_games': 0,
            'avg_score': 0.0,
            'consultations': 0,
            'last_activity': None
        }
    
    async def initialize(self):
        """初始化系统"""
        try:
            if not self.is_initialized:
                self.system = EyeHealthSystem()
                await self.system.initialize()
                self.is_initialized = True
                logger.info("Web系统初始化完成")
        except Exception as e:
            logger.error(f"Web系统初始化失败: {e}")
            raise
    
    async def process_request(self, user_message: str) -> Dict[str, Any]:
        """处理用户请求"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 分析请求类型
            request_type = self._analyze_request_type(user_message)
            
            # 更新统计信息
            self._update_stats(request_type)
            
            # 处理请求
            if request_type == "vision_test":
                return await self._handle_vision_test(user_message)
            elif request_type == "training":
                return await self._handle_training(user_message)
            elif request_type == "consultation":
                return await self._handle_consultation(user_message)
            elif request_type == "analysis":
                return await self._handle_analysis(user_message)
            else:
                # 使用智能代理处理
                result = await self.system.process_request(user_message)
                return {
                    "type": "general",
                    "response": result.get("result", "处理完成"),
                    "status": "success"
                }
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "type": "error",
                "response": f"处理请求时出错: {str(e)}",
                "status": "error"
            }
    
    def _analyze_request_type(self, message: str) -> str:
        """分析请求类型"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['视力检测', 'vision test', '检测视力', '视力测试']):
            return "vision_test"
        elif any(word in message_lower for word in ['训练', 'training', '游戏', 'game', '眼动', '专注']):
            return "training"
        elif any(word in message_lower for word in ['咨询', '症状', 'consultation', 'symptom', '建议']):
            return "consultation"
        elif any(word in message_lower for word in ['分析', '报告', 'analysis', 'report', '趋势']):
            return "analysis"
        else:
            return "general"
    
    def _update_stats(self, request_type: str):
        """更新统计信息"""
        self.stats['last_activity'] = datetime.now().isoformat()
        
        if request_type == "vision_test":
            self.stats['total_tests'] += 1
        elif request_type == "training":
            self.stats['total_games'] += 1
        elif request_type == "consultation":
            self.stats['consultations'] += 1
        
        # 更新平均分数（模拟）
        if self.stats['total_tests'] > 0:
            self.stats['avg_score'] = round(4.2 + (self.stats['total_tests'] % 10) * 0.1, 1)
    
    async def _handle_vision_test(self, message: str) -> Dict[str, Any]:
        """处理视力检测请求"""
        try:
            if "高级" in message or "综合" in message:
                tester = AdvancedVisionTest()
                report = tester.start_comprehensive_test()
                return {
                    "type": "vision_test",
                    "response": f"高级视力检测报告：{report}",
                    "status": "success"
                }
            else:
                tester = VisionTester()
                result = tester.run_test()
                return {
                    "type": "vision_test",
                    "response": f"基础视力检测结果：{result}",
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"视力检测出错: {e}")
            return {
                "type": "vision_test",
                "response": f"视力检测出错: {str(e)}",
                "status": "error"
            }
    
    async def _handle_training(self, message: str) -> Dict[str, Any]:
        """处理训练请求"""
        if "眼动" in message:
            return {
                "type": "training",
                "response": "即将进入眼动追踪小游戏，请点击下方按钮开始。",
                "action": "redirect",
                "url": "/eye_tracking_game",
                "status": "success"
            }
        elif "专注" in message:
            return {
                "type": "training",
                "response": "即将进入专注力训练小游戏，请点击下方按钮开始。",
                "action": "redirect",
                "url": "/focus_game",
                "status": "success"
            }
        elif "反应" in message:
            return {
                "type": "training",
                "response": "即将进入反应速度训练小游戏，请点击下方按钮开始。",
                "action": "redirect",
                "url": "/reaction_game",
                "status": "success"
            }
        elif "记忆" in message:
            return {
                "type": "training",
                "response": "即将进入记忆训练小游戏，请点击下方按钮开始。",
                "action": "redirect",
                "url": "/memory_game",
                "status": "success"
            }
        elif "颜色" in message:
            return {
                "type": "training",
                "response": "即将进入颜色匹配训练小游戏，请点击下方按钮开始。",
                "action": "redirect",
                "url": "/color_matching_game",
                "status": "success"
            }
        else:
            return {
                "type": "training",
                "response": "请选择具体的训练类型。",
                "status": "error"
            }
    
    async def _handle_analysis(self, message: str) -> Dict[str, Any]:
        """处理数据分析请求"""
        try:
            analytics = VisionAnalytics()
            if "趋势" in message:
                report = analytics.analyze_vision_trends()
                return {
                    "type": "analysis",
                    "response": f"视力趋势分析：{report}",
                    "status": "success"
                }
            elif "表现" in message:
                report = analytics.analyze_game_performance()
                return {
                    "type": "analysis",
                    "response": f"训练表现分析：{report}",
                    "status": "success"
                }
            elif "洞察" in message:
                report = analytics.generate_personalized_insights()
                return {
                    "type": "analysis",
                    "response": f"个性化洞察：{report}",
                    "status": "success"
                }
            else:
                report = analytics.create_vision_report()
                return {
                    "type": "analysis",
                    "response": f"综合分析报告：{report}",
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"数据分析出错: {e}")
            return {
                "type": "analysis",
                "response": f"数据分析出错: {str(e)}",
                "status": "error"
            }
    
    async def _handle_consultation(self, message: str) -> Dict[str, Any]:
        """处理健康咨询请求"""
        try:
            api = DeepseekAPI()
            advice = api.get_health_advice(message)
            return {
                "type": "consultation",
                "response": f"健康建议：{advice}",
                "status": "success"
            }
        except Exception as e:
            logger.error(f"健康咨询出错: {e}")
            return {
                "type": "consultation",
                "response": f"健康咨询出错: {str(e)}",
                "status": "error"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()

# 创建全局系统实例
web_system = WebEyeHealthSystem()

@app.route('/')
def index():
    """主页"""
    return render_template('eye_health_dashboard.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            })
        
        # 添加到聊天历史
        chat_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # 异步处理请求
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(web_system.process_request(user_message))
        finally:
            loop.close()
        
        # 添加AI响应到聊天历史
        chat_history.append({
            'role': 'assistant',
            'content': result.get('response', '处理完成'),
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'response': result.get('response', '处理完成'),
            'type': result.get('type', 'general'),
            'status': result.get('status', 'success')
        })
        
    except Exception as e:
        logger.error(f"聊天API错误: {e}")
        return jsonify({
            'success': False,
            'error': f'处理请求时出错: {str(e)}'
        })

@app.route('/api/stats')
def get_stats():
    """获取统计信息API"""
    try:
        stats = web_system.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"获取统计信息错误: {e}")
        return jsonify({
            'success': False,
            'error': f'获取统计信息失败: {str(e)}'
        })

@app.route('/api/chat/history')
def get_chat_history():
    """获取聊天历史API"""
    try:
        return jsonify({
            'success': True,
            'history': chat_history
        })
    except Exception as e:
        logger.error(f"获取聊天历史错误: {e}")
        return jsonify({
            'success': False,
            'error': f'获取聊天历史失败: {str(e)}'
        })

@app.route('/api/system/status')
def system_status():
    """系统状态API"""
    try:
        return jsonify({
            'success': True,
            'status': 'running',
            'initialized': web_system.is_initialized,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"系统状态检查错误: {e}")
        return jsonify({
            'success': False,
            'error': f'系统状态检查失败: {str(e)}'
        })

@app.route('/api/vision/test', methods=['POST'])
def start_vision_test():
    """启动视力检测API"""
    try:
        data = request.get_json()
        test_type = data.get('type', 'basic')  # basic 或 advanced
        
        # 这里可以启动实际的视力检测
        response = f"正在启动{test_type}视力检测..."
        
        return jsonify({
            'success': True,
            'message': response,
            'test_type': test_type
        })
    except Exception as e:
        logger.error(f"启动视力检测错误: {e}")
        return jsonify({
            'success': False,
            'error': f'启动视力检测失败: {str(e)}'
        })

@app.route('/api/training/start', methods=['POST'])
def start_training():
    """启动训练游戏API"""
    try:
        data = request.get_json()
        game_type = data.get('type', 'comprehensive')
        
        # 这里可以启动实际的训练游戏
        response = f"正在启动{game_type}训练游戏..."
        
        return jsonify({
            'success': True,
            'message': response,
            'game_type': game_type
        })
    except Exception as e:
        logger.error(f"启动训练游戏错误: {e}")
        return jsonify({
            'success': False,
            'error': f'启动训练游戏失败: {str(e)}'
        })

@app.route('/api/health')
def health_check():
    """健康检查API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/image/recognition', methods=['POST'])
def image_recognition():
    """眼部图片识别API，集成AI健康报告"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '未收到图片文件'}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': '未选择图片'}), 400
        # 保存临时文件
        save_dir = 'uploads'
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file.filename)
        file.save(file_path)
        # 调用图片分析
        try:
            result = analyze_image(file_path)
            # 调用大模型生成健康报告
            deepseek = DeepseekAPI()
            report = deepseek.get_health_advice(f'图片识别结果: {result}')
            return jsonify({'success': True, 'result': result, 'report': report})
        except Exception as e:
            return jsonify({'success': False, 'error': f'图片分析失败: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'})

@app.route('/eye_tracking_game')
def eye_tracking_game():
    return render_template('eye_health_eye_tracking.html')

@app.route('/focus_game')
def focus_game():
    return render_template('eye_health_focus_game.html')

@app.route('/focus_training_game')
def focus_training_game():
    """专注力训练游戏页面"""
    return render_template('focus_training_game.html')

@app.route('/reaction_game')
def reaction_game():
    return render_template('eye_health_reaction_game.html')

@app.route('/reaction_training_game')
def reaction_training_game():
    """反应速度训练游戏页面"""
    return render_template('reaction_training_game.html')

@app.route('/memory_game')
def memory_game():
    """记忆游戏页面"""
    return render_template('memory_game.html')

def main():
    """主函数"""
    print("=== 眼部健康大模型Web应用 ===")
    print("正在启动Web服务器...")
    
    try:
        # 初始化系统
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(web_system.initialize())
        loop.close()
        
        print("✅ 系统初始化完成")
        print("🌐 启动Web服务器...")
        print("📱 访问地址: http://localhost:5000")
        print("🔧 API文档: http://localhost:5000/api/health")
        
        # 启动Flask应用
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 