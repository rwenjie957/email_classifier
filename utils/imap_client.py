import imaplib
import logging
from pathlib import Path
import json


logger = logging.getLogger(__name__)

class IMAP:
    def __init__(self, config: dict):
        self.m = imaplib.IMAP4_SSL(host=config["imap_server"])
        self.m.login(config["user"], config["password"])
        logger.debug("登陆成功")

    def close(self):
        self.m.logout()
        logger.debug("退出成功")

    @staticmethod
    def str2utf7(folder):               #处理非ascii码文件夹
        return folder.encode('utf-7').decode().replace('+', '&')
    
    def get_email_uids(self, type_="UNSEEN", folder="INBOX"):
        folder = self.str2utf7(folder)
        message_UID=[]
        
        status, response = self.m.select(folder)
        if status!="OK":
            logger.error(response)                  # 如果目标文件夹不存在就报错
            raise

        status, emails=self.m.uid("SEARCH", None, type_)
        if(not len(emails[0])):
            logger.info(f"没有{type_}邮件")
        else:
            for i in emails[0].decode().split():
                message_UID.append(i)
        self.m.close()
        return message_UID
    
    def get_email_content(self, uid, folder="INBOX"):
        folder = self.str2utf7(folder)
        status, response = self.m.select(folder)
        if status!="OK":
            logger.error(response)
            raise
        status, email = self.m.uid("FETCH", uid, "(RFC822)")
        self.m.close()
        return email[0][1]
    
    def move(self, uids: int|str|list, dst_folder, src_folder="INBOX"):
        dst_folder=self.str2utf7(dst_folder)
        src_folder=self.str2utf7(src_folder)

        if isinstance(uids, str):
            uid_str = uids
        elif isinstance(uids, int):
            uid_str = str(uids)
        elif isinstance(uids, list):
            uid_str = ','.join(uids)
        else:
            logger.error(f"uids类型错误")
            return

        status, response = self.m.select(src_folder)
        if status!="OK":
            logger.error(response)
            raise 

        status, _ = self.m.uid("COPY", uid_str, dst_folder)

        if isinstance(uids, list):
            for uid in uids:
                self.m.uid('STORE', uid, '+FLAGS', '\\Deleted')
        else:
            self.m.uid('STORE', uid_str, '+FLAGS', '\\Deleted')
        self.m.expunge()
        self.m.close()
        logger.info(f"{uid_str}已移动至{dst_folder}")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s"
    )
    import json
    with open('../config.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    