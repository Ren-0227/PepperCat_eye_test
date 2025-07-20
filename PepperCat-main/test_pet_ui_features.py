import sys
import time
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.pet_chat_dialog import PetChatDialog
from src.ui.upgrade_machine import UpgradeMachine
from src.ui.battle_dialog import BattleDialog

def test_main_window():
    print("[TEST] 主窗口显示...")
    win = MainWindow()
    win.show()
    assert win.isVisible(), "主窗口未显示"
    print("PASS: 主窗口显示")
    return win

def test_bubble_menu(win):
    print("[TEST] 右键菜单弹出...")
    win.show_bubble_menu(win.pet_widget.rect().center())
    assert win.bubble_menu.isVisible(), "气泡菜单未弹出"
    print("PASS: 气泡菜单弹出")

def test_chat_dialog(win):
    print("[TEST] 聊天窗口弹出...")
    dlg = PetChatDialog(win)
    dlg.show()
    assert dlg.isVisible(), "聊天窗口未弹出"
    print("PASS: 聊天窗口弹出")
    dlg.close()

def test_upgrade_machine(win):
    print("[TEST] 升级窗口弹出...")
    dlg = UpgradeMachine(win)
    dlg.show()
    assert dlg.isVisible(), "升级窗口未弹出"
    print("PASS: 升级窗口弹出")
    dlg.close()

def test_battle_dialog(win):
    print("[TEST] 对战窗口弹出...")
    dlg = BattleDialog(win)
    dlg.show()
    assert dlg.isVisible(), "对战窗口未弹出"
    print("PASS: 对战窗口弹出")
    dlg.close()

def test_follow_toggle(win):
    print("[TEST] 跟随/停止跟随切换...")
    win.follow_mouse_enabled = False
    win.toggle_follow_mouse()
    assert win.follow_mouse_enabled, "跟随未开启"
    win.toggle_follow_mouse()
    assert not win.follow_mouse_enabled, "跟随未关闭"
    print("PASS: 跟随/停止跟随切换")

def run_all_tests():
    app = QApplication(sys.argv)
    win = test_main_window()
    test_bubble_menu(win)
    test_chat_dialog(win)
    test_upgrade_machine(win)
    test_battle_dialog(win)
    test_follow_toggle(win)
    print("\n所有桌宠UI核心功能自动化测试通过！")
    # 关闭主窗口
    win.close()
    app.quit()

if __name__ == "__main__":
    run_all_tests() 