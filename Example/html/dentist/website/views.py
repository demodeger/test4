# NewSIte\dentist\website\views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category, Comment, Poll, Option
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
import feedparser
import re
from website.forms import PollForm
from datetime import datetime
import random

def remove_img_tags(value):
    return re.sub(r'<img[^>]+>', '', value)



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

class BlogView(ListView):
    model = Post
    template_name = 'blog.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        query = self.request.GET.get('q')  # Retrieve the search query

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        if query:
            # Filter posts by title or body containing the query
            queryset = queryset.filter(Q(title__icontains=query) | Q(body__icontains=query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rss_url = 'https://www.trthaber.com/manset_articles.rss'
        feed = feedparser.parse(rss_url)
    
    # Extract data from entries
        main_news = [extract_entry_data(entry) for entry in feed.entries[1:20]]
        main_news2 = [extract_entry_data(entry) for entry in feed.entries[1:5]]
        

        # Annotate each category with the count of posts using the correct related field name
        categories_with_count = Category.objects.annotate(
            posts_count=Count('posts')  # Adjusted from 'post' to 'posts'
        )
        
        context['categories'] = categories_with_count

        context['main_news'] = main_news
        context['main_news2'] = main_news2

        return context

    
    
class ArticleDetailView(DetailView):
    model = Post
    template_name = 'blognews.html'


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = self.object
            new_comment.save()
            return redirect(self.object.get_absolute_url())

        # If the form is not valid, render the same page with the existing context and form errors
        context = self.get_context_data(**kwargs)
        context['comment_form'] = comment_form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_posts = Post.objects.all().order_by('-id')[:6]
        rss_url = 'https://www.trthaber.com/manset_articles.rss'
        feed = feedparser.parse(rss_url)
        main_news = [extract_entry_data(entry) for entry in feed.entries[1:20]]
        main_news2 = [extract_entry_data(entry) for entry in feed.entries[1:5]]

        post = self.get_object()
        context['comments'] = post.comments.filter(active=True)
        context['comment_form'] = CommentForm() # Initialize an empty form for GET request
        context['paragraphs'] = post.split_body_into_paragraphs()
        context['related_blogs'] = Post.objects.exclude(id=post.id)[:6]
        context['main_news'] = main_news
        context['main_news2'] = main_news2
        context['latest_posts'] = latest_posts
        return context
    


def get_image_from_entry(entry):
    
    
    if 'media_content' in entry and len(entry['media_content']) > 0:
        # Get the first image URL
        image_url = entry['media_content'][0].get('url')
        return image_url
    # Return None if no image is found
    return None

def extract_entry_data(entry):
    
    image_url = get_image_from_entry(entry)
    summary = entry.get('summary', 'No Summary Provided')
    clean_summary = remove_img_tags(summary)
    return {
        'title': entry.get('title', 'No Title Provided'),
        'summary': clean_summary,
        'published': entry.get('published', 'No Publish Date Provided'),
        'image_url': image_url,
        'author': entry.get('author', 'No Summary Provided'),
        'time': entry.get('time', 'No Summary Provided'),
        # Add other fields as needed based on your data structure
    }




def home(request):
    # New RSS feed URLs
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    rss_url_business = 'https://abonerss.iha.com.tr/xml/standartrss?UserCode=3047&UstKategori=0&UserName=kimdenduydun&UserPassword=rss2&Kategori=0&Sehir=0&wp=0&tagp=0&tip=1'
    rss_url_tech = 'https://www.trthaber.com/bilim_teknoloji_articles.rss'
    rss_url_gen = 'https://abonerss.iha.com.tr/xml/standartrss?UserCode=3047&UstKategori=0&UserName=kimdenduydun&UserPassword=rss2&Kategori=8&Sehir=0&wp=0&tagp=0&tip=1'
    rss_url_sports = 'https://www.trthaber.com/spor_articles.rss'
    rss_url_politika = 'https://www.trthaber.com/sondakika_articles.rss'
    rss_url_dunya = 'https://www.trthaber.com/dunya_articles.rss'
    rss_url_saglik = 'https://www.trthaber.com/saglik_articles.rss'
    rss_url_sanat = 'https://www.trthaber.com/kultur_sanat_articles.rss'
    rss_url_econ = 'https://www.trthaber.com/ekonomi_articles.rss'
    rss_url_yemek = 'https://www.lezizyemeklerim.com/rss/yemek-tarifleri/yoresel-tarifler'
    # Fetch data from the RSS feeds
    feed_general = feedparser.parse(rss_url_general)
    feed_business = feedparser.parse(rss_url_business)
    feed_tech = feedparser.parse(rss_url_tech)
    feed_gen = feedparser.parse(rss_url_gen)
    feed_sports = feedparser.parse(rss_url_sports)
    feed_politika = feedparser.parse(rss_url_politika)
    feed_dunya = feedparser.parse(rss_url_dunya)
    feed_saglik = feedparser.parse(rss_url_saglik)
    feed_sanat = feedparser.parse(rss_url_sanat)
    feed_econ = feedparser.parse(rss_url_econ)
    feed_yemek = feedparser.parse(rss_url_yemek)

    # Process articles
    politika_news = [extract_entry_data(entry) for entry in feed_politika.entries[1:2]] #single politika
    politika_news_all = [extract_entry_data(entry) for entry in feed_politika.entries[2:6]] #4 politika
    politika_news_all2 = [extract_entry_data(entry) for entry in feed_politika.entries[4:6]] #4 politika
    saglik_news = [extract_entry_data(entry) for entry in feed_saglik.entries[1:2]] #single politika
    saglik_news_all = [extract_entry_data(entry) for entry in feed_saglik.entries[2:4]] #4 politika
    saglik_news_all2 = [extract_entry_data(entry) for entry in feed_saglik.entries[4:6]] #4 politika
    sanat_news = [extract_entry_data(entry) for entry in feed_sanat.entries[1:2]] #single politika
    sanat_news_all = [extract_entry_data(entry) for entry in feed_sanat.entries[2:4]] #4 politika
    sanat_news_all2 = [extract_entry_data(entry) for entry in feed_sanat.entries[4:6]] #4 politika
    dunya_news = [extract_entry_data(entry) for entry in feed_dunya.entries[1:2]]
    dunya_news_all = [extract_entry_data(entry) for entry in feed_dunya.entries[2:4]]
    dunya_news_all2 = [extract_entry_data(entry) for entry in feed_dunya.entries[4:6]]
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:4]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]] 
    featured_news = [extract_entry_data(entry) for entry in feed_econ.entries[1:20]] #econ
    business_news = feed_business.entries[:4]
    tech_news = [extract_entry_data(entry) for entry in feed_tech.entries[0:1]]
    tech_news_all = [extract_entry_data(entry) for entry in feed_tech.entries[1:6]]  
    gen_news = [extract_entry_data(entry) for entry in feed_gen.entries[1:10]]
    sports_news = [extract_entry_data(entry) for entry in feed_sports.entries[1:2]]
    sports_news_all = [extract_entry_data(entry) for entry in feed_sports.entries[2:4]]
    sports_news_all2 = [extract_entry_data(entry) for entry in feed_sports.entries[4:6]]
    featured_news3 = [extract_entry_data(entry) for entry in feed_general.entries[2:3]] 
    featured_news4 = [extract_entry_data(entry) for entry in feed_sports.entries[2:6]]
    featured_news5 = feed_sports.entries[6:8]
    featured_news6 = feed_sports.entries[6:7]
    econ_news = [extract_entry_data(entry) for entry in feed_econ.entries[1:2]]
    econ_news_all = [extract_entry_data(entry) for entry in feed_econ.entries[2:4]]
    econ_news_all2 = [extract_entry_data(entry) for entry in feed_econ.entries[4:6]]

    top_news = [extract_entry_data(entry) for entry in feed_general.entries[1:2]]

    # Featured News 2
    featured_news2 = [extract_entry_data(entry) for entry in feed_general.entries[1:2]]
    yemek_tarif = [extract_entry_data(entry) for entry in feed_yemek.entries[0:3]]

    latest_posts = Post.objects.all().order_by('-id')[:6]


    poll = Poll.objects.first()  # Or use another method to select the poll

        # Check if the form is submitted
    if request.method == 'POST' and 'poll' in request.POST:
        # This assumes your form sends the ID of the chosen option
        option_id = request.POST.get('option')
        option = get_object_or_404(Option, pk=option_id)
        option.votes += 1
        option.save()
        print(request.method)

        # Redirect to prevent double submissions
        return redirect('home')
    else:
        # If the method is GET or it's not a poll submission, display a new form
        form = PollForm()

    current_date = datetime.now()
        

    
        

    context = {
        'top_news': top_news,
        'main_news': main_news,
        'featured_news': featured_news,
        'business_news': business_news,
        'tech_news': tech_news,
        'gen_news': gen_news,
        'sports_news': sports_news,
        'featured_news2': featured_news2,
        'featured_news3': featured_news3,
        'featured_news4': featured_news4,
        'featured_news5': featured_news5,
        'featured_news6': featured_news6,
        'politika_news': politika_news,
        'politika_news_all': politika_news_all,
        'politika_news_all2': politika_news_all2,
        'dunya_news': dunya_news,
        'dunya_news_all': dunya_news_all,
        'saglik_news': saglik_news,
        'saglik_news_all': saglik_news_all,
        'sanat_news': sanat_news,
        'sanat_news_all': sanat_news_all,
        'dunya_news_all2': dunya_news_all2,
        'tech_news_all': tech_news_all,
        'econ_news_all': econ_news_all,
        'econ_news_all2': econ_news_all2,
        'econ_news': econ_news,
        'sports_news_all': sports_news_all,
        'sports_news_all2': sports_news_all2,
        'saglik_news_all2': saglik_news_all2,
        'sanat_news_all2': sanat_news_all2,
        'yemek_tarif': yemek_tarif,
        'main_news1': main_news1,
        'poll': poll,
        'form': form,
        'current_date': current_date,
        'latest_posts': latest_posts,

    }

    return render(request, 'home.html', context)



def about(request):
    return render(request, 'about.html')




def single(request, entry_id):
    # Retrieve all news entries stored in the session
    all_news = request.session.get('all_news', [])
    
    # Find the specific entry by entry_id
    entry = next((item for item in all_news if item.get('id') == int(entry_id)), None)

    if entry:
        return render(request, 'singlenews.html', {'entry': entry})
    else:
        # Handle case where entry is not found
        return HttpResponseNotFound('<h1>News item not found</h1>')
    



def elements(request):
    return render(request, 'elements.html')

#def contact(request):
   # if request.method == "POST":
    #    message_name = request.POST['message-name']
     #   message_email = request.POST['message-email']
      #  message_subject = request.POST['message-subject']
       # message = request.POST['message']
#
 #       send_mail(
  #          message_subject,
   #         message,
    #        message_email,
     #       ['haberallllll@gmail.com'],  # Change to your email address
      #  )
#
 #       return render(request, 'contact.html', {'message_name': message_name})
#
 #   else:
  #      return render(request, 'contact.html', {})

class BaseView(ListView):
    template_name = 'contact.html', 'category.html', 'home.html', 'about.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_posts'] = Post.objects.order_by('')[0:6]
        return context
    
def finance(request):
    

    rss_url_econ = 'https://www.trthaber.com/ekonomi_articles.rss'
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    feed_general = feedparser.parse(rss_url_general)
    feed_econ = feedparser.parse(rss_url_econ)
    econ_news = [extract_entry_data(entry) for entry in feed_econ.entries[1:2]]
    econ_news_all = [extract_entry_data(entry) for entry in feed_econ.entries[2:4]]
    econ_news_all2 = [extract_entry_data(entry) for entry in feed_econ.entries[4:6]]
    econ_news_all3 = [extract_entry_data(entry) for entry in feed_econ.entries[1:20]]
    econ_news_all4 = [extract_entry_data(entry) for entry in feed_econ.entries[6:8]] #tradenews
    econ_news_all5 = [extract_entry_data(entry) for entry in feed_econ.entries[8:9]]
    econ_news_all6 = [extract_entry_data(entry) for entry in feed_econ.entries[9:13]]
    econ_news_all7 = [extract_entry_data(entry) for entry in feed_econ.entries[13:14]]
    econ_news_all8 = [extract_entry_data(entry) for entry in feed_econ.entries[14:18]]
    econ_news_all9 = [extract_entry_data(entry) for entry in feed_econ.entries[18:20]]
    econ_news_all10 = [extract_entry_data(entry) for entry in feed_econ.entries[20:22]]
    econ_news_all11 = [extract_entry_data(entry) for entry in feed_econ.entries[22:25]]
    econ_news_all12 = [extract_entry_data(entry) for entry in feed_econ.entries[25:28]]
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:4]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]]


    context = {
        'econ_news_all': econ_news_all,
        'econ_news_all2': econ_news_all2,
        'econ_news': econ_news,
        'econ_news_all3': econ_news_all3,
        'econ_news_all4': econ_news_all4,
        'econ_news_all5': econ_news_all5,
        'econ_news_all6': econ_news_all6,
        'econ_news_all7': econ_news_all7,
        'econ_news_all8': econ_news_all8,
        'econ_news_all9': econ_news_all9,
        'econ_news_all10': econ_news_all10,
        'econ_news_all11': econ_news_all11,
        'econ_news_all12': econ_news_all12,
        'main_news': main_news,
        'main_news1': main_news1,

    }
    
    
    return render(request, 'finance.html', context)    

def tech(request):

    rss_url_econ = 'https://www.trthaber.com/bilim_teknoloji_articles.rss'
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    feed_general = feedparser.parse(rss_url_general)
    feed_econ = feedparser.parse(rss_url_econ)
    econ_news = [extract_entry_data(entry) for entry in feed_econ.entries[1:2]]
    econ_news_all = [extract_entry_data(entry) for entry in feed_econ.entries[2:4]]
    econ_news_all2 = [extract_entry_data(entry) for entry in feed_econ.entries[4:6]]
    econ_news_all3 = [extract_entry_data(entry) for entry in feed_econ.entries[1:20]]
    econ_news_all4 = [extract_entry_data(entry) for entry in feed_econ.entries[6:8]] #tradenews
    econ_news_all5 = [extract_entry_data(entry) for entry in feed_econ.entries[8:9]]
    econ_news_all6 = [extract_entry_data(entry) for entry in feed_econ.entries[9:13]]
    econ_news_all7 = [extract_entry_data(entry) for entry in feed_econ.entries[13:14]]
    econ_news_all8 = [extract_entry_data(entry) for entry in feed_econ.entries[14:18]]
    econ_news_all9 = [extract_entry_data(entry) for entry in feed_econ.entries[18:20]]
    econ_news_all10 = [extract_entry_data(entry) for entry in feed_econ.entries[20:22]]
    econ_news_all11 = [extract_entry_data(entry) for entry in feed_econ.entries[22:25]]
    econ_news_all12 = [extract_entry_data(entry) for entry in feed_econ.entries[25:28]]
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:4]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]]


    context = {
        'econ_news_all': econ_news_all,
        'econ_news_all2': econ_news_all2,
        'econ_news': econ_news,
        'econ_news_all3': econ_news_all3,
        'econ_news_all4': econ_news_all4,
        'econ_news_all5': econ_news_all5,
        'econ_news_all6': econ_news_all6,
        'econ_news_all7': econ_news_all7,
        'econ_news_all8': econ_news_all8,
        'econ_news_all9': econ_news_all9,
        'econ_news_all10': econ_news_all10,
        'econ_news_all11': econ_news_all11,
        'econ_news_all12': econ_news_all12,
        'main_news': main_news,
        'main_news1': main_news1,

    }

    return render(request, 'tech.html', context)

def sports(request):

    rss_url_sports = 'https://www.trthaber.com/spor_articles.rss'
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    feed_general = feedparser.parse(rss_url_general)
    feed_econ = feedparser.parse(rss_url_sports)
    econ_news = [extract_entry_data(entry) for entry in feed_econ.entries[1:2]]
    econ_news_all = [extract_entry_data(entry) for entry in feed_econ.entries[2:4]]
    econ_news_all2 = [extract_entry_data(entry) for entry in feed_econ.entries[4:6]]
    econ_news_all3 = [extract_entry_data(entry) for entry in feed_econ.entries[1:20]]
    econ_news_all4 = [extract_entry_data(entry) for entry in feed_econ.entries[6:8]] #tradenews
    econ_news_all5 = [extract_entry_data(entry) for entry in feed_econ.entries[8:9]]
    econ_news_all6 = [extract_entry_data(entry) for entry in feed_econ.entries[9:13]]
    econ_news_all7 = [extract_entry_data(entry) for entry in feed_econ.entries[13:14]]
    econ_news_all8 = [extract_entry_data(entry) for entry in feed_econ.entries[14:18]]
    econ_news_all9 = [extract_entry_data(entry) for entry in feed_econ.entries[18:20]]
    econ_news_all10 = [extract_entry_data(entry) for entry in feed_econ.entries[20:22]]
    econ_news_all11 = [extract_entry_data(entry) for entry in feed_econ.entries[22:25]]
    econ_news_all12 = [extract_entry_data(entry) for entry in feed_econ.entries[25:28]]
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:4]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]]


    context = {
        'econ_news_all': econ_news_all,
        'econ_news_all2': econ_news_all2,
        'econ_news': econ_news,
        'econ_news_all3': econ_news_all3,
        'econ_news_all4': econ_news_all4,
        'econ_news_all5': econ_news_all5,
        'econ_news_all6': econ_news_all6,
        'econ_news_all7': econ_news_all7,
        'econ_news_all8': econ_news_all8,
        'econ_news_all9': econ_news_all9,
        'econ_news_all10': econ_news_all10,
        'econ_news_all11': econ_news_all11,
        'econ_news_all12': econ_news_all12,
        'main_news': main_news,
        'main_news1': main_news1,

    }

    return render(request, 'sports.html', context)

def yasam(request):

    rss_url_yasam = 'https://www.trthaber.com/yasam_articles.rss'
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    feed_general = feedparser.parse(rss_url_general)
    feed_econ = feedparser.parse(rss_url_yasam)
    econ_news = [extract_entry_data(entry) for entry in feed_econ.entries[1:2]]
    econ_news_all = [extract_entry_data(entry) for entry in feed_econ.entries[2:4]]
    econ_news_all2 = [extract_entry_data(entry) for entry in feed_econ.entries[4:6]]
    econ_news_all3 = [extract_entry_data(entry) for entry in feed_econ.entries[1:20]]
    econ_news_all4 = [extract_entry_data(entry) for entry in feed_econ.entries[6:8]] #tradenews
    econ_news_all5 = [extract_entry_data(entry) for entry in feed_econ.entries[8:9]]
    econ_news_all6 = [extract_entry_data(entry) for entry in feed_econ.entries[9:13]]
    econ_news_all7 = [extract_entry_data(entry) for entry in feed_econ.entries[13:14]]
    econ_news_all8 = [extract_entry_data(entry) for entry in feed_econ.entries[14:18]]
    econ_news_all9 = [extract_entry_data(entry) for entry in feed_econ.entries[18:20]]
    econ_news_all10 = [extract_entry_data(entry) for entry in feed_econ.entries[20:22]]
    econ_news_all11 = [extract_entry_data(entry) for entry in feed_econ.entries[22:25]]
    econ_news_all12 = [extract_entry_data(entry) for entry in feed_econ.entries[25:28]]
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:4]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]]


    context = {
        'econ_news_all': econ_news_all,
        'econ_news_all2': econ_news_all2,
        'econ_news': econ_news,
        'econ_news_all3': econ_news_all3,
        'econ_news_all4': econ_news_all4,
        'econ_news_all5': econ_news_all5,
        'econ_news_all6': econ_news_all6,
        'econ_news_all7': econ_news_all7,
        'econ_news_all8': econ_news_all8,
        'econ_news_all9': econ_news_all9,
        'econ_news_all10': econ_news_all10,
        'econ_news_all11': econ_news_all11,
        'econ_news_all12': econ_news_all12,
        'main_news': main_news,
        'main_news1': main_news1,

    }

    return render(request, 'yasam.html', context)

def dunya(request):

    rss_url_dunya = 'https://www.trthaber.com/dunya_articles.rss'
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    feed_general = feedparser.parse(rss_url_general)
    feed_econ = feedparser.parse(rss_url_dunya)
    econ_news = [extract_entry_data(entry) for entry in feed_econ.entries[1:2]]
    econ_news_all = [extract_entry_data(entry) for entry in feed_econ.entries[2:4]]
    econ_news_all2 = [extract_entry_data(entry) for entry in feed_econ.entries[4:6]]
    econ_news_all3 = [extract_entry_data(entry) for entry in feed_econ.entries[1:20]]
    econ_news_all4 = [extract_entry_data(entry) for entry in feed_econ.entries[6:8]] #tradenews
    econ_news_all5 = [extract_entry_data(entry) for entry in feed_econ.entries[8:9]]
    econ_news_all6 = [extract_entry_data(entry) for entry in feed_econ.entries[9:13]]
    econ_news_all7 = [extract_entry_data(entry) for entry in feed_econ.entries[13:14]]
    econ_news_all8 = [extract_entry_data(entry) for entry in feed_econ.entries[14:18]]
    econ_news_all9 = [extract_entry_data(entry) for entry in feed_econ.entries[18:20]]
    econ_news_all10 = [extract_entry_data(entry) for entry in feed_econ.entries[20:22]]
    econ_news_all11 = [extract_entry_data(entry) for entry in feed_econ.entries[22:25]]
    econ_news_all12 = [extract_entry_data(entry) for entry in feed_econ.entries[25:28]]
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:4]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]]


    context = {
        'econ_news_all': econ_news_all,
        'econ_news_all2': econ_news_all2,
        'econ_news': econ_news,
        'econ_news_all3': econ_news_all3,
        'econ_news_all4': econ_news_all4,
        'econ_news_all5': econ_news_all5,
        'econ_news_all6': econ_news_all6,
        'econ_news_all7': econ_news_all7,
        'econ_news_all8': econ_news_all8,
        'econ_news_all9': econ_news_all9,
        'econ_news_all10': econ_news_all10,
        'econ_news_all11': econ_news_all11,
        'econ_news_all12': econ_news_all12,
        'main_news': main_news,
        'main_news1': main_news1,

    }

    return render(request, 'dunya.html', context)

def contact(request):
    

    
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    feed_general = feedparser.parse(rss_url_general)
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:20]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]]


    context = {
        'main_news': main_news,
        'main_news1': main_news1,

    }
    
    
    return render(request, 'contact.html', context)   

def about(request):
    

    
    rss_url_general = 'https://www.trthaber.com/manset_articles.rss'
    feed_general = feedparser.parse(rss_url_general)
    main_news = [extract_entry_data(entry) for entry in feed_general.entries[0:20]]
    main_news1 = [extract_entry_data(entry) for entry in feed_general.entries[4:8]]


    context = {
        'main_news': main_news,
        'main_news1': main_news1,

    }
    
    
    return render(request, 'about.html', context)

