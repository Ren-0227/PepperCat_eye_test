#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌宠应用主程序
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec()) 