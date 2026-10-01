from django.conf import settings
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=300)
    brand = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    tags = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image_url = models.URLField(max_length=600, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def content_text(self):
        """The text the recommendation model actually reads."""
        return f"{self.name} {self.category} {self.brand} {self.tags}"

    @property
    def category_display(self):
        return self.category.split(',')[0].strip().title() if self.category else ''


class Interaction(models.Model):
    VIEW = 'view'
    LIKE = 'like'
    ACTION_CHOICES = [(VIEW, 'View'), (LIKE, 'Like')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='interactions')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default=VIEW)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.action} {self.product}"
