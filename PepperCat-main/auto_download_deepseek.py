import subprocess
import sys
import shutil

MODEL_NAME = "deepseek-coder"  # 或 deepseek-llm

def is_ollama_installed():
    return shutil.which("ollama") is not None

def is_model_downloaded(model_name):
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10
        )
        return model_name in result.stdout
    except Exception as e:
        print(f"[错误] 检查模型时出错: {e}")
        return False

def download_model(model_name):
    print(f"正在下载模型 {model_name}，请耐心等待...")
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in process.stdout:
            print(line, end="")
        process.wait()
        if process.returncode == 0:
            print(f"[完成] 模型 {model_name} 下载成功。")
            return True
        else:
            print(f"[失败] 模型下载失败，请检查网络或Ollama配置。")
            return False
    except Exception as e:
        print(f"[错误] 下载模型时出错: {e}")
        return False

def main():
    if not is_ollama_installed():
        print("[提示] 未检测到 Ollama，请先安装 Ollama：https://ollama.com/")
        sys.exit(1)
    if is_model_downloaded(MODEL_NAME):
        print(f"[提示] 已检测到本地存在模型 {MODEL_NAME}，无需重复下载。")
    else:
        print(f"[提示] 未检测到本地模型 {MODEL_NAME}，即将自动下载。")
        download_model(MODEL_NAME)

if __name__ == "__main__":
    main()