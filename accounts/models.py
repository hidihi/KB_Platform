from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# User DB
class User(AbstractUser):
    # 이달의 출석 횟수
    check_cnt = models.PositiveIntegerField(default=0, blank=True, null=False)
    # 이달의 성공 횟수
    success = models.PositiveIntegerField(default=0, blank=True, null=False)
    # 오늘 게임을 했나 안했나의 여부 check
    tmp = models.IntegerField(default=-1, blank=True, null=False)
    # 내가 한 찍은 결과 값
    my_result = models.IntegerField(default=0, blank=True, null=False)