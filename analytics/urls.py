from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main dashboard
    path('', views.analytics_dashboard, name='dashboard'),
    
    # System health monitoring (real-time)
    path('system-health/', views.system_health_dashboard, name='system_health'),
    
    # Individual user analytics
    path('user/<int:user_id>/', views.user_analytics, name='user_detail'),
    
    # API endpoints for charts
    path('api/daily-trends/', views.api_daily_trends, name='api_daily_trends'),
    path('api/pdf-analytics/', views.api_pdf_analytics, name='api_pdf_analytics'),
    path('api/healthcare-insights/', views.api_healthcare_insights, name='api_healthcare_insights'),
    
    # Real-time system health API
    path('api/system-health/', views.api_system_health_realtime, name='api_system_health'),
]