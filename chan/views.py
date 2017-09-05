from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import timezone
from .models import Post, Users_base
from math import ceil
import datetime
import re

def index(request, page=0):
    t_on_page = 3
    page = int(page)
    posts = Post.objects.filter(parent_thread=None)
    if posts.count() <= t_on_page * page:
        raise Http404('Page does not exist')

    pages_total_count = ceil(posts.count() / t_on_page)
    pages_total = list(range(pages_total_count))
    
    for p in posts:
        try:
            p.last_post_id = Post.objects.filter(parent_thread=p.post_id, sage=False).last().post_id
        except AttributeError: #no posts in thread
            p.last_post_id = p.post_id

    posts = sorted(list(posts), key=lambda p: p.last_post_id, reverse=True) #sort threads py last post id

    data = []
    for p in posts[page*t_on_page:page*t_on_page + t_on_page]:
        data.append({
            'op': p,
            'related_posts': Post.objects.filter(parent_thread = p.post_id).order_by('-post_id')[:3:-1],
            })

    return render(request, 'chan/index.html', {'posts': data, 'pages': pages_total})
    
def create(request, thread_id=None):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')


    try: 
        user = Users_base.objects.get(ip=ip)
        new_user = False
    except Users_base.DoesNotExist:
        user = Users_base.objects.create(
            ip = ip,
            last_post_date = timezone.now(),
            ban_reason = None,
            )
        new_user = True

    if user.is_banned():
        allow_post = False
        result_message = 'Ban: {}; expires: {}'.format(user.ban_reason, user.ban_expire.ctime())
    elif (timezone.now() - user.last_post_date < datetime.timedelta(seconds = 5)) and not new_user:
        allow_post = False
        result_message = 'You post too fast'
    else:
        allow_post = True
        user.last_post_date = timezone.now()
        user.save()
    
    post_message = request.POST['message']
    post_message = re.sub('\[b(:.*)?\](.*?)\[\/b\1?\]', '<strong>\\2</strong>', post_message)
    post_message = re.sub('\[i(:.*)?\](.*?)\[\/i\1?\]', '<em>\\2</em>', post_message)
    post_message = re.sub('\[u(:.*)?\](.*?)\[\/u\1?\]', '<u>\\2</u>', post_message)
    post_message = re.sub('\[s(:.*)?\](.*?)\[\/s\1?\]', '<div class="spoiler">\\2</div>', post_message)
    post_message = post_message.replace('&', '&amp;')
    post_message = post_message.replace('<', '&lt;')
    post_message = post_message.replace('>', '&gt;')

    if allow_post:
        post_data = Post.objects.create(
            message = post_message,
            mail = request.POST['mail'],
            date = timezone.now(),
            sage = True if 'sage' in request.POST else False, 
            ip = ip,
            parent_thread = thread_id,
            file = request.FILES['file'] if 'file' in request.FILES else None,
            )
        result_message = 'Post send'
    
    if thread_id is None: #If user created new thread.
        threads = Post.objects.filter(parent_thread=None)
        if threads.count() > 10: #Maximum number of threads on the board.
            last_thread_id = threads.order_by('post_id').first().post_id
            threads.order_by('post_id').first().delete() #delete last thread
            Post.objects.filter(parent_thread = last_thread_id).delete() #delete posts in last thread

    
    return render(request, 'chan/message.html', {'message': result_message})
    

def thread(request, thread_id):
    op_post = get_object_or_404(Post, post_id=thread_id, parent_thread=None)
    posts = Post.objects.filter(parent_thread=(thread_id))
    return render(request, 'chan/thread.html', {'op_post': op_post, 'posts': posts})