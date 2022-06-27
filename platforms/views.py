from django.shortcuts import get_object_or_404, redirect, render
from . models import Card, Benefit, Account, Trans, LSTM
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
import datetime
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDate, Abs
from django.db.models import Func, F


# Create your views here.
def index(request):
    return render(request, 'platforms/index.html')

# --------------------- 은행 (전체계좌-상세계좌, 이체, 지점찾기) ---------------------
# 1. 전체 계좌 페이지


def total_accounts(request):
    # 해당 user에 해당하는 계좌 list
    all_accounts = Account.objects.filter(user=request.user)
    acc_total = sum(all_accounts.values_list('total', flat=True))

    account_0 = all_accounts.filter(acc_detail=0)
    account_1 = all_accounts.filter(acc_detail=1)
    account_2 = all_accounts.filter(acc_detail=2)

    ###### 입출금 자유 ######
    total_bank0 = []
    for i in range(len(account_0)):
        tmp = 0
        all_trans = Trans.objects.filter(account_id=account_0[i].acc_num)
        tmp_acc = Account.objects.get(acc_num=account_0[i].acc_num)
        for trans in all_trans:
            tmp += trans.trans_price
        total_bank0.append(tmp)
        tmp_acc.total = tmp
        tmp_acc.save()

    ###### 예금 / 적금 / 주택청약 ######
    total_bank1 = []
    for i in range(len(account_1)):
        tmp = 0
        all_trans = Trans.objects.filter(account_id=account_1[i].acc_num)
        tmp_acc = Account.objects.get(acc_num=account_1[i].acc_num)
        for trans in all_trans:
            tmp += trans.trans_price
        total_bank1.append(tmp)
        tmp_acc.total = tmp
        tmp_acc.save()

    ###### 골드 ######
    total_bank2 = []
    for i in range(len(account_2)):
        tmp = 0
        all_trans = Trans.objects.filter(account_id=account_2[i].acc_num)
        tmp_acc = Account.objects.get(acc_num=account_2[i].acc_num)
        for trans in all_trans:
            tmp += trans.trans_price
        total_bank2.append(tmp)
        tmp_acc.total = tmp
        tmp_acc.save()

    context = {
        'all_accounts': all_accounts,
        'account_0': account_0,
        'account_1': account_1,
        'account_2': account_2,
        'acc_total': acc_total,

        'sum_total0': sum(total_bank0),
        'sum_total1': sum(total_bank1),
        'sum_total2': sum(total_bank2),
    }
    return render(request, 'platforms/total_accounts.html', context)

# 2. 상세 계좌 페이지


def accounts(request, pk):
    account = get_object_or_404(Account, pk=pk)
    all_trans = account.trans.all().order_by('-id')
    tmp_trans = account.trans.all()

    trans_sum = sum(all_trans.values_list('trans_price', flat=True))
    totals = []
    result = 0
    for trans in tmp_trans:
        result += trans.trans_price
        totals.append(result)
    totals = totals[::-1]
    datas = zip(all_trans, totals)
    context = {
        "account": account,
        "all_trans": datas,
        'trans_sum': trans_sum,
    }
    return render(request, 'platforms/accounts.html', context)

# 3. 이체 페이지


def transfer(request, pk):
    account = Account.objects.get(pk=pk)
    if request.method == 'POST':
        # 내 계좌번호
        acc_pwd = request.POST['acc_pwd']
        acc_pwd = int(acc_pwd)
        # 입력받은 계좌 비번이랑 현재 비번이랑 일치할 때 이체 시작
        if account.acc_pwd == acc_pwd:
            # 거래 시간 얻기
            trans_date = datetime.datetime.now()
            trans_date = trans_date.replace(microsecond=0)

            # 보낼 계좌번호
            acc_num = request.POST['acc_num']

            # 금액을 int로 변환
            price = request.POST['trans_price']
            price = int(price)

            # 문구
            youContent = request.POST['youContent']
            meContent = request.POST['meContent']

            myTrans = Trans(trans_date=trans_date, trans_price=-price,
                            trans_content=meContent, trans_type=3, account_id=account.acc_num)
            youtTrans = Trans(trans_date=trans_date, trans_price=price,
                              trans_content=youContent, trans_type=3, account_id=acc_num)

            myTrans.save()
            youtTrans.save()
            return redirect('platforms:total_accounts')
    else:
        context = {
            "account": account
        }
        return render(request, 'platforms/transfer.html', context)

# 4. 지점찾기 페이지


def find_kb(request):
    return render(request, 'platforms/find_kb.html')

# --------- 증권 (주식계좌, 주식잔고, 주식차트, 종가 UP&DOWN-출석체크,결과보기) ---------
# 5. 주식 계좌 페이지


def stock_account(request):
    all_accounts = Account.objects.filter(
        user=request.user)  # 해당 user에 해당하는 계좌 list
    stock_acc = all_accounts.filter(acc_type=1)  # user의 증권 계좌

    total_bank0 = []
    for i in range(len(stock_acc)):
        tmp = 0
        all_trans = Trans.objects.filter(account_id=stock_acc[i].acc_num)
        tmp_acc = Account.objects.get(acc_num=stock_acc[i].acc_num)
        for trans in all_trans:
            tmp += trans.trans_price
        total_bank0.append(tmp)
        tmp_acc.total = tmp
        tmp_acc.save()

    context = {
        'all_accounts': stock_acc
    }
    return render(request, 'platforms/stock_account.html', context)

# 6. 주식 잔고 페이지


def stock(request):
    return render(request, 'platforms/stock.html')

# 7. 주식 차트 페이지


def stock_charts(request):
    return render(request, 'platforms/stock_charts.html')

# 8. 종가 UP&DOWN 페이지


def stock_game(request):
    # 마지막 ID로 주기!
    model = LSTM.objects.get(id=130)
    pred = model.pred

    context = {
        'pred': pred,
    }
    return render(request, 'platforms/stock_game.html', context)

# 9. 출석체크 페이지


def attendance(request):
    goldbaby = request.user
    model = LSTM.objects.get(id=130)
    act = model.act

    if goldbaby.tmp == -1:
        if act == goldbaby.my_result:
            goldbaby.success += 1
            goldbaby.save()

            trans_date = datetime.datetime.now()
            trans_date = trans_date.replace(microsecond=0)
            myTrans = Trans(trans_date=trans_date, trans_price=0.0019,
                            trans_content="KB금쪽리워드환급", trans_type=3, account_id="110-378-912021")
            myTrans.save()

    return render(request, 'platforms/attendance.html')

# 10. 결과보기 페이지


def updown_result(request):
    model = LSTM.objects.get(id=130)
    act = model.act
    user_act = request.user.my_result

    context = {
        'act': act,
        'user_act': user_act,
    }
    return render(request, 'platforms/updown_result.html', context)

# ----------------------------- 카드 (카드목록, 카드추천) -----------------------------
# 11. 카드목록 페이지


def cards(request):
    check_cards = Card.objects.filter(card_type=0)  # 체크카드 목록
    debit_cards = Card.objects.filter(card_type=1)  # 신용카드 목록

    benefits = Benefit.objects.all()  # 카드 혜택 목록
    context = {
        'check_cards': check_cards,
        'debit_cards': debit_cards,
        'benefits': benefits,
    }
    return render(request, 'platforms/cards.html', context)

# 12. 카드추천 페이지


def cards_recom(request):
    ### ========= 카드추천 알고리즘 ========= ###
    cards = [0, 0, 0, 0, 0, 0, 0]

    all_accounts = Account.objects.filter(
        user=request.user)  # 해당 user에 해당하는 계좌 list
    all_accounts = all_accounts.filter(
        acc_type=0)   # 해당 user의 은행 계좌만 (증권, 금 제외)

    # for 알고리즘
    cards = [0, 0, 0, 0, 0, 0, 0, 0]
    for j in range(len(cards)):
        # card 0번째 5번째 object 없음
        if j == 0 or j == 5:
            continue
        # 그렇지 않으면 확인 !
        else:
            # 카드에 해당 하는 benefits 뽑아내기
            benefits = Benefit.objects.filter(card_id=j)
            for i in range(len(all_accounts)):
                all_trans = Trans.objects.filter(
                    account_id=all_accounts[i].acc_num)

                for trans in all_trans:
                    # if trans.trans_date.year==2022 and trans.trans_date.month==3:
                    if trans.trans_date.year == 2022:
                        # 출금일 때만 type 체크
                        if trans.trans_price < 0:
                            # benefit 확인
                            for benefit in benefits:
                                # 해당 내용이 컨텐츠 안에 있다면
                                if trans.trans_content.find(benefit.service_name) != -1:
                                    # 할인이 %인것만
                                    if benefit.percent < 100:
                                        cards[j] += (trans.trans_price * -
                                                     1) * benefit.percent

    # 1, 3, 4
    check_max = max(cards[1], cards[3], cards[4])

    # 2, 6, 7
    debit_max = max(cards[2], cards[6], cards[7])

    for i in range(len(cards)):
        if cards[i] == check_max:
            check_id = i
        elif cards[i] == debit_max:
            debet_id = i

    # for 차트
    types = [0, 0, 0, 0, 0, 0]
    # 은행 계좌 for문
    for i in range(len(all_accounts)):
        all_trans = Trans.objects.filter(account_id=all_accounts[i].acc_num)
        for trans in all_trans:
            if trans.trans_date.year == 2022 and trans.trans_date.month == 5:
                # 출금일 때만 type 체크
                if trans.trans_price < 0:
                    # 소비 type이 0인 경우 :: 식비
                    if trans.trans_type == 0:
                        types[0] += trans.trans_price
                    # 소비 type이 1인 경우 :: 이동통신
                    elif trans.trans_type == 1:
                        types[1] += trans.trans_price
                    # 소비 type이 2인 경우 :: 쇼핑
                    elif trans.trans_type == 2:
                        types[2] += trans.trans_price
                    # 소비 type이 3인 경우 :: 문화생활
                    elif trans.trans_type == 3:
                        types[3] += trans.trans_price
                    # 소비 type이 4인 경우 :: 의료
                    elif trans.trans_type == 4:
                        types[4] += trans.trans_price
                    # 소비 type이 5인 경우 :: 교통비
                    elif trans.trans_type == 5:
                        types[5] += trans.trans_price

    for i in range(len(types)):
        types[i] *= -1

    check_card = Card.objects.get(id=check_id)  # 체크카드 PICK
    debit_card = Card.objects.get(id=debet_id)  # 신용카드 PICK

    cc_id = check_card.id
    dc_id = debit_card.id
    cc_benefits = Benefit.objects.filter(card_id=cc_id)  # 카드 혜택 목록
    cc3 = cc_benefits[:3]

    dc_benefits = Benefit.objects.filter(card_id=dc_id)  # 카드 혜택 목록
    dc3 = dc_benefits[:3]

    context = {
        'check_card': check_card,
        'debit_card': debit_card,
        'cc_benefits': cc_benefits,
        'cc3': cc3,
        'dc_benefits': dc_benefits,
        'dc3': dc3,
        'types': types,
        'cards': cards,
    }
    return render(request, 'platforms/cards_recom.html', context)

# --------------------- 습관 (소비습관, 자산현황, myGold 확인하기) ---------------------
# 13. 소비습관 페이지


def charts(request):
    all_accounts = Account.objects.filter(
        user=request.user)  # 해당 user에 해당하는 계좌 list
    all_accounts = all_accounts.filter(
        acc_type=0)   # 해당 user의 은행 계좌만 (증권, 금 제외)

    types = [0, 0, 0, 0, 0, 0]
    # 은행 계좌 for문
    for i in range(len(all_accounts)):
        all_trans = Trans.objects.filter(account_id=all_accounts[i].acc_num)
        for trans in all_trans:
            if trans.trans_date.year == 2022 and trans.trans_date.month == 5:
                # 출금일 때만 type 체크
                if trans.trans_price < 0:
                    # 소비 type이 0인 경우 :: 식비
                    if trans.trans_type == 0:
                        types[0] += trans.trans_price
                    # 소비 type이 1인 경우 :: 이동통신
                    elif trans.trans_type == 1:
                        types[1] += trans.trans_price
                    # 소비 type이 2인 경우 :: 쇼핑
                    elif trans.trans_type == 2:
                        types[2] += trans.trans_price
                    # 소비 type이 3인 경우 :: 문화생활
                    elif trans.trans_type == 3:
                        types[3] += trans.trans_price
                    # 소비 type이 4인 경우 :: 의료
                    elif trans.trans_type == 4:
                        types[4] += trans.trans_price
                    # 소비 type이 5인 경우 :: 교통비
                    elif trans.trans_type == 5:
                        types[5] += trans.trans_price

    for i in range(len(types)):
        types[i] *= -1

    months = [0, 0, 0, 0, 0, 0]
    for i in range(len(all_accounts)):
        all_trans = Trans.objects.filter(account_id=all_accounts[i].acc_num)
        for trans in all_trans:
            if trans.trans_date.year == 2022:
                # 출금일 때만 type 체크
                if trans.trans_price < 0:
                    # 1월달 소비
                    if trans.trans_date.month == 1:
                        months[0] += trans.trans_price
                    # 2월달 소비
                    elif trans.trans_date.month == 2:
                        months[1] += trans.trans_price
                    # 3월달 소비
                    elif trans.trans_date.month == 3:
                        months[2] += trans.trans_price
                    # 4월달 소비
                    elif trans.trans_date.month == 4:
                        months[3] += trans.trans_price
                    # 5월달 소비
                    elif trans.trans_date.month == 5:
                        months[4] += trans.trans_price
    for i in range(len(months)):
        months[i] *= -1
        months[i] //= 10000  # 만원 단위를 위해 10000으로 나눠줌

    days = [0, 0, 0, 0, 0, 0, 0]
    for i in range(len(all_accounts)):
        all_trans = Trans.objects.filter(account_id=all_accounts[i].acc_num)
        for trans in all_trans:
            # 이번년도 이번 달 소비 CHECK !
            if trans.trans_date.year == 2022 and trans.trans_date.month == 5:
                # 출금일 때만 type 체크
                if trans.trans_price < 0:
                    # 월요일 소비
                    if trans.trans_date.weekday() == 1:
                        days[0] += trans.trans_price
                    # 화요일 소비
                    elif trans.trans_date.weekday() == 2:
                        days[1] += trans.trans_price
                    # 수요일 소비
                    elif trans.trans_date.weekday() == 3:
                        days[2] += trans.trans_price
                    # 목요일 소비
                    elif trans.trans_date.weekday() == 4:
                        days[3] += trans.trans_price
                    # 금요일 소비
                    elif trans.trans_date.weekday() == 5:
                        days[4] += trans.trans_price
                    # 토요일 소비
                    elif trans.trans_date.weekday() == 6:
                        days[5] += trans.trans_price
                    # 일요일 소비
                    elif trans.trans_date.weekday() == 0:
                        days[6] += trans.trans_price
    for i in range(len(days)):
        days[i] *= -1
        days[i] //= 10000  # 만원 단위를 위해 10000으로 나눠줌

    account = Account.objects.get(acc_num="110-773-912015")
    tmp_trans = account.trans.all()

    total_days = []
    totals = []
    result = 0
    for trans in tmp_trans:
        if trans.trans_date.month == 5:
            # .date().isoformat()
            total_days.append(trans.trans_date.date().isoformat())
            result += trans.trans_price
            totals.append(result)
    totals = totals[::-1]
    total_days = list(set(total_days))
    total_days.sort()  # 5월달 거래한 일자 list (중복 제거, 정렬)

    # 식비
    a0 = Trans.objects.filter(Q(account_id="110-773-912015") & Q(trans_type=0) & Q(trans_price__lte=0)).annotate(
        day=TruncMonth('trans_date')).values('day').annotate(day_total=Sum(Abs('trans_price'))).values_list('day_total', flat=True)
    # 이동통신
    a1 = Trans.objects.filter(Q(account_id="110-773-912015") & Q(trans_type=1) & Q(trans_price__lte=0)).annotate(
        day=TruncMonth('trans_date')).values('day').annotate(day_total=Sum(Abs('trans_price'))).values_list('day_total', flat=True)
    # 쇼핑
    a2 = Trans.objects.filter(Q(account_id="110-773-912015") & Q(trans_type=2) & Q(trans_price__lte=0)).annotate(
        day=TruncMonth('trans_date')).values('day').annotate(day_total=Sum(Abs('trans_price'))).values_list('day_total', flat=True)
    # 문화생활
    a3 = Trans.objects.filter(Q(account_id="110-773-912015") & Q(trans_type=3) & Q(trans_price__lte=0)).annotate(
        day=TruncMonth('trans_date')).values('day').annotate(day_total=Sum(Abs('trans_price'))).values_list('day_total', flat=True)
    # 의료비
    a4 = Trans.objects.filter(Q(account_id="110-773-912015") & Q(trans_type=4) & Q(trans_price__lte=0)).annotate(
        day=TruncMonth('trans_date')).values('day').annotate(day_total=Sum(Abs('trans_price'))).values_list('day_total', flat=True)
    # 교통비
    a5 = Trans.objects.filter(Q(account_id="110-773-912015") & Q(trans_type=5) & Q(trans_price__lte=0)).annotate(
        day=TruncMonth('trans_date')).values('day').annotate(day_total=Sum(Abs('trans_price'))).values_list('day_total', flat=True)

    context = {
        'months': months,
        'days': days,
        'types': types,
        'total_days': total_days,
        'totals': totals,
        'a0': a0,
        'a1': a1,
        'a2': a2,
        'a3': a3,
        'a4': a4,
        'a5': a5,
    }
    return render(request, 'platforms/charts.html', context)

# 14. 자산현황 페이지


def myAsset(request):
    all_accounts = Account.objects.filter(
        user=request.user)  # 해당 user에 해당하는 계좌 list

    all_bank = all_accounts.filter(acc_type=0)  # user의 은행 계좌
    all_stock = all_accounts.filter(acc_type=1)  # user의 증권 계좌
    all_gold = all_accounts.filter(acc_type=2)  # user의  금  계좌

    # 은행 계좌 전체 총액
    bank_total = 0
    # 주식 계좌 전체 총액
    stock_total = 0
    # 주식 계좌 중 예수금 금액
    stock_tmp = 0
    # 금 계좌 전체 총액
    gold_total = 0
    # 금 계좌 중 리워드 금액
    goldReward = 0

    # ========================== detail 값 저장 ==========================
    bank_detail0 = 0
    bank_detail1 = 0

    d_bank0 = all_bank.filter(acc_detail=0)  # 입출금자유
    d_bank1 = all_bank.filter(acc_detail=1)  # 예금 / 적금 / 주택청약

    for i in range(len(d_bank0)):
        all_trans = Trans.objects.filter(account_id=d_bank0[i].acc_num)
        for trans in all_trans:
            bank_detail0 += trans.trans_price

    for i in range(len(d_bank1)):
        all_trans = Trans.objects.filter(account_id=d_bank1[i].acc_num)
        for trans in all_trans:
            bank_detail1 += trans.trans_price
    # ========================== detail 값 저장 ==========================

    # 은행 계좌
    for i in range(len(all_bank)):
        all_trans = Trans.objects.filter(account_id=all_bank[i].acc_num)
        for trans in all_trans:
            bank_total += trans.trans_price

    # 주식 계좌
    for i in range(len(all_stock)):
        all_trans = Trans.objects.filter(account_id=all_stock[i].acc_num)
        for trans in all_trans:
            stock_total += trans.trans_price
            # 예수금이 들어가 있다면
            if trans.trans_content.find("예수금") != -1:
                stock_tmp += trans.trans_price

    for i in range(len(all_gold)):
        all_trans = Trans.objects.filter(account_id=all_gold[i].acc_num)
        for trans in all_trans:
            gold_total += trans.trans_price
            # 예수금이 들어가 있다면
            if trans.trans_content == 'KB금쪽리워드환급':
                goldReward += trans.trans_price

    mytotal = bank_total + stock_total + int(gold_total * 74304)
    mytotal = int(mytotal)
    context = {
        # 값 정보 (파이차트용)
        'bank_total': bank_total,
        'stock_total': stock_total,
        'stock_tmp': stock_tmp,
        'gold_total': gold_total,
        'goldReward': goldReward,
        'bank_detail0': bank_detail0,
        'bank_detail1': bank_detail1,

        # 계좌 정보 (표 출력용)
        'all_bank': all_bank,
        'all_stock': all_stock,
        'all_gold': all_gold,
        'mytotal': mytotal,
    }
    return render(request, 'platforms/myAsset.html', context)

# 15. myGold 페이지


def myGold(request):
    # 해당 user에 해당하는 계좌 list
    all_accounts = Account.objects.filter(user=request.user)
    account_2 = all_accounts.filter(acc_detail=2)
    goldbaby = request.user

    ###### 골드 ######
    total_bank2 = []
    for i in range(len(account_2)):
        tmp = 0
        all_trans = Trans.objects.filter(account_id=account_2[i].acc_num)
        tmp_acc = Account.objects.get(acc_num=account_2[i].acc_num)
        for trans in all_trans:
            tmp += trans.trans_price
        total_bank2.append(tmp)
        tmp_acc.total = tmp
        tmp_acc.save()

    context = {
        'sum_total2': sum(total_bank2),
        'user_success': goldbaby.success * 0.0019,
    }
    return render(request, 'platforms/myGold.html', context)

# 16. 예측 값 저장 페이지


def setResult(request):
    goldbaby = request.user
    data = 0

    if goldbaby.tmp == -1:
        result = request.POST['answer']
        if result == '상승':
            data = '상승'
            goldbaby.check_cnt += 1
            goldbaby.my_result = 1

        else:
            data = '하락'
            goldbaby.check_cnt += 1
            goldbaby.my_result = 0

        goldbaby.tmp = 0
        goldbaby.save()

    tmp = goldbaby.tmp
    context = {
        'data': data,
        'tmp': tmp,
    }
    return render(request, 'platforms/stock_game.html', context)
