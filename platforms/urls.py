from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'platforms'
urlpatterns = [
    # main 화면
    path('index/', views.index, name="index"),
    
    # 은행 (전체계좌-상세계좌, 이체, 지점찾기)
    path('total_accounts/', views.total_accounts, name="total_accounts"),   # 전체계좌
    path('<str:pk>/accounts/', views.accounts, name="accounts"),                     # 상세계좌
    path('<str:pk>/transfer/', views.transfer, name="transfer"),            # 이체
    path('find_kb/', views.find_kb, name="find_kb"),                        # 지점찾기

    # 증권 (주식계좌, 주식잔고, 주식차트, 종가 UP&DOWN-출석체크,결과보기)
    path('stock_account/', views.stock_account, name="stock_account"),      # 주식 전체계좌
    path('stock/', views.stock, name="stock"),                              # 주식 잔고
    path('stock_charts/', views.stock_charts, name="stock_charts"),         # 주식 차트
    path('stock_game/', views.stock_game, name="stock_game"),               # 종가UP&DOWN
    path('attendance/', views.attendance, name="attendance"),               # 출석체크
    path('updown_result/', views.updown_result, name="updown_result"),      # 결과

    # 카드 (카드목록, 카드추천)
    path('cards/', views.cards, name="cards"),                              # 카드목록
    path('cards_recom/', views.cards_recom, name="cards_recom"),            # 카드추천

    # 습관 (소비습관, 자산현황, myGold 확인하기)
    path('charts/', views.charts, name="charts"),                           # 소비습관
    path('myAsset/', views.myAsset, name="myAsset"),                        # 자산현황
    path('myGold/', views.myGold, name="myGold"),                           # my Gold
    path('setResult/', views.setResult, name="setResult")                   # 예측 값 받아서 정리

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
