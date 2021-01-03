from django.db import models


# Create ImageRecords Model
class ImageRecord(models.Model):
    id = models.AutoField(primary_key=True)
    Image = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)  # When it was create
    creator = models.ForeignKey('auth.User', related_name='ImageProcessing', on_delete=models.CASCADE)

    def __str__(self):
        latest_id = str(self.id)
        return latest_id
