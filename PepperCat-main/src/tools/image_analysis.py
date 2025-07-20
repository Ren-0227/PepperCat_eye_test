#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的图像分析工具
支持眼部图片AI分析、疾病检测、健康评估等功能
"""

import cv2
import numpy as np
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import asyncio

# 尝试导入深度学习相关库
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("警告: PyTorch未安装，将使用基础图像分析方法")

# 尝试导入MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("警告: MediaPipe未安装，将使用OpenCV进行面部检测")

from src.openmanus_agent.tool_base import BaseTool

class EyeImageAnalyzer:
    """眼部图像分析器"""
    
    def __init__(self):
        self.face_mesh = None
        self.eye_cascade = None
        self.analysis_results = {}
        
        # 初始化检测模型
        self._init_models()
        
        # 眼部健康指标
        self.health_indicators = {
            'redness': 0.0,      # 红肿程度 (0-1)
            'fatigue': 0.0,      # 疲劳程度 (0-1)
            'dryness': 0.0,      # 干涩程度 (0-1)
            'clarity': 0.0,      # 清晰度 (0-1)
            'symmetry': 0.0,     # 对称性 (0-1)
            'pupil_size': 0.0,   # 瞳孔大小 (0-1)
            'sclera_color': 0.0, # 巩膜颜色 (0-1)
        }
    
    def _init_models(self):
        """初始化检测模型"""
        try:
            # 初始化MediaPipe面部网格
            if MEDIAPIPE_AVAILABLE:
                self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
            
            # 初始化OpenCV眼部级联分类器
            cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            if os.path.exists(cascade_path):
                self.eye_cascade = cv2.CascadeClassifier(cascade_path)
            else:
                print("警告: 未找到眼部级联分类器文件")
                
        except Exception as e:
            print(f"模型初始化失败: {e}")
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """分析眼部图像"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return {"error": f"图像文件不存在: {image_path}"}
            
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {"error": f"无法读取图像: {image_path}"}
            
            # 预处理图像
            processed_image = self._preprocess_image(image)
            
            # 检测眼部区域
            eye_regions = self._detect_eye_regions(processed_image)
            if not eye_regions:
                return {"error": "未检测到眼部区域"}
            
            # 分析每个眼部区域
            analysis_results = []
            for i, eye_region in enumerate(eye_regions):
                eye_analysis = self._analyze_eye_region(eye_region, f"eye_{i+1}")
                analysis_results.append(eye_analysis)
            
            # 综合评估
            overall_health = self._evaluate_overall_health(analysis_results)
            
            # 生成报告
            report = self._generate_report(analysis_results, overall_health)
            
            return {
                "status": "success",
                "image_path": image_path,
                "analysis_results": analysis_results,
                "overall_health": overall_health,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"图像分析失败: {str(e)}"}
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """预处理图像"""
        # 调整图像大小
        height, width = image.shape[:2]
        if width > 800:
            scale = 800 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # 增强对比度
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def _detect_eye_regions(self, image: np.ndarray) -> List[np.ndarray]:
        """检测眼部区域"""
        eye_regions = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用MediaPipe检测眼部关键点
        if self.face_mesh:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                height, width = image.shape[:2]
                
                # 左眼关键点 (362-386)
                left_eye_points = []
                for i in range(362, 387):
                    point = landmarks.landmark[i]
                    x, y = int(point.x * width), int(point.y * height)
                    left_eye_points.append([x, y])
                
                # 右眼关键点 (33-57)
                right_eye_points = []
                for i in range(33, 58):
                    point = landmarks.landmark[i]
                    x, y = int(point.x * width), int(point.y * height)
                    right_eye_points.append([x, y])
                
                # 提取眼部区域
                for eye_points in [left_eye_points, right_eye_points]:
                    if len(eye_points) > 0:
                        eye_region = self._extract_eye_region(image, eye_points)
                        if eye_region is not None:
                            eye_regions.append(eye_region)
        
        # 如果MediaPipe失败，使用OpenCV级联分类器
        if not eye_regions and self.eye_cascade:
            eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 5)
            for (x, y, w, h) in eyes:
                eye_region = image[y:y+h, x:x+w]
                eye_regions.append(eye_region)
        
        return eye_regions
    
    def _extract_eye_region(self, image: np.ndarray, eye_points: List[List[int]]) -> Optional[np.ndarray]:
        """提取眼部区域"""
        try:
            # 计算边界框
            points = np.array(eye_points, dtype=np.int32)
            x, y, w, h = cv2.boundingRect(points)
            
            # 扩展边界框
            margin = 10
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(image.shape[1] - x, w + 2 * margin)
            h = min(image.shape[0] - y, h + 2 * margin)
            
            # 提取区域
            eye_region = image[y:y+h, x:x+w]
            
            # 确保区域足够大
            if eye_region.shape[0] > 20 and eye_region.shape[1] > 20:
                return eye_region
            
        except Exception as e:
            print(f"提取眼部区域失败: {e}")
        
        return None
    
    def _analyze_eye_region(self, eye_region: np.ndarray, eye_name: str) -> Dict[str, Any]:
        """分析单个眼部区域"""
        analysis = {
            "eye_name": eye_name,
            "size": eye_region.shape,
            "health_indicators": {}
        }
        
        try:
            # 转换为HSV颜色空间
            hsv = cv2.cvtColor(eye_region, cv2.COLOR_BGR2HSV)
            
            # 分析红肿程度 (红色区域)
            red_lower = np.array([0, 50, 50])
            red_upper = np.array([10, 255, 255])
            red_mask = cv2.inRange(hsv, red_lower, red_upper)
            redness = np.sum(red_mask > 0) / (eye_region.shape[0] * eye_region.shape[1])
            analysis["health_indicators"]["redness"] = min(redness * 5, 1.0)
            
            # 分析疲劳程度 (眼袋和黑眼圈)
            gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
            dark_pixels = np.sum(gray < 80)
            total_pixels = gray.shape[0] * gray.shape[1]
            fatigue = dark_pixels / total_pixels
            analysis["health_indicators"]["fatigue"] = min(fatigue * 3, 1.0)
            
            # 分析清晰度 (边缘检测)
            edges = cv2.Canny(gray, 50, 150)
            clarity = np.sum(edges > 0) / total_pixels
            analysis["health_indicators"]["clarity"] = min(clarity * 2, 1.0)
            
            # 分析对称性
            symmetry = self._calculate_symmetry(eye_region)
            analysis["health_indicators"]["symmetry"] = symmetry
            
            # 检测瞳孔
            pupil_analysis = self._detect_pupil(eye_region)
            analysis["health_indicators"]["pupil_size"] = pupil_analysis.get("size", 0.0)
            
            # 分析巩膜颜色
            sclera_color = self._analyze_sclera_color(eye_region)
            analysis["health_indicators"]["sclera_color"] = sclera_color
            
        except Exception as e:
            print(f"分析眼部区域失败: {e}")
        
        return analysis
    
    def _calculate_symmetry(self, eye_region: np.ndarray) -> float:
        """计算对称性"""
        try:
            gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # 计算左右对称性
            left_half = gray[:, :width//2]
            right_half = cv2.flip(gray[:, width//2:], 1)
            
            # 确保两个半部分大小相同
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            # 计算差异
            diff = cv2.absdiff(left_half, right_half)
            symmetry = 1.0 - (np.sum(diff) / (diff.shape[0] * diff.shape[1] * 255))
            
            return max(0.0, min(1.0, symmetry))
            
        except Exception:
            return 0.5
    
    def _detect_pupil(self, eye_region: np.ndarray) -> Dict[str, Any]:
        """检测瞳孔"""
        try:
            gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
            
            # 使用霍夫圆检测
            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30, minRadius=5, maxRadius=50
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                if len(circles) > 0:
                    # 选择最大的圆作为瞳孔
                    largest_circle = max(circles, key=lambda x: x[2])
                    x, y, radius = largest_circle
                    
                    # 计算瞳孔大小比例
                    eye_area = eye_region.shape[0] * eye_region.shape[1]
                    pupil_area = np.pi * radius * radius
                    pupil_ratio = pupil_area / eye_area
                    
                    return {
                        "size": min(pupil_ratio * 10, 1.0),
                        "center": (x, y),
                        "radius": radius
                    }
            
        except Exception as e:
            print(f"瞳孔检测失败: {e}")
        
        return {"size": 0.0}
    
    def _analyze_sclera_color(self, eye_region: np.ndarray) -> float:
        """分析巩膜颜色"""
        try:
            hsv = cv2.cvtColor(eye_region, cv2.COLOR_BGR2HSV)
            
            # 白色巩膜的范围
            white_lower = np.array([0, 0, 200])
            white_upper = np.array([180, 30, 255])
            white_mask = cv2.inRange(hsv, white_lower, white_upper)
            
            # 黄色巩膜的范围 (可能表示疾病)
            yellow_lower = np.array([20, 50, 100])
            yellow_upper = np.array([30, 255, 255])
            yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            
            total_pixels = eye_region.shape[0] * eye_region.shape[1]
            white_ratio = np.sum(white_mask > 0) / total_pixels
            yellow_ratio = np.sum(yellow_mask > 0) / total_pixels
            
            # 健康巩膜应该是白色，黄色表示异常
            sclera_health = white_ratio - yellow_ratio * 2
            return max(0.0, min(1.0, sclera_health))
            
        except Exception:
            return 0.5
    
    def _evaluate_overall_health(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估整体健康状况"""
        if not analysis_results:
            return {"overall_score": 0.0, "status": "无法评估"}
        
        # 计算平均指标
        avg_indicators = {}
        for indicator in ["redness", "fatigue", "clarity", "symmetry", "pupil_size", "sclera_color"]:
            values = [result["health_indicators"].get(indicator, 0.0) for result in analysis_results]
            avg_indicators[indicator] = np.mean(values)
        
        # 计算整体健康分数
        # 红肿和疲劳是负面指标，其他是正面指标
        overall_score = (
            (1.0 - avg_indicators["redness"]) * 0.2 +
            (1.0 - avg_indicators["fatigue"]) * 0.2 +
            avg_indicators["clarity"] * 0.2 +
            avg_indicators["symmetry"] * 0.15 +
            avg_indicators["sclera_color"] * 0.15 +
            (0.5 - abs(avg_indicators["pupil_size"] - 0.3)) * 0.1  # 瞳孔大小适中最好
        )
        
        # 确定健康状况
        if overall_score >= 0.8:
            status = "优秀"
        elif overall_score >= 0.6:
            status = "良好"
        elif overall_score >= 0.4:
            status = "一般"
        else:
            status = "需要关注"
        
        return {
            "overall_score": overall_score,
            "status": status,
            "average_indicators": avg_indicators
        }
    
    def _generate_report(self, analysis_results: List[Dict[str, Any]], overall_health: Dict[str, Any]) -> str:
        """生成分析报告"""
        report = "眼部健康分析报告\n"
        report += "=" * 50 + "\n\n"
        
        # 整体评估
        report += f"整体健康状况: {overall_health['status']}\n"
        report += f"健康评分: {overall_health['overall_score']:.2f}/1.00\n\n"
        
        # 详细指标
        if overall_health.get("average_indicators"):
            indicators = overall_health["average_indicators"]
            report += "详细指标:\n"
            report += f"- 红肿程度: {indicators.get('redness', 0):.2f} (越低越好)\n"
            report += f"- 疲劳程度: {indicators.get('fatigue', 0):.2f} (越低越好)\n"
            report += f"- 清晰度: {indicators.get('clarity', 0):.2f} (越高越好)\n"
            report += f"- 对称性: {indicators.get('symmetry', 0):.2f} (越高越好)\n"
            report += f"- 巩膜健康: {indicators.get('sclera_color', 0):.2f} (越高越好)\n\n"
        
        # 建议
        report += "健康建议:\n"
        if overall_health['overall_score'] >= 0.8:
            report += "- 眼部健康状况良好，继续保持\n"
            report += "- 定期进行眼部检查\n"
            report += "- 保持良好的用眼习惯\n"
        elif overall_health['overall_score'] >= 0.6:
            report += "- 眼部健康状况一般，需要关注\n"
            report += "- 减少用眼时间，多休息\n"
            report += "- 建议咨询眼科医生\n"
        else:
            report += "- 眼部健康状况需要关注\n"
            report += "- 立即减少用眼时间\n"
            report += "- 建议尽快就医检查\n"
        
        return report
    
    def cleanup(self):
        """清理资源"""
        if self.face_mesh:
            self.face_mesh.close()


class ImageAnalysisTool(BaseTool):
    """图像分析工具"""
    
    name: str = "image_analysis"
    description: str = "分析眼部图片，检测眼部健康状况，包括红肿、疲劳、对称性等指标"
    
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "要分析的图片路径"
            }
        },
        "required": ["image_path"]
    }
    
    def __init__(self):
        super().__init__()
        self.analyzer = EyeImageAnalyzer()
    
    async def execute(self, image_path: str, **kwargs) -> str:
        """执行图像分析"""
        try:
            # 检查文件路径
            if not os.path.exists(image_path):
                return f"错误: 图片文件不存在 - {image_path}"
            
            # 分析图像
            result = self.analyzer.analyze_image(image_path)
            
            if "error" in result:
                return f"分析失败: {result['error']}"
            
            # 格式化输出
            output = f"图像分析完成！\n\n"
            output += result["report"]
            output += f"\n\n分析时间: {result['timestamp']}"
            
            return output
            
        except Exception as e:
            return f"图像分析出错: {str(e)}"
    
    def cleanup(self):
        """清理资源"""
        if self.analyzer:
            self.analyzer.cleanup()


# 测试函数
def test_image_analysis():
    """测试图像分析功能"""
    analyzer = EyeImageAnalyzer()
    
    # 测试图片路径
    test_images = [
        "pictures/glaucoma_classification_1.png",
        "pictures/E.png"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n分析图片: {image_path}")
            result = analyzer.analyze_image(image_path)
            
            if "error" in result:
                print(f"错误: {result['error']}")
            else:
                print("分析成功!")
                print(f"整体健康评分: {result['overall_health']['overall_score']:.2f}")
                print(f"健康状况: {result['overall_health']['status']}")
        else:
            print(f"图片不存在: {image_path}")
    
    analyzer.cleanup()


if __name__ == "__main__":
    test_image_analysis() 