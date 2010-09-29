ResizeImageField
================
(extension of RemovableImageField)
=================================

by Wim Feijen, Go2People.

What does it do?
----------------
ResizeImageField is a replacement for django's ImageField. It has two major benefits:
1. Creation of thumbnails and scaled images.
1. Extends the image upload form and adds a preview and a checkbox to remove the existing image.

It's easy to use:
- Replace ImageField by ResizeImageField
- No further changes are necessary

Requirements:
-------------
Working installation of PIL, the Python Imaging Library

Usage
-----
- add resize_image to your app
- add resize_filters.py to your templatetags
- in settings.py, set a PHOTO_DIR, f.e. photos/original
- in models.py, add:
  - from settings import PHOTO_DIR
  - from resize_image import ResizeImageField
  - photo = ResizeImageField(upload_to=PHOTO_DIR, blank=True)

Scaled images will be stored in 'photos/scaled', 
thumbnails will be stored in 'photos/thumb'.

Access your images from your template. Add::

  {% load resize_filters %} 
  {{ address.photo.url|thumb }} 

or::

  {{ address.photo.url|scaled }} 

Defaults
-------
- Scaled images are max. 200x200 pixels by default
- Thumbnails are 50x50 pixels.

Override the default behaviour in settings.py

Scaling is done by PIL's thumbnail function, transparency is conserved.

Credits
------
This code is an adaptation from python snippet 636 by tomZ: "Updated Filefield / ImageField with a delete checkbox" 
