from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.conf import settings
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    ProfileUpdateForm
)
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .models import CustomUser

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Аккаунт не активен до подтверждения email
            user.save()

            # Генерация токена для подтверждения email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirmation_link = request.build_absolute_uri(f'/activate/{uid}/{token}/')

            # Отправка email с подтверждением
            send_mail(
                subject = 'Подтверждение регистрации',
                message = f'Перейдите по ссылке для активации: {confirmation_link}',
                from_email = 'admin@shop.com',
                recipient_list = [user.email],
                auth_user="",
                auth_password="",
                fail_silently=False,
            )

            return redirect('user:email_confirmation_sent')
    else:
        form = CustomUserCreationForm()

    return render(request, 'user/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return render(request, 'activation_invalid.html')

def email_confirmation_sent(request):
    return render(request, 'user/email_confirmation_sent.html')

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        print(f"Form errors: {form.errors}")
        print(f"POST data: {request.POST}")
        print(f'Form Validity: {form.is_valid()}')
        if form.is_valid():
            user = form.get_user()
            print(f"User auth: {user.is_authenticated}")
            print(user)
            if user.is_active:
                login(request, user)
                return redirect('user:profile')
            else:
                messages.error(request, 'Ваш аккаунт не активирован. Пожалуйста, проверьте вашу почту для активации.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('products:home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('user:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'user/profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomSetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Обновляем сессию пользователя
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Пароль успешно изменён!')
            return redirect('user:profile')
    else:
        form = CustomSetPasswordForm(request.user)
    
    return render(request, 'user/change_password.html', {'form': form})

def password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    reverse('user:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                # Send email
                subject = 'Сброс пароля'
                message = render_to_string('user/password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                #settings.DEFAULT_FROM_EMAIL,
                send_mail(
                    subject=subject,
                    message=message,
                    auth_user="",
                    auth_password="",
                    from_email="mvkiselev@legion.ru",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            return redirect('user:password_reset_done')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'user/password_reset.html', {'form': form})

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('user:password_reset_complete')
    form_class = CustomSetPasswordForm

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    #template_name = 'user/password_reset_complete.html'
    def get(self, request):
        return render(request, 'user/password_reset_complete.html')
