from django.db import models

class Post(models.Model):
    message = models.CharField(max_length=1000)
    mail = models.CharField(max_length=100, blank=True, default='')
    date = models.DateTimeField('Post date')
    sage = models.BooleanField('Sage')
    parent_thread = models.PositiveIntegerField('Parent', blank=True, null=True)
    ip = models.GenericIPAddressField()
    post_id = models.AutoField(primary_key=True)
    media = models.FileField(upload_to='uploads/', blank=True, null=True)
    replies = models.CharField(max_length=1000, blank=True)


    def __str__(self):
        return self.message

class Users_base(models.Model):
    ip = models.GenericIPAddressField()
    last_post_date = models.DateTimeField('Last post date')
    ban_reason = models.CharField(max_length=500, blank=True, null=True)
    ban_expire = models.DateTimeField('Expire date', blank=True, null=True)

    def is_banned(self):
        from django.utils import timezone
        if self.ban_reason is not None:
            if self.ban_expire and (self.ban_expire > timezone.now()): 
                return True
            else: #ban expired
                self.ban_reason = None
                self.save()
                return False

    def __str__(self):
        return self.ip