import time
from datetime import datetime

from OpenSSL import crypto

from app.models.pitch_setting import AnswerMode



#
# t1 = int(datetime.now().timestamp())
# t2 = int(time.time())
# print(AnswerMode.CONCORDANCE.to_dict().get("index"))
# print(AnswerMode.CONCORDANCE.__index__())


def get_serial_no_from_cert( cert_path):
    with open(cert_path, 'r') as f:
        cert_content = f.read()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_content)
    return cert.get_serial_number()


sn = get_serial_no_from_cert("/home/yu/gitdev/shengyibaodian/app/wepay/apiclient_cert.pem")
print(sn)