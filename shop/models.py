
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.CharField(max_length=50)
    rating = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ReviewAnalysis(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='analysis')
    is_negative = models.BooleanField()
    keywords = models.TextField()
    summary = models.TextField(null=True, blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
