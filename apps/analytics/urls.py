from django.urls import path

from .views import trigger_recalculation, analytics_dashboard


app_name = 'analytics'

urlpatterns = [
    path('', analytics_dashboard, name='dashboard'),
    path('recalculate/', trigger_recalculation, name='recalculate'),
]
