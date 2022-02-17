# coding: utf-8
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

sendAddress = 'mail.sender.googl@gmail.com'
password = 'efxBfx2GJHWb25E'

def sendmail(subject='件名', bodyText='本文', fromAddress='hideki.tanji@gmail.com', toAddress='hideki.tanji@gmail.com'):

    # SMTPサーバに接続
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpobj.starttls()
    smtpobj.login(sendAddress, password)

    # メール作成
    msg = MIMEText(bodyText)
    msg['Subject'] = subject
    msg['From'] = fromAddress
    msg['To'] = toAddress
    msg['Date'] = formatdate()

    # 作成したメールを送信
    smtpobj.send_message(msg)
    smtpobj.close()

if __name__ == "__main__":
    sendmail()
