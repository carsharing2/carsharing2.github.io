from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^page(?P<page>[0-9]+)/$', views.index, name='index_page'),
    url(r'^createpost/$', views.create, name = 'create'),
    url(r'^(?P<thread_id>[0-9]+)/createpost/$', views.create, name='create_post'),
    url(r'^(?P<thread_id>[0-9]+)/getposts/$', views.thread, {'render_posts_only' : True}, name='get_posts'),
    url(r'^(?P<thread_id>[0-9]+)/$', views.thread, name='thread'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
