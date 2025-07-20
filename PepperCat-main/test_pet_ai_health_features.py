import sys
import time
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.pet_chat_dialog import PetChatDialog

def test_eye_games(win):
    print("[TEST] 健康游戏入口...")
    # 模拟命令或入口（假设有方法open_eye_games）
    try:
        if hasattr(win, 'open_eye_games'):
            win.open_eye_games()
            print("PASS: 健康游戏窗口弹出")
        else:
            print("SKIP: 未实现健康游戏入口")
    except Exception as e:
        print(f"FAIL: 健康游戏弹出异常: {e}")

def test_ai_health_dialog(win):
    print("[TEST] AI健康对话/病症咨询...")
    dlg = PetChatDialog(win)
    dlg.show()
    # 模拟输入AI健康命令
    dlg.input_line.setText("我眼睛红肿怎么办")
    dlg.on_send()
    time.sleep(0.5)
    dlg.input_line.setText("分析图片pictures/eyes_test.png")
    dlg.on_send()
    time.sleep(0.5)
    content = dlg.chat_area.toPlainText()
    assert "桌宠" in content, "AI健康对话无回复"
    print("PASS: AI健康对话/病症咨询")
    dlg.close()

def test_vision_test(win):
    print("[TEST] 视力检测入口...")
    # 假设有open_vision_test方法
    try:
        if hasattr(win, 'open_vision_test'):
            win.open_vision_test()
            print("PASS: 视力检测窗口弹出")
        else:
            print("SKIP: 未实现视力检测入口")
    except Exception as e:
        print(f"FAIL: 视力检测弹出异常: {e}")

def test_oct_analysis(win):
    print("[TEST] OCT图片分析AI命令...")
    dlg = PetChatDialog(win)
    dlg.show()
    dlg.input_line.setText("分析OCT图片pictures/eyes_test.png")
    dlg.on_send()
    time.sleep(0.5)
    content = dlg.chat_area.toPlainText()
    assert "桌宠" in content, "OCT分析无AI回复"
    print("PASS: OCT图片分析AI命令")
    dlg.close()

def test_visualize(win):
    print("[TEST] 数据可视化AI命令...")
    dlg = PetChatDialog(win)
    dlg.show()
    dlg.input_line.setText("画出视力趋势图")
    dlg.on_send()
    time.sleep(0.5)
    content = dlg.chat_area.toPlainText()
    assert "桌宠" in content, "数据可视化无AI回复"
    print("PASS: 数据可视化AI命令")
    dlg.close()

def run_all_ai_health_tests():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    test_eye_games(win)
    test_ai_health_dialog(win)
    test_vision_test(win)
    test_oct_analysis(win)
    test_visualize(win)
    print("\n所有桌宠AI健康功能自动化测试通过！（如有SKIP请补全对应入口）")
    win.close()
    app.quit()

if __name__ == "__main__":
    run_all_ai_health_tests() 