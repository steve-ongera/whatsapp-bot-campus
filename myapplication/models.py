from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class WhatsAppGroup(models.Model):
    """Model to represent WhatsApp groups"""
    group_id = models.CharField(max_length=100, unique=True)
    group_name = models.CharField(max_length=255)
    group_type = models.CharField(
        max_length=50, 
        choices=[
            ('class', 'Class Group'),
            ('study', 'Study Group'),
            ('general', 'General Group')
        ],
        default='class'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.group_name} ({self.group_id})"


class GroupMember(models.Model):
    """Model to represent members in WhatsApp groups"""
    whatsapp_group = models.ForeignKey(WhatsAppGroup, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=50,
        choices=[
            ('student', 'Student'),
            ('class_rep', 'Class Representative'),
            ('teacher', 'Teacher'),
            ('admin', 'Admin')
        ],
        default='student'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['whatsapp_group', 'phone_number']
    
    def __str__(self):
        return f"{self.name} - {self.whatsapp_group.group_name}"


class ImportantKeyword(models.Model):
    """Model to store keywords that indicate important messages"""
    keyword = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('schedule', 'Schedule'),
            ('assignment', 'Assignment'),
            ('exam', 'Exam'),
            ('deadline', 'Deadline'),
            ('meeting', 'Meeting'),
            ('announcement', 'Announcement'),
            ('task', 'Task'),
            ('report', 'Report')
        ]
    )
    weight = models.IntegerField(default=1, help_text="Importance weight (1-10)")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.keyword} ({self.category})"


class Message(models.Model):
    """Model to store WhatsApp messages"""
    message_id = models.CharField(max_length=100, unique=True)
    whatsapp_group = models.ForeignKey(WhatsAppGroup, on_delete=models.CASCADE)
    sender = models.ForeignKey(GroupMember, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
            ('document', 'Document'),
            ('audio', 'Audio'),
            ('video', 'Video'),
            ('sticker', 'Sticker')
        ],
        default='text'
    )
    timestamp = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.name} at {self.timestamp}"


class MessageClassification(models.Model):
    """Model to store message classification results"""
    message = models.OneToOneField(Message, on_delete=models.CASCADE)
    is_important = models.BooleanField(default=False)
    importance_score = models.FloatField(default=0.0)
    detected_keywords = models.JSONField(default=list, blank=True)
    classification_method = models.CharField(
        max_length=50,
        choices=[
            ('keyword', 'Keyword Based'),
            ('ml', 'Machine Learning'),
            ('manual', 'Manual Classification'),
            ('sender_role', 'Based on Sender Role')
        ],
        default='keyword'
    )
    confidence_level = models.FloatField(default=0.0)
    classified_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "Important" if self.is_important else "Not Important"
        return f"{status} - Score: {self.importance_score}"


class BotResponse(models.Model):
    """Model to store bot responses and actions"""
    original_message = models.ForeignKey(Message, on_delete=models.CASCADE)
    response_type = models.CharField(
        max_length=50,
        choices=[
            ('broadcast', 'Broadcast to Group'),
            ('direct_message', 'Direct Message'),
            ('escalate', 'Escalate to Human'),
            ('ignore', 'Ignore Message'),
            ('auto_reply', 'Auto Reply')
        ]
    )
    response_content = models.TextField(blank=True, null=True)
    recipients = models.JSONField(default=list, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.response_type} for message {self.original_message.message_id}"


class BotConfiguration(models.Model):
    """Model to store bot configuration settings"""
    whatsapp_group = models.OneToOneField(WhatsAppGroup, on_delete=models.CASCADE)
    auto_broadcast_important = models.BooleanField(default=True)
    minimum_importance_score = models.FloatField(default=0.7)
    escalation_threshold = models.FloatField(default=0.5)
    enable_keyword_detection = models.BooleanField(default=True)
    enable_sender_role_priority = models.BooleanField(default=True)
    notification_delay_minutes = models.IntegerField(default=0)
    max_messages_per_hour = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bot Config for {self.whatsapp_group.group_name}"


class MessageSummary(models.Model):
    """Model to store daily/weekly message summaries"""
    whatsapp_group = models.ForeignKey(WhatsAppGroup, on_delete=models.CASCADE)
    summary_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily Summary'),
            ('weekly', 'Weekly Summary'),
            ('custom', 'Custom Period')
        ]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_messages = models.IntegerField(default=0)
    important_messages = models.IntegerField(default=0)
    summary_content = models.TextField()
    key_topics = models.JSONField(default=list, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.summary_type} for {self.whatsapp_group.group_name} ({self.start_date})"


class UserInteraction(models.Model):
    """Model to track user interactions with the bot"""
    user = models.ForeignKey(GroupMember, on_delete=models.CASCADE)
    interaction_type = models.CharField(
        max_length=50,
        choices=[
            ('command', 'Bot Command'),
            ('query', 'Information Query'),
            ('feedback', 'Feedback'),
            ('request_summary', 'Request Summary'),
            ('report_issue', 'Report Issue')
        ]
    )
    content = models.TextField()
    bot_response = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    was_helpful = models.BooleanField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.interaction_type} at {self.timestamp}"


class BotPerformanceMetrics(models.Model):
    """Model to track bot performance metrics"""
    whatsapp_group = models.ForeignKey(WhatsAppGroup, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    messages_processed = models.IntegerField(default=0)
    important_messages_detected = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    false_negatives = models.IntegerField(default=0)
    accuracy_score = models.FloatField(default=0.0)
    response_time_avg = models.FloatField(default=0.0)  # in seconds
    user_satisfaction_score = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['whatsapp_group', 'date']
    
    def __str__(self):
        return f"Metrics for {self.whatsapp_group.group_name} - {self.date}"