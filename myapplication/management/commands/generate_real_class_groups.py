import random
from django.core.management.base import BaseCommand
from myapplication.models import WhatsAppGroup, GroupMember

class Command(BaseCommand):
    help = "Add real members to specific WhatsApp class groups"

    members = [
        ("Steve Mwikali", "0712345678"),
        ("Faith Kamau", "0798765432"),
        ("Brian Otieno", "0723456789"),
        ("Mary Wanjiku", "0700111222"),
        ("John Mwangi", "0744556677"),
        ("Cynthia Achieng", "0711223344"),
        ("Kevin Kiptoo", "0709988776"),
        ("Angela Njeri", "0733445566"),
        ("Samuel Njoroge", "0799887766"),
        ("Diana Chebet", "0722334455"),
        ("Elvis Maina", "0711888999"),
        ("Lucy Wambui", "0788996655"),
        ("Peter Kilonzo", "0765432109"),
        ("Nancy Nyambura", "0710101010"),
        ("Collins Ouma", "0799001122"),
        ("Betty Wairimu", "0700998877"),
        ("George Karani", "0744332211"),
        ("Grace Mutua", "0711777888"),
        ("James Muriuki", "0707001234"),
        ("Mercy Nduta", "0712456789"),
        ("Joseph Karanja", "0712003040"),
        ("Eunice Waithera", "0722005030"),
        ("Mark Wekesa", "0799001123"),
        ("Irene Adhiambo", "0722233445"),
        ("Dennis Kimani", "0700998871"),
        ("Janet Muthoni", "0700111133"),
    ]

    target_groups = [
        "Physics Class Group",
        "Math Revision Class",
        "Biology Classmates Hub",
        "Chemistry Q&A",
        "History Discussion Forum",
    ]

    def handle(self, *args, **kwargs):
        groups = WhatsAppGroup.objects.filter(group_name__in=self.target_groups)

        if not groups.exists():
            self.stdout.write(self.style.ERROR("No matching groups found!"))
            return

        for group in groups:
            group_size = random.choice([8, 10, 13])
            # Remove the used_members restriction
            group_members = random.sample(self.members, group_size)

            for idx, (name, phone) in enumerate(group_members):
                role = (
                    'class_rep' if idx == 0 else
                    'teacher' if idx == 1 else
                    'student'
                )

                GroupMember.objects.create(
                    whatsapp_group=group,
                    name=name,
                    phone_number=phone,
                    role=role
                )

            self.stdout.write(self.style.SUCCESS(
                f"Added {group_size} members to '{group.group_name}'"
            ))