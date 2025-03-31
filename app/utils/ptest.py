from app.models.pitch_setting import AnswerMode


print(AnswerMode.CONCORDANCE.to_dict().get("index"))
print(AnswerMode.CONCORDANCE.__index__())

