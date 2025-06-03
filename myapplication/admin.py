from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    WhatsAppGroup, GroupMember, ImportantKeyword, Message, 
    MessageClassification, BotResponse, BotConfiguration, 
    MessageSummary, UserInteraction, BotPerformanceMetrics
)


@admin.register(WhatsAppGroup)
class WhatsAppGroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'group_id', 'group_type', 'member_count', 'message_count', 'is_active', 'created_at']
    list_filter = ['group_type', 'is_active', 'created_at']
    search_fields = ['group_name', 'group_id']
    readonly_fields = ['created_at', 'member_count', 'message_count', 'recent_activity']
    fieldsets = (
        ('Basic Information', {
            'fields': ('group_name', 'group_id', 'group_type', 'is_active')
        }),
        ('Statistics', {
            'fields': ('member_count', 'message_count', 'recent_activity', 'created_at'),
            'classes': ('collapse',)
        })
    )

    def member_count(self, obj):
        count = obj.groupmember_set.filter(is_active=True).count()
        url = reverse('admin:myapplication_groupmember_changelist') + f'?whatsapp_group__id__exact={obj.id}'
        return format_html('<a href="{}">{} members</a>', url, count)
    member_count.short_description = 'Active Members'

    def message_count(self, obj):
        count = obj.message_set.count()
        url = reverse('admin:myapplication_message_changelist') + f'?whatsapp_group__id__exact={obj.id}'
        return format_html('<a href="{}">{} messages</a>', url, count)
    message_count.short_description = 'Total Messages'

    def recent_activity(self, obj):
        recent_messages = obj.message_set.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).count()
        return f"{recent_messages} messages in last 7 days"
    recent_activity.short_description = 'Recent Activity'


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'whatsapp_group', 'role', 'message_count', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'whatsapp_group', 'joined_at']
    search_fields = ['name', 'phone_number', 'whatsapp_group__group_name']
    readonly_fields = ['joined_at', 'message_count', 'last_message']
    fieldsets = (
        ('Member Information', {
            'fields': ('whatsapp_group', 'name', 'phone_number', 'role', 'is_active')
        }),
        ('Activity Statistics', {
            'fields': ('message_count', 'last_message', 'joined_at'),
            'classes': ('collapse',)
        })
    )
    
    def message_count(self, obj):
        count = obj.message_set.count()
        return count
    message_count.short_description = 'Messages Sent'
    
    def last_message(self, obj):
        last_msg = obj.message_set.order_by('-timestamp').first()
        if last_msg:
            return f"{last_msg.timestamp.strftime('%Y-%m-%d %H:%M')} - {last_msg.content[:50]}..."
        return "No messages"
    last_message.short_description = 'Last Message'


@admin.register(ImportantKeyword)
class ImportantKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'category', 'weight', 'usage_count', 'is_active', 'created_at']
    list_filter = ['category', 'weight', 'is_active', 'created_at']
    search_fields = ['keyword', 'category']
    readonly_fields = ['created_at', 'usage_count']
    fieldsets = (
        ('Keyword Configuration', {
            'fields': ('keyword', 'category', 'weight', 'is_active')
        }),
        ('Statistics', {
            'fields': ('usage_count', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def usage_count(self, obj):
        # This would need to be implemented based on how you track keyword usage
        # For now, returning a placeholder
        return "Track implementation needed"
    usage_count.short_description = 'Times Detected'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_preview', 'sender', 'whatsapp_group', 'message_type', 'importance_status', 'timestamp']
    list_filter = ['message_type', 'whatsapp_group', 'timestamp', 'sender__role']
    search_fields = ['content', 'sender__name', 'whatsapp_group__group_name', 'message_id']
    readonly_fields = ['message_id', 'received_at', 'importance_display', 'classification_details']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Message Information', {
            'fields': ('message_id', 'whatsapp_group', 'sender', 'message_type')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'received_at')
        }),
        ('Classification', {
            'fields': ('importance_display', 'classification_details'),
            'classes': ('collapse',)
        })
    )
    
    def message_preview(self, obj):
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return preview
    message_preview.short_description = 'Message Content'
    
    def importance_status(self, obj):
        try:
            classification = obj.messageclassification
            color = 'green' if classification.is_important else 'gray'
            status = 'Important' if classification.is_important else 'Normal'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, status
            )
        except:
            return format_html('<span style="color: orange;">Unclassified</span>')
    importance_status.short_description = 'Importance'
    
    def importance_display(self, obj):
        try:
            classification = obj.messageclassification
            return f"Important: {classification.is_important}, Score: {classification.importance_score}"
        except:
            return "Not classified"
    importance_display.short_description = 'Classification Status'
    
    def classification_details(self, obj):
        try:
            classification = obj.messageclassification
            details = {
                'Method': classification.classification_method,
                'Confidence': classification.confidence_level,
                'Keywords': classification.detected_keywords
            }
            return format_html('<pre>{}</pre>', json.dumps(details, indent=2))
        except:
            return "No classification data"
    classification_details.short_description = 'Classification Details'


@admin.register(MessageClassification)
class MessageClassificationAdmin(admin.ModelAdmin):
    list_display = ['message_preview', 'is_important', 'importance_score', 'classification_method', 'confidence_level', 'classified_at']
    list_filter = ['is_important', 'classification_method', 'classified_at']
    search_fields = ['message__content', 'detected_keywords']
    readonly_fields = ['classified_at', 'detected_keywords_display']
    
    fieldsets = (
        ('Classification Results', {
            'fields': ('message', 'is_important', 'importance_score', 'confidence_level')
        }),
        ('Method & Keywords', {
            'fields': ('classification_method', 'detected_keywords_display')
        }),
        ('Timestamp', {
            'fields': ('classified_at',)
        })
    )
    
    def message_preview(self, obj):
        return obj.message.content[:50] + "..." if len(obj.message.content) > 50 else obj.message.content
    message_preview.short_description = 'Message'
    
    def detected_keywords_display(self, obj):
        if obj.detected_keywords:
            return format_html('<pre>{}</pre>', json.dumps(obj.detected_keywords, indent=2))
        return "No keywords detected"
    detected_keywords_display.short_description = 'Detected Keywords'


@admin.register(BotResponse)
class BotResponseAdmin(admin.ModelAdmin):
    list_display = ['response_type', 'message_preview', 'is_sent', 'sent_at', 'created_at']
    list_filter = ['response_type', 'is_sent', 'sent_at', 'created_at']
    search_fields = ['response_content', 'original_message__content']
    readonly_fields = ['created_at', 'recipients_display']
    
    fieldsets = (
        ('Response Information', {
            'fields': ('original_message', 'response_type', 'response_content')
        }),
        ('Delivery', {
            'fields': ('recipients_display', 'is_sent', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
    
    def message_preview(self, obj):
        return obj.original_message.content[:50] + "..."
    message_preview.short_description = 'Original Message'
    
    def recipients_display(self, obj):
        if obj.recipients:
            return format_html('<pre>{}</pre>', json.dumps(obj.recipients, indent=2))
        return "No recipients"
    recipients_display.short_description = 'Recipients'


@admin.register(BotConfiguration)
class BotConfigurationAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_group', 'auto_broadcast_important', 'minimum_importance_score', 'max_messages_per_hour', 'updated_at']
    list_filter = ['auto_broadcast_important', 'enable_keyword_detection', 'enable_sender_role_priority']
    search_fields = ['whatsapp_group__group_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Group Configuration', {
            'fields': ('whatsapp_group',)
        }),
        ('Classification Settings', {
            'fields': ('minimum_importance_score', 'escalation_threshold', 'enable_keyword_detection', 'enable_sender_role_priority')
        }),
        ('Response Settings', {
            'fields': ('auto_broadcast_important', 'notification_delay_minutes', 'max_messages_per_hour')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(MessageSummary)
class MessageSummaryAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_group', 'summary_type', 'date_range', 'total_messages', 'important_messages', 'generated_at']
    list_filter = ['summary_type', 'whatsapp_group', 'generated_at']
    search_fields = ['whatsapp_group__group_name', 'summary_content']
    readonly_fields = ['generated_at', 'key_topics_display']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Summary Information', {
            'fields': ('whatsapp_group', 'summary_type', 'start_date', 'end_date')
        }),
        ('Statistics', {
            'fields': ('total_messages', 'important_messages')
        }),
        ('Content', {
            'fields': ('summary_content', 'key_topics_display')
        }),
        ('Timestamp', {
            'fields': ('generated_at',)
        })
    )
    
    def date_range(self, obj):
        return f"{obj.start_date} to {obj.end_date}"
    date_range.short_description = 'Period'
    
    def key_topics_display(self, obj):
        if obj.key_topics:
            return format_html('<pre>{}</pre>', json.dumps(obj.key_topics, indent=2))
        return "No topics identified"
    key_topics_display.short_description = 'Key Topics'


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'interaction_type', 'content_preview', 'was_helpful', 'timestamp']
    list_filter = ['interaction_type', 'was_helpful', 'timestamp', 'user__role']
    search_fields = ['user__name', 'content', 'bot_response']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Interaction Information', {
            'fields': ('user', 'interaction_type', 'timestamp')
        }),
        ('Content', {
            'fields': ('content', 'bot_response')
        }),
        ('Feedback', {
            'fields': ('was_helpful',)
        })
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(BotPerformanceMetrics)
class BotPerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_group', 'date', 'accuracy_score', 'messages_processed', 'response_time_avg', 'user_satisfaction_score']
    list_filter = ['whatsapp_group', 'date']
    search_fields = ['whatsapp_group__group_name']
    readonly_fields = ['precision_score', 'recall_score']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('whatsapp_group', 'date')
        }),
        ('Processing Metrics', {
            'fields': ('messages_processed', 'important_messages_detected', 'response_time_avg')
        }),
        ('Accuracy Metrics', {
            'fields': ('accuracy_score', 'false_positives', 'false_negatives', 'precision_score', 'recall_score')
        }),
        ('User Satisfaction', {
            'fields': ('user_satisfaction_score',)
        })
    )
    
    def precision_score(self, obj):
        if obj.important_messages_detected + obj.false_positives > 0:
            precision = obj.important_messages_detected / (obj.important_messages_detected + obj.false_positives)
            return f"{precision:.2%}"
        return "N/A"
    precision_score.short_description = 'Precision'
    
    def recall_score(self, obj):
        if obj.important_messages_detected + obj.false_negatives > 0:
            recall = obj.important_messages_detected / (obj.important_messages_detected + obj.false_negatives)
            return f"{recall:.2%}"
        return "N/A"
    recall_score.short_description = 'Recall'


# Custom admin site configuration
admin.site.site_header = "WhatsApp Bot Administration"
admin.site.site_title = "WhatsApp Bot Admin"
admin.site.index_title = "Welcome to WhatsApp Bot Administration"

# Add custom CSS for better display
class Media:
    css = {
        'all': ('admin/css/custom_admin.css',)
    }