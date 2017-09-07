import re

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')

def post_handler(text):
    #Html protect symbols
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    #Bbcodes
    text = re.sub('\[b(:.*)?\](.*?)\[\/b\1?\]', '<strong>\\2</strong>', text)
    text = re.sub('\[i(:.*)?\](.*?)\[\/i\1?\]', '<em>\\2</em>', text)
    text = re.sub('\[u(:.*)?\](.*?)\[\/u\1?\]', '<u>\\2</u>', text)
    text = re.sub('\[s(:.*)?\](.*?)\[\/s\1?\]', '<div class="spoiler">\\2</div>', text)
    

    #Reply links
    text = re.sub('&gt;&gt;(\d+)', '<a href="#\\1" class="replto">>>\\1</a>', text) 
    return text

def get_replies_list(text):
    return list(map(int, re.findall('>>(\d+)', text)))
