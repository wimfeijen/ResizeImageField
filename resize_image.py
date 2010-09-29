# Adapted from: http://www.djangosnippets.org/snippets/636/
# ResizeImageField stands for ScalableAndRemovableImageField
from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

import os

import Image # from PIL

ORIGINAL_NAME = os.path.basename(settings.PHOTO_DIR)
SCALED_NAME = getattr(settings, 'SCALED_NAME', 'scaled')
THUMB_NAME = getattr(settings, 'THUMB_NAME', 'thumb')

SCALED_SIZE = getattr(settings, 'SCALED_SIZE', (200, 200))
THUMB_SIZE = getattr(settings, 'SCALED_SIZE', (50, 50)) # height, width

class DeleteCheckboxWidget(forms.CheckboxInput):
    def __init__(self, *args, **kwargs):
        self.is_image = kwargs.pop('is_image')
        self.value = kwargs.pop('initial')
        super(DeleteCheckboxWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = value or self.value
        if value:
            attrs['style'] = 'width:auto;'
            s = u'<label for="%s">%s %s</label>' % (
                    attrs['id'],
                    super(DeleteCheckboxWidget, self).render(name, False, attrs),
                    _('Delete')
                )
            if self.is_image:
                s += u'<br><img src="%s%s" height="100">' % (settings.MEDIA_URL, unicode(value).replace(ORIGINAL_NAME, SCALED_NAME, 1))
            else:
                s += u'<br><a href="%s%s">%s</a>' % (settings.MEDIA_URL, value, os.path.basename(value))
            return s
        else:
            return u''


class RemovableFileFormWidget(forms.MultiWidget):
    def __init__(self, is_image=False, initial=None, **kwargs):
        widgets = (forms.FileInput(), DeleteCheckboxWidget(is_image=is_image, initial=initial))
        super(RemovableFileFormWidget, self).__init__(widgets)

    def decompress(self, value):
        return [None, value]

class RemovableFileFormField(forms.MultiValueField):
    widget = RemovableFileFormWidget
    field = forms.FileField
    is_image = False

    def __init__(self, *args, **kwargs):
        fields = [self.field(*args, **kwargs), forms.BooleanField(required=False)]
        # Compatibility with form_for_instance
        if kwargs.get('initial'):
            initial = kwargs['initial']
        else:
            initial = None
        self.widget = self.widget(is_image=self.is_image, initial=initial)
        super(RemovableFileFormField, self).__init__(fields, label=kwargs.pop('label'), required=False)

    def compress(self, data_list):
        return data_list


class ResizeImageFormField(RemovableFileFormField):
    field = forms.ImageField
    is_image = True

class ResizeImageField(models.ImageField):

    def delete_file(self, instance, *args, **kwargs):
        '''Overwrite delete method. Delete scaled instances as well.'''
        if getattr(instance, self.attname):
            image = getattr(instance, '%s' % self.name)
            file_name = image.path
            # If the file exists and no other object of this type references it,
            # delete it from the filesystem.
            if os.path.exists(file_name) and \
                not instance.__class__._default_manager.filter(**{'%s__exact' % self.name: getattr(instance, self.attname)}).exclude(pk=instance._get_pk_val()):
                if os.path.exists(file_name):
                    os.remove(file_name)
                scaled_name = file_name.replace(ORIGINAL_NAME, SCALED_NAME, 1)
                if os.path.exists(scaled_name):
                    os.remove(scaled_name)
                thumb_name = file_name.replace(ORIGINAL_NAME, THUMB_NAME, 1)
                if os.path.exists(thumb_name):
                    os.remove(thumb_name)

    def get_internal_type(self):
        '''Copied from Django snippet example and probably incorrect.'''
        return 'FileField'

    def check_or_create_dir(self, full_path):
        '''Create dir if it does not yet exist.'''
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

    def save_form_data(self, instance, data):
        '''Save/replace or delete file. If saving, store scaled images as well.'''
        if data and data[0]: # Replace file
            self.delete_file(instance)
            super(ResizeImageField, self).save_form_data(instance, data[0])
            image = getattr(instance, '%s' % self.name)
            file_path = image.path
            img = Image.open(file_path)
            self.resize(img, file_path, SCALED_NAME, SCALED_SIZE)
            self.resize(img, file_path, THUMB_NAME, THUMB_SIZE)
                
        if data and data[1]: # Delete file
            self.delete_file(instance)
            setattr(instance, self.name, None)

    def resize(self, img, file_path, new_name, new_size):
        '''Resize image, using PIL, and save.'''
        new_path = file_path.replace(ORIGINAL_NAME, new_name, 1)
        self.check_or_create_dir(new_path)
        img.thumbnail(new_size, Image.ANTIALIAS)
        try:
            transparency = img.info['transparency']
            img.save(new_path, transparency=transparency)
        except:
            img.save(new_path)

    def formfield(self, **kwargs):
        '''Django default.'''
        defaults = {'form_class': ResizeImageFormField}
        defaults.update(kwargs)
        return super(ResizeImageField, self).formfield(**defaults)

