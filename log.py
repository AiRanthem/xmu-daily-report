# 日志配置
import io
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def get_log_string() -> str:
    txt = log_stream.getvalue()
    log_stream.truncate(0)
    return txt
