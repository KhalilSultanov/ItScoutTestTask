from django.db import models


class UploadedImage(models.Model):
    image = models.ImageField(upload_to="uploads/")
    result = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.image.name} - {self.result}"
