from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

UserModel = get_user_model()


class Sponsor(models.Model):
    name_ko = models.CharField(max_length=100, default='')
    name_en = models.CharField(max_length=100)
    homepage_url = models.CharField(max_length=100, default='')
    logo = models.ImageField(upload_to='images/sponsor/')
    level = models.CharField(max_length=20,
                             choices=[('Diamond', 'Diamond'), ('Sapphire', 'Sapphire'), ('Gold', 'Gold'), ('Media', 'Media')],
                             default='Gold')

    def __str__(self):
        return self.name_ko


class Speaker(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    company = models.CharField(max_length=100, default='')
    profile_img = models.ImageField(upload_to='images/speaker/', default=None, blank=True)
    bio = models.TextField(max_length=1000, default='')
    twitter = models.CharField(max_length=100, default='', blank=True)
    facebook = models.CharField(max_length=100, default='', blank=True)
    blog = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    start_time = models.CharField(max_length=10)
    end_time = models.CharField(max_length=10)

    def __str__(self):
        return self.start_time


class Room(models.Model):
    room_name = models.CharField(max_length=10)

    def __str__(self):
        return self.room_name


class TechSession(models.Model):
    title = models.CharField(max_length=100)
    details = models.TextField(max_length=2000)
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True)
    slide = models.FileField(upload_to='slides/', default='', blank=True)
    video_url = models.CharField(max_length=1000, default='', blank=True)
    ad1_url = models.CharField(max_length=1000, default='', blank=True)
    ad2_url = models.CharField(max_length=1000, default='', blank=True)
    open_date = models.DateField(default='2021-12-07')

    session_type = models.CharField(max_length=20,
                                    choices=[('Keynote', 'Keynote'), ('Sponsor', 'Sponsor'), ('Tech', "Tech"),
                                             ('Community', "Community"), ('Online', 'Online'),
                                             ('TimeTable', 'TimeTable')],
                                    default='Tech')
    qna_enable = models.BooleanField(default=False, blank=True)
    qna_date = models.DateField(blank=True, default='2021-12-07')
    qna_time = models.TimeField(blank=True, default='00:00:00')
    qna_location = models.CharField(max_length=100, default='Gather Town')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=None, null=True, blank=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, default=None, null=True, blank=True)


class VirtualBooth(models.Model):
    sponsor = models.OneToOneField(Sponsor, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, default='', blank=True)
    short_desc = models.CharField(max_length=200, default='', blank=True)
    body = models.TextField(max_length=10000, default='', blank=True)
    custom_logo = models.ImageField(upload_to='images/virtualbooth/', null=True, default=None, blank=True)
    video1 = models.CharField(max_length=100, default='', blank=True)
    video2 = models.CharField(max_length=100, default='', blank=True)
    video3 = models.CharField(max_length=100, default='', blank=True)
    image1 = models.ImageField(upload_to='images/virtualbooth/', default=None, blank=True)
    image1_link = models.FileField(upload_to='files/virtualbooth/', default='', blank=True)
    image2 = models.ImageField(upload_to='images/virtualbooth/', default=None, blank=True)
    image2_link = models.FileField(upload_to='files/virtualbooth/', default='', blank=True)
    image3 = models.ImageField(upload_to='images/virtualbooth/', default=None, blank=True)
    link1 = models.CharField(max_length=100, default='', blank=True)
    link1_txt = models.CharField(max_length=100, default='', blank=True)
    link2 = models.CharField(max_length=100, default='', blank=True)
    link2_txt = models.CharField(max_length=100, default='', blank=True)
    link3 = models.CharField(max_length=100, default='', blank=True)
    link3_txt = models.CharField(max_length=100, default='', blank=True)
    link4 = models.CharField(max_length=100, default='', blank=True)
    link4_txt = models.CharField(max_length=100, default='', blank=True)
    link5 = models.CharField(max_length=100, default='', blank=True)
    link5_txt = models.CharField(max_length=100, default='', blank=True)


class Profile(models.Model):
    GITHUB = 'github'

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    is_check_navercloud = models.BooleanField(default=False)
    login_type = models.CharField(max_length=10)
    complete = models.BooleanField(default=False)
    company = models.CharField(max_length=100, default='', blank=True)
    job = models.CharField(max_length=100, default='', blank=True)
    agree_with_private = models.BooleanField(default=False, null=True)
    agree_with_sponsor = models.BooleanField(default=False, null=True)
    naver_cloud_form = models.CharField(max_length=10000, default='', blank=True)


@receiver(post_save, sender=UserModel)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=UserModel)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)


class AdVideo(models.Model):
    url = models.CharField(max_length=100, default='')


class RegistrationCount(models.Model):
    reg_type = models.CharField(max_length=20)
    count = models.IntegerField()
