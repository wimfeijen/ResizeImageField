from django.db import models
from django.utils.translation import ugettext_lazy as _

from settings import PHOTO_DIR 

from resize_image import ResizeImageField

class Address(models.Model):
    photo = ResizeImageField(upload_to=PHOTO_DIR, blank=True, verbose_name=_('Foto'))
