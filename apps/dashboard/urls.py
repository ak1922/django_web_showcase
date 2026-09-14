from django.urls import path
from django.contrib.auth import views as auth_views

from .views import index, register_user, welcome


app_name = 'dashboard'


urlpatterns = [
    path('dashboard', index, name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', register_user, name='register'),
    path('', welcome, name='welcome'),
]
