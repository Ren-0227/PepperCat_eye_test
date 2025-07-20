from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QPixmap
import threading
import asyncio
from src.openmanus_agent.mcp_patch import PatchedMCPAgent
from src.openmanus_agent.web_search import WebSearchTool
from src.openmanus_agent.file_ops import FileOpsTool
from src.openmanus_agent.tool_collection import ToolCollection
from src.openmanus_agent.file_tools import ReadFileTool
from src.openmanus_agent.visualize_tool import VisualizeTool
from src.openmanus_agent.deepseek_qa import DeepseekQATool
import re
import base64
from src.tools.eye_games import EyeGamesTool
from src.tools.image_analysis import ImageAnalysisTool
from src.tools.vision_test import VisionTestTool

class PetChatDialog(QDialog):
    message_ready = pyqtSignal(str, str)  # sender, text

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("智能命令 · 桌宠对话")
        self.setFixedSize(520, 540)
        self.setStyleSheet("""
            QDialog { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fafc, stop:1 #e3e6ed); border-radius: 20px; }
            QLabel#titleLabel { font-size: 28px; font-weight: bold; color: #2d3a4b; margin-bottom: 8px; }
            QLabel#subtitleLabel { font-size: 16px; color: #4b5a6a; margin-bottom: 12px; }
            QTextEdit, QLineEdit { background: #fff; border-radius: 10px; font-size: 16px; }
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #388E3C); color: #fff; border-radius: 10px; font-size: 18px; font-weight: bold; min-width: 100px; min-height: 44px; }
            QPushButton:hover { background: #43a047; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)
        # 标题
        title = QLabel("🐾 智能命令 · 桌宠对话")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        subtitle = QLabel("和你的AI桌宠畅聊，获取知识、自动调用工具链！")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        # 聊天区
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Consolas", 14))
        self.chat_area.setMinimumHeight(320)
        layout.addWidget(self.chat_area)
        # 输入区
        input_row = QHBoxLayout()
        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("请输入问题或命令，如：查天气并保存到文件/讲讲强化学习/写入文件...")
        self.input_line.setFont(QFont("Arial", 14))
        self.send_btn = QPushButton("发送", self)
        self.send_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.send_btn.setFixedHeight(48)
        input_row.addWidget(self.input_line, 4)
        input_row.addWidget(self.send_btn, 1)
        layout.addLayout(input_row)
        self.send_btn.clicked.connect(self.on_send)
        self.input_line.returnPressed.connect(self.on_send)
        self.history = []  # 用于多轮对话上下文
        self.message_ready.connect(self.append_message)

    def on_send(self):
        user_text = self.input_line.text().strip()
        if not user_text:
            return
        self.append_message("user", user_text)
        self.input_line.clear()
        self.send_btn.setEnabled(False)
        threading.Thread(target=self._run_mcp, args=(user_text,), daemon=True).start()

    def _run_mcp(self, user_text):
        # 在子线程中调用 asyncio 运行 MCPAgent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._call_mcp(user_text))
        self.message_ready.emit("pet", result)
        self.send_btn.setEnabled(True)

    async def _call_mcp(self, user_text):
        agent = PatchedMCPAgent()
        agent.available_tools = ToolCollection(
            WebSearchTool(), FileOpsTool(),
            ReadFileTool(), VisualizeTool(), DeepseekQATool(),
            EyeGamesTool(), ImageAnalysisTool(), VisionTestTool()
        )
        await agent.initialize()
        # 1. 让LLM输出plan
        # 构造messages和system_msgs
        messages = [type('Msg', (), {'content': user_text})()]
        system_msgs = [type('Msg', (), {'content': agent.system_prompt})()]
        plan = await agent.llm.ask_tool(messages, system_msgs=system_msgs)
        if hasattr(plan, 'content'):
            plan_str = plan.content
        else:
            plan_str = str(plan)
        self.message_ready.emit("pet", f"📝 任务规划：<br>{plan_str.replace(chr(10), '<br>')}")
        # 2. 解析plan
        steps = self.parse_plan(plan_str)
        last_result = None
        for i, step in enumerate(steps):
            tool_name = step['tool'].lower()
            args = step['args']
            tool = agent.available_tools.tool_map.get(tool_name)
            if not tool:
                self.message_ready.emit("pet", f"❌ 未找到工具：{tool_name}")
                continue
            try:
                # 简单参数处理：如果args里有(上一步结果)，替换为last_result
                for k, v in args.items():
                    if isinstance(v, str) and '(上一步结果' in v:
                        args[k] = last_result or ''
                result = await tool.execute(**args)
                self.message_ready.emit("pet", f"✅ [{tool_name}] 结果：<br>{result}")
                # 新增：如果是visualize，自动调用deepseekqa总结
                if tool_name == "visualize":
                    # 尝试找到原始数据内容
                    data_for_summary = args.get("data", "")
                    summary_tool = agent.available_tools.tool_map.get("deepseekqa")
                    if summary_tool and data_for_summary:
                        summary = await summary_tool.execute(data=data_for_summary, question="请用一句话总结这组数据")
                        self.message_ready.emit("pet", f"🧠 总结：<br>{summary}")
                # 新增：如果是image_analysis，自动调用deepseekqa生成详细报告
                elif tool_name == "image_analysis":
                    analysis_result = result
                    summary_tool = agent.available_tools.tool_map.get("deepseekqa")
                    if summary_tool:
                        detailed_report = await summary_tool.execute(data=analysis_result, question="请基于这个眼部检测结果，生成一份详细的健康建议报告，包括预防措施、注意事项和就医建议")
                        self.message_ready.emit("pet", f"🏥 详细健康报告：<br>{detailed_report}")
                last_result = result
            except Exception as e:
                self.message_ready.emit("pet", f"❌ [{tool_name}] 执行出错：{e}")
        return last_result or "任务已完成"

    def parse_plan(self, plan_str):
        # 解析 [stepX]-toolname: arg1, arg2 结构，并智能提取参数
        import re
        steps = []
        for line in plan_str.strip().splitlines():
            m = re.match(r'\[step(\d+)\]-(\w+):(.+)', line.strip())
            if m:
                tool = m.group(2).strip().lower()
                arg_str = m.group(3).strip().strip('"')
                # 自动将(stepN结果)等替换为(上一步结果)
                arg_str = re.sub(r'\(step\d+结果\)', '(上一步结果)', arg_str)
                # 智能参数提取
                if tool == 'websearchtool':
                    args = {'query': arg_str}
                elif tool == 'fileopstool':
                    # 更宽松地提取csv/文件名
                    file_match = re.search(r'([\w\-_.]+\.csv)', arg_str, re.I)
                    if not file_match:
                        file_match = re.search(r'保存到[\s\'\"]*([\w\-_.]+)', arg_str)
                    filename = file_match.group(1) if file_match else 'weather.csv'
                    # 只取前两个参数，忽略多余参数
                    parts = [p.strip() for p in arg_str.split(',') if p.strip()]
                    content = '(上一步结果)'
                    if len(parts) > 1:
                        # 如果第二个参数不是(上一步结果)，用它，否则兜底
                        if '(上一步结果)' in parts[1]:
                            content = '(上一步结果)'
                        else:
                            content = parts[1]
                    args = {'filename': filename, 'content': content}
                elif tool == 'read_file':
                    file_match = re.search(r'["\']([\w\-_.]+\.\w+)["\']', arg_str)
                    filename = file_match.group(1) if file_match else arg_str
                    args = {'filename': filename}
                elif tool == 'visualize':
                    parts = [x.strip() for x in arg_str.split(',', 1)]
                    args = {'data': parts[0], 'chart_type': parts[1] if len(parts)>1 else 'line'}
                elif tool == 'deepseekqa' or tool == 'deepseek_qa':
                    # 只取前两个参数，忽略多余参数
                    parts = [p.strip() for p in arg_str.split(',') if p.strip()]
                    data = '(上一步结果)'
                    question = ''
                    if len(parts) > 1:
                        if '(上一步结果)' in parts[0]:
                            data = '(上一步结果)'
                        else:
                            data = parts[0]
                        question = parts[1]
                    elif len(parts) == 1:
                        question = parts[0]
                    args = {'data': data, 'question': question}
                elif tool == 'eyegames' or tool == 'eye_games':
                    # 解析眼部游戏类型
                    game_type = 'all'  # 默认启动所有游戏
                    if '记忆' in arg_str or 'memory' in arg_str.lower():
                        game_type = 'memory'
                    elif '专注' in arg_str or 'focus' in arg_str.lower():
                        game_type = 'focus'
                    elif '反应' in arg_str or 'reaction' in arg_str.lower():
                        game_type = 'reaction'
                    args = {'game_type': game_type}
                elif tool == 'image_analysis':
                    # 解析图像分析参数
                    parts = [x.strip() for x in arg_str.split(',', 1)]
                    args = {'image_path': parts[0]}
                else:
                    args = {'input': arg_str}
                steps.append({'tool': tool, 'args': args})
        return steps

    def append_message(self, sender, text):
        # 检查是否为base64图片
        if sender == "pet" and isinstance(text, str) and text.strip().startswith("data:image/png;base64,"):
            self.show_image_from_base64(text.strip())
            return  # 不在聊天区插入图片base64文本
        # 只展示用户消息和AI的最终总结（如deepseekqa），不展示step计划和中间结果
        if sender == "user":
            html = f'<div style="text-align:right; margin:18px 0 18px 40px;"><span style="display:inline-block; background:#e0f7fa; color:#00796b; border-radius:16px; padding:12px 20px; max-width:70%; font-size:16px;">{text}</span></div>'
            self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
            self.chat_area.insertHtml(html)
            self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
        elif sender == "pet":
            # 只展示deepseekqa/总结类消息
            if text.strip().startswith("🧠 总结：") or text.strip().startswith("✅ [deepseekqa]") or text.strip().startswith("✅ [deepseek_qa]"):
                # 去掉多余前缀
                summary_text = re.sub(r"^✅ \\[deepseekqa\\] 结果：<br>|^✅ \\[deepseek_qa\\] 结果：<br>", "", text.strip())
                html = f'<div style="text-align:left; margin:18px 40px 18px 0;"><span style="display:inline-block; background:#fffde7; color:#795548; border-radius:16px; padding:12px 20px; max-width:70%; font-size:16px;">{summary_text}</span></div>'
                self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
                self.chat_area.insertHtml(html)
                self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
                # 新增：用TTS音色克隆合成语音并播放
                try:
                    self.speak_with_user_voice(summary_text)
                except Exception as e:
                    print(f"[TTS语音合成失败] {e}")
        # 其它AI消息（如📝 任务规划、step提示等）不展示在聊天区，仅后台处理

    def show_image_from_base64(self, base64_str):
        if base64_str.startswith("data:image/png;base64,"):
            img_data = base64.b64decode(base64_str.split(",", 1)[1])
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            dlg = QDialog(self)
            dlg.setWindowTitle("可视化结果")
            layout = QVBoxLayout(dlg)
            label = QLabel()
            label.setPixmap(pixmap)
            layout.addWidget(label)
            dlg.setFixedSize(pixmap.width()+40, pixmap.height()+40)
            dlg.exec()

    def speak_with_user_voice(self, text):
        """用Coqui TTS和用户音色合成语音并播放"""
        import os
        from TTS.api import TTS
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PyQt6.QtCore import QUrl
        # 检查音色样本
        user_voice = "user_voice.wav"
        if not os.path.exists(user_voice):
            print("[TTS] 未找到用户音色样本user_voice.wav，跳过语音合成")
            return
        # 合成语音
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)
        tts.tts_to_file(text=text, speaker_wav=user_voice, file_path="pet_tts_out.wav")
        # 播放
        audio_output = QAudioOutput()
        player = QMediaPlayer()
        player.setAudioOutput(audio_output)
        player.setSource(QUrl.fromLocalFile(os.path.abspath("pet_tts_out.wav")))
        audio_output.setVolume(0.8)
        player.play() 