from django.db import models

# Model class which corresponds to a database table
class HelloWorldModel(models.Model):
    hello_world_str = models.CharField(max_length=100)
    model_info = models.CharField(max_length=300)

class UserAccount(models.Model):
    user_name = models.CharField(max_length=200)
    user_email = models.EmailField(max_length=300)
    user_phone = models.BigIntegerField()
    box_number = models.ForeignKey('BoxInfo', on_delete=models.CASCADE)

class BoxInfo(models.Model):
    date_made = models.DateField()