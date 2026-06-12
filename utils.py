import imaplib
from email.parser import BytesParser
from email.policy import default
from bs4 import BeautifulSoup
import re
import logging
from pathlib import Path
import json


logger = logging.getLogger(__name__)

class IMAP:
    def __init__(self, host, user, password):
        self.m = imaplib.IMAP4_SSL(host=host)
        self.m.login(user, password)
        logger.debug("登陆成功")

    def close(self):
        self.m.logout()
        logger.debug("退出成功")

    def get_email_uids(self, type_="UNSEEN", folder="INBOX"):
        message_UID=[]
        self.m.select(folder)
        status, emails=self.m.uid("SEARCH", None, type_)
        if(not len(emails[0])):
            logger.info(f"没有{type_}邮件")
        else:
            for i in emails[0].decode().split():
                message_UID.append(i)
        self.m.close()
        return message_UID
    
    def get_email_content(self, uid, folder="INBOX"):
        self.m.select(folder)
        status, email = self.m.uid("FETCH", uid, "(RFC822)")
        self.m.close()
        return email[0][1]
    
    def move(self, uids, dst_folder, src_folder="INBOX"):
        dst_folder=dst_folder.encode('utf-7').decode().replace('+', '&')    #处理非ascii码文件夹
        if isinstance(uids, str):
            uid_str = uids
        elif isinstance(uids, int):
            uid_str = str(uids)
        elif isinstance(uids, list):
            uid_str = ','.join(uids)
        else:
            logger.error(f"uids类型错误")
            return
        
        self.m.select("INBOX")
        status, _ = self.m.uid("COPY", uid_str, dst_folder)

        if isinstance(uids, list):
            for uid in uids:
                self.m.uid('STORE', uid, '+FLAGS', '\\Deleted')
        else:
            self.m.uid('STORE', uid_str, '+FLAGS', '\\Deleted')
        self.m.expunge()
        self.m.close()
        logger.info(f"{uid_str}已移动")


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


def load_config(file='config.json'):
    f = Path(file)
    if not f.exists():
        logger.error("配置文件不存在，已自动创建")
        Path.copy('config_example.json', f)
        raise FileNotFoundError
    with open(f, 'r', encoding='utf-8') as cfg:
        config = json.load(cfg)
    return config


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s"
    )
    config = load_config()
    
    box1 = config['imap_settings'][0]
    i = IMAP(box1['imap_server'], box1['user'], box1['password'])

    news = i.get_email_uids('ALL')[0]
    if news:
        for n in news:
            raw = i.get_email_content(n)
            logger.info(parseEmail(raw))
            print(parseEmail(raw), flush=True)
            break
    i.close()
