from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
import datetime
from src.tools.web_search import web_search

class AICommandDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("智能命令对话框")
        self.setFixedSize(480, 320)
        layout = QVBoxLayout(self)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("请输入你的需求，如：帮我查找现在的时间")
        self.result = QTextEdit(self)
        self.result.setReadOnly(True)
        self.btn = QPushButton("执行", self)
        layout.addWidget(self.input)
        layout.addWidget(self.result)
        layout.addWidget(self.btn)
        self.input.returnPressed.connect(self.run_command)
        self.btn.clicked.connect(self.run_command)

    def run_command(self):
        text = self.input.text().strip()
        if not text:
            return
        if "时间" in text:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.result.append(f"现在的时间是：{now}")
        elif "美国总统" in text:
            answer = web_search("current president of the United States")
            self.result.append(f"搜索结果：\n{answer}")
        elif "搜索" in text:
            # 例如“帮我搜索现在的美国总统是谁”
            query = text.replace("帮我搜索", "").strip()
            answer = web_search(query)
            self.result.append(f"搜索结果：\n{answer}")
        else:
            self.result.append("暂不支持该命令。") 