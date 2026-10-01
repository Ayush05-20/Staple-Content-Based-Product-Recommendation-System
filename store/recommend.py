"""
Content-based recommendation engine.

Training happens OFFLINE (in Google Colab, or the optional local
management command). This module only LOADS the two files that
training produces and uses them to answer "what's similar to product X".

Files expected in ml_models/:
    - similarity_matrix.pkl  -> NxN cosine similarity scores
    - product_ids.pkl        -> list mapping matrix row -> Product.id
"""

import os
import pickle

from django.conf import settings

from .models import Product

ML_MODELS_DIR = os.path.join(settings.BASE_DIR, 'ml_models')

_cache = {}


def _load():
    """Load the pkl files once per process and keep them in memory."""
    if 'similarity_matrix' not in _cache:
        sim_path = os.path.join(ML_MODELS_DIR, 'similarity_matrix.pkl')
        ids_path = os.path.join(ML_MODELS_DIR, 'product_ids.pkl')

        if not (os.path.exists(sim_path) and os.path.exists(ids_path)):
            _cache['similarity_matrix'] = None
            _cache['product_ids'] = None
            return None, None

        with open(sim_path, 'rb') as f:
            _cache['similarity_matrix'] = pickle.load(f)
        with open(ids_path, 'rb') as f:
            _cache['product_ids'] = pickle.load(f)

    return _cache['similarity_matrix'], _cache['product_ids']


def model_is_ready():
    sim, ids = _load()
    return sim is not None and ids is not None


def get_similar_products(product_id, top_n=8):
    """Return up to top_n products most similar to product_id."""
    similarity_matrix, product_ids = _load()

    if similarity_matrix is None or product_id not in product_ids:
        # Model not trained yet, or this product didn't exist at training
        # time (added after the last retrain) -> no similarity data for it.
        return []

    idx = product_ids.index(product_id)
    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = [s for s in scores if s[0] != idx and s[1] > 0][:top_n]

    similar_ids = [product_ids[i] for i, _ in scores]
    products = list(Product.objects.filter(id__in=similar_ids))
    products.sort(key=lambda p: similar_ids.index(p.id))
    return products


def get_homepage_picks(user, top_n=8):
    """
    Very simple personalization: average the similarity rows of every
    product the user has viewed, rank everything against that average.
    Falls back to newest products for a logged-out user / new user.
    """
    similarity_matrix, product_ids = _load()

    if not user.is_authenticated or similarity_matrix is None:
        return None  # caller falls back to a plain newest-products query

    from .models import Interaction
    seen_ids = list(
        Interaction.objects.filter(user=user).values_list('product_id', flat=True)
    )
    seen_indices = [product_ids.index(pid) for pid in seen_ids if pid in product_ids]

    if not seen_indices:
        return None

    import numpy as np
    avg_scores = np.mean(similarity_matrix[seen_indices], axis=0)
    ranked = sorted(enumerate(avg_scores), key=lambda x: x[1], reverse=True)
    recommended_ids = [product_ids[i] for i, _ in ranked if product_ids[i] not in seen_ids][:top_n]

    products = list(Product.objects.filter(id__in=recommended_ids))
    products.sort(key=lambda p: recommended_ids.index(p.id))
    return products
