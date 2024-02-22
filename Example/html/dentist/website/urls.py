# NewSIte\dentist\website\urls.py

from django.urls import path
from . import views
from .views import BlogView, ArticleDetailView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('blog/category/<slug:category_slug>/', BlogView.as_view(), name='blog_by_category'),
    path('blog/', BlogView.as_view(), name='blog'),  # Use BlogView for the /blog/ URL
    path('blognews/<int:pk>/', ArticleDetailView.as_view(), name='blognews'),
    path('elements/', views.elements, name='elements'),
    path('contact/', views.contact, name='contact'),
    path('about.html/', views.contact, name='about_html'),
    path('finance/', views.finance, name='finance'),
    path('tech/', views.tech, name='tech'),
    path('yasam/', views.yasam, name='yasam'),
    path('sports/', views.sports, name='sports'),
    path('dunya/', views.dunya, name='dunya'),
    path('singlenews/<int:entry_id>/', views.single, name='singlenews'),
    path('blognews/<int:pk>/', ArticleDetailView.as_view(), name='home'),
]
