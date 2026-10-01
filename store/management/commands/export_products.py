import csv
from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = "Export current products to products_export.csv."

    def handle(self, *args, **options):
        path = 'products_export.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'category', 'brand', 'tags'])
            for p in Product.objects.all().order_by('id'):
                writer.writerow([p.id, p.name, p.category, p.brand, p.tags])

        self.stdout.write(self.style.SUCCESS(
            f"Exported {Product.objects.count()} products to {path}. "
            f"Upload this file to Colab to retrain the model."
        ))
