# context_processors.py
from .models import Post

def random_posts(_):
    # Your context processor logic using the 'request' object
    return {'random_posts': Post.objects.order_by('?')[:4]}
