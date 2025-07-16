from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import uuid

from myapplication.models import (
    WhatsAppGroup, GroupMember, ImportantKeyword, Message,
    MessageClassification
)


class Command(BaseCommand):
    help = 'Generates sample WhatsApp messages for every group for yesterday and today'

    def handle(self, *args, **options):
        generator = MessageGenerator()
        generator.run()


class MessageGenerator:
    def __init__(self):
        self.yesterday = timezone.now() - timedelta(days=1)
        self.today = timezone.now()

        self.message_templates = {
            'assignment': [
                "Assignment on {subject} is due tomorrow at 5 PM",
                "Don't forget to submit your {subject} report by {deadline}",
                "Assignment reminder: {subject} project submission deadline is {deadline}",
                "Please complete the {subject} assignment and submit before {deadline}",
                "Urgent: {subject} assignment due in 2 hours!"
            ],
            'exam': [
                "Exam schedule for {subject} has been changed to {date}",
                "Important: {subject} exam is tomorrow at 9 AM",
                "Exam notification: {subject} test on {date}",
                "Please prepare for {subject} exam scheduled for {date}",
                "Exam hall for {subject} is Room 101"
            ],
            'schedule': [
                "Class schedule updated: {subject} moved to {time}",
                "Tomorrow's {subject} class is cancelled",
                "Schedule change: {subject} class at {time}",
                "Meeting scheduled for {date} at {time}",
                "Class timetable has been updated"
            ],
            'announcement': [
                "Important announcement: {content}",
                "Notice: {content}",
                "Please note: {content}",
                "Announcement from administration: {content}",
                "Update: {content}"
            ],
            'casual': [
                "Good morning everyone!",
                "How's everyone doing?",
                "Thanks for the help yesterday",
                "See you all in class",
                "Have a great day!",
                "Anyone free for lunch?",
                "Great presentation today",
                "Thanks for sharing the notes",
                "Looking forward to the weekend",
                "Hope everyone is well"
            ],
            'meeting': [
                "Meeting scheduled for {date} at {time}",
                "Team meeting tomorrow at 2 PM",
                "Please attend the meeting on {date}",
                "Meeting agenda has been shared",
                "Don't forget about today's meeting"
            ],
            'deadline': [
                "Deadline for {task} is {date}",
                "Final deadline: {date}",
                "Please submit by {date}",
                "Deadline extended to {date}",
                "Last date for submission: {date}"
            ]
        }

        self.subjects = [
            "Mathematics", "Physics", "Chemistry", "Biology", "English",
            "History", "Computer Science", "Literature", "Psychology", "Economics"
        ]

        self.tasks = [
            "project submission", "report writing", "presentation",
            "assignment completion", "quiz preparation", "lab report"
        ]

    def generate_message_content(self, message_type):
        template = random.choice(self.message_templates.get(message_type, self.message_templates['casual']))
        replacements = {
            '{subject}': random.choice(self.subjects),
            '{task}': random.choice(self.tasks),
            '{date}': (timezone.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
            '{time}': f"{random.randint(8, 17)}:{random.choice(['00', '30'])}",
            '{deadline}': (timezone.now() + timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d %H:%M'),
            '{content}': "Library will be closed for maintenance this weekend"
        }
        for k, v in replacements.items():
            template = template.replace(k, v)
        return template

    def calculate_importance_score(self, content, sender_role):
        keywords = ImportantKeyword.objects.filter(is_active=True)
        score = sum(kw.weight * 0.1 for kw in keywords if kw.keyword.lower() in content.lower())
        role_multipliers = {'teacher': 1.5, 'admin': 1.4, 'class_rep': 1.2, 'student': 1.0}
        score *= role_multipliers.get(sender_role, 1.0)
        return min(score, 1.0), [kw.keyword for kw in keywords if kw.keyword.lower() in content.lower()]

    def generate_messages_for_day(self, group, target_date, num_messages=20):
        members = list(GroupMember.objects.filter(whatsapp_group=group, is_active=True))
        if not members:
            print(f"Skipping group '{group.group_name}' (no active members)")
            return 0

        message_types = ['casual'] * 10 + ['assignment'] * 3 + ['exam'] * 2 + ['schedule'] * 2 + ['announcement'] * 2 + ['meeting']
        for i in range(num_messages):
            timestamp = target_date.replace(hour=random.randint(6, 22), minute=random.randint(0, 59), second=0, microsecond=0)
            sender = random.choice(members)
            message_type = random.choice(message_types)
            content = self.generate_message_content(message_type)

            message = Message.objects.create(
                message_id=f"msg_{uuid.uuid4().hex[:10]}",
                whatsapp_group=group,
                sender=sender,
                content=content,
                message_type='text',
                timestamp=timestamp,
                received_at=timestamp
            )

            importance_score, detected_keywords = self.calculate_importance_score(content, sender.role)
            MessageClassification.objects.create(
                message=message,
                is_important=importance_score >= 0.7,
                importance_score=importance_score,
                detected_keywords=detected_keywords,
                classification_method='keyword',
                confidence_level=min(importance_score + 0.1, 1.0),
                classified_at=timestamp
            )
            print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] {sender.name} ({group.group_name}): {content[:60]}...")
        return num_messages

    def run(self):
        print("🔄 Generating messages for all WhatsApp groups...\n" + "="*60)

        groups = WhatsAppGroup.objects.filter(is_active=True)
        if not groups.exists():
            print("❌ No active WhatsApp groups found.")
            return

        total_messages = 0
        total_important = 0

        for group in groups:
            print(f"\n📚 Processing Group: {group.group_name} ({group.group_id})")

            print(f"  ➤ Yesterday: {self.yesterday.date()}")
            y_count = self.generate_messages_for_day(group, self.yesterday, 25)

            print(f"  ➤ Today: {self.today.date()}")
            t_count = self.generate_messages_for_day(group, self.today, 20)

            group_total = Message.objects.filter(whatsapp_group=group).count()
            group_important = MessageClassification.objects.filter(message__whatsapp_group=group, is_important=True).count()

            total_messages += group_total
            total_important += group_important

            print(f"✅ Done with '{group.group_name}' — Total: {group_total}, Important: {group_important}\n")

        print("="*60)
        print(f"✅ Message generation complete for all groups.")
        print(f"📊 Grand total messages: {total_messages}")
        print(f"⭐ Important messages: {total_important} ({(total_important / total_messages * 100):.1f}%)" if total_messages else "No messages generated.")

