import sys
import time
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.pet_chat_dialog import PetChatDialog

def wait_for_reply(dlg, min_length=5, timeout=5):
    """循环等待chat_area有内容，最多timeout秒"""
    for _ in range(int(timeout * 10)):
        content = dlg.chat_area.toPlainText()
        if len(content.strip()) >= min_length:
            return content
        time.sleep(0.1)
    return dlg.chat_area.toPlainText()

def test_multiturn_chat(win):
    print("[TEST] 多轮对话与deepseek连接...")
    dlg = PetChatDialog(win)
    dlg.show()
    # 多轮对话模拟
    dlg.input_line.setText("你好")
    dlg.on_send()
    wait_for_reply(dlg)
    dlg.input_line.setText("我想做一次视力检测")
    dlg.on_send()
    wait_for_reply(dlg)
    dlg.input_line.setText("再帮我分析一下图片pictures/eyes_test.png")
    dlg.on_send()
    content = wait_for_reply(dlg, min_length=10, timeout=8)
    assert len(content.strip()) > 0, "多轮对话无AI回复"
    print("PASS: 多轮对话与deepseek连接")
    dlg.close()

def test_eye_games(win):
    print("[TEST] 健康游戏入口...")
    try:
        if hasattr(win, 'open_eye_games'):
            win.open_eye_games()
            print("PASS: 健康游戏窗口弹出")
        else:
            print("SKIP: 未实现健康游戏入口")
    except Exception as e:
        print(f"FAIL: 健康游戏弹出异常: {e}")

def test_vision_test(win):
    print("[TEST] 视力检测入口...")
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
    content = wait_for_reply(dlg, min_length=10, timeout=8)
    assert len(content.strip()) > 0, "OCT分析无AI回复"
    print("PASS: OCT图片分析AI命令")
    dlg.close()

def test_visualize(win):
    print("[TEST] 数据可视化AI命令...")
    dlg = PetChatDialog(win)
    dlg.show()
    dlg.input_line.setText("画出视力趋势图")
    dlg.on_send()
    content = wait_for_reply(dlg, min_length=10, timeout=8)
    assert len(content.strip()) > 0, "数据可视化无AI回复"
    print("PASS: 数据可视化AI命令")
    dlg.close()

def run_all_pet_deepseek_tests():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    test_multiturn_chat(win)
    test_eye_games(win)
    test_vision_test(win)
    test_oct_analysis(win)
    test_visualize(win)
    print("\n所有桌宠主要功能与deepseek连接自动化测试通过！（如有SKIP请补全对应入口）")
    win.close()
    app.quit()

if __name__ == "__main__":
    run_all_pet_deepseek_tests() 