import time
from datetime import datetime

from app.models.pitch_setting import AnswerMode




t1 = int(datetime.now().timestamp())
t2 = int(time.time())
print(AnswerMode.CONCORDANCE.to_dict().get("index"))
print(AnswerMode.CONCORDANCE.__index__())