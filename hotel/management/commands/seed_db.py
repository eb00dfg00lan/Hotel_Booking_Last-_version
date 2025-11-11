from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help = 'Try to run tools.db.init_db and tools.db.seed_database from Streamlit project'
    def handle(self, *args, **options):
        try:
            from tools.db import init_db, seed_database
            init_db()
            seed_database()
            self.stdout.write(self.style.SUCCESS('DB initialized and seeded via tools.db'))
        except Exception as e:
            self.stderr.write(f'Error running tools.db functions: {e}')
            from hotel.models import Hotel, Room
            if Hotel.objects.count() == 0:
                h = Hotel.objects.create(name='Seed Hotel', address='Seed Ave 1')
                Room.objects.create(hotel=h, title='Basic', price=50, capacity=2)
                self.stdout.write(self.style.SUCCESS('Created fallback seed data'))
