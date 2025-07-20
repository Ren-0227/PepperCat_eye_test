# advanced_vision_test.py
import cv2
import numpy as np
import mediapipe as mp
import time
import json
import os
from enum import Enum
from typing import Dict, List, Tuple, Optional
import threading
import queue

class AdvancedVisionTest:
    """高级视力检测系统"""
    
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.hands = mp.solutions.hands.Hands(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        
        # 测试状态
        self.is_testing = False
        self.test_results = {}
        self.eye_tracking_data = []
        
        # 初始化测试参数
        self._init_parameters()
    
    def _init_parameters(self):
        """初始化测试参数"""
        self.distance = 60  # 标准距离60cm
        self.current_size = 0.5
        self.direction = 0
        self.correct_count = 0
        self.total_count = 0
        self.response_times = []
        
    def start_comprehensive_test(self) -> Dict:
        """开始综合视力测试"""
        print("=== 高级视力检测系统 ===")
        print("1. 基础视力测试")
        print("2. 色觉测试")
        print("3. 对比度测试")
        print("4. 周边视野测试")
        print("5. 眼动追踪分析")
        
        results = {}
        
        # 基础视力测试
        print("\n开始基础视力测试...")
        results['basic_vision'] = self._basic_vision_test()
        
        # 色觉测试
        print("\n开始色觉测试...")
        results['color_vision'] = self._color_vision_test()
        
        # 对比度测试
        print("\n开始对比度测试...")
        results['contrast_sensitivity'] = self._contrast_test()
        
        # 周边视野测试
        print("\n开始周边视野测试...")
        results['peripheral_vision'] = self._peripheral_vision_test()
        
        # 眼动追踪分析
        print("\n开始眼动追踪分析...")
        results['eye_tracking'] = self._eye_tracking_analysis()
        
        # 生成综合报告
        comprehensive_report = self._generate_comprehensive_report(results)
        
        return comprehensive_report
    
    def _basic_vision_test(self) -> Dict:
        """基础视力测试（改进版E字表）"""
        self.is_testing = True
        test_start = time.time()
        
        while self.is_testing and self.total_count < 10:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # 处理帧
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 检测面部和手势
            face_results = self.face_mesh.process(rgb_frame)
            hand_results = self.hands.process(rgb_frame)
            
            # 更新距离检测
            if face_results.multi_face_landmarks:
                self.distance = self._calculate_distance(face_results.multi_face_landmarks[0])
            
            # 检测手势响应
            if hand_results.multi_hand_landmarks:
                hand_direction = self._detect_hand_direction(hand_results.multi_hand_landmarks[0])
                if hand_direction is not None:
                    self._process_response(hand_direction)
            
            # 显示测试内容
            self._display_test_content(frame)
            
            # 检查退出条件
            if self.total_count >= 10 or self.correct_count >= 8:
                break
        
        test_duration = time.time() - test_start
        accuracy = self.correct_count / max(self.total_count, 1)
        
        return {
            'accuracy': accuracy,
            'correct_count': self.correct_count,
            'total_count': self.total_count,
            'average_response_time': np.mean(self.response_times) if self.response_times else 0,
            'test_duration': test_duration,
            'estimated_vision': self._estimate_vision_level(accuracy)
        }
    
    def _color_vision_test(self) -> Dict:
        """色觉测试"""
        colors = ['red', 'green', 'blue', 'yellow']
        color_results = {}
        
        for color in colors:
            print(f"请识别屏幕上的{color}色")
            result = self._single_color_test(color)
            color_results[color] = result
        
        return {
            'color_results': color_results,
            'overall_score': sum(color_results.values()) / len(color_results)
        }
    
    def _single_color_test(self, color: str) -> float:
        """单色测试"""
        # 创建彩色测试图像
        test_img = self._create_color_test_image(color)
        
        start_time = time.time()
        response_time = None
        
        while time.time() - start_time < 10:  # 10秒超时
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # 显示测试图像
            self._display_color_test(frame, test_img)
            
            # 检测手势响应
            hand_results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if hand_results.multi_hand_landmarks:
                response_time = time.time() - start_time
                break
        
        return response_time if response_time else 10.0
    
    def _create_color_test_image(self, color: str) -> np.ndarray:
        """创建颜色测试图像"""
        img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        
        color_map = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255)
        }
        
        cv2.circle(img, (100, 100), 50, color_map.get(color, (0, 0, 0)), -1)
        return img
    
    def _contrast_test(self) -> Dict:
        """对比度敏感度测试"""
        contrast_levels = [1.0, 0.8, 0.6, 0.4, 0.2]
        contrast_results = {}
        
        for level in contrast_levels:
            result = self._single_contrast_test(level)
            contrast_results[level] = result
        
        return {
            'contrast_results': contrast_results,
            'threshold': self._find_contrast_threshold(contrast_results)
        }
    
    def _single_contrast_test(self, contrast_level: float) -> bool:
        """单次对比度测试"""
        # 创建对比度测试图像
        test_img = self._create_contrast_test_image(contrast_level)
        
        start_time = time.time()
        detected = False
        
        while time.time() - start_time < 5:  # 5秒超时
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # 显示测试图像
            self._display_contrast_test(frame, test_img)
            
            # 检测手势响应
            hand_results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if hand_results.multi_hand_landmarks:
                detected = True
                break
        
        return detected
    
    def _create_contrast_test_image(self, contrast_level: float) -> np.ndarray:
        """创建对比度测试图像"""
        img = np.ones((200, 200, 3), dtype=np.uint8) * 128
        gray_value = int(128 + (255 - 128) * contrast_level)
        cv2.rectangle(img, (50, 50), (150, 150), (gray_value, gray_value, gray_value), -1)
        return img
    
    def _peripheral_vision_test(self) -> Dict:
        """周边视野测试"""
        positions = [(0.2, 0.2), (0.8, 0.2), (0.2, 0.8), (0.8, 0.8)]  # 屏幕四个角落
        peripheral_results = {}
        
        for i, pos in enumerate(positions):
            result = self._single_peripheral_test(pos)
            peripheral_results[f'position_{i}'] = result
        
        return {
            'peripheral_results': peripheral_results,
            'overall_coverage': sum(peripheral_results.values()) / len(peripheral_results)
        }
    
    def _single_peripheral_test(self, position: Tuple[float, float]) -> bool:
        """单次周边视野测试"""
        start_time = time.time()
        detected = False
        
        while time.time() - start_time < 3:  # 3秒超时
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # 在指定位置显示测试点
            self._display_peripheral_test(frame, position)
            
            # 检测手势响应
            hand_results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if hand_results.multi_hand_landmarks:
                detected = True
                break
        
        return detected
    
    def _eye_tracking_analysis(self) -> Dict:
        """眼动追踪分析"""
        tracking_data = []
        start_time = time.time()
        
        while time.time() - start_time < 30:  # 30秒眼动追踪
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # 处理帧
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = self.face_mesh.process(rgb_frame)
            
            if face_results.multi_face_landmarks:
                eye_data = self._extract_eye_data(face_results.multi_face_landmarks[0])
                tracking_data.append({
                    'timestamp': time.time() - start_time,
                    'eye_data': eye_data
                })
            
            # 显示眼动追踪界面
            self._display_eye_tracking(frame, tracking_data)
        
        return self._analyze_eye_tracking(tracking_data)
    
    def _extract_eye_data(self, landmarks) -> Dict:
        """提取眼动数据"""
        # 左眼关键点
        left_eye = [
            landmarks.landmark[33],   # 左眼外角
            landmarks.landmark[133],  # 左眼内角
            landmarks.landmark[160],  # 左眼上眼睑
            landmarks.landmark[159],  # 左眼下眼睑
        ]
        
        # 右眼关键点
        right_eye = [
            landmarks.landmark[362],  # 右眼外角
            landmarks.landmark[263],  # 右眼内角
            landmarks.landmark[386],  # 右眼上眼睑
            landmarks.landmark[385],  # 右眼下眼睑
        ]
        
        return {
            'left_eye': {
                'center': self._calculate_eye_center(left_eye),
                'openness': self._calculate_eye_openness(left_eye)
            },
            'right_eye': {
                'center': self._calculate_eye_center(right_eye),
                'openness': self._calculate_eye_openness(right_eye)
            }
        }
    
    def _calculate_eye_center(self, eye_landmarks) -> Tuple[float, float]:
        """计算眼睛中心点"""
        x_coords = [landmark.x for landmark in eye_landmarks]
        y_coords = [landmark.y for landmark in eye_landmarks]
        return (np.mean(x_coords), np.mean(y_coords))
    
    def _calculate_eye_openness(self, eye_landmarks) -> float:
        """计算眼睛开合度"""
        # 计算上下眼睑之间的距离
        upper_lid = eye_landmarks[2]
        lower_lid = eye_landmarks[3]
        distance = np.sqrt((upper_lid.x - lower_lid.x)**2 + (upper_lid.y - lower_lid.y)**2)
        return distance
    
    def _analyze_eye_tracking(self, tracking_data: List[Dict]) -> Dict:
        """分析眼动追踪数据"""
        if not tracking_data:
            return {'error': 'No tracking data available'}
        
        # 计算眼动统计
        left_eye_centers = [data['eye_data']['left_eye']['center'] for data in tracking_data]
        right_eye_centers = [data['eye_data']['right_eye']['center'] for data in tracking_data]
        openness_values = [
            (data['eye_data']['left_eye']['openness'] + data['eye_data']['right_eye']['openness']) / 2
            for data in tracking_data
        ]
        
        # 计算眼动范围
        left_x_range = max([center[0] for center in left_eye_centers]) - min([center[0] for center in left_eye_centers])
        left_y_range = max([center[1] for center in left_eye_centers]) - min([center[1] for center in left_eye_centers])
        right_x_range = max([center[0] for center in right_eye_centers]) - min([center[0] for center in right_eye_centers])
        right_y_range = max([center[1] for center in right_eye_centers]) - min([center[1] for center in right_eye_centers])
        
        return {
            'average_openness': np.mean(openness_values),
            'openness_variance': np.var(openness_values),
            'left_eye_movement_range': (left_x_range, left_y_range),
            'right_eye_movement_range': (right_x_range, right_y_range),
            'blink_frequency': self._calculate_blink_frequency(openness_values),
            'eye_fatigue_score': self._calculate_eye_fatigue_score(openness_values)
        }
    
    def _calculate_blink_frequency(self, openness_values: List[float]) -> float:
        """计算眨眼频率"""
        threshold = np.mean(openness_values) * 0.7
        blinks = sum(1 for i in range(1, len(openness_values)) 
                    if openness_values[i] < threshold and openness_values[i-1] >= threshold)
        return blinks / (len(openness_values) / 30)  # 假设30fps
    
    def _calculate_eye_fatigue_score(self, openness_values: List[float]) -> float:
        """计算眼疲劳评分"""
        # 基于眼睛开合度的变化计算疲劳评分
        variance = np.var(openness_values)
        mean_openness = np.mean(openness_values)
        
        # 疲劳评分：开合度变化大且平均值较低表示疲劳
        fatigue_score = (1 - mean_openness) * variance * 10
        return min(1.0, fatigue_score)
    
    def _generate_comprehensive_report(self, results: Dict) -> Dict:
        """生成综合视力报告"""
        report = {
            'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'basic_vision': results.get('basic_vision', {}),
            'color_vision': results.get('color_vision', {}),
            'contrast_sensitivity': results.get('contrast_sensitivity', {}),
            'peripheral_vision': results.get('peripheral_vision', {}),
            'eye_tracking': results.get('eye_tracking', {}),
            'overall_assessment': self._generate_overall_assessment(results),
            'recommendations': self._generate_recommendations(results)
        }
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _generate_overall_assessment(self, results: Dict) -> str:
        """生成整体评估"""
        basic_vision = results.get('basic_vision', {})
        color_vision = results.get('color_vision', {})
        contrast_sensitivity = results.get('contrast_sensitivity', {})
        peripheral_vision = results.get('peripheral_vision', {})
        eye_tracking = results.get('eye_tracking', {})
        
        assessment = []
        
        # 基础视力评估
        if basic_vision.get('accuracy', 0) < 0.7:
            assessment.append("基础视力需要关注")
        elif basic_vision.get('accuracy', 0) < 0.9:
            assessment.append("基础视力良好")
        else:
            assessment.append("基础视力优秀")
        
        # 色觉评估
        if color_vision.get('overall_score', 0) < 0.7:
            assessment.append("色觉可能存在异常")
        else:
            assessment.append("色觉正常")
        
        # 对比度敏感度评估
        contrast_threshold = contrast_sensitivity.get('threshold', 1.0)
        if contrast_threshold > 0.6:
            assessment.append("对比度敏感度良好")
        else:
            assessment.append("对比度敏感度需要关注")
        
        # 周边视野评估
        peripheral_coverage = peripheral_vision.get('overall_coverage', 0)
        if peripheral_coverage < 0.7:
            assessment.append("周边视野需要关注")
        else:
            assessment.append("周边视野正常")
        
        # 眼疲劳评估
        eye_fatigue = eye_tracking.get('eye_fatigue_score', 0)
        if eye_fatigue > 0.5:
            assessment.append("存在眼疲劳现象")
        else:
            assessment.append("眼疲劳程度正常")
        
        return "；".join(assessment)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        basic_vision = results.get('basic_vision', {})
        color_vision = results.get('color_vision', {})
        eye_tracking = results.get('eye_tracking', {})
        
        # 基于基础视力的建议
        if basic_vision.get('accuracy', 0) < 0.7:
            recommendations.append("建议进行专业眼科检查")
        
        # 基于色觉的建议
        if color_vision.get('overall_score', 0) < 0.7:
            recommendations.append("建议进行专业色觉检查")
        
        # 基于眼疲劳的建议
        eye_fatigue = eye_tracking.get('eye_fatigue_score', 0)
        if eye_fatigue > 0.5:
            recommendations.append("建议适当休息，减少用眼时间")
            recommendations.append("建议使用护眼产品")
        
        # 通用建议
        recommendations.append("建议定期进行视力检查")
        recommendations.append("保持良好的用眼习惯")
        
        return recommendations
    
    def _save_report(self, report: Dict):
        """保存测试报告"""
        reports_dir = "vision_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"{reports_dir}/vision_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"测试报告已保存至: {filename}")
    
    # 辅助方法
    def _calculate_distance(self, landmarks) -> float:
        """计算面部距离"""
        left_eye = landmarks.landmark[159]
        right_eye = landmarks.landmark[386]
        eye_distance_px = np.sqrt((right_eye.x - left_eye.x)**2 + (right_eye.y - left_eye.y)**2)
        
        # 使用物理模型计算距离
        average_face_width = 0.16  # 米
        focal_length = 600  # 相机焦距
        distance = (average_face_width * focal_length) / (eye_distance_px * self.cap.get(3))
        return max(30, min(100, distance * 100))  # 转换为厘米
    
    def _detect_hand_direction(self, hand_landmarks) -> Optional[int]:
        """检测手势方向"""
        # 简化的手势检测逻辑
        wrist = hand_landmarks.landmark[0]
        index_tip = hand_landmarks.landmark[8]
        
        # 计算手指方向
        dx = index_tip.x - wrist.x
        dy = index_tip.y - wrist.y
        angle = np.degrees(np.arctan2(dy, dx))
        
        # 映射到四个方向
        direction = int((angle + 45) % 360 // 90) * 90
        return direction
    
    def _process_response(self, detected_direction: int):
        """处理用户响应"""
        self.total_count += 1
        if detected_direction == self.direction:
            self.correct_count += 1
        
        # 记录响应时间
        self.response_times.append(time.time())
        
        # 更新测试参数
        self.direction = (self.direction + 90) % 360
        if self.correct_count < self.total_count - 2:
            self.current_size = min(1.0, self.current_size * 1.1)
        else:
            self.current_size = max(0.1, self.current_size * 0.9)
    
    def _estimate_vision_level(self, accuracy: float) -> float:
        """估算视力水平"""
        # 基于准确率估算视力
        if accuracy >= 0.9:
            return 5.0
        elif accuracy >= 0.8:
            return 4.8
        elif accuracy >= 0.7:
            return 4.6
        elif accuracy >= 0.6:
            return 4.4
        else:
            return 4.0
    
    def _find_contrast_threshold(self, contrast_results: Dict) -> float:
        """找到对比度阈值"""
        for level in sorted(contrast_results.keys(), reverse=True):
            if contrast_results[level]:
                return float(level)
        return 0.0
    
    # 显示方法
    def _display_test_content(self, frame: np.ndarray):
        """显示测试内容"""
        # 创建测试图像
        test_img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        cv2.putText(test_img, "E", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5)
        
        # 旋转图像
        rotated_img = self._rotate_image(test_img, self.direction)
        resized_img = cv2.resize(rotated_img, 
                                (int(rotated_img.shape[1] * self.current_size),
                                 int(rotated_img.shape[0] * self.current_size)))
        
        # 合并到主画面
        x_offset = (frame.shape[1] - resized_img.shape[1]) // 2
        y_offset = (frame.shape[0] - resized_img.shape[0]) // 2
        
        if x_offset >= 0 and y_offset >= 0:
            frame[y_offset:y_offset+resized_img.shape[0], 
                 x_offset:x_offset+resized_img.shape[1]] = resized_img
        
        # 添加信息显示
        info_text = [
            f"准确率: {self.correct_count}/{self.total_count}",
            f"距离: {self.distance:.1f}cm",
            f"方向: {['右', '下', '左', '上'][self.direction // 90]}"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, 30 + 30*i),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Advanced Vision Test', frame)
        cv2.waitKey(1)
    
    def _display_color_test(self, frame: np.ndarray, test_img: np.ndarray):
        """显示颜色测试"""
        x_offset = (frame.shape[1] - test_img.shape[1]) // 2
        y_offset = (frame.shape[0] - test_img.shape[0]) // 2
        
        if x_offset >= 0 and y_offset >= 0:
            frame[y_offset:y_offset+test_img.shape[0], 
                 x_offset:x_offset+test_img.shape[1]] = test_img
        
        cv2.putText(frame, "请识别颜色", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Color Vision Test', frame)
        cv2.waitKey(1)
    
    def _display_contrast_test(self, frame: np.ndarray, test_img: np.ndarray):
        """显示对比度测试"""
        x_offset = (frame.shape[1] - test_img.shape[1]) // 2
        y_offset = (frame.shape[0] - test_img.shape[0]) // 2
        
        if x_offset >= 0 and y_offset >= 0:
            frame[y_offset:y_offset+test_img.shape[0], 
                 x_offset:x_offset+test_img.shape[1]] = test_img
        
        cv2.putText(frame, "请识别图形", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Contrast Test', frame)
        cv2.waitKey(1)
    
    def _display_peripheral_test(self, frame: np.ndarray, position: Tuple[float, float]):
        """显示周边视野测试"""
        x = int(position[0] * frame.shape[1])
        y = int(position[1] * frame.shape[0])
        
        cv2.circle(frame, (x, y), 20, (0, 255, 0), -1)
        
        cv2.putText(frame, "请看向绿点", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Peripheral Vision Test', frame)
        cv2.waitKey(1)
    
    def _display_eye_tracking(self, frame: np.ndarray, tracking_data: List[Dict]):
        """显示眼动追踪"""
        # 绘制眼动轨迹
        if len(tracking_data) > 1:
            for i in range(1, len(tracking_data)):
                prev_data = tracking_data[i-1]['eye_data']
                curr_data = tracking_data[i]['eye_data']
                
                prev_left = prev_data['left_eye']['center']
                curr_left = curr_data['left_eye']['center']
                prev_right = prev_data['right_eye']['center']
                curr_right = curr_data['right_eye']['center']
                
                # 绘制左眼轨迹
                cv2.line(frame, 
                         (int(prev_left[0] * frame.shape[1]), int(prev_left[1] * frame.shape[0])),
                         (int(curr_left[0] * frame.shape[1]), int(curr_left[1] * frame.shape[0])),
                         (0, 255, 0), 2)
                
                # 绘制右眼轨迹
                cv2.line(frame, 
                         (int(prev_right[0] * frame.shape[1]), int(prev_right[1] * frame.shape[0])),
                         (int(curr_right[0] * frame.shape[1]), int(curr_right[1] * frame.shape[0])),
                         (255, 0, 0), 2)
        
        cv2.putText(frame, "眼动追踪中...", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Eye Tracking', frame)
        cv2.waitKey(1)
    
    @staticmethod
    def _rotate_image(img: np.ndarray, angle: int) -> np.ndarray:
        """旋转图像"""
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, M, (w, h))
    
    def cleanup(self):
        """清理资源"""
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_mesh.close()
        self.hands.close()

# 使用示例
if __name__ == "__main__":
    try:
        advanced_tester = AdvancedVisionTest()
        report = advanced_tester.start_comprehensive_test()
        
        print("\n=== 综合视力检测报告 ===")
        print(f"测试时间: {report['test_timestamp']}")
        print(f"整体评估: {report['overall_assessment']}")
        print("\n建议:")
        for rec in report['recommendations']:
            print(f"- {rec}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
    finally:
        if 'advanced_tester' in locals():
            advanced_tester.cleanup() 