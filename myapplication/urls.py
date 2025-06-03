from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    # Group management
    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/config/', views.bot_configuration, name='bot_configuration'),
    path('groups/<int:group_id>/summary/', views.message_summary, name='message_summary'),
    
    # Message management
    path('messages/', views.message_list, name='message_list'),
    path('messages/important/', views.important_messages, name='important_messages'),
    
    # Keywords management
    path('keywords/', views.keywords_list, name='keywords_list'),
    path('keywords/add/', views.add_keyword, name='add_keyword'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    
    # API endpoint for WhatsApp webhook
    path('webhook/', views.webhook, name='webhook'),

    path('settings/', views.settings_view, name='settings'),
    path('help/', views.help_view, name='help'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]