from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Sponsor, TechSession, Speaker, VirtualBooth,\
    Profile, AdVideo, Room, TimeSlot, RegistrationCount


class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'path', 'access_at')

    @admin.display(ordering='user__first_name', description='username')
    def get_user_name(self, obj):
        if obj.user is None:
            return 'Anon'
        return obj.user.first_name


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name_ko', 'homepage_url', 'level')


class TechSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_speaker', 'session_type', 'get_room', 'get_time', 'video_url')

    @admin.display(ordering='speaker__name', description='Speaker')
    def get_speaker(self, obj):
        return obj.speaker.name

    @admin.display(ordering='room__room_name', description='Room')
    def get_room(self, obj):
        if obj.room is None:
            return obj.session_type
        return obj.room.room_name

    @admin.display(ordering='timeslot__start_time', description='Time')
    def get_time(self, obj):
        if obj.time_slot is None:
            return "--"
        return obj.time_slot.start_time


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')


class VirtualBoothAdmin(admin.ModelAdmin):
    list_display = ('get_sponsor',)

    @admin.display(ordering='sponsor__name_ko', description="Sponsor")
    def get_sponsor(self, obj):
        return obj.sponsor.name_ko


class SponsorNightAdmin(admin.ModelAdmin):
    list_display = ('get_sponsor', 'event_date')

    @admin.display(ordering='sponsor__name_ko', description="Sponsor")
    def get_sponsor(self, obj):
        return obj.sponsor.name_ko


class BofAdmin(admin.ModelAdmin):
    list_display = ('title', 'moderator', 'bof_date', 'bof_time')


class RegistrationCountAdmin(admin.ModelAdmin):
    list_display = ('reg_type', 'count')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class OneTimeTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'expired', 'expire_at')


class AdVideoAdmin(admin.ModelAdmin):
    list_display = ('url',)


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time')


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name',)


def export_to_csv(modeladmin, request, queryset):
    from django.http import HttpResponse
    import csv

    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;' 'filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    title = ['name', 'email', 'company', 'job']
    writer.writerow(title)
    # Write data rows
    for u in User.objects.all():
        data_row = [u.first_name, u.email, u.profile.company, u.profile.job]
        writer.writerow(data_row)

    return response


def export_naver_agree(modeladmin, request, queryset):
    from django.http import HttpResponse
    import csv

    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;' 'filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    title = ['name', 'email', 'naver_cloud_form']
    writer.writerow(title)

    for p in Profile.objects.filter(is_check_navercloud=True):
        u = p.user
        name = u.first_name
        email = u.email
        apply_form = p.naver_cloud_form
        data_row = [name, email, apply_form]
        writer.writerow(data_row)
    return response


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

    actions = [export_to_csv, export_naver_agree]


export_to_csv.short_description = 'Export to CSV'  #short description


admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(TechSession, TechSessionAdmin)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(VirtualBooth, VirtualBoothAdmin)
admin.site.register(AdVideo, AdVideoAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(RegistrationCount, RegistrationCountAdmin)
