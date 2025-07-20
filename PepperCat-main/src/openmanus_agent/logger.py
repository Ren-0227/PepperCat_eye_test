import sys
from datetime import datetime
from loguru import logger as _logger

_print_level = "INFO"
def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    global _print_level
    _print_level = print_level
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )
    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    # _logger.add(PROJECT_ROOT / f"logs/{log_name}.log", level=logfile_level)  # 可选本地日志
    return _logger
logger = define_log_level() 