from django.template.response import TemplateResponse
from django.http import Http404
from django.shortcuts import get_object_or_404

from mafiasi.dashboard.models import News

def index(request):
    news_list = News.objects.filter(frontpage=True, published=True) \
                .order_by('-created_at')

    return TemplateResponse(request, 'dashboard/index.html', {
        'news_list': news_list
    })

def show_news(request, news_pk):
    news = get_object_or_404(News, pk=news_pk)
    if not news.published and news.created_by != request.user:
        raise Http404

    return TemplateResponse(request, 'dashboard/show_news.html', {
        'news': news
    })
