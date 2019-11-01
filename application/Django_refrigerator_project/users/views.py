from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required  #for using @login_required decorator on top of a function
from .forms import UserRegisterForm     #our created form
from .models import Users
import datetime

def register(request):
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Your account has been created. You are now able to log in')
                
                user = Users()
                user.username = username
                user.eff_bgn_ts = datetime.datetime.now()
                user.eff_end_ts = datetime.datetime.max - datetime.timedelta(1)
                user.save()

            except:
                print("Adding User failed")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})



