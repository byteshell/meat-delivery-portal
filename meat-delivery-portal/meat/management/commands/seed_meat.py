import random
from datetime import timedelta, datetime
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
        company_addresses = [
            "123 Main St, Springfield", "456 Oak Ave, Shelbyville", "789 Maple Rd, Capital City",
            "101 River Dr, Ogdenville", "202 Hilltop Ln, North Haverbrook", "303 Lakeview Blvd, Brockway",
            "404 Pine St, Waverly Hills", "505 Cedar Ct, Cypress Creek", "606 Elm St, West Springfield",
            "707 Birch Ave, Monorail City"
        ]
        company_latlng = [
            (40.7128, -74.0060), (41.8781, -87.6298), (34.0522, -118.2437),
            (29.7604, -95.3698), (39.9526, -75.1652), (33.4484, -112.0740),
            (32.7767, -96.7970), (37.7749, -122.4194), (47.6062, -122.3321),
            (42.3601, -71.0589)
        ]
        meat_types = ['beef', 'pork', 'chicken', 'lamb']
        companies = []

        # Create companies if not exist
        for idx, name in enumerate(company_names):
            username = name.lower().replace(' ', '_')
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('password123')
                user.save()
            address = company_addresses[idx % len(company_addresses)]
            lat, lng = company_latlng[idx % len(company_latlng)]
            profile, _ = Profile.objects.get_or_create(
                user=user,
                role='company',
                company_name=name,
                defaults={'address': address, 'latitude': lat, 'longitude': lng}
            )
            # Update address and geolocation if already exists
            profile.address = address
            profile.latitude = lat
            profile.longitude = lng
            profile.save()
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

        # --- Clear previous order history ---
        Item.objects.all().delete()
        Order.objects.all().delete()

        # Massive order history for forecast
        all_meats = list(Meat.objects.all())
        customer_user = User.objects.get(username='customer')
        order_count = 2000
        items_created = 0

        # Set the start and end date for the range
        start_date = datetime(2024, 5, 1)
        end_date = datetime(2025, 5, 1)
        total_days = (end_date - start_date).days

        # Create orders and items with correct created_at using save(update_fields=['created_at'])
        orders = []
        for _ in range(order_count):
            random_days = random.randint(0, total_days - 1)
            random_seconds = random.randint(0, 86399)
            naive_order_date = start_date + timedelta(days=random_days, seconds=random_seconds)
            # Make the datetime timezone-aware
            order_date = timezone.make_aware(naive_order_date, timezone.get_default_timezone())
            order = Order.objects.create(
                user=customer_user,
                status=random.choice(['pending', 'processing', 'delivered'])
                # created_at will be set after save
            )
            order.created_at = order_date
            order.save(update_fields=['created_at'])
            orders.append(order)

        # Now create items for each order
        for order in orders:
            meats_in_order = random.sample(all_meats, k=random.randint(1, 5))
            for meat in meats_in_order:
                if meat.quantity > 0:
                    qty = random.randint(1, min(10, meat.quantity))
                    Item.objects.create(
                        order=order,
                        meat=meat,
                        quantity=qty,
                        price=meat.price
                    )
                    items_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {order_count} orders and {items_created} order items for history.'))
