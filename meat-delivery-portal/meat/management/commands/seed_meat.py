import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Profile
from meat.models import Meat
from orders.models import Order, Item

class Command(BaseCommand):
    help = 'Seed the database with two sample users, massive meat data, and massive order history'

    def handle(self, *args, **kwargs):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
            Profile.objects.get_or_create(user=admin_user, role='company', company_name='AdminMeatCo')
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / adminpass123'))
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.WARNING('Admin user already exists.'))

        # Create customer user
        if not User.objects.filter(username='customer').exists():
            customer_user = User.objects.create_user('customer', 'customer@example.com', 'customerpass123')
            Profile.objects.get_or_create(user=customer_user, role='client')
            self.stdout.write(self.style.SUCCESS('Created customer user: customer / customerpass123'))
        else:
            customer_user = User.objects.get(username='customer')
            self.stdout.write(self.style.WARNING('Customer user already exists.'))

        company_names = [
            "RedCow Ltd", "Porky Partners", "ChickenKing", "LambLand", "MeatMaster", "PrimeCuts", "FarmFresh", "UrbanMeat", "CountryBeef", "PoultryPro"
        ]
        meat_types = ['beef', 'pork', 'chicken', 'lamb']
        companies = []

        # Create companies if not exist
        for name in company_names:
            username = name.lower().replace(' ', '_')
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('password123')
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user, role='company', company_name=name)
            companies.append(profile)

        # Create massive meat data
        meats = []
        for i in range(500):
            company = random.choice(companies)
            meat_type = random.choice(meat_types)
            quantity = random.randint(10, 500)
            price = round(random.uniform(3.0, 25.0), 2)
            meats.append(Meat(
                company=company,
                meat_type=meat_type,
                quantity=quantity,
                price=price
            ))
        Meat.objects.bulk_create(meats)
        self.stdout.write(self.style.SUCCESS('Successfully seeded 500+ meat entries.'))

        # Massive order history for forecast
        all_meats = list(Meat.objects.all())
        # Add 2000 random orders for the customer user, spread over the last 90 days
        customer_user = User.objects.get(username='customer')
        order_count = 2000
        items_created = 0
        for _ in range(order_count):
            days_ago = random.randint(0, 89)
            order_date = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            order = Order.objects.create(
                user=customer_user,
                status=random.choice(['pending', 'processing', 'delivered']),
                created_at=order_date
            )
            meats_in_order = random.sample(all_meats, k=random.randint(1, 5))
            for meat in meats_in_order:
                qty = random.randint(1, min(10, meat.quantity))
                if qty > 0:
                    Item.objects.create(
                        order=order,
                        meat=meat,
                        quantity=qty,
                        price=meat.price
                    )
                    items_created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {order_count} orders and {items_created} order items for history.'))
