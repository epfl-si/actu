from django.shortcuts import render
from .models import News

def list_news(request):
    news = News.objects.all()

    context = {
        'news': news
    }

    return render(request,'list.html', context)
