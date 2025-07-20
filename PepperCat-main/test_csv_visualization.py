#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV分析和可视化功能测试脚本
测试CSV文件读取、分析和图表生成功能
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from datetime import datetime
import io
import base64

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class CSVVisualizationTester:
    """CSV分析和可视化测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.passed_tests = 0
        self.total_tests = 0
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "status": status,
            "message": message,
            "success": success
        }
        self.test_results[test_name] = result
        
        print(f"{status} {test_name}: {message}")
    
    def test_csv_reading(self):
        """测试CSV文件读取"""
        print("\n=== 测试CSV文件读取 ===")
        
        try:
            # 测试读取视力数据CSV
            df = pd.read_csv("../eyes_test.csv")
            self.log_test("CSV文件读取", True, f"成功读取{len(df)}行数据")
            
            # 检查数据结构
            columns = df.columns.tolist()
            expected_columns = ['date', 'left_eye_vision', 'right_eye_vision', 'eye_pressure', 'eye_fatigue', 'test_duration', 'accuracy']
            
            if all(col in columns for col in expected_columns):
                self.log_test("数据结构检查", True, f"包含所有预期列: {len(columns)}列")
            else:
                missing = [col for col in expected_columns if col not in columns]
                self.log_test("数据结构检查", False, f"缺少列: {missing}")
            
            # 检查数据类型
            numeric_columns = ['left_eye_vision', 'right_eye_vision', 'eye_pressure', 'eye_fatigue', 'test_duration', 'accuracy']
            numeric_check = all(pd.api.types.is_numeric_dtype(df[col]) for col in numeric_columns)
            self.log_test("数据类型检查", numeric_check, "数值列数据类型正确")
            
            # 检查数据完整性
            null_count = df.isnull().sum().sum()
            self.log_test("数据完整性", null_count == 0, f"无缺失数据")
            
            return df
            
        except Exception as e:
            self.log_test("CSV文件读取", False, f"读取失败: {e}")
            return None
    
    def test_data_analysis(self, df):
        """测试数据分析功能"""
        print("\n=== 测试数据分析 ===")
        
        if df is None:
            self.log_test("数据分析", False, "无数据可分析")
            return
        
        try:
            # 基础统计
            stats = df.describe()
            self.log_test("基础统计分析", True, f"生成统计信息，包含{len(stats)}个统计指标")
            
            # 视力趋势分析
            left_vision_mean = df['left_eye_vision'].mean()
            right_vision_mean = df['right_eye_vision'].mean()
            self.log_test("视力均值分析", True, f"左眼: {left_vision_mean:.2f}, 右眼: {right_vision_mean:.2f}")
            
            # 准确率分析
            accuracy_mean = df['accuracy'].mean()
            self.log_test("准确率分析", True, f"平均准确率: {accuracy_mean:.1f}%")
            
            # 眼压分析
            pressure_mean = df['eye_pressure'].mean()
            self.log_test("眼压分析", True, f"平均眼压: {pressure_mean:.1f} mmHg")
            
            # 疲劳度分析
            fatigue_mean = df['eye_fatigue'].mean()
            self.log_test("疲劳度分析", True, f"平均疲劳度: {fatigue_mean:.1f}/10")
            
            # 测试时长分析
            duration_mean = df['test_duration'].mean()
            self.log_test("测试时长分析", True, f"平均测试时长: {duration_mean:.0f}秒")
            
        except Exception as e:
            self.log_test("数据分析", False, f"分析失败: {e}")
    
    def test_visualization(self, df):
        """测试可视化功能"""
        print("\n=== 测试可视化功能 ===")
        
        if df is None:
            self.log_test("可视化", False, "无数据可可视化")
            return
        
        try:
            # 创建图表目录
            charts_dir = "test_charts"
            os.makedirs(charts_dir, exist_ok=True)
            
            # 1. 视力趋势折线图
            plt.figure(figsize=(12, 6))
            plt.plot(df.index, df['left_eye_vision'], 'b-o', label='左眼视力', linewidth=2, markersize=4)
            plt.plot(df.index, df['right_eye_vision'], 'r-s', label='右眼视力', linewidth=2, markersize=4)
            plt.title('视力变化趋势', fontsize=14, fontweight='bold')
            plt.xlabel('测试次数')
            plt.ylabel('视力水平')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{charts_dir}/vision_trend.png", dpi=300, bbox_inches='tight')
            plt.close()
            self.log_test("视力趋势图", True, "视力趋势折线图生成成功")
            
            # 2. 准确率柱状图
            plt.figure(figsize=(10, 6))
            plt.bar(df.index, df['accuracy'], alpha=0.7, color='skyblue', edgecolor='navy')
            plt.title('测试准确率', fontsize=14, fontweight='bold')
            plt.xlabel('测试次数')
            plt.ylabel('准确率 (%)')
            plt.ylim(0, 100)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{charts_dir}/accuracy_bar.png", dpi=300, bbox_inches='tight')
            plt.close()
            self.log_test("准确率柱状图", True, "准确率柱状图生成成功")
            
            # 3. 眼压散点图
            plt.figure(figsize=(10, 6))
            plt.scatter(df['eye_pressure'], df['accuracy'], alpha=0.6, c=df['eye_fatigue'], cmap='viridis')
            plt.colorbar(label='疲劳度')
            plt.title('眼压与准确率关系', fontsize=14, fontweight='bold')
            plt.xlabel('眼压 (mmHg)')
            plt.ylabel('准确率 (%)')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{charts_dir}/pressure_accuracy_scatter.png", dpi=300, bbox_inches='tight')
            plt.close()
            self.log_test("眼压散点图", True, "眼压与准确率散点图生成成功")
            
            # 4. 综合统计图
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 视力分布直方图
            axes[0, 0].hist(df['left_eye_vision'], bins=10, alpha=0.7, color='blue', label='左眼')
            axes[0, 0].hist(df['right_eye_vision'], bins=10, alpha=0.7, color='red', label='右眼')
            axes[0, 0].set_title('视力分布')
            axes[0, 0].set_xlabel('视力水平')
            axes[0, 0].set_ylabel('频次')
            axes[0, 0].legend()
            
            # 疲劳度箱线图
            axes[0, 1].boxplot([df['eye_fatigue']], labels=['疲劳度'])
            axes[0, 1].set_title('疲劳度分布')
            axes[0, 1].set_ylabel('疲劳度等级')
            
            # 测试时长趋势
            axes[1, 0].plot(df.index, df['test_duration'], 'g-o', linewidth=2)
            axes[1, 0].set_title('测试时长变化')
            axes[1, 0].set_xlabel('测试次数')
            axes[1, 0].set_ylabel('时长 (秒)')
            axes[1, 0].grid(True, alpha=0.3)
            
            # 相关性热力图
            corr_matrix = df[['left_eye_vision', 'right_eye_vision', 'eye_pressure', 'eye_fatigue', 'test_duration', 'accuracy']].corr()
            im = axes[1, 1].imshow(corr_matrix, cmap='coolwarm', aspect='auto')
            axes[1, 1].set_title('变量相关性')
            axes[1, 1].set_xticks(range(len(corr_matrix.columns)))
            axes[1, 1].set_yticks(range(len(corr_matrix.columns)))
            axes[1, 1].set_xticklabels(corr_matrix.columns, rotation=45)
            axes[1, 1].set_yticklabels(corr_matrix.columns)
            
            # 添加相关系数标签
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    text = axes[1, 1].text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                                          ha="center", va="center", color="black")
            
            plt.tight_layout()
            plt.savefig(f"{charts_dir}/comprehensive_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
            self.log_test("综合统计图", True, "综合统计分析图生成成功")
            
        except Exception as e:
            self.log_test("可视化", False, f"可视化失败: {e}")
    
    def test_advanced_analytics(self, df):
        """测试高级分析功能"""
        print("\n=== 测试高级分析 ===")
        
        if df is None:
            self.log_test("高级分析", False, "无数据可分析")
            return
        
        try:
            # 趋势分析
            from scipy import stats
            
            # 左眼视力趋势
            x = np.arange(len(df))
            slope_left, intercept_left, r_value_left, p_value_left, std_err_left = stats.linregress(x, df['left_eye_vision'])
            
            # 右眼视力趋势
            slope_right, intercept_right, r_value_right, p_value_right, std_err_right = stats.linregress(x, df['right_eye_vision'])
            
            self.log_test("视力趋势分析", True, f"左眼趋势: {slope_left:.3f}, 右眼趋势: {slope_right:.3f}")
            
            # 相关性分析
            correlation = df['left_eye_vision'].corr(df['right_eye_vision'])
            self.log_test("双眼相关性", True, f"双眼视力相关性: {correlation:.3f}")
            
            # 异常值检测
            from scipy.stats import zscore
            z_scores = zscore(df[['left_eye_vision', 'right_eye_vision', 'eye_pressure', 'accuracy']])
            outliers = (abs(z_scores) > 2).any(axis=1)
            outlier_count = outliers.sum()
            self.log_test("异常值检测", True, f"检测到{outlier_count}个异常值")
            
            # 时间序列分析
            df['date'] = pd.to_datetime(df['date'])
            df_sorted = df.sort_values('date')
            
            # 计算移动平均
            df_sorted['left_vision_ma'] = df_sorted['left_eye_vision'].rolling(window=3).mean()
            df_sorted['right_vision_ma'] = df_sorted['right_eye_vision'].rolling(window=3).mean()
            
            self.log_test("时间序列分析", True, "移动平均计算成功")
            
            # 生成分析报告
            report = {
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_summary": {
                    "total_records": len(df),
                    "date_range": f"{df['date'].min().strftime('%Y-%m-%d')} 到 {df['date'].max().strftime('%Y-%m-%d')}",
                    "left_vision_avg": df['left_eye_vision'].mean(),
                    "right_vision_avg": df['right_eye_vision'].mean(),
                    "accuracy_avg": df['accuracy'].mean()
                },
                "trend_analysis": {
                    "left_vision_trend": slope_left,
                    "right_vision_trend": slope_right,
                    "trend_significance": p_value_left < 0.05
                },
                "correlation_analysis": {
                    "left_right_correlation": correlation,
                    "pressure_accuracy_correlation": df['eye_pressure'].corr(df['accuracy']),
                    "fatigue_accuracy_correlation": df['eye_fatigue'].corr(df['accuracy'])
                },
                "quality_metrics": {
                    "outlier_count": outlier_count,
                    "data_completeness": 1.0 - df.isnull().sum().sum() / (len(df) * len(df.columns))
                }
            }
            
            # 保存报告
            with open("test_charts/analysis_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            self.log_test("分析报告生成", True, "详细分析报告已保存")
            
        except Exception as e:
            self.log_test("高级分析", False, f"高级分析失败: {e}")
    
    def test_visualization_tool(self):
        """测试可视化工具"""
        print("\n=== 测试可视化工具 ===")
        
        try:
            # 导入可视化工具
            from src.openmanus_agent.visualize_tool import VisualizeTool
            
            tool = VisualizeTool()
            self.log_test("可视化工具创建", True, "可视化工具创建成功")
            
            # 准备测试数据
            test_data = """date,left_eye_vision,right_eye_vision,accuracy
2024-06-01,5.2,5.1,85
2024-06-02,5.0,5.2,82
2024-06-03,4.8,5.0,78
2024-06-04,5.1,5.3,87
2024-06-05,5.3,5.2,90"""
            
            # 测试折线图
            import asyncio
            async def test_line_chart():
                return await tool.execute(data=test_data, chart_type="line")
            
            result = asyncio.run(test_line_chart())
            self.log_test("折线图生成", result.startswith("data:image/png;base64,"), "折线图生成成功")
            
            # 测试柱状图
            async def test_bar_chart():
                return await tool.execute(data=test_data, chart_type="bar")
            
            result = asyncio.run(test_bar_chart())
            self.log_test("柱状图生成", result.startswith("data:image/png;base64,"), "柱状图生成成功")
            
            # 测试散点图
            async def test_scatter_chart():
                return await tool.execute(data=test_data, chart_type="scatter")
            
            result = asyncio.run(test_scatter_chart())
            self.log_test("散点图生成", result.startswith("data:image/png;base64,"), "散点图生成成功")
            
        except Exception as e:
            self.log_test("可视化工具", False, f"可视化工具测试失败: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始CSV分析和可视化功能测试")
        print("=" * 50)
        
        # 运行各项测试
        df = self.test_csv_reading()
        self.test_data_analysis(df)
        self.test_visualization(df)
        self.test_advanced_analytics(df)
        self.test_visualization_tool()
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 CSV分析和可视化测试报告")
        print("=" * 50)
        
        print(f"总测试数: {self.total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.total_tests - self.passed_tests}")
        print(f"通过率: {self.passed_tests/self.total_tests*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {test_name}: {result['message']}")
        
        # 保存报告到文件
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "pass_rate": float(self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0.0,
            "results": self.test_results
        }
        
        with open("csv_visualization_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: csv_visualization_test_report.json")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 所有CSV分析和可视化功能测试通过！")
        else:
            print(f"\n⚠️  有 {self.total_tests - self.passed_tests} 个测试失败，请检查相关功能")


def main():
    """主函数"""
    print("CSV分析和可视化功能测试工具")
    print("此工具将测试CSV文件读取、分析和图表生成功能")
    
    # 创建测试器
    tester = CSVVisualizationTester()
    
    try:
        # 运行所有测试
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 