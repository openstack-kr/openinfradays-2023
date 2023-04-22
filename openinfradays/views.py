import json
import random
import requests
import uuid

from datetime import datetime, date

from django.contrib import auth
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.template.defaulttags import register

from .models import Sponsor, TechSession, VirtualBooth, \
    AdVideo, Room, TimeSlot, RegistrationCount


@register.filter
def get_session_by_room_id(sessions, room_id):
    return sessions.get(room_id)


def agreement_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if not request.user.profile.agree_with_private:
                    return redirect('/join')
            except Exception as e:
                pass
        return function(request, *args, **kwargs)
    return wrap


def make_menu_context(current=None):
    context = {'about_current': '', 'sponsor_current': '', 'schedule_current': '', 'program_current': '',
               'virtualbooth_current': '', 'intro': False}
    if current is not None:
        key = '%s_current' % current
        context[key] = 'current'
    return context


def index(request):
    diamond = Sponsor.objects.filter(level='Diamond')
    sapphire = Sponsor.objects.filter(level='Sapphire')
    gold = Sponsor.objects.filter(level='Gold')
    media = Sponsor.objects.filter(level='Media')
    keynote_session = TechSession.objects.filter(session_type='Keynote')
    sponsor_session = TechSession.objects.filter(session_type='Sponsor')
    regcount = RegistrationCount.objects.all()
    cnt = 0
    for r in regcount:
        cnt += r.count
    menu = make_menu_context('index')
    today = datetime.today().strftime('%m월  %d일')
    context = {'diamond': diamond, 'sapphire': sapphire,
               'gold': gold, 'media': media,
               'keynote': keynote_session, 'sponsor': sponsor_session,
               'reg_count': cnt, 'today': today}
    return render(request, 'index.html', {**menu, **context})


def about(request):
    context = make_menu_context('about')
    return render(request, 'about.html', context)


def bulk(request):
    return render(request, 'bulk.html')


def sponsors(request):
    diamond = Sponsor.objects.filter(level='Diamond')
    sapphire = Sponsor.objects.filter(level='Sapphire')
    gold = Sponsor.objects.filter(level='Gold')
    media = Sponsor.objects.filter(level='Media')
    menu = make_menu_context('sponsor')
    context = {'diamond': diamond, 'sapphire': sapphire, 'gold': gold, 'media': media}
    return render(request, 'sponsors.html', {**menu, **context})


def virtualbooth(request):
    vb = VirtualBooth.objects.all()
    menu = make_menu_context('virtualbooth')
    context = {'virtualbooth': vb}
    return render(request, 'virtualbooth.html', {**menu, **context})


def schedules(request):
    rooms = Room.objects.all()
    slots = TimeSlot.objects.all()
    tech_session = TechSession.objects.filter(Q(session_type='Tech') | Q(session_type='Sponsor')
                                              | Q(session_type='Keynote') | Q(session_type='TimeTable'))
    session_per_time = {}
    for s in slots:
        session_per_time[s.start_time] = {}
    for t in tech_session:
        if t.room is None:
            session_per_time[t.time_slot.start_time]['all'] = t
        else:
            session_per_time[t.time_slot.start_time][t.room.room_name] = t

    menu = make_menu_context('schedule')
    context = {'rooms': rooms, 'sessions': session_per_time}
    return render(request, 'schedules.html', {**menu, **context})


def virtualbooth_detail(request, virtualbooth_id):
    virtualbooth = VirtualBooth.objects.get(id=virtualbooth_id)
    menu = make_menu_context('virtualbooth')
    context = {'vb': virtualbooth}
    return render(request, 'virtualbooth_detail.html', {**menu, **context})


def session_detail(request, session_id):
    session = TechSession.objects.get(id=session_id)
    ads = AdVideo.objects.all()
    menu = make_menu_context('program')
    ads_link = []
    ad1_url = ''
    ad2_url = ''
    for ad in ads:
        ads_link.append(ad.url)

    for i in range(10):
        random.shuffle(ads_link)

    if len(ads_link) > 2:
        ad1_url = ads_link[0]
        ad2_url = ads_link[1]

    now = datetime.now()
    release = False
    if now.month == session.open_date.month and \
        (( now.day == session.open_date.day and now.hour >= 10 ) or
         ( now.day == (session.open_date.day + 1) and now.hour < 10)):
        release = True

    if now.month == session.open_date.month and now.day >= 7 and \
            ( session.session_type == "Keynote" or session.session_type == 'Community'):
        release = True

    if request.user.is_staff:
        release = True

    context = {'session': session, 'ad1_url': ad1_url, 'ad2_url': ad2_url, 'release': release}
    return render(request, 'session_detail.html', {**menu, **context})


def session_list(request):
    menu = make_menu_context('program')
    keynote = TechSession.objects.filter(session_type='Keynote')
    tech = TechSession.objects.filter(session_type='Tech')
    sponsor = TechSession.objects.filter(session_type='Sponsor')
    online = TechSession.objects.filter(session_type='Online')
    context = {'keynote': keynote, 'sponsor': sponsor, 'tech': tech, 'online': online}
    return render(request, 'sessions.html', {**menu, **context})


def event(request):
    return render(request, 'event.html')

