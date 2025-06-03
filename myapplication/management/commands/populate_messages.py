import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapplication.models import WhatsAppGroup, GroupMember, Message

class Command(BaseCommand):
    help = "Populate Message model with realistic WhatsApp messages for each group member"

    # Message templates organized by context and role
    message_templates = {
        'schedule': [
            "What time is the {subject} class tomorrow?",
            "Has the {subject} class been postponed?",
            "When is our next {subject} session?",
            "The timetable shows {subject} at 10am, is that correct?",
            "Are we having {subject} class today?",
            "Class cancelled for today due to teacher being unavailable",
            "Reminder: {subject} class starts in 30 minutes",
            "Schedule update: {subject} moved to 2pm",
            "No class tomorrow, enjoy your day off!",
            "Double period for {subject} this Friday"
        ],
        'assignment': [
            "When is the {subject} assignment due?",
            "Can someone share the assignment requirements?",
            "I need help with question 3 of the {subject} homework",
            "Assignment submitted! That was challenging 😅",
            "The essay should be at least 1000 words",
            "Don't forget to include references in your report",
            "Group project teams announced, check your emails",
            "Extension granted for the {subject} assignment until Friday",
            "Sample solutions uploaded to the portal",
            "Working on the research project, anyone want to collaborate?"
        ],
        'exam': [
            "How many questions will be in the {subject} exam?",
            "What topics should we focus on for the test?",
            "Practice papers available on the website",
            "Exam hall: Room 201, be there 15 minutes early",
            "Good luck everyone for tomorrow's {subject} exam! 📚",
            "Results are out! Check the portal",
            "Practical exam scheduled for next week",
            "Revision session this Saturday at 2pm",
            "Mock test on Friday, attendance mandatory",
            "Final exam timetable released"
        ],
        'deadline': [
            "Deadline for {subject} project is tomorrow!",
            "Urgent: Submit your reports by 5pm today",
            "Last chance to submit the assignment",
            "Extension deadline: Monday 11:59pm",
            "Don't miss the registration deadline",
            "Fee payment due by end of this week",
            "Application deadline extended by 3 days",
            "Hurry up! Only 2 hours left",
            "Late submissions will be penalized",
            "Final call for project submissions"
        ],
        'meeting': [
            "Meeting at 3pm in the library",
            "Study group session tomorrow at 4pm",
            "Can we reschedule the group discussion?",
            "Conference room booked for our presentation",
            "Team meeting cancelled due to conflicts",
            "Online meeting link shared via email",
            "Workshop registration is now open",
            "Guest lecture tomorrow, attendance compulsory",
            "Seminar on career guidance this Friday",
            "Group work meeting in the cafeteria"
        ],
        'announcement': [
            "Important notice: Classes suspended tomorrow",
            "New semester registration starts Monday",
            "Library hours extended during exam period",
            "Attention: Parking restrictions on campus",
            "Holiday announcement: No classes next week",
            "Student elections next month, register to vote",
            "Scholarship applications now open",
            "Campus wifi will be down for maintenance",
            "New course offerings for next semester",
            "Graduation ceremony date announced"
        ],
        'casual': [
            "Good morning everyone! ☀️",
            "Has anyone seen the teacher today?",
            "Thanks for sharing those notes!",
            "See you all tomorrow 👋",
            "Happy weekend everyone!",
            "Does anyone have the textbook PDF?",
            "Great job on the presentation!",
            "Coffee break anyone? ☕",
            "Weather is nice today 🌤️",
            "Looking forward to the holidays",
            "Anyone free for lunch?",
            "That class was interesting!",
            "Hope everyone is doing well",
            "Thanks for the help with the assignment",
            "Enjoyed today's discussion"
        ],
        'questions': [
            "Can someone explain chapter 5?",
            "What was the homework for today?",
            "Which formula should we use for this problem?",
            "Anyone have notes from last week?",
            "How do we solve this equation?",
            "What's the format for the report?",
            "Can someone share the reading list?",
            "Is the assignment individual or group work?",
            "What software should we use for the project?",
            "How many pages should the essay be?"
        ],
        'responses': [
            "Yes, that's correct",
            "Thanks for the clarification!",
            "I'll check and get back to you",
            "Good question, let me find out",
            "Here's the information you requested",
            "You're welcome! Happy to help",
            "I think it's on page 45 of the textbook",
            "Let me share the document with everyone",
            "That works for me",
            "Count me in!",
            "I'll be there",
            "Thanks for the reminder",
            "Got it, thanks!",
            "Perfect timing!",
            "Absolutely!"
        ]
    }

    # Subject mappings for different groups
    subject_mappings = {
        'Physics Class Group': 'Physics',
        'Math Revision Class': 'Mathematics',
        'Biology Classmates Hub': 'Biology',
        'Chemistry Q&A': 'Chemistry',
        'History Discussion Forum': 'History'
    }

    def handle(self, *args, **kwargs):
        groups = WhatsAppGroup.objects.all()
        
        if not groups.exists():
            self.stdout.write(self.style.ERROR("No WhatsApp groups found! Please create groups first."))
            return

        total_messages = 0
        
        for group in groups:
            members = GroupMember.objects.filter(whatsapp_group=group)
            
            if not members.exists():
                self.stdout.write(self.style.WARNING(f"No members found for group: {group.group_name}"))
                continue
                
            group_messages = 0
            subject = self.subject_mappings.get(group.group_name, 'General')
            
            self.stdout.write(f"\n📱 Populating messages for: {group.group_name}")
            
            for member in members:
                # Each member gets 4-8 messages
                message_count = random.randint(4, 8)
                
                for i in range(message_count):
                    # Generate message
                    message_content = self.generate_message(member.role, subject)
                    message_type = self.get_message_type()
                    
                    # Generate timestamp (last 30 days)
                    timestamp = self.generate_timestamp()
                    
                    # Create unique message ID
                    message_id = f"{group.id}_{member.id}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{i}"
                    
                    # Create message
                    Message.objects.create(
                        message_id=message_id,
                        whatsapp_group=group,
                        sender=member,
                        content=message_content,
                        message_type=message_type,
                        timestamp=timestamp
                    )
                    
                    group_messages += 1
                
                self.stdout.write(f"  👤 {member.name} ({member.role}): {message_count} messages")
            
            total_messages += group_messages
            self.stdout.write(f"  📊 Total messages for {group.group_name}: {group_messages}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully created {total_messages} messages across {groups.count()} groups"))
        
        # Statistics
        self.show_statistics()

    def generate_message(self, role, subject):
        """Generate realistic message based on role and subject"""
        
        # Teachers send more announcements and schedule updates
        if role == 'teacher':
            categories = ['schedule', 'assignment', 'exam', 'deadline', 'announcement']
            weights = [0.25, 0.25, 0.20, 0.20, 0.10]
        
        # Class reps send more organizational messages
        elif role == 'class_rep':
            categories = ['schedule', 'meeting', 'announcement', 'deadline', 'casual']
            weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        
        # Students ask more questions and casual messages
        else:
            categories = ['questions', 'casual', 'responses', 'assignment', 'exam']
            weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        
        # Select category based on weights
        category = random.choices(categories, weights=weights)[0]
        
        # Get message template
        templates = self.message_templates.get(category, self.message_templates['casual'])
        message = random.choice(templates)
        
        # Replace subject placeholder
        if '{subject}' in message:
            message = message.replace('{subject}', subject)
        
        return message

    def get_message_type(self):
        """Generate message type with realistic distribution"""
        types = ['text', 'image', 'document', 'audio', 'video', 'sticker']
        weights = [0.75, 0.10, 0.08, 0.04, 0.02, 0.01]  # Text is most common
        
        return random.choices(types, weights=weights)[0]

    def generate_timestamp(self):
        """Generate realistic timestamp within last 30 days"""
        now = timezone.now()
        days_back = random.randint(0, 30)
        hours_back = random.randint(0, 23)
        minutes_back = random.randint(0, 59)
        
        # Avoid late night messages (most messages between 7am-10pm)
        if random.random() < 0.8:  # 80% chance of daytime message
            hour = random.randint(7, 22)
            timestamp = now - timedelta(days=days_back, hours=hours_back, minutes=minutes_back)
            timestamp = timestamp.replace(hour=hour)
        else:
            timestamp = now - timedelta(days=days_back, hours=hours_back, minutes=minutes_back)
        
        return timestamp

    def show_statistics(self):
        """Show message statistics"""
        total_messages = Message.objects.count()
        
        self.stdout.write(f"\n📊 MESSAGE STATISTICS:")
        self.stdout.write(f"Total messages: {total_messages}")
        
        # Messages by type
        self.stdout.write(f"\n📝 Messages by type:")
        for msg_type, _ in Message._meta.get_field('message_type').choices:
            count = Message.objects.filter(message_type=msg_type).count()
            percentage = (count / total_messages * 100) if total_messages > 0 else 0
            self.stdout.write(f"  {msg_type.title()}: {count} ({percentage:.1f}%)")
        
        # Messages by group
        self.stdout.write(f"\n👥 Messages by group:")
        for group in WhatsAppGroup.objects.all():
            count = Message.objects.filter(whatsapp_group=group).count()
            self.stdout.write(f"  {group.group_name}: {count} messages")
        
        # Messages by role
        self.stdout.write(f"\n🎭 Messages by role:")
        roles = ['teacher', 'class_rep', 'student']
        for role in roles:
            count = Message.objects.filter(sender__role=role).count()
            percentage = (count / total_messages * 100) if total_messages > 0 else 0
            self.stdout.write(f"  {role.title()}: {count} ({percentage:.1f}%)")

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing messages before creating new ones',
        )
        
        parser.add_argument(
            '--group',
            type=str,
            help='Only populate messages for specific group name',
        )

        # Handle clear option
        def handle_with_clear(self, *args, **options):
            if options.get('clear'):
                Message.objects.all().delete()
                self.stdout.write(self.style.WARNING("🗑️ Cleared all existing messages"))
            
            # Filter by specific group if provided
            if options.get('group'):
                groups = WhatsAppGroup.objects.filter(group_name__icontains=options['group'])
                if not groups.exists():
                    self.stdout.write(self.style.ERROR(f"No group found containing: {options['group']}"))
                    return
            
            # Call original handle method
            self.handle(*args, **options)