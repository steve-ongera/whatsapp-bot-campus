from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
import re

from .models import (
    WhatsAppGroup, GroupMember, Message, MessageClassification, 
    BotResponse, ImportantKeyword, BotConfiguration, MessageSummary,
    UserInteraction, BotPerformanceMetrics
)


def dashboard(request):
    """Main dashboard view"""
    context = {
        'total_groups': WhatsAppGroup.objects.filter(is_active=True).count(),
        'total_messages': Message.objects.count(),
        'important_messages': MessageClassification.objects.filter(is_important=True).count(),
        'recent_messages': Message.objects.select_related('sender', 'whatsapp_group').order_by('-timestamp')[:10]
    }
    return render(request, 'chatbot/dashboard.html', context)



def group_list(request):
    """List all WhatsApp groups"""
    groups = WhatsAppGroup.objects.filter(is_active=True).annotate(
        member_count=Count('groupmember'),
        message_count=Count('message')
    )
    return render(request, 'group_list.html', {'groups': groups})


def group_detail(request, group_id):
    """Detailed view of a specific group"""
    group = get_object_or_404(WhatsAppGroup, id=group_id)
    members = GroupMember.objects.filter(whatsapp_group=group, is_active=True)
    
    # Get recent messages with pagination
    messages_list = Message.objects.filter(whatsapp_group=group).select_related(
        'sender', 'messageclassification'
    ).order_by('-timestamp')
    
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    messages = paginator.get_page(page_number)
    
    # Get bot configuration
    try:
        bot_config = BotConfiguration.objects.get(whatsapp_group=group)
    except BotConfiguration.DoesNotExist:
        bot_config = None
    
    context = {
        'group': group,
        'members': members,
        'messages': messages,
        'bot_config': bot_config
    }
    return render(request, 'group_detail.html', context)


def message_list(request):
    """List all messages with filtering options"""
    messages = Message.objects.select_related('sender', 'whatsapp_group').order_by('-timestamp')
    
    # Filter by importance
    if request.GET.get('important') == 'true':
        messages = messages.filter(messageclassification__is_important=True)
    
    # Filter by group
    group_id = request.GET.get('group')
    if group_id:
        messages = messages.filter(whatsapp_group_id=group_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        messages = messages.filter(content__icontains=search_query)
    
    paginator = Paginator(messages, 25)
    page_number = request.GET.get('page')
    page_messages = paginator.get_page(page_number)
    
    context = {
        'messages': page_messages,
        'groups': WhatsAppGroup.objects.filter(is_active=True),
        'search_query': search_query or '',
        'show_important': request.GET.get('important') == 'true'
    }
    return render(request, 'message_list.html', context)


def important_messages(request):
    """View only important messages"""
    important_msgs = Message.objects.filter(
        messageclassification__is_important=True
    ).select_related('sender', 'whatsapp_group', 'messageclassification').order_by('-timestamp')
    
    paginator = Paginator(important_msgs, 20)
    page_number = request.GET.get('page')
    messages = paginator.get_page(page_number)
    
    return render(request, 'important_messages.html', {'messages': messages})


def keywords_list(request):
    """List and manage important keywords"""
    keywords = ImportantKeyword.objects.filter(is_active=True).order_by('category', 'keyword')
    return render(request, 'keywords_list.html', {'keywords': keywords})


def add_keyword(request):
    """Add new important keyword"""
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '').strip().lower()
        category = request.POST.get('category')
        weight = int(request.POST.get('weight', 1))
        
        if keyword and category:
            ImportantKeyword.objects.get_or_create(
                keyword=keyword,
                defaults={'category': category, 'weight': weight}
            )
            messages.success(request, f'Keyword "{keyword}" added successfully!')
        else:
            messages.error(request, 'Please provide both keyword and category.')
        
        return redirect('keywords_list')
    
    categories = ImportantKeyword._meta.get_field('category').choices
    return render(request, 'add_keyword.html', {'categories': categories})


def bot_configuration(request, group_id):
    """Configure bot settings for a group"""
    group = get_object_or_404(WhatsAppGroup, id=group_id)
    
    try:
        config = BotConfiguration.objects.get(whatsapp_group=group)
    except BotConfiguration.DoesNotExist:
        config = BotConfiguration.objects.create(whatsapp_group=group)
    
    if request.method == 'POST':
        config.auto_broadcast_important = request.POST.get('auto_broadcast') == 'on'
        config.minimum_importance_score = float(request.POST.get('min_score', 0.7))
        config.escalation_threshold = float(request.POST.get('escalation_threshold', 0.5))
        config.enable_keyword_detection = request.POST.get('keyword_detection') == 'on'
        config.enable_sender_role_priority = request.POST.get('sender_priority') == 'on'
        config.notification_delay_minutes = int(request.POST.get('delay_minutes', 0))
        config.max_messages_per_hour = int(request.POST.get('max_messages', 50))
        config.save()
        
        messages.success(request, 'Bot configuration updated successfully!')
        return redirect('group_detail', group_id=group.id)
    
    return render(request, 'bot_configuration.html', {
        'group': group,
        'config': config
    })


def analytics(request):
    """Analytics and performance metrics"""
    # Get date range from request or default to last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Get metrics
    total_messages = Message.objects.filter(timestamp__date__range=[start_date, end_date]).count()
    important_messages = MessageClassification.objects.filter(
        message__timestamp__date__range=[start_date, end_date],
        is_important=True
    ).count()
    
    # Get performance metrics
    performance_metrics = BotPerformanceMetrics.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    # Group statistics
    group_stats = WhatsAppGroup.objects.annotate(
        message_count=Count('message', filter=Q(message__timestamp__date__range=[start_date, end_date])),
        important_count=Count('message__messageclassification', 
                            filter=Q(message__messageclassification__is_important=True,
                                   message__timestamp__date__range=[start_date, end_date]))
    ).filter(is_active=True)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_messages': total_messages,
        'important_messages': important_messages,
        'performance_metrics': performance_metrics,
        'group_stats': group_stats,
        'accuracy_rate': round((important_messages / total_messages * 100) if total_messages > 0 else 0, 2)
    }
    return render(request, 'analytics.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """Webhook to receive WhatsApp messages"""
    try:
        data = json.loads(request.body)
        
        # Extract message data (this will depend on your WhatsApp API provider)
        message_data = data.get('message', {})
        group_id = message_data.get('group_id')
        sender_phone = message_data.get('from')
        content = message_data.get('text', '')
        message_id = message_data.get('id')
        timestamp = timezone.now()
        
        if not all([group_id, sender_phone, message_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get or create group and member
        group, _ = WhatsAppGroup.objects.get_or_create(
            group_id=group_id,
            defaults={'group_name': f'Group {group_id}', 'group_type': 'class'}
        )
        
        member, _ = GroupMember.objects.get_or_create(
            whatsapp_group=group,
            phone_number=sender_phone,
            defaults={'name': f'User {sender_phone}', 'role': 'student'}
        )
        
        # Create message
        message = Message.objects.create(
            message_id=message_id,
            whatsapp_group=group,
            sender=member,
            content=content,
            timestamp=timestamp,
            message_type='text'
        )
        
        # Process message for importance
        process_message_importance(message)
        
        return JsonResponse({'status': 'success', 'message_id': message.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def process_message_importance(message):
    """Process message to determine importance"""
    content_lower = message.content.lower()
    importance_score = 0.0
    detected_keywords = []
    
    # Check for important keywords
    keywords = ImportantKeyword.objects.filter(is_active=True)
    for keyword in keywords:
        if keyword.keyword in content_lower:
            importance_score += keyword.weight * 0.1
            detected_keywords.append(keyword.keyword)
    
    # Boost score based on sender role
    if message.sender.role in ['class_rep', 'teacher', 'admin']:
        importance_score += 0.3
    
    # Check for urgent indicators
    urgent_words = ['urgent', 'important', 'deadline', 'emergency', 'asap']
    for word in urgent_words:
        if word in content_lower:
            importance_score += 0.2
            break
    
    # Determine if message is important
    is_important = importance_score >= 0.5
    
    # Create classification
    classification = MessageClassification.objects.create(
        message=message,
        is_important=is_important,
        importance_score=min(importance_score, 1.0),
        detected_keywords=detected_keywords,
        classification_method='keyword',
        confidence_level=min(importance_score, 1.0)
    )
    
    # Create bot response if important
    if is_important:
        BotResponse.objects.create(
            original_message=message,
            response_type='broadcast',
            response_content=f"Important message detected: {message.content[:100]}...",
            recipients=['all']
        )
    
    return classification


def message_summary(request, group_id):
    """Generate message summary for a group"""
    group = get_object_or_404(WhatsAppGroup, id=group_id)
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    
    if request.GET.get('days'):
        days = int(request.GET.get('days', 7))
        start_date = end_date - timedelta(days=days)
    
    # Get messages in date range
    messages = Message.objects.filter(
        whatsapp_group=group,
        timestamp__date__range=[start_date, end_date]
    ).select_related('messageclassification')
    
    important_messages = messages.filter(messageclassification__is_important=True)
    
    # Generate summary
    summary_content = f"""
    Summary for {group.group_name}
    Period: {start_date} to {end_date}
    
    Total Messages: {messages.count()}
    Important Messages: {important_messages.count()}
    
    Key Important Messages:
    """
    
    for msg in important_messages.order_by('-messageclassification__importance_score')[:5]:
        summary_content += f"\n- {msg.sender.name}: {msg.content[:100]}..."
    
    context = {
        'group': group,
        'summary_content': summary_content,
        'start_date': start_date,
        'end_date': end_date,
        'total_messages': messages.count(),
        'important_messages': important_messages.count()
    }
    
    return render(request, 'message_summary.html', context)