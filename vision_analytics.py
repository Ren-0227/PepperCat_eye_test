# vision_analytics.py
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import os
from collections import defaultdict

class VisionAnalytics:
    """视力数据分析系统"""
    
    def __init__(self):
        self.vision_data = []
        self.game_data = []
        self.user_profile = {}
        self.analysis_results = {}
        
        # 加载数据
        self._load_data()
    
    def _load_data(self):
        """加载视力检测和游戏数据"""
        # 加载视力检测报告
        reports_dir = "vision_reports"
        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(reports_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            data['source'] = 'vision_test'
                            data['filename'] = filename
                            self.vision_data.append(data)
                    except Exception as e:
                        print(f"加载文件 {filename} 失败: {e}")
        
        # 加载游戏历史
        game_history_file = "game_history.json"
        if os.path.exists(game_history_file):
            try:
                with open(game_history_file, 'r', encoding='utf-8') as f:
                    self.game_data = json.load(f)
            except Exception as e:
                print(f"加载游戏历史失败: {e}")
        
        # 加载用户记忆
        user_memory_file = "user_memory.json"
        if os.path.exists(user_memory_file):
            try:
                with open(user_memory_file, 'r', encoding='utf-8') as f:
                    self.user_profile = json.load(f)
            except Exception as e:
                print(f"加载用户记忆失败: {e}")
    
    def analyze_vision_trends(self) -> Dict:
        """分析视力变化趋势"""
        if not self.vision_data:
            return {"error": "没有视力检测数据"}
        
        # 按时间排序
        sorted_data = sorted(self.vision_data, key=lambda x: x.get('test_timestamp', ''))
        
        # 提取基础视力数据
        vision_scores = []
        timestamps = []
        
        for data in sorted_data:
            if 'basic_vision' in data and 'estimated_vision' in data['basic_vision']:
                vision_scores.append(data['basic_vision']['estimated_vision'])
                timestamps.append(data['test_timestamp'])
        
        if not vision_scores:
            return {"error": "没有有效的视力数据"}
        
        # 计算趋势
        trend_analysis = self._calculate_trend(vision_scores, timestamps)
        
        # 分析变化模式
        pattern_analysis = self._analyze_patterns(vision_scores)
        
        return {
            'trend': trend_analysis,
            'patterns': pattern_analysis,
            'current_vision': vision_scores[-1] if vision_scores else None,
            'best_vision': max(vision_scores) if vision_scores else None,
            'worst_vision': min(vision_scores) if vision_scores else None,
            'improvement': self._calculate_improvement(vision_scores)
        }
    
    def analyze_game_performance(self) -> Dict:
        """分析游戏表现"""
        if not self.game_data:
            return {"error": "没有游戏数据"}
        
        # 按游戏类型分组
        game_performance = defaultdict(list)
        for game in self.game_data:
            game_type = game['game_type']
            game_performance[game_type].append(game)
        
        analysis = {}
        for game_type, games in game_performance.items():
            scores = [g['score'] for g in games]
            accuracies = [g['accuracy'] for g in games]
            reaction_times = [g.get('avg_reaction_time', 0) for g in games if g.get('avg_reaction_time', 0) > 0]
            
            analysis[game_type] = {
                'total_games': len(games),
                'avg_score': np.mean(scores),
                'best_score': max(scores),
                'avg_accuracy': np.mean(accuracies),
                'avg_reaction_time': np.mean(reaction_times) if reaction_times else 0,
                'improvement_trend': self._calculate_improvement(scores),
                'recent_performance': self._analyze_recent_performance(games)
            }
        
        return analysis
    
    def generate_personalized_insights(self) -> Dict:
        """生成个性化洞察"""
        insights = {
            'vision_health': self._analyze_vision_health(),
            'training_recommendations': self._generate_training_recommendations(),
            'risk_assessment': self._assess_vision_risks(),
            'improvement_goals': self._set_improvement_goals()
        }
        
        return insights
    
    def create_vision_report(self) -> Dict:
        """创建综合视力报告"""
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vision_trends': self.analyze_vision_trends(),
            'game_performance': self.analyze_game_performance(),
            'personalized_insights': self.generate_personalized_insights(),
            'recommendations': self._generate_comprehensive_recommendations()
        }
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _calculate_trend(self, values: List[float], timestamps: List[str]) -> Dict:
        """计算趋势"""
        if len(values) < 2:
            return {"trend": "stable", "slope": 0, "confidence": 0}
        
        # 计算线性回归
        x = np.arange(len(values))
        y = np.array(values)
        
        # 线性回归
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        # 计算R²
        y_pred = np.polyval(coeffs, x)
        r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
        
        # 判断趋势
        if slope > 0.1 and r_squared > 0.3:
            trend = "improving"
        elif slope < -0.1 and r_squared > 0.3:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": slope,
            "confidence": r_squared,
            "change_rate": slope * len(values)  # 总体变化率
        }
    
    def _analyze_patterns(self, values: List[float]) -> Dict:
        """分析数据模式"""
        if len(values) < 3:
            return {"pattern": "insufficient_data"}
        
        # 计算变化率
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        
        # 分析波动性
        volatility = np.std(changes)
        
        # 分析周期性
        if len(values) >= 7:
            # 简单的周期性检测
            weekly_avg = np.mean(values[-7:]) if len(values) >= 7 else np.mean(values)
            overall_avg = np.mean(values)
            weekly_trend = weekly_avg - overall_avg
        else:
            weekly_trend = 0
        
        return {
            "volatility": volatility,
            "weekly_trend": weekly_trend,
            "consistency": 1 - volatility / np.mean(values) if np.mean(values) > 0 else 0,
            "pattern": self._identify_pattern(changes)
        }
    
    def _identify_pattern(self, changes: List[float]) -> str:
        """识别变化模式"""
        if not changes:
            return "no_pattern"
        
        positive_changes = sum(1 for c in changes if c > 0)
        negative_changes = sum(1 for c in changes if c < 0)
        total_changes = len(changes)
        
        if positive_changes / total_changes > 0.7:
            return "consistently_improving"
        elif negative_changes / total_changes > 0.7:
            return "consistently_declining"
        elif abs(positive_changes - negative_changes) / total_changes < 0.3:
            return "fluctuating"
        else:
            return "mixed"
    
    def _calculate_improvement(self, values: List[float]) -> Dict:
        """计算改进情况"""
        if len(values) < 2:
            return {"improvement_rate": 0, "status": "insufficient_data"}
        
        initial = values[0]
        current = values[-1]
        improvement_rate = (current - initial) / initial if initial != 0 else 0
        
        if improvement_rate > 0.05:
            status = "improving"
        elif improvement_rate < -0.05:
            status = "declining"
        else:
            status = "stable"
        
        return {
            "improvement_rate": improvement_rate,
            "status": status,
            "total_change": current - initial
        }
    
    def _analyze_recent_performance(self, games: List[Dict]) -> Dict:
        """分析最近表现"""
        if len(games) < 3:
            return {"trend": "insufficient_data"}
        
        recent_games = games[-3:]
        older_games = games[:-3] if len(games) > 3 else games
        
        recent_avg = np.mean([g['score'] for g in recent_games])
        older_avg = np.mean([g['score'] for g in older_games])
        
        improvement = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        
        return {
            "recent_avg_score": recent_avg,
            "improvement_vs_older": improvement,
            "trend": "improving" if improvement > 0.1 else "declining" if improvement < -0.1 else "stable"
        }
    
    def _analyze_vision_health(self) -> Dict:
        """分析视力健康状况"""
        vision_trends = self.analyze_vision_trends()
        
        if 'error' in vision_trends:
            return {"status": "no_data", "message": "没有视力数据"}
        
        current_vision = vision_trends.get('current_vision', 5.0)
        trend = vision_trends.get('trend', {}).get('trend', 'stable')
        
        # 视力健康评估
        if current_vision >= 4.8:
            health_status = "excellent"
        elif current_vision >= 4.5:
            health_status = "good"
        elif current_vision >= 4.0:
            health_status = "fair"
        else:
            health_status = "poor"
        
        # 趋势评估
        if trend == "improving":
            trend_status = "positive"
        elif trend == "declining":
            trend_status = "concerning"
        else:
            trend_status = "stable"
        
        return {
            "current_status": health_status,
            "trend_status": trend_status,
            "overall_health": "good" if health_status in ["excellent", "good"] and trend_status != "concerning" else "needs_attention"
        }
    
    def _generate_training_recommendations(self) -> List[str]:
        """生成训练建议"""
        recommendations = []
        
        # 基于视力趋势的建议
        vision_trends = self.analyze_vision_trends()
        if 'error' not in vision_trends:
            trend = vision_trends.get('trend', {}).get('trend', 'stable')
            if trend == "declining":
                recommendations.append("建议增加视力训练频率，每天进行15-20分钟的视力训练")
                recommendations.append("建议减少用眼时间，每30分钟休息5分钟")
            elif trend == "improving":
                recommendations.append("继续保持当前的训练习惯，视力正在改善")
        
        # 基于游戏表现的建议
        game_performance = self.analyze_game_performance()
        if 'error' not in game_performance:
            for game_type, performance in game_performance.items():
                if performance.get('avg_accuracy', 0) < 0.7:
                    recommendations.append(f"建议多练习{game_type}游戏以提高准确率")
                if performance.get('avg_reaction_time', 0) > 1.0:
                    recommendations.append(f"建议通过{game_type}游戏训练反应速度")
        
        # 通用建议
        recommendations.append("建议定期进行视力检查，至少每3个月一次")
        recommendations.append("保持良好的用眼习惯，避免长时间连续用眼")
        
        return recommendations
    
    def _assess_vision_risks(self) -> Dict:
        """评估视力风险"""
        risks = []
        risk_level = "low"
        
        vision_trends = self.analyze_vision_trends()
        if 'error' not in vision_trends:
            current_vision = vision_trends.get('current_vision', 5.0)
            trend = vision_trends.get('trend', {}).get('trend', 'stable')
            
            if current_vision < 4.0:
                risks.append("视力水平较低，建议及时就医")
                risk_level = "high"
            elif current_vision < 4.5:
                risks.append("视力需要关注，建议增加训练")
                risk_level = "medium"
            
            if trend == "declining":
                risks.append("视力呈下降趋势，需要重点关注")
                risk_level = "high" if risk_level == "high" else "medium"
        
        # 基于游戏表现的风险评估
        game_performance = self.analyze_game_performance()
        if 'error' not in game_performance:
            for game_type, performance in game_performance.items():
                if performance.get('avg_accuracy', 0) < 0.5:
                    risks.append(f"{game_type}游戏表现较差，可能存在视觉处理问题")
                    risk_level = "medium" if risk_level == "low" else risk_level
        
        return {
            "risk_level": risk_level,
            "risks": risks,
            "recommendations": self._generate_risk_recommendations(risk_level, risks)
        }
    
    def _generate_risk_recommendations(self, risk_level: str, risks: List[str]) -> List[str]:
        """生成风险应对建议"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.append("建议尽快进行专业眼科检查")
            recommendations.append("建议减少用眼时间，增加户外活动")
            recommendations.append("建议使用护眼产品，如防蓝光眼镜")
        elif risk_level == "medium":
            recommendations.append("建议增加视力训练频率")
            recommendations.append("建议定期进行视力检查")
            recommendations.append("建议改善用眼环境，如调整屏幕亮度")
        else:
            recommendations.append("继续保持良好的用眼习惯")
            recommendations.append("建议定期进行视力检查以预防问题")
        
        return recommendations
    
    def _set_improvement_goals(self) -> Dict:
        """设定改进目标"""
        vision_trends = self.analyze_vision_trends()
        
        if 'error' in vision_trends:
            return {"goals": [], "timeline": "no_data"}
        
        current_vision = vision_trends.get('current_vision', 5.0)
        goals = []
        
        # 短期目标（1个月）
        if current_vision < 4.8:
            short_term_goal = min(current_vision + 0.2, 5.0)
            goals.append({
                "type": "short_term",
                "target": short_term_goal,
                "timeline": "1个月",
                "description": f"将视力提升到{short_term_goal:.1f}"
            })
        
        # 中期目标（3个月）
        if current_vision < 5.0:
            medium_term_goal = min(current_vision + 0.3, 5.0)
            goals.append({
                "type": "medium_term",
                "target": medium_term_goal,
                "timeline": "3个月",
                "description": f"将视力提升到{medium_term_goal:.1f}"
            })
        
        # 长期目标（6个月）
        if current_vision < 5.0:
            long_term_goal = 5.0
            goals.append({
                "type": "long_term",
                "target": long_term_goal,
                "timeline": "6个月",
                "description": f"达到最佳视力{long_term_goal:.1f}"
            })
        
        return {
            "goals": goals,
            "current_vision": current_vision,
            "motivation": self._generate_motivation_message(current_vision)
        }
    
    def _generate_motivation_message(self, current_vision: float) -> str:
        """生成激励信息"""
        if current_vision >= 4.8:
            return "您的视力已经很好了！继续保持良好的用眼习惯。"
        elif current_vision >= 4.5:
            return "您的视力不错，通过训练还有提升空间！"
        elif current_vision >= 4.0:
            return "您的视力需要关注，但通过努力训练一定能够改善！"
        else:
            return "不要担心，通过专业的训练和指导，视力是可以改善的！"
    
    def _generate_comprehensive_recommendations(self) -> Dict:
        """生成综合建议"""
        vision_health = self._analyze_vision_health()
        risk_assessment = self._assess_vision_risks()
        training_recs = self._generate_training_recommendations()
        
        return {
            "immediate_actions": self._get_immediate_actions(vision_health, risk_assessment),
            "long_term_plan": self._create_long_term_plan(vision_health, risk_assessment),
            "training_schedule": self._create_training_schedule(),
            "monitoring_plan": self._create_monitoring_plan()
        }
    
    def _get_immediate_actions(self, vision_health: Dict, risk_assessment: Dict) -> List[str]:
        """获取立即行动建议"""
        actions = []
        
        if risk_assessment.get('risk_level') == 'high':
            actions.append("立即预约眼科医生进行专业检查")
            actions.append("减少用眼时间，增加休息频率")
        
        if vision_health.get('trend_status') == 'concerning':
            actions.append("增加视力训练频率")
            actions.append("改善用眼环境")
        
        actions.append("开始记录每日用眼时间和视力训练情况")
        actions.append("设置定时提醒，每30分钟休息5分钟")
        
        return actions
    
    def _create_long_term_plan(self, vision_health: Dict, risk_assessment: Dict) -> Dict:
        """创建长期计划"""
        plan = {
            "month_1": ["建立规律的视力训练习惯", "改善用眼环境", "开始记录视力变化"],
            "month_3": ["评估训练效果", "调整训练计划", "考虑专业指导"],
            "month_6": ["全面视力评估", "制定新的训练目标", "建立长期维护计划"]
        }
        
        if risk_assessment.get('risk_level') == 'high':
            plan["month_1"].append("定期进行专业眼科检查")
        
        return plan
    
    def _create_training_schedule(self) -> Dict:
        """创建训练计划"""
        return {
            "daily_training": {
                "duration": "15-20分钟",
                "activities": ["视力训练游戏", "眼动追踪练习", "专注力训练"],
                "frequency": "每天1-2次"
            },
            "weekly_assessment": {
                "vision_test": "每周进行一次视力检测",
                "game_performance": "每周评估游戏表现",
                "progress_tracking": "记录训练进度和改善情况"
            },
            "monthly_review": {
                "comprehensive_analysis": "每月进行综合视力分析",
                "plan_adjustment": "根据分析结果调整训练计划",
                "goal_review": "回顾和更新改进目标"
            }
        }
    
    def _create_monitoring_plan(self) -> Dict:
        """创建监测计划"""
        return {
            "daily_monitoring": ["记录用眼时间", "记录视力训练情况", "记录眼疲劳程度"],
            "weekly_monitoring": ["进行视力检测", "评估游戏表现", "分析训练效果"],
            "monthly_monitoring": ["综合视力分析", "生成详细报告", "调整训练策略"],
            "alert_conditions": [
                "视力下降超过0.2",
                "连续3次游戏表现下降",
                "出现眼疲劳症状"
            ]
        }
    
    def _save_report(self, report: Dict):
        """保存分析报告"""
        reports_dir = "analytics_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{reports_dir}/vision_analytics_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"分析报告已保存至: {filename}")
    
    def plot_vision_trends(self, save_path: str = None):
        """绘制视力趋势图"""
        if not self.vision_data:
            print("没有视力数据可供绘图")
            return
        
        # 提取数据
        timestamps = []
        vision_scores = []
        
        for data in sorted(self.vision_data, key=lambda x: x.get('test_timestamp', '')):
            if 'basic_vision' in data and 'estimated_vision' in data['basic_vision']:
                timestamps.append(data['test_timestamp'])
                vision_scores.append(data['basic_vision']['estimated_vision'])
        
        if not vision_scores:
            print("没有有效的视力数据")
            return
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        
        # 主趋势图
        plt.subplot(2, 2, 1)
        plt.plot(range(len(vision_scores)), vision_scores, 'b-o', linewidth=2, markersize=6)
        plt.title('视力变化趋势', fontsize=14, fontweight='bold')
        plt.xlabel('检测次数')
        plt.ylabel('视力水平')
        plt.grid(True, alpha=0.3)
        
        # 分布图
        plt.subplot(2, 2, 2)
        plt.hist(vision_scores, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('视力分布', fontsize=14, fontweight='bold')
        plt.xlabel('视力水平')
        plt.ylabel('频次')
        
        # 变化率图
        plt.subplot(2, 2, 3)
        changes = [vision_scores[i] - vision_scores[i-1] for i in range(1, len(vision_scores))]
        plt.bar(range(len(changes)), changes, alpha=0.7, color='lightcoral')
        plt.title('视力变化率', fontsize=14, fontweight='bold')
        plt.xlabel('检测间隔')
        plt.ylabel('变化量')
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # 统计信息
        plt.subplot(2, 2, 4)
        stats_text = f"""
        统计信息:
        平均视力: {np.mean(vision_scores):.2f}
        最高视力: {max(vision_scores):.2f}
        最低视力: {min(vision_scores):.2f}
        标准差: {np.std(vision_scores):.2f}
        检测次数: {len(vision_scores)}
        """
        plt.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
        plt.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        else:
            plt.show()

# 使用示例
if __name__ == "__main__":
    analytics = VisionAnalytics()
    
    # 生成综合报告
    report = analytics.create_vision_report()
    
    print("=== 视力数据分析报告 ===")
    print(f"报告生成时间: {report['report_date']}")
    
    # 显示视力趋势
    vision_trends = report['vision_trends']
    if 'error' not in vision_trends:
        print(f"\n视力趋势: {vision_trends['trend']['trend']}")
        print(f"当前视力: {vision_trends['current_vision']:.2f}")
        print(f"改进情况: {vision_trends['improvement']['status']}")
    
    # 显示个性化洞察
    insights = report['personalized_insights']
    print(f"\n视力健康状况: {insights['vision_health']['overall_health']}")
    print(f"风险等级: {insights['risk_assessment']['risk_level']}")
    
    # 显示建议
    print("\n训练建议:")
    for rec in insights['training_recommendations']:
        print(f"- {rec}")
    
    # 绘制趋势图
    analytics.plot_vision_trends("vision_trends.png") 