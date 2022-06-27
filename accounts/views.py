from django.shortcuts import get_object_or_404, redirect, render
from . models import User
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
#from django.contrib.auth.models import User
from django.db.models import Q

# 1. 로그인
def login(request):
    if request.method == 'POST':
        user_name = request.POST['userID']
        password = request.POST['password']
        user = authenticate(request, username=user_name, password=password)
        if user is not None:
            auth.login(request, user)
            return render(request, 'platforms/index.html')
        else:
            return render(request, 'accounts/login.html', {'error': 'user_name or password is incorrect.'})
    else:
        return render(request, 'accounts/login.html')

# 2. 로그아웃
def logout(request):
    auth.logout(request)
    return render(request, 'platforms/index.html')

# 3. 회원가입    
def register(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            user = User.objects.create_user(
                username=request.POST['userID'],
                password=request.POST['password1'],
                first_name=request.POST['username'],
            )
            auth.login(request, user)
            return redirect('accounts:login')
        return render(request, 'accounts/register.html')
    return render(request, 'accounts/register.html')