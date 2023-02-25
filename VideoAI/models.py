from django.db import models
import os
# Create your models here.

def content_file_name(instance, filename): 
    print(instance)
    name, ext = filename.split('.') 
    file_path = f'{instance.username}/{name}.{ext}' 
    return file_path

class ImageModel(models.Model):
    image = models.ImageField(upload_to=content_file_name)
    
    def delete(self, *args, **kwargs):
        # Delete the file when the object is deleted from the database
        os.remove(self.image.path)
        super(ImageModel, self).delete(*args, **kwargs)