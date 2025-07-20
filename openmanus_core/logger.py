import logging
import sys
from pathlib import Path

# 配置日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# 创建日志目录
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# 配置根日志记录器
def setup_logger(name: str = "openmanus") -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # 避免重复添加处理器
        logger.setLevel(LOG_LEVEL)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVEL)
        console_formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_dir / "openmanus.log", encoding='utf-8')
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# 创建默认日志记录器
logger = setup_logger("openmanus") 