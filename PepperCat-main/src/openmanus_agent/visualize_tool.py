#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的可视化工具
支持多种图表类型和数据可视化功能
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import asyncio

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置Seaborn样式
sns.set_style("whitegrid")
sns.set_palette("husl")

from src.openmanus_agent.tool_base import BaseTool

class DataVisualizer:
    """数据可视化器"""
    
    def __init__(self):
        self.output_dir = "visualization_outputs"
        self.ensure_output_dir()
        
        # 图表类型映射
        self.chart_types = {
            'line': self.create_line_chart,
            'bar': self.create_bar_chart,
            'scatter': self.create_scatter_chart,
            'histogram': self.create_histogram,
            'boxplot': self.create_boxplot,
            'heatmap': self.create_heatmap,
            'pie': self.create_pie_chart,
            'area': self.create_area_chart,
            'violin': self.create_violin_plot,
            'correlation': self.create_correlation_matrix
        }
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def visualize_data(self, data: Union[pd.DataFrame, str], 
                      chart_type: str = 'auto',
                      title: str = None,
                      x_column: str = None,
                      y_column: str = None,
                      **kwargs) -> Dict[str, Any]:
        """可视化数据"""
        try:
            # 处理数据输入
            if isinstance(data, str):
                # 如果是文件路径，读取数据
                if data.endswith('.csv'):
                    df = pd.read_csv(data)
                elif data.endswith('.json'):
                    df = pd.read_json(data)
                else:
                    return {"error": f"不支持的文件格式: {data}"}
            else:
                df = data
            
            if df.empty:
                return {"error": "数据为空"}
            
            # 自动选择图表类型
            if chart_type == 'auto':
                chart_type = self._auto_select_chart_type(df, x_column, y_column)
            
            # 创建图表
            if chart_type in self.chart_types:
                result = self.chart_types[chart_type](df, title, x_column, y_column, **kwargs)
                return result
            else:
                return {"error": f"不支持的图表类型: {chart_type}"}
                
        except Exception as e:
            return {"error": f"可视化失败: {str(e)}"}
    
    def _auto_select_chart_type(self, df: pd.DataFrame, x_col: str, y_col: str) -> str:
        """自动选择图表类型"""
        if x_col and y_col:
            if df[x_col].dtype in ['object', 'category']:
                return 'bar'
            else:
                return 'line'
        elif len(df.columns) >= 2:
            return 'scatter'
        else:
            return 'histogram'
    
    def create_line_chart(self, df: pd.DataFrame, title: str, x_col: str, y_col: str, **kwargs) -> Dict[str, Any]:
        """创建折线图"""
        try:
            plt.figure(figsize=(12, 8))
            
            if x_col and y_col:
                plt.plot(df[x_col], df[y_col], marker='o', linewidth=2, markersize=6)
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            else:
                # 使用索引作为x轴
                for col in df.select_dtypes(include=[np.number]).columns:
                    plt.plot(df.index, df[col], marker='o', label=col, linewidth=2)
                plt.xlabel('索引')
                plt.ylabel('数值')
                plt.legend()
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 保存图表
            filename = f"line_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "line",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建折线图失败: {str(e)}"}
    
    def create_bar_chart(self, df: pd.DataFrame, title: str, x_col: str, y_col: str, **kwargs) -> Dict[str, Any]:
        """创建柱状图"""
        try:
            plt.figure(figsize=(12, 8))
            
            if x_col and y_col:
                plt.bar(df[x_col], df[y_col], alpha=0.7, color='skyblue', edgecolor='navy')
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            else:
                # 使用数值列创建柱状图
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    plt.bar(range(len(df)), df[col], alpha=0.7, color='skyblue', edgecolor='navy')
                    plt.xlabel('索引')
                    plt.ylabel(col)
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 保存图表
            filename = f"bar_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "bar",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建柱状图失败: {str(e)}"}
    
    def create_scatter_chart(self, df: pd.DataFrame, title: str, x_col: str, y_col: str, **kwargs) -> Dict[str, Any]:
        """创建散点图"""
        try:
            plt.figure(figsize=(12, 8))
            
            if x_col and y_col:
                plt.scatter(df[x_col], df[y_col], alpha=0.6, s=50)
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            else:
                # 使用前两个数值列
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6, s=50)
                    plt.xlabel(numeric_cols[0])
                    plt.ylabel(numeric_cols[1])
                else:
                    return {"error": "需要至少两个数值列来创建散点图"}
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 保存图表
            filename = f"scatter_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "scatter",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建散点图失败: {str(e)}"}
    
    def create_histogram(self, df: pd.DataFrame, title: str, x_col: str, y_col: str, **kwargs) -> Dict[str, Any]:
        """创建直方图"""
        try:
            plt.figure(figsize=(12, 8))
            
            if x_col:
                data = df[x_col]
            else:
                # 使用第一个数值列
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    data = df[numeric_cols[0]]
                else:
                    return {"error": "需要数值列来创建直方图"}
            
            plt.hist(data, bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            else:
                plt.title(f"{data.name} 分布直方图", fontsize=16, fontweight='bold')
            
            plt.xlabel(data.name)
            plt.ylabel('频次')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 保存图表
            filename = f"histogram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "histogram",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建直方图失败: {str(e)}"}
    
    def create_boxplot(self, df: pd.DataFrame, title: str = None, x_col: str = None, y_col: str = None, **kwargs) -> Dict[str, Any]:
        """创建箱线图"""
        try:
            plt.figure(figsize=(12, 8))
            
            if x_col and y_col:
                df.boxplot(column=y_col, by=x_col, ax=plt.gca())
            else:
                # 使用所有数值列
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    df[numeric_cols].boxplot(ax=plt.gca())
                else:
                    return {"error": "需要数值列来创建箱线图"}
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 保存图表
            filename = f"boxplot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "boxplot",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建箱线图失败: {str(e)}"}
    
    def create_heatmap(self, df: pd.DataFrame, title: str = None, x_col: str = None, y_col: str = None, **kwargs) -> Dict[str, Any]:
        """创建热力图"""
        try:
            plt.figure(figsize=(12, 10))
            
            # 计算相关性矩阵
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] < 2:
                return {"error": "需要至少两个数值列来创建热力图"}
            
            correlation_matrix = numeric_df.corr()
            
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": .8})
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            else:
                plt.title("相关性热力图", fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            
            # 保存图表
            filename = f"heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "heatmap",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建热力图失败: {str(e)}"}
    
    def create_pie_chart(self, df: pd.DataFrame, title: str = None, x_col: str = None, y_col: str = None, **kwargs) -> Dict[str, Any]:
        """创建饼图"""
        try:
            plt.figure(figsize=(10, 8))
            
            if x_col and y_col:
                plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%', startangle=90)
            else:
                # 使用第一个分类列和第一个数值列
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                    plt.pie(df[numeric_cols[0]], labels=df[categorical_cols[0]], 
                           autopct='%1.1f%%', startangle=90)
                else:
                    return {"error": "需要分类列和数值列来创建饼图"}
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            
            plt.axis('equal')
            plt.tight_layout()
            
            # 保存图表
            filename = f"pie_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "pie",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建饼图失败: {str(e)}"}
    
    def create_area_chart(self, df: pd.DataFrame, title: str = None, x_col: str = None, y_col: str = None, **kwargs) -> Dict[str, Any]:
        """创建面积图"""
        try:
            plt.figure(figsize=(12, 8))
            
            if x_col and y_col:
                plt.fill_between(df[x_col], df[y_col], alpha=0.6)
                plt.plot(df[x_col], df[y_col], linewidth=2)
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            else:
                # 使用索引和第一个数值列
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    plt.fill_between(df.index, df[numeric_cols[0]], alpha=0.6)
                    plt.plot(df.index, df[numeric_cols[0]], linewidth=2)
                    plt.xlabel('索引')
                    plt.ylabel(numeric_cols[0])
                else:
                    return {"error": "需要数值列来创建面积图"}
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 保存图表
            filename = f"area_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "area",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建面积图失败: {str(e)}"}
    
    def create_violin_plot(self, df: pd.DataFrame, title: str = None, x_col: str = None, y_col: str = None, **kwargs) -> Dict[str, Any]:
        """创建小提琴图"""
        try:
            plt.figure(figsize=(12, 8))
            
            if x_col and y_col:
                sns.violinplot(data=df, x=x_col, y=y_col)
            else:
                # 使用所有数值列
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    sns.violinplot(data=df[numeric_cols])
                else:
                    return {"error": "需要数值列来创建小提琴图"}
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 保存图表
            filename = f"violin_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "violin",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建小提琴图失败: {str(e)}"}
    
    def create_correlation_matrix(self, df: pd.DataFrame, title: str = None, x_col: str = None, y_col: str = None, **kwargs) -> Dict[str, Any]:
        """创建相关性矩阵图"""
        try:
            plt.figure(figsize=(12, 10))
            
            # 计算相关性矩阵
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] < 2:
                return {"error": "需要至少两个数值列来创建相关性矩阵"}
            
            correlation_matrix = numeric_df.corr()
            
            # 创建掩码矩阵（只显示上三角）
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            
            sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": .8})
            
            if title:
                plt.title(title, fontsize=16, fontweight='bold')
            else:
                plt.title("相关性矩阵", fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            
            # 保存图表
            filename = f"correlation_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "correlation",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建相关性矩阵失败: {str(e)}"}
    
    def create_comprehensive_analysis(self, df: pd.DataFrame, title: str = None) -> Dict[str, Any]:
        """创建综合分析图表"""
        try:
            # 创建子图
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(title or "数据综合分析", fontsize=20, fontweight='bold')
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            # 1. 折线图
            if len(numeric_cols) > 0:
                axes[0, 0].plot(df.index, df[numeric_cols[0]], marker='o')
                axes[0, 0].set_title(f"{numeric_cols[0]} 趋势")
                axes[0, 0].grid(True, alpha=0.3)
            
            # 2. 直方图
            if len(numeric_cols) > 0:
                axes[0, 1].hist(df[numeric_cols[0]], bins=20, alpha=0.7)
                axes[0, 1].set_title(f"{numeric_cols[0]} 分布")
                axes[0, 1].grid(True, alpha=0.3)
            
            # 3. 箱线图
            if len(numeric_cols) > 0:
                df[numeric_cols].boxplot(ax=axes[0, 2])
                axes[0, 2].set_title("数值分布")
                axes[0, 2].tick_params(axis='x', rotation=45)
            
            # 4. 散点图
            if len(numeric_cols) >= 2:
                axes[1, 0].scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6)
                axes[1, 0].set_xlabel(numeric_cols[0])
                axes[1, 0].set_ylabel(numeric_cols[1])
                axes[1, 0].set_title("相关性分析")
                axes[1, 0].grid(True, alpha=0.3)
            
            # 5. 热力图
            if len(numeric_cols) >= 2:
                correlation_matrix = df[numeric_cols].corr()
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                           square=True, ax=axes[1, 1], cbar_kws={"shrink": .8})
                axes[1, 1].set_title("相关性热力图")
            
            # 6. 统计摘要
            if len(numeric_cols) > 0:
                stats_text = df[numeric_cols].describe().to_string()
                axes[1, 2].text(0.1, 0.9, stats_text, transform=axes[1, 2].transAxes,
                               fontsize=8, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                axes[1, 2].set_title("统计摘要")
                axes[1, 2].axis('off')
            
            plt.tight_layout()
            
            # 保存图表
            filename = f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "status": "success",
                "chart_type": "comprehensive",
                "filepath": filepath,
                "filename": filename
            }
            
        except Exception as e:
            return {"error": f"创建综合分析失败: {str(e)}"}


class VisualizeTool(BaseTool):
    """可视化工具"""
    
    name: str = "visualize"
    description: str = "创建数据可视化图表，支持折线图、柱状图、散点图、直方图、箱线图、热力图等多种图表类型"
    
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "要可视化的数据（CSV文件路径或JSON数据）"
            },
            "chart_type": {
                "type": "string",
                "enum": ["line", "bar", "scatter", "histogram", "boxplot", "heatmap", "pie", "area", "violin", "correlation", "auto", "comprehensive"],
                "description": "图表类型"
            },
            "title": {
                "type": "string",
                "description": "图表标题"
            },
            "x_column": {
                "type": "string",
                "description": "X轴列名"
            },
            "y_column": {
                "type": "string",
                "description": "Y轴列名"
            }
        },
        "required": ["data"]
    }
    
    def __init__(self):
        super().__init__()
        self.visualizer = DataVisualizer()
    
    async def execute(self, data: str, chart_type: str = "auto", 
                     title: str = None, x_column: str = None, y_column: str = None, **kwargs) -> str:
        """执行数据可视化"""
        try:
            # 处理数据输入
            if data.endswith('.csv'):
                df = pd.read_csv(data)
            elif data.endswith('.json'):
                df = pd.read_json(data)
            else:
                # 尝试解析为JSON字符串
                try:
                    df = pd.read_json(data)
                except:
                    return f"错误: 不支持的数据格式 - {data}"
            
            if df.empty:
                return "错误: 数据为空"
            
            # 执行可视化
            result = self.visualizer.visualize_data(
                df, chart_type, title, x_column, y_column, **kwargs
            )
            
            if "error" in result:
                return f"可视化失败: {result['error']}"
            
            # 返回结果
            output = f"可视化完成！\n"
            output += f"图表类型: {result['chart_type']}\n"
            output += f"文件路径: {result['filepath']}\n"
            output += f"文件名: {result['filename']}\n"
            
            if title:
                output += f"标题: {title}\n"
            
            return output
            
        except Exception as e:
            return f"可视化出错: {str(e)}"
    
    def cleanup(self):
        """清理资源"""
        pass


# 测试函数
def test_visualization():
    """测试可视化功能"""
    visualizer = DataVisualizer()
    
    # 创建测试数据
    test_data = pd.DataFrame({
        '日期': pd.date_range('2024-01-01', periods=30, freq='D'),
        '左眼视力': np.random.normal(5.0, 0.3, 30),
        '右眼视力': np.random.normal(5.1, 0.3, 30),
        '眼压': np.random.normal(17, 2, 30),
        '疲劳度': np.random.uniform(1, 10, 30)
    })
    
    # 测试不同类型的图表
    chart_types = ['line', 'bar', 'scatter', 'histogram', 'boxplot', 'heatmap']
    
    for chart_type in chart_types:
        print(f"\n测试 {chart_type} 图表...")
        result = visualizer.visualize_data(
            test_data, 
            chart_type=chart_type,
            title=f"测试 {chart_type} 图表",
            x_column='日期',
            y_column='左眼视力'
        )
        
        if "error" in result:
            print(f"错误: {result['error']}")
        else:
            print(f"成功: {result['filename']}")
    
    # 测试综合分析
    print("\n测试综合分析...")
    result = visualizer.create_comprehensive_analysis(test_data, "视力数据综合分析")
    if "error" in result:
        print(f"错误: {result['error']}")
    else:
        print(f"成功: {result['filename']}")


if __name__ == "__main__":
    test_visualization() 