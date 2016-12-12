from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Packet(models.Model):
    # [NOTICE] Field.null default is False
    name = models.CharField(max_length=128)
    content = models.TextField()
    latitude = models.DecimalField(max_digits=16, decimal_places=12)
    longitude = models.DecimalField(max_digits=16, decimal_places=12)
    create_time = models.DateTimeField(auto_now_add=True)  # [NOTICE] is corresponding to python's datetime.datetime
    creator = models.ForeignKey(User, related_name='created_packets')
    owner = models.ForeignKey(User, null=True, related_name='owning_packets')  # take care of the related_name
    owneders = models.ManyToManyField(User, related_name="owned_packets")
    ignorers = models.ManyToManyField(User, related_name="ignored_packets")
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    can_see_time = models.DateTimeField()  # from 0 to 1 day
    die_time = models.DateTimeField()  # maximum is 1 year
    last_owner = models.ForeignKey(User)

    def __str__(self):
        return self.name.encode("utf-8")


class Comment(models.Model):
    packet = models.ForeignKey(Packet)
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)  # [NOT SURE] suppuse once create, won't change the comment
    content = models.TextField()
    only_creator_can_see = models.BooleanField(default=False)

    def __str__(self):
        return self.content.encode("utf-8")
