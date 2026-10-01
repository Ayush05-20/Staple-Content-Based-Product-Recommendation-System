import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = "Import products from data/products_import.csv into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', default=str(settings.BASE_DIR / 'data' / 'products_import.csv'),
            help='Path to the CSV file to import.'
        )
        parser.add_argument(
            '--wipe', action='store_true',
            help='Delete all existing products first (recommended for a fresh, matching import).'
        )

    def handle(self, *args, **options):
        path = options['file']

        if options['wipe']:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(f"Removed {deleted} existing rows.")

        if Product.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Products already exist in the database. For the bundled "
                "similarity_matrix.pkl to line up correctly, this import "
                "should run against an EMPTY table. Re-run with --wipe if "
                "you want a clean, matching import."
            ))

        created = 0
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = []
            for row in reader:
                if not row.get('Name'):
                    continue
                products.append(Product(
                    name=row['Name'][:300],
                    brand=(row.get('BrandClean') or '')[:150],
                    category=(row.get('CategoryShort') or row.get('Category') or '')[:300],
                    description=row.get('Description') or '',
                    tags=row.get('Tags') or '',
                    price=0,
                    image_url=(row.get('ImageURL') or '')[:600],
                ))
            Product.objects.bulk_create(products)
            created = len(products)

        self.stdout.write(self.style.SUCCESS(f"Imported {created} products."))
