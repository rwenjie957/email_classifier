from pathlib import Path
import json
import logging
import re
from shutil import copy

logger = logging.getLogger(__name__)

def load_config(file):
    f = Path(file)
    if not f.exists():
        if file=="config.json":
            copy('config_example.json', f)
        elif file=="categories.json":
            copy('categories_example.json', f)
        logger.error("配置文件不存在，已自动创建，请修改后再运行")
        raise FileNotFoundError
    
    with open(f, 'r', encoding='utf-8') as cfg:
        config = json.load(cfg)
    return config

def load_prompts(enabled_categories, dir_="prompts"):
    f = Path(dir_)
    if not f.exists():
        raise FileNotFoundError
    
    system_prompt = ""
    with open(f / "base.md", "r", encoding="utf-8") as p1:
        s_p = re.split('<categories>', p1.read())
    
    system_prompt += s_p[0]
    part = s_p[1]
    
    for i in enabled_categories:
        sub_prompts = f / (i + ".md")
        if not sub_prompts.exists():
            logger.warning(f"分类模板 {sub_prompts} 不存在！")
            continue
        with open(f / (i + ".md"), "r", encoding="utf-8") as p2:
            temp = re.split("EXAMPLE JSON OUTPUT:", p2.read())
        
        system_prompt += temp[0].strip() + '\n\n'
        part += temp[1].strip() + '\n'
    system_prompt += part
    
    return system_prompt


if __name__ == '__main__':
    enabled_categories=["bill","advertisment","reminder","update","verification","others"]
    p = load_prompts(enabled_categories, '../prompts')
    print(p)
