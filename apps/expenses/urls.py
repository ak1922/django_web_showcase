from django.urls import path
from .views import expense_dashboard, create_expense, process_approval


app_name = 'expenses'


urlpatterns = [
    path('', expense_dashboard, name='dashboard'),
    path('new/', create_expense, name='create'),
    path('<int:pk>/<str:action>', process_approval, name='process')
]
