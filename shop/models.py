
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    link = models.TextField(null=False)
    genre = models.TextField()
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
    tokens = models.TextField(null=False,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{'추천' if self.recommend else '비추천'} - {self.created_at.strftime('%Y-%m-%d')}"
    
    
    
class ReviewAnalysis(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    total_reviews = models.PositiveIntegerField(default=0)
    positive_count = models.PositiveIntegerField(default=0)
    neutral_count = models.PositiveIntegerField(default=0)
    negative_count = models.PositiveIntegerField(default=0)
    average_length = models.FloatField(default=0.0)
    cluster_json = models.JSONField(null=True, blank=True)
    wordcloud_image = models.ImageField(upload_to='wordclouds/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def sentiment_ratio(self):
        total = self.total_reviews or 1
        return {
            "긍정": round(self.positive_count / total * 100, 1),
            "애매": round(self.neutral_count / total * 100, 1),
            "부정": round(self.negative_count / total * 100, 1)
        }
