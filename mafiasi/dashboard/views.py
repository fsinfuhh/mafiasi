from django.template.response import TemplateResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.conf import settings

from mafiasi.dashboard.models import News, Panel

def index(request):
    news_list = News.objects.filter(frontpage=True, published=True) \
                .order_by('-created_at')
    panel_list = Panel.objects.filter(shown=True).order_by('position')

    return TemplateResponse(request, 'dashboard/index.html', {
        'news_list': news_list,
        'panel_list': panel_list,
        'service_links': settings.SERVICE_LINKS,
        'wiki_search_url': settings.WIKI_URL + 'index.php',
        'activated_services': settings.DASHBOARD_SERVICES
    })

def show_news(request, news_pk):
    news = get_object_or_404(News, pk=news_pk)
    if not news.published and news.created_by != request.user:
        raise Http404

    return TemplateResponse(request, 'dashboard/show_news.html', {
        'news': news
    })
