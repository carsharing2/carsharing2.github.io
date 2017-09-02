from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.utils import timezone
from .models import Post, Users_base
from math import ceil
import datetime


def index(request, page=0):
    t_on_page = 3
    page = int(page)
    posts = Post.objects.filter(parent_thread = None)
    if posts.count() <= t_on_page * page:
        raise Http404('Page does not exist')

    pages_total_count = ceil(posts.count() / t_on_page)
    pages_total = list(range(pages_total_count))
    
    for p in posts:
        try:
            p.last_post_id = Post.objects.filter(parent_thread = p.post_id, sage = False).last().post_id
        except AttributeError: #no posts in thread
            p.last_post_id = p.post_id

    posts = sorted(list(posts), key = lambda p: p.last_post_id, reverse = True) #sort threads py last post id

    data = []
    for p in posts[page*t_on_page:page*t_on_page + t_on_page]:
        data.append({
            'op': p,
            'related_posts': Post.objects.filter(parent_thread = p.post_id).order_by('-post_id')[:3:-1],
            })

    return render(request, 'chan/index.html', {'posts': data, 'pages': pages_total})
    
def create(request):
    thread_id = int(request.POST['thread_id'])
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') #get ip func
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    #sage = True if 'sage' in request.POST else False

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
        message = 'Ban: {}; expires: {}'.format(user.ban_reason, user.ban_expire.ctime())
    elif (timezone.now() - user.last_post_date < datetime.timedelta(seconds = 15)) and not new_user:
        allow_post = False
        message = 'You post too fast'
    else:
        allow_post = True
        user.last_post_date = timezone.now()
        user.save()
    

    if allow_post:
        post_data = Post.objects.create(
            message = request.POST['message'],
            mail = request.POST['mail'],
            date = timezone.now(),
            sage = request.POST['sage'], #Need to bool() probably
            ip = ip,
            parent_thread = thread_id if thread_id != -1 else None,
            )
        message = 'Post send'

    
    if thread_id == -1: #If user created new thread.
        threads = Post.objects.filter(parent_thread = None)
        if threads.count() > 10: #Maximum number of threads on the board.
            last_thread_id = threads.order_by('post_id').first().post_id
            threads.order_by('post_id').first().delete() #Delete last thread
            Post.objects.filter(parent_thread = last_thread_id).delete() #Delete posts in last thread
    
    
    ajax_data = {'message': message}
    return JsonResponse(ajax_data)
    

def thread(request, thread_id):
    op_post = get_object_or_404(Post, post_id = thread_id, parent_thread = None)
    posts = Post.objects.filter(parent_thread = (thread_id))
    try:
        message = request.session.pop('message')
    except KeyError:
        message = None
    return render(request, 'chan/thread.html', {'op_post': op_post, 'posts': posts, 'message': message})