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
    AdVideo, Room, TimeSlot, RegistrationCount, Handsonlab, HandsonlabApply


@register.filter
def get_session_by_room_id(sessions, room_id):
    return sessions.get(room_id)


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
    support = Sponsor.objects.filter(level='Support')
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


def schedules_day1(request):
    rooms = Room.objects.filter(day1=True)
    slots = TimeSlot.objects.filter(event_date="Day 1").order_by('start_time')
    tech_session = TechSession.objects.filter(Q(event_date='Day 1') & (Q(session_type='Tech') | Q(session_type='Sponsor')
                                              | Q(session_type='Keynote') | Q(session_type='TimeTable')))
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
    return render(request, 'schedules_day1.html', {**menu, **context})


def schedules_day2(request):
    rooms = Room.objects.filter(day2=True)
    slots = TimeSlot.objects.filter(event_date="Day 2").order_by('start_time')
    tech_session = TechSession.objects.filter(
        Q(event_date='Day 2') & (Q(session_type='Tech') | Q(session_type='Sponsor')
                                 | Q(session_type='Keynote') | Q(session_type='TimeTable')))
    session_per_time = {}
    try:
        for s in slots:
            session_per_time[s.start_time] = {}
        for t in tech_session:
            if t.room is None:
                session_per_time[t.time_slot.start_time]['all'] = t
            else:
                session_per_time[t.time_slot.start_time][t.room.room_name] = t
    except:
        print('a')

    rename_rooms = ['Track 1: General', 'Track 2: NVMe & General', 'Track 3: AI', 'Track 4: Server & Storage', 'CXL Forum']
    menu = make_menu_context('schedule')
    context = {'rename_rooms': rename_rooms, 'rooms': rooms, 'sessions': session_per_time}
    return render(request, 'schedules_day2_tmp.html', {**menu, **context})


def handsonlab(request):
    hol = Handsonlab.objects.all()
    d = {}
    for h in hol:
        hola = HandsonlabApply.objects.filter(handsonlab=h.title)
        if len(hola) >= h.max_capacity:
            d[h.title] = True
        else:
            d[h.title] = False
    return render(request, 'handsonlab.html', {'d': d})


def handsonlab_detail(request, title):
    try:
        r = render(request, 'handsonlab/%s.html' % title)
    except:
        r = render(request, "404.html")
    return r


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


def check_to_plan9(name, phone):
    import requests
    data = {'name': name, 'phone': phone}

    res = requests.post(url="https://www.plan9.co.kr/openinfra/assets/app/db_add.php",
                        params={
                            "type": "3",
                        },headers={
                            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "Host": "www.plan9.co.kr",
                        },
                        data=data
                        )
    d = res.text
    if 'alert' in d:
        return None, None, None, False

    from urllib.parse import urlparse
    from urllib.parse import parse_qs
    pu = d.split("location.href='")[1].split("&result=1")[0]
    query = parse_qs(urlparse(pu).query)
    return query['name'][0], query['email'][0], query['company'][0], True


def registration_check(request):
    if request.method == "POST":
        name = request.POST.get('input_name')
        phone = request.POST.get('input_phone')
        r_name, email, company, flag = check_to_plan9(name, phone)
        return render(request, 'profile.html', {'name': r_name, 'email': email, 'company': company, 'flag': flag})

    return render(request, 'registration_check.html')


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def handsonlab_apply(request, handsonlab_title, option=None):
    title = {'mantech': 'Kubernetes on Openstack with kuryr', 'skt': '쿠버네티스환경에 어플리케이션 배포하기', 'gluesys': '고성능 RAID 컨트롤러, GRAID SupremeRAID A to Z',
             'akamai': '쿠버네티스 환경에서 HA 기반의 웹 서비스 구성하기', 'hashicorp': 'HashiCorp Vault 핸즈온 실습', 'xslab': 'ARM 서버 클라우드 기반 쿠버네티스 구성해보기'}
    rtitle = title[handsonlab_title]
    op = {'s1': '13:30 ~ 14:20', 's2': '14:30 ~ 15:20', 's3': '15:30 ~ 16:20', 's4': '16:30 ~ 17:20'}

    if request.method != "POST" and option and option not in op:
        return render(request, '404.html')

    if option:
        rtitle = "%s (%s)" % (rtitle, op.get(option, 's1'))
        handsonlab_title = "%s_%s" % (handsonlab_title, option)

    if request.method != "POST":
        return render(request, 'handsonlab_apply.html', {'htitle': handsonlab_title.split("_")[0], 'title': rtitle, 'option': option})

    name = request.POST.get('input_name')
    phone = request.POST.get('input_phone')
    r_name, email, company, flag = check_to_plan9(name, phone)

    if not flag:
        return render(request, 'profile.html', {'name': r_name, 'email': email, 'company': company, 'flag': flag})

    apply = HandsonlabApply.objects.filter(handsonlab=handsonlab_title)
    entity = HandsonlabApply.objects.filter(phone=phone)
    hol = Handsonlab.objects.get(title=handsonlab_title)

    if entity:
        entity = entity.get()
        if entity.handsonlab == handsonlab_title:
            return render(request, 'handsonlab_apply.html', {'finish': 2, 'title': rtitle})
        else:
            t = title[entity.handsonlab.split('_')[0]]
            if option:
                t = "%s (%s)" % (t, op.get(option))
            return render(request, 'handsonlab_apply.html', {'finish': 3, 'other_title': t})

    if len(apply) >= hol.max_capacity:
        return render(request, 'handsonlab_apply.html', {'finish': 1, 'title': rtitle})


    hola = HandsonlabApply()
    hola.handsonlab = handsonlab_title
    hola.name = r_name
    hola.email = email
    hola.phone = phone
    hola.company = company
    hola.save()
    return render(request, 'handsonlab_apply.html', {'title': rtitle, 'flag': flag, 'email': email})


def handler404(request, exception, template_name="404.html"):
    return render(request, template_name, status=404)
