from django.db import models

# Create your models here.

def content_file_name(instance, filename): 
    print(instance)
    name, ext = filename.split('.') 
    file_path = f'{instance.username}/{name}.{ext}' 
    return file_path

class ImageModel(models.Model):
    image = models.ImageField(upload_to=content_file_name)