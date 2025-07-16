
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    pc_min_req = models.TextField()
    price = models.IntegerField(null=False)
    developer = models.TextField(null=False)
    summary = models.TextField(null=True)
    created_at = models.DateTimeField()
    
    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    recommend = models.BooleanField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{'추천' if self.recommend else '비추천'} - {self.created_at.strftime('%Y-%m-%d')}"
    
    
    
class ReviewAnalysis(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='analysis')
    is_negative = models.BooleanField()
    keywords = models.TextField()
    summary = models.TextField(null=True, blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
