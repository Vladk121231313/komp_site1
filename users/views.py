from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('usersname')
            messages.success(request, f'Аккаунт {username} создан! Теперь вы можете войти.')
            
            return redirect('auth:login')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте введённые данные.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')