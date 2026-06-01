from django.db import models

class Driver(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    vehicle = models.CharField(max_length=50)

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

class DriverLocation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    lat = models.FloatField()
    lon = models.FloatField()
    otp = models.CharField(max_length=6)

class Ride(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    fare = models.FloatField(default=0)

class Feedback(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()