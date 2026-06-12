from utils import *
from classifier import *
import json
import logging
from pathlib import Path

cfg = load_config()
api_key = cfg["llm_service"]["api_key"]
base_url = cfg["llm_service"]["base_url"]
model = cfg["llm_service"]["model"]
log_path = Path(cfg["logs"]["dir"]) / 'log.txt'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


for box in cfg['imap_settings']:
    logger.info(f"正在处理邮箱:{box["imap_server"]}")
    i = IMAP(box["imap_server"], box["user"], box["password"])
    emails=i.get_email_uids(box["policy"], box["default_directory"])
    for uid in emails:
        logger.info(f"正在处理邮件{uid}")
        content = parseEmail(i.get_email_content(uid))
        reason, result_str = classifer(api_key, 'prompt.md', content, base_url, model)
        logger.debug(reason)
        logger.info(result_str)
        logger.debug(content)
        result = json.loads(result_str)
        if result['type']=='reminder':
            i.move(uid, '提醒')
        elif result['type']=='verification':
            i.move(uid, '验证码')
        elif result['type']=='bill':
            i.move(uid, '账单')
            print(result['amount']+ result['currency'])
        elif result['type']=='update':
            i.move(uid, '更新')
        elif result['type']=='advertisement':
            i.move(uid, '广告')
        elif result['type']=='others':
            i.move(uid, '其它')
    i.close()