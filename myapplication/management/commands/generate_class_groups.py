import random
import string
from django.core.management.base import BaseCommand
from myapplication.models import WhatsAppGroup

class Command(BaseCommand):
    help = 'Generate 5 WhatsApp groups related to education class'

    def handle(self, *args, **kwargs):
        group_names = [
            'Physics Class Group',
            'Math Revision Class',
            'Biology Classmates Hub',
            'Chemistry Q&A',
            'History Discussion Forum'
        ]

        for name in group_names:
            group_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            if not WhatsAppGroup.objects.filter(group_name=name).exists():
                WhatsAppGroup.objects.create(
                    group_id=group_id,
                    group_name=name,
                    group_type='class',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created group: {name} ({group_id})'))
            else:
                self.stdout.write(self.style.WARNING(f'Group "{name}" already exists'))
