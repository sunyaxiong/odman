from hashlib import sha1

from django.db import models
from django.utils.translation import ugettext_lazy as _

from odman import settings


class BaseQuerySet(models.query.QuerySet):
    def delete(self):
        '''
        Update is_delete field to True.
        '''
        fields = (f.name for f in self.model._meta.fields)
        if 'is_deleted' in fields:
            return self.update(is_deleted=True)
        else:
            super(BaseQuerySet, self).delete()


class BaseManager(models.manager.Manager.from_queryset(BaseQuerySet)):
    def get_queryset(self):
        queryset = super(BaseManager, self).get_queryset()
        fields = (f.name for f in self.model._meta.fields)
        if 'is_deleted' in fields:
            queryset = queryset.filter(is_deleted=False)
        return queryset


class BaseModel(models.Model):
    is_deleted = models.BooleanField(default=False, editable=False, verbose_name=_('is deleted'))
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name=_('created datetime'))
    dt_updated = models.DateTimeField(auto_now=True, verbose_name=_('updated datetime'))

    objects = BaseManager()

    class Meta:
        abstract = True

    def delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return str(self.id)


def file_upload_to(instance, filename):
    content = instance.file.file.read()
    content_hash = sha1(content).hexdigest()
    suffix = filename.split('.')[-1]
    args = [
            settings.MEDIA_ROOT,
            'attache',
            '%s.%s' % (content_hash, suffix),
            ]
    return '/'.join(args)


class BaseFile(models.Model):
    title = models.CharField(max_length=32, blank=True, verbose_name="文件名")
    file = models.FileField(upload_to=file_upload_to, blank=True, verbose_name=_('file'))
    file_url = models.URLField(max_length=512, null=True, blank=True, verbose_name="文件url")
    is_deleted = models.BooleanField(default=False, verbose_name="删除标志")
    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self):
        self.is_deleted = True
        self.save()
