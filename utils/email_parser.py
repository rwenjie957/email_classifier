from email.parser import BytesParser
from email.policy import default
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

# 提取邮件的发件人，主题和正文内容
def parseEmail(raw_email):
    parser = BytesParser(policy=default)
    msg = parser.parsebytes(raw_email)
    # 打印邮件头部信息
    main_info = f'''发件人: {msg["From"]}\n主题: {msg["Subject"]}\n'''
    # 获取邮件正文内容
    main_info += f"正文:"
    part_nums = 1;
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":          # 不处理附件
            continue

        if part.get_content_type() == "text/plain":
            main_info += f'\n------------part{part_nums}-------------\n'
            part_nums += 1
            content = part.get_content()
            main_info += (content + '\n')
        elif part.get_content_type() == "text/html":
            main_info += f'\n------------part{part_nums}-------------\n'
            main_info += "<html>\n"
            html = part.get_content()
            main_info += (parseHTML(html) +'\n')
            main_info += "</html>\n"
        
    return main_info


def parseHTML(html):
    soup = BeautifulSoup(html, 'lxml')
    text = soup.get_text().strip()
    text = re.sub(r'\x20{2,}', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub('\t', '', text)
    return text