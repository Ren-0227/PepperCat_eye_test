#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCT图片分析工具
专门用于分析OCT（光学相干断层扫描）图片，检测眼部疾病
"""

import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 尝试导入深度学习相关库
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("警告: PyTorch未安装，将使用传统图像分析方法")

from src.openmanus_agent.tool_base import BaseTool

class OCTAnalyzer:
    """OCT图片分析器"""
    
    def __init__(self):
        self.analysis_results = {}
        
        # OCT疾病特征库
        self.disease_features = {
            'glaucoma': {
                'keywords': ['青光眼', 'glaucoma', '眼压', '视神经'],
                'features': ['视神经杯扩大', '视网膜神经纤维层变薄', '视野缺损'],
                'severity_levels': ['轻度', '中度', '重度']
            },
            'macular_degeneration': {
                'keywords': ['黄斑变性', 'macular degeneration', 'AMD', '黄斑'],
                'features': ['黄斑区异常', '玻璃膜疣', '地图样萎缩'],
                'severity_levels': ['早期', '中期', '晚期']
            },
            'diabetic_retinopathy': {
                'keywords': ['糖尿病视网膜病变', 'diabetic retinopathy', '微血管瘤', '出血'],
                'features': ['微血管瘤', '视网膜出血', '硬性渗出', '新生血管'],
                'severity_levels': ['非增殖期', '增殖期', '严重']
            },
            'retinal_detachment': {
                'keywords': ['视网膜脱离', 'retinal detachment', '视网膜裂孔'],
                'features': ['视网膜层分离', '视网膜下积液', '视网膜裂孔'],
                'severity_levels': ['部分脱离', '完全脱离', '紧急']
            },
            'normal': {
                'keywords': ['正常', 'normal', '健康'],
                'features': ['视网膜层结构正常', '视神经正常', '黄斑区正常'],
                'severity_levels': ['健康']
            }
        }
    
    def analyze_oct_image(self, image_path: str) -> Dict[str, Any]:
        """分析OCT图片"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return {"error": f"OCT图片文件不存在: {image_path}"}
            
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {"error": f"无法读取OCT图片: {image_path}"}
            
            # 预处理图像
            processed_image = self._preprocess_oct_image(image)
            
            # 分析OCT特征
            oct_features = self._analyze_oct_features(processed_image)
            
            # 疾病检测
            disease_analysis = self._detect_diseases(oct_features)
            
            # 生成报告
            report = self._generate_oct_report(disease_analysis, oct_features)
            
            return {
                "status": "success",
                "image_path": image_path,
                "oct_features": oct_features,
                "disease_analysis": disease_analysis,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"OCT分析失败: {str(e)}"}
    
    def _preprocess_oct_image(self, image: np.ndarray) -> np.ndarray:
        """预处理OCT图像"""
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 图像增强
        # 直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 降噪
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        return denoised
    
    def _analyze_oct_features(self, image: np.ndarray) -> Dict[str, Any]:
        """分析OCT特征"""
        features = {
            'retinal_layers': {},
            'optic_nerve': {},
            'macula': {},
            'vessels': {},
            'abnormalities': []
        }
        
        try:
            # 1. 视网膜层分析
            features['retinal_layers'] = self._analyze_retinal_layers(image)
            
            # 2. 视神经分析
            features['optic_nerve'] = self._analyze_optic_nerve(image)
            
            # 3. 黄斑区分析
            features['macula'] = self._analyze_macula(image)
            
            # 4. 血管分析
            features['vessels'] = self._analyze_vessels(image)
            
            # 5. 异常检测
            features['abnormalities'] = self._detect_abnormalities(image)
            
        except Exception as e:
            print(f"特征分析出错: {e}")
        
        return features
    
    def _analyze_retinal_layers(self, image: np.ndarray) -> Dict[str, Any]:
        """分析视网膜层"""
        height, width = image.shape
        
        # 使用边缘检测识别视网膜层
        edges = cv2.Canny(image, 50, 150)
        
        # 霍夫线变换检测水平线（视网膜层边界）
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                               minLineLength=width//4, maxLineGap=10)
        
        layer_info = {
            'layer_count': 0,
            'layer_thickness': [],
            'layer_regularity': 0.0,
            'layer_continuity': 0.0
        }
        
        if lines is not None:
            # 过滤水平线
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 10:  # 水平线
                    horizontal_lines.append((y1, y2))
            
            layer_info['layer_count'] = len(horizontal_lines)
            
            # 计算层厚度
            if len(horizontal_lines) > 1:
                horizontal_lines.sort(key=lambda x: x[0])
                for i in range(len(horizontal_lines) - 1):
                    thickness = horizontal_lines[i+1][0] - horizontal_lines[i][0]
                    layer_info['layer_thickness'].append(thickness)
        
        return layer_info
    
    def _analyze_optic_nerve(self, image: np.ndarray) -> Dict[str, Any]:
        """分析视神经"""
        height, width = image.shape
        
        # 在图像中心区域寻找视神经
        center_region = image[height//4:3*height//4, width//4:3*width//4]
        
        # 使用圆形检测寻找视神经杯
        circles = cv2.HoughCircles(
            center_region, cv2.HOUGH_GRADIENT, 1, 20,
            param1=50, param2=30, minRadius=10, maxRadius=100
        )
        
        optic_nerve_info = {
            'cup_disc_ratio': 0.0,
            'cup_area': 0,
            'disc_area': 0,
            'cup_depth': 0.0
        }
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            if len(circles) > 0:
                # 选择最大的圆作为视神经杯
                largest_circle = max(circles, key=lambda x: x[2])
                x, y, radius = largest_circle
                
                optic_nerve_info['cup_area'] = np.pi * radius * radius
                optic_nerve_info['cup_disc_ratio'] = min(radius / 50.0, 1.0)  # 估算杯盘比
                optic_nerve_info['cup_depth'] = self._estimate_cup_depth(center_region, x, y, radius)
        
        return optic_nerve_info
    
    def _analyze_macula(self, image: np.ndarray) -> Dict[str, Any]:
        """分析黄斑区"""
        height, width = image.shape
        
        # 黄斑区通常在图像中心
        macula_region = image[height//3:2*height//3, width//3:2*width//3]
        
        macula_info = {
            'fovea_depth': 0.0,
            'macular_thickness': 0.0,
            'drusen_count': 0,
            'geographic_atrophy': False
        }
        
        # 计算黄斑区厚度
        macula_info['macular_thickness'] = np.mean(macula_region)
        
        # 检测玻璃膜疣（drusen）
        macula_info['drusen_count'] = self._count_drusen(macula_region)
        
        # 检测地图样萎缩
        macula_info['geographic_atrophy'] = self._detect_geographic_atrophy(macula_region)
        
        return macula_info
    
    def _analyze_vessels(self, image: np.ndarray) -> Dict[str, Any]:
        """分析血管"""
        # 使用形态学操作检测血管
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        vessels = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        
        vessel_info = {
            'vessel_density': 0.0,
            'vessel_tortuosity': 0.0,
            'microaneurysms': 0,
            'hemorrhages': 0
        }
        
        # 计算血管密度
        vessel_pixels = np.sum(vessels > 50)
        total_pixels = vessels.shape[0] * vessels.shape[1]
        vessel_info['vessel_density'] = vessel_pixels / total_pixels
        
        # 检测微血管瘤
        vessel_info['microaneurysms'] = self._count_microaneurysms(image)
        
        # 检测出血
        vessel_info['hemorrhages'] = self._count_hemorrhages(image)
        
        return vessel_info
    
    def _detect_abnormalities(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测异常"""
        abnormalities = []
        
        # 检测异常亮区（可能是渗出）
        bright_regions = self._detect_bright_regions(image)
        for region in bright_regions:
            abnormalities.append({
                'type': 'exudate',
                'location': region['location'],
                'size': region['size'],
                'confidence': region['confidence']
            })
        
        # 检测异常暗区（可能是出血）
        dark_regions = self._detect_dark_regions(image)
        for region in dark_regions:
            abnormalities.append({
                'type': 'hemorrhage',
                'location': region['location'],
                'size': region['size'],
                'confidence': region['confidence']
            })
        
        # 检测不规则区域
        irregular_regions = self._detect_irregular_regions(image)
        for region in irregular_regions:
            abnormalities.append({
                'type': 'irregular_structure',
                'location': region['location'],
                'size': region['size'],
                'confidence': region['confidence']
            })
        
        return abnormalities
    
    def _detect_diseases(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """基于特征检测疾病"""
        disease_scores = {}
        
        # 青光眼评分
        glaucoma_score = 0.0
        if features['optic_nerve']['cup_disc_ratio'] > 0.6:
            glaucoma_score += 0.4
        if features['optic_nerve']['cup_disc_ratio'] > 0.8:
            glaucoma_score += 0.3
        if len(features['retinal_layers']['layer_thickness']) > 0:
            avg_thickness = np.mean(features['retinal_layers']['layer_thickness'])
            if avg_thickness < 80:  # 视网膜神经纤维层变薄
                glaucoma_score += 0.3
        disease_scores['glaucoma'] = min(glaucoma_score, 1.0)
        
        # 黄斑变性评分
        amd_score = 0.0
        if features['macula']['drusen_count'] > 5:
            amd_score += 0.3
        if features['macula']['drusen_count'] > 10:
            amd_score += 0.3
        if features['macula']['geographic_atrophy']:
            amd_score += 0.4
        disease_scores['macular_degeneration'] = min(amd_score, 1.0)
        
        # 糖尿病视网膜病变评分
        dr_score = 0.0
        if features['vessels']['microaneurysms'] > 3:
            dr_score += 0.3
        if features['vessels']['hemorrhages'] > 2:
            dr_score += 0.3
        if len([a for a in features['abnormalities'] if a['type'] == 'exudate']) > 2:
            dr_score += 0.4
        disease_scores['diabetic_retinopathy'] = min(dr_score, 1.0)
        
        # 视网膜脱离评分
        rd_score = 0.0
        irregular_count = len([a for a in features['abnormalities'] if a['type'] == 'irregular_structure'])
        if irregular_count > 3:
            rd_score += 0.5
        if features['retinal_layers']['layer_continuity'] < 0.5:
            rd_score += 0.5
        disease_scores['retinal_detachment'] = min(rd_score, 1.0)
        
        # 正常评分
        normal_score = 1.0 - max(disease_scores.values())
        disease_scores['normal'] = max(normal_score, 0.0)
        
        return disease_scores
    
    def _generate_oct_report(self, disease_scores: Dict[str, Any], features: Dict[str, Any]) -> str:
        """生成OCT分析报告"""
        report = "OCT图片分析报告\n"
        report += "=" * 50 + "\n\n"
        
        # 疾病检测结果
        report += "疾病检测结果:\n"
        sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
        
        for disease, score in sorted_diseases:
            if score > 0.1:  # 只显示有意义的检测结果
                disease_name = {
                    'glaucoma': '青光眼',
                    'macular_degeneration': '黄斑变性',
                    'diabetic_retinopathy': '糖尿病视网膜病变',
                    'retinal_detachment': '视网膜脱离',
                    'normal': '正常'
                }.get(disease, disease)
                
                severity = self._get_severity_level(disease, score)
                report += f"- {disease_name}: {severity} (置信度: {score:.1%})\n"
        
        report += "\n详细特征分析:\n"
        
        # 视神经分析
        optic_nerve = features['optic_nerve']
        report += f"- 杯盘比: {optic_nerve['cup_disc_ratio']:.2f}\n"
        if optic_nerve['cup_disc_ratio'] > 0.6:
            report += "  ⚠️  杯盘比偏高，需要关注青光眼风险\n"
        
        # 黄斑区分析
        macula = features['macula']
        report += f"- 玻璃膜疣数量: {macula['drusen_count']}\n"
        if macula['drusen_count'] > 5:
            report += "  ⚠️  玻璃膜疣较多，需要关注黄斑变性\n"
        
        # 血管分析
        vessels = features['vessels']
        report += f"- 微血管瘤数量: {vessels['microaneurysms']}\n"
        report += f"- 出血点数量: {vessels['hemorrhages']}\n"
        if vessels['microaneurysms'] > 3 or vessels['hemorrhages'] > 2:
            report += "  ⚠️  血管异常，需要关注糖尿病视网膜病变\n"
        
        # 异常检测
        abnormalities = features['abnormalities']
        report += f"- 检测到异常区域: {len(abnormalities)}个\n"
        for i, abnormality in enumerate(abnormalities[:3]):  # 只显示前3个
            report += f"  {i+1}. {abnormality['type']} (置信度: {abnormality['confidence']:.1%})\n"
        
        # 建议
        report += "\n医学建议:\n"
        primary_disease = sorted_diseases[0][0]
        primary_score = sorted_diseases[0][1]
        
        if primary_score > 0.7:
            if primary_disease == 'glaucoma':
                report += "- 建议立即就医，进行青光眼专科检查\n"
                report += "- 定期监测眼压和视神经\n"
            elif primary_disease == 'macular_degeneration':
                report += "- 建议眼科专科就诊，评估黄斑变性程度\n"
                report += "- 考虑抗VEGF治疗\n"
            elif primary_disease == 'diabetic_retinopathy':
                report += "- 建议内分泌科和眼科联合治疗\n"
                report += "- 控制血糖，定期眼底检查\n"
            elif primary_disease == 'retinal_detachment':
                report += "- 紧急情况！立即就医\n"
                report += "- 避免剧烈运动，保持头部稳定\n"
        elif primary_score > 0.3:
            report += "- 建议定期眼科检查\n"
            report += "- 注意眼部健康，避免用眼过度\n"
        else:
            report += "- 眼部结构基本正常\n"
            report += "- 建议定期体检，保持良好用眼习惯\n"
        
        report += f"\n分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        report += "\n\n⚠️  注意：此分析仅供参考，最终诊断请以医生为准"
        
        return report
    
    def _get_severity_level(self, disease: str, score: float) -> str:
        """获取疾病严重程度"""
        if disease in self.disease_features:
            levels = self.disease_features[disease]['severity_levels']
            if score > 0.8:
                return levels[-1] if len(levels) > 0 else "严重"
            elif score > 0.5:
                return levels[1] if len(levels) > 1 else "中度"
            else:
                return levels[0] if len(levels) > 0 else "轻度"
        return "未知"
    
    # 辅助方法
    def _estimate_cup_depth(self, image: np.ndarray, x: int, y: int, radius: int) -> float:
        """估算视神经杯深度"""
        try:
            # 在视神经杯区域计算平均灰度值
            cup_region = image[max(0, y-radius):min(image.shape[0], y+radius),
                              max(0, x-radius):min(image.shape[1], x+radius)]
            return np.mean(cup_region)
        except:
            return 0.0
    
    def _count_drusen(self, image: np.ndarray) -> int:
        """计算玻璃膜疣数量"""
        # 使用斑点检测
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold = 50
        params.maxThreshold = 200
        params.filterByArea = True
        params.minArea = 10
        params.maxArea = 1000
        
        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(image)
        return len(keypoints)
    
    def _detect_geographic_atrophy(self, image: np.ndarray) -> bool:
        """检测地图样萎缩"""
        # 检测大面积的暗区
        dark_pixels = np.sum(image < 50)
        total_pixels = image.shape[0] * image.shape[1]
        dark_ratio = dark_pixels / total_pixels
        return dark_ratio > 0.3
    
    def _count_microaneurysms(self, image: np.ndarray) -> int:
        """计算微血管瘤数量"""
        # 使用圆形检测
        circles = cv2.HoughCircles(
            image, cv2.HOUGH_GRADIENT, 1, 10,
            param1=30, param2=20, minRadius=2, maxRadius=8
        )
        return len(circles[0]) if circles is not None else 0
    
    def _count_hemorrhages(self, image: np.ndarray) -> int:
        """计算出血点数量"""
        # 检测暗色圆形区域
        dark_regions = self._detect_dark_regions(image)
        return len([r for r in dark_regions if r['size'] < 50])
    
    def _detect_bright_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测亮区（渗出）"""
        # 阈值检测
        _, binary = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 20:
                x, y, w, h = cv2.boundingRect(contour)
                regions.append({
                    'location': (x, y),
                    'size': area,
                    'confidence': min(area / 100.0, 1.0)
                })
        
        return regions
    
    def _detect_dark_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测暗区（出血）"""
        # 阈值检测
        _, binary = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10:
                x, y, w, h = cv2.boundingRect(contour)
                regions.append({
                    'location': (x, y),
                    'size': area,
                    'confidence': min(area / 50.0, 1.0)
                })
        
        return regions
    
    def _detect_irregular_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测不规则区域"""
        # 使用边缘检测
        edges = cv2.Canny(image, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 30:
                # 计算不规则度
                perimeter = cv2.arcLength(contour, True)
                irregularity = perimeter * perimeter / (4 * np.pi * area)
                
                if irregularity > 2.0:  # 不规则形状
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append({
                        'location': (x, y),
                        'size': area,
                        'confidence': min(irregularity / 5.0, 1.0)
                    })
        
        return regions


class OCTAnalysisTool(BaseTool):
    """OCT图片分析工具"""
    
    name: str = "oct_analysis"
    description: str = "分析OCT（光学相干断层扫描）图片，检测青光眼、黄斑变性、糖尿病视网膜病变等眼部疾病"
    
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "要分析的OCT图片路径"
            }
        },
        "required": ["image_path"]
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analyzer = OCTAnalyzer()
    
    async def execute(self, image_path: str, **kwargs) -> str:
        """执行OCT图片分析"""
        try:
            # 检查文件路径
            if not os.path.exists(image_path):
                return f"错误: OCT图片文件不存在 - {image_path}"
            
            # 分析OCT图片
            result = self.analyzer.analyze_oct_image(image_path)
            
            if "error" in result:
                return f"OCT分析失败: {result['error']}"
            
            # 格式化输出
            output = f"OCT图片分析完成！\n\n"
            output += result["report"]
            
            return output
            
        except Exception as e:
            return f"OCT分析出错: {str(e)}"
    
    def cleanup(self):
        """清理资源"""
        pass


# 测试函数
def test_oct_analysis():
    """测试OCT分析功能"""
    analyzer = OCTAnalyzer()
    
    # 测试图片路径
    test_images = [
        "pictures/glaucoma_classification_1.png",
        "pictures/E.png"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n分析OCT图片: {image_path}")
            result = analyzer.analyze_oct_image(image_path)
            
            if "error" in result:
                print(f"错误: {result['error']}")
            else:
                print("分析成功!")
                print(f"检测到异常: {len(result['abnormalities'])}个")
                print(f"主要疾病: {max(result['disease_analysis'].items(), key=lambda x: x[1])[0]}")
        else:
            print(f"图片不存在: {image_path}")


if __name__ == "__main__":
    test_oct_analysis() 