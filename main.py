from utils.classifier import LLM
from utils.imap_client import IMAP
from utils.utils import * 
from utils.email_parser import *
import json
import logging
from pathlib import Path


cfg = load_config('config.json')
categories = load_config("categories.json")
system_prompt = load_prompts(cfg["enabled_categories"])

llm = LLM(cfg['llm_service'])
log_path = Path(cfg["logs"]["log_dir"]) / 'log.txt'


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
    logger.debug(f"正在处理邮箱:{box["userCredentials"]["imap_server"]}")
    i = IMAP(box["userCredentials"])
    emails=i.get_email_uids(box["policy"], box["default_directory"])
    for uid in emails:
        logger.info(f"正在处理邮件{uid}")
        content = parseEmail(i.get_email_content(uid))
        logger.debug(content)

        reason, result = llm.classify(system_prompt, content)
        logger.debug(reason)
        logger.info(result)
        
        try:
            result = json.loads(result)
        except:
            logger.warning("json解析错误")
            continue    
    
        c = categories[result['type']]
        i.move(uid, c['folder'])
        for f in c['result_fields']:
            print(result[f])
    i.close()