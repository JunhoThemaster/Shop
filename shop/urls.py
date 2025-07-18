"""
URL configuration for shopbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from shop.admservice import admin_view
from shop.admservice.admin_view import admin_home

urlpatterns = [
    path('',views.home,name="home"),
    path('admins',admin_home,name="admin_home"),
    path("api/product/<int:product_id>/summary/", views.summarize_review, name="review_summary_api"),
    path("api/admins/<int:product_id>/sent_ratio", admin_view.init_sentiment_ratio,name="init_sentiment_api"),
    path("api/admins/<int:product_id>/get_sent",admin_view.get_sentiment_ratio,name= "get_sentiment_api"),
    path("api/admins/<int:product_id>/get_trend",admin_view.get_review_trend,name = "get_trend_api")
    # path('product/<int:product_id>/',views.product_detail,name="product_detail")
]
