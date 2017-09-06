from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import timezone
from .models import Post, Users_base
from chan import utils
from math import ceil
import datetime

def index(request, page=0):
    threads_on_page = 3
    page = int(page)
    posts = Post.objects.filter(parent_thread=None)
    if posts.count() <= threads_on_page * page:
        raise Http404('Page does not exist')

    pages_total_count = ceil(posts.count() / threads_on_page)
    pages_total = list(range(pages_total_count)) #List of pages numbers
    
    for p in posts:
        try:
            p.last_post_id = Post.objects.filter(parent_thread=p.post_id, sage=False).last().post_id
        except AttributeError: #No posts in thread, so last post date is date of OP post
            p.last_post_id = p.post_id

    posts = sorted(list(posts), key=lambda p: p.last_post_id, reverse=True) #Sort threads py last post id

    data = []
    for p in posts[page*threads_on_page:page*threads_on_page + threads_on_page]:
        data.append({
            'op': p,
            'related_posts': Post.objects.filter(parent_thread=p.post_id).order_by('-post_id')[:3:-1],
            })

    return render(request, 'chan/index.html', {'posts': data, 'pages': pages_total})
    
def create(request, thread_id=None):
    ip = utils.get_ip(request)
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
    

    if allow_post:
        new_post = Post(
            message = utils.post_handler(post_message),
            mail = request.POST['mail'],
            date = timezone.now(),
            sage = True if 'sage' in request.POST else False, 
            ip = ip,
            parent_thread = thread_id,
            media = request.FILES['file'] if 'file' in request.FILES else None,
            )
        new_post.save()

        for link in utils.get_replies_list(post_message):
           p = Post.objects.get(post_id=link)
           p.replies += str(new_post.post_id) + ';'
           p.save()

        result_message = 'Post send'
    
    if thread_id is None: #If user created new thread.
        threads = Post.objects.filter(parent_thread=None)
        if threads.count() > 10: #Maximum number of threads on the board.
            last_thread_id = threads.order_by('post_id').first().post_id
            threads.order_by('post_id').first().delete() #delete last thread
            Post.objects.filter(parent_thread=last_thread_id).delete() #delete posts in last thread
            

    
    return render(request, 'chan/message.html', {'message': result_message})
    

def thread(request, thread_id):
    op_post = get_object_or_404(Post, post_id=thread_id, parent_thread=None)
    op_post.replies = op_post.replies.split(';')[:-1]

    posts = Post.objects.filter(parent_thread=(thread_id))
    for p in posts:
        p.replies = p.replies.split(';')[:-1]
    return render(request, 'chan/thread.html', {'op_post': op_post, 'posts': posts})