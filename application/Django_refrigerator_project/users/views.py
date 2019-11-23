from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import User, AuthUser
import datetime


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                username = form.cleaned_data.get('username')
                auth_user = AuthUser.objects.filter(username=username).first()
                messages.success(
                    request, f'Your account has been created. You are now able to log in')
                user = User(username=username, eff_bgn_ts=datetime.datetime.now(
                ), eff_end_ts=datetime.datetime.max - datetime.timedelta(1))
                user.auth_user = auth_user
                user.save()
            except Exception as error:
                print(error)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
