from django.apps import apps
from django.template.response import TemplateResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.conf import settings

from mafiasi.base.base_apps import BaseService
from mafiasi.dashboard.models import News, Panel


def index(request):
    news_list = News.objects.filter(frontpage=True, published=True) \
                .order_by('-created_at')
    panel_list = Panel.objects.filter(shown=True).order_by('position')
    service_list = [i for i in apps.get_app_configs() if isinstance(i, BaseService)]

    return TemplateResponse(request, 'dashboard/index.html', {
        'news_list': news_list,
        'panel_list': panel_list,
        'wiki_search_url': settings.WIKI_URL + '/index.php',
        'services': service_list,
        'service_names': [i.name for i in service_list]
    })


def show_news(request, news_pk):
    news = get_object_or_404(News, pk=news_pk)
    if not news.published and news.created_by != request.user:
        raise Http404

    return TemplateResponse(request, 'dashboard/show_news.html', {
        'news': news
    })
