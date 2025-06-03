from django.core.management.base import BaseCommand
from myapplication.models import ImportantKeyword

class Command(BaseCommand):
    help = "Populate ImportantKeyword model with predefined keywords"

    keywords_data = [
        # Schedule Keywords (Weight 6-8)
        ("class", "schedule", 7),
        ("timetable", "schedule", 8),
        ("schedule", "schedule", 8),
        ("time", "schedule", 6),
        ("when", "schedule", 6),
        ("date", "schedule", 7),
        ("tomorrow", "schedule", 7),
        ("today", "schedule", 8),
        ("next week", "schedule", 7),
        ("postponed", "schedule", 8),
        ("cancelled", "schedule", 9),
        ("reschedule", "schedule", 8),

        # Assignment Keywords (Weight 7-9)
        ("assignment", "assignment", 9),
        ("homework", "assignment", 8),
        ("submit", "assignment", 8),
        ("submission", "assignment", 8),
        ("project", "assignment", 7),
        ("essay", "assignment", 7),
        ("research", "assignment", 7),
        ("report", "assignment", 7),
        ("write", "assignment", 6),
        ("complete", "assignment", 7),
        ("finish", "assignment", 7),

        # Exam Keywords (Weight 8-10)
        ("exam", "exam", 9),
        ("test", "exam", 8),
        ("quiz", "exam", 8),
        ("assessment", "exam", 8),
        ("evaluation", "exam", 7),
        ("midterm", "exam", 9),
        ("final", "exam", 10),
        ("practical", "exam", 8),
        ("oral", "exam", 8),
        ("written", "exam", 7),
        ("marks", "exam", 7),
        ("grade", "exam", 7),
        ("result", "exam", 8),

        # Deadline Keywords (Weight 8-10)
        ("deadline", "deadline", 10),
        ("due", "deadline", 9),
        ("urgent", "deadline", 9),
        ("asap", "deadline", 8),
        ("immediately", "deadline", 8),
        ("last day", "deadline", 9),
        ("extension", "deadline", 8),
        ("late", "deadline", 8),
        ("overdue", "deadline", 9),

        # Meeting Keywords (Weight 7-8)
        ("meeting", "meeting", 8),
        ("conference", "meeting", 7),
        ("discussion", "meeting", 7),
        ("seminar", "meeting", 7),
        ("workshop", "meeting", 7),
        ("presentation", "meeting", 7),
        ("group work", "meeting", 7),
        ("team", "meeting", 7),
        ("attend", "meeting", 8),

        # Announcement Keywords (Weight 6-8)
        ("announcement", "announcement", 8),
        ("notice", "announcement", 8),
        ("alert", "announcement", 7),
        ("update", "announcement", 7),
        ("news", "announcement", 6),
        ("information", "announcement", 6),
        ("reminder", "announcement", 8),
        ("important", "announcement", 8),
        ("attention", "announcement", 8),

        # Task Keywords (Weight 6-8)
        ("task", "task", 7),
        ("activity", "task", 6),
        ("work", "task", 6),
        ("do", "task", 6),
        ("action", "task", 7),
        ("objective", "task", 6),
        ("goal", "task", 6),
        ("target", "task", 7),
        ("accomplish", "task", 7),

        # Report Keywords (Weight 6-8)
        ("report", "report", 8),
        ("summary", "report", 7),
        ("analysis", "report", 7),
        ("findings", "report", 7),
        ("conclusion", "report", 6),
        ("documentation", "report", 6),
        ("feedback", "report", 7),
        ("review", "report", 7),
        ("status", "report", 7),
    ]

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0
        
        self.stdout.write("Starting to populate ImportantKeyword model...")

        for keyword, category, weight in self.keywords_data:
            obj, created = ImportantKeyword.objects.get_or_create(
                keyword=keyword.lower(),
                defaults={
                    'category': category,
                    'weight': weight,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✓ Created: {keyword} ({category}) - Weight: {weight}")
            else:
                # Update existing keyword if needed
                if obj.category != category or obj.weight != weight:
                    obj.category = category
                    obj.weight = weight
                    obj.save()
                    updated_count += 1
                    self.stdout.write(f"↻ Updated: {keyword} ({category}) - Weight: {weight}")
                else:
                    self.stdout.write(f"- Exists: {keyword} ({category}) - Weight: {weight}")

        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n✅ Import completed successfully!"))
        self.stdout.write(f"📊 Total keywords processed: {len(self.keywords_data)}")
        self.stdout.write(f"➕ New keywords created: {created_count}")
        self.stdout.write(f"🔄 Keywords updated: {updated_count}")
        
        # Category breakdown
        self.stdout.write(f"\n📋 Keywords by category:")
        categories = {}
        for _, category, _ in self.keywords_data:
            categories[category] = categories.get(category, 0) + 1
        
        for category, count in categories.items():
            self.stdout.write(f"   {category.title()}: {count} keywords")
        
        # Weight distribution
        self.stdout.write(f"\n⚖️ Weight distribution:")
        weights = {}
        for _, _, weight in self.keywords_data:
            weights[weight] = weights.get(weight, 0) + 1
        
        for weight in sorted(weights.keys()):
            self.stdout.write(f"   Weight {weight}: {weights[weight]} keywords")

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing keywords before adding new ones',
        )

        # If clear option is used
        if '--clear' in parser.parse_known_args()[0].__dict__ and parser.parse_known_args()[0].clear:
            ImportantKeyword.objects.all().delete()
            self.stdout.write(self.style.WARNING("🗑️ Cleared all existing keywords"))