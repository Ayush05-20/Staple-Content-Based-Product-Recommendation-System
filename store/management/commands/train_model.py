import os
import pickle

from django.conf import settings
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from store.models import Product


class Command(BaseCommand):
    help = (
        "Train the content-based similarity model locally and save the "
        ".pkl files into ml_models/. This is the same TF-IDF + cosine "
        "similarity approach as the Colab notebook (see README) - use "
        "whichever is more convenient. Run this again any time you add "
        "products and want them included in recommendations."
    )

    def handle(self, *args, **options):
        products = list(Product.objects.all().order_by('id'))
        if not products:
            self.stdout.write(self.style.ERROR("No products in the database yet. Import some first."))
            return

        texts = [p.content_text for p in products]
        product_ids = [p.id for p in products]

        self.stdout.write(f"Vectorizing {len(products)} products...")
        vectorizer = TfidfVectorizer(stop_words='english', max_features=20000)
        tfidf_matrix = vectorizer.fit_transform(texts)

        self.stdout.write("Computing cosine similarity matrix...")
        similarity_matrix = cosine_similarity(tfidf_matrix)

        ml_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        os.makedirs(ml_dir, exist_ok=True)

        with open(os.path.join(ml_dir, 'similarity_matrix.pkl'), 'wb') as f:
            pickle.dump(similarity_matrix, f)
        with open(os.path.join(ml_dir, 'product_ids.pkl'), 'wb') as f:
            pickle.dump(product_ids, f)

        self.stdout.write(self.style.SUCCESS(
            f"Saved similarity_matrix.pkl and product_ids.pkl for {len(products)} products."
        ))
