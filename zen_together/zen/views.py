from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from models import TotalZen
#import facebook #bguo no longer exists
# from allauth.facebook.models import FacebookApp, FacebookAccount, FacebookAccessToken
# Ben - These modules have moved / changed to 
# allauth.socialaccount.providers.facebook.provider
from allauth.socialaccount.providers.facebook.provider import FacebookAccount, FacebookProvider
from tracking.models import Visitor
#from avatar.models import Avatar
from django.contrib.gis.geoip import GeoIP
import settings
import ast
import datetime
import urllib, urllib2
import json

def home(request):
    tempdic = {}
    tz = TotalZen.objects.get(pk=1)
    tempdic["totalZen"] = tz.total
    return render_to_response('index.html',tempdic,context_instance=RequestContext(request))

def about(request):
    tempdic = {}
    return render_to_response('about.html',tempdic,context_instance=RequestContext(request))

def logout(request, **kwargs):
    #messages.add_message(request, messages.SUCCESS,
    #    ugettext("You have signed out.")
    #)
    kwargs['template_name'] = kwargs.pop('template_name', 'signup.html')
    from django.contrib.auth.views import logout as _logout
    return _logout(request, **kwargs)

def start(request):
    tempdic = {}
    geo = GeoIP()
    try:
        if settings.DEPLOY:
            my_ip_dat = geo.city(request.META['HTTP_X_REAL_IP'])
        else:
            my_ip_dat = geo.city(request.META['REMOTE_ADDR'])
    except Exception, e:
        my_ip_dat = {}
        my_ip_dat['country_code'] = 'NA'
        my_ip_dat['region'] = 'NA'
        my_ip_dat['city'] = 'NA'
        print "start geoip error: " + str(e)

    try:
        if request.user.is_authenticated:
            if "NA" in my_ip_dat['country_code']:
                request.user.get_profile().curLocation = "NA"
            elif my_ip_dat['country_code'] == "US":
                request.user.get_profile().curLocation = str(my_ip_dat['city']) + ", " + str(my_ip_dat['region']) + ", " + str(my_ip_dat['country_code'])
            else:
                request.user.get_profile().curLocation = str(my_ip_dat['city']) + ", " + str(my_ip_dat['country_code'])
            request.user.get_profile().save()
    except Exception, e:
        print e

    #Determine user account type
    try:
        djangoUser = FacebookAccount.objects.get(user=request.user.pk)
        tempdic["social"] = True
        #print djangoUser
    except:  # user is NOT authentiacted OR is authenticated, but does not have a social acct:
        #print "no social"
        tempdic["friends"] = 0
        tempdic["social"] = False
        #tempdic["zenFriendMap"] = 0
        return render_to_response('start.html',tempdic,context_instance=RequestContext(request))

    fbapp = FacebookApp.objects.get(pk=1)
    zenFriends = 0

    #Make sure fb cookie matches id of current user
    
    fbToken = FacebookAccessToken.objects.get(app=fbapp, account=djangoUser)
    try:
        g = facebook.GraphAPI(fbToken.access_token)
        fb_me = g.get_object("me")
    except:
        tempdic["error"] = "Your Facebook session has expired. Please <a href=\"/accounts/logout/\">sign out</a> and try again."
        return render_to_response('start.html', tempdic, context_instance=RequestContext(request))
    
    fb_friends = g.get_connections(djangoUser.social_id, "friends")
    #Find a way to query friends using this app directly from FB
    #currentVisitors = Visitor.objects.active().filter(url=request.path)
    currentVisitors = Visitor.objects.active()
    #print currentVisitors[0].user
    #print fb_friends["data"]
    
    friendNames = []

    for friend in fb_friends["data"]:
        friendNames.append(friend["name"])
    #print friendNames
    
    co_list = []
    st_list = []
    try:
        co_list.append(my_ip_dat['country_code'])
        st_list.append(my_ip_dat['region'])
    except:
        pass
    
    zenFriendMap = {} #[Friend Name] > AVATAR_URL
    #print currentVisitors
    for visitor in currentVisitors:
        #print str(FacebookAccount.objects.get(user=visitor.user.pk).name) #Print fb acct of each active visitor
        if not visitor.user: #To address "Nonetype object has no attribute is_authenticated" error
            continue

        #Compile list of uniquecountries + states/provinces/etc 
        try:
            if visitor.ip_address != '10.0.0.1':
                ip_dat = geo.city(visitor.ip_address)
                if ip_dat['country_code'] not in co_list:
                    co_list.append(ip_dat['country_code'])
                if ip_dat['region'] not in st_list:
                    st_list.append(ip_dat['region'])
        except Exception, e:
            print 'visitor geoip error: ' + str(e)
            ip_dat = {}
            ip_dat['country_code'] = 'NA'
            ip_dat['region'] = 'NA'
        #If the stored fb acct for this visitor is in current uers fb friend list, pluck 'em'
        if (visitor.user.is_authenticated and not (visitor.user.pk == 1) and not (visitor.user.pk == request.user.pk)): 
            #Don't count admin acct or the current user
            #print visitor.user.username
            if str(FacebookAccount.objects.get(user=visitor.user.pk).name) in friendNames:
                #zenFriendNames.append(str(FacebookAccount.objects.get(user=visitor.user.pk).name))
                if visitor.user.get_profile().meditating: #Get meditating status for all meditating friends
                    # 2010, 12-1, 25
                    #Format time for Javascript Date. Months are 0-11
                    endTime = (visitor.user.get_profile().meditating_start + datetime.timedelta(minutes=visitor.user.get_profile().meditating_time))
                    if endTime < datetime.datetime.now(): #if user left meditating page before session complete
                        endTimeJs = ""
                    else:
                        endTime = endTime - datetime.datetime.now()
                        endTimeJs = "+"+str(endTime.seconds)

                    #,visitor.user.get_profile().meditating_time
                else:
                    endTimeJs = ""

                zenFriendMap[visitor.user.first_name] = [FacebookAccount.objects.get(user=visitor.user.pk).social_id,endTimeJs,ip_dat['country_code'],ip_dat['region'],visitor.session_key]
                zenFriends += 1
    tempdic['cos'] = co_list
    tempdic['regs'] = st_list
    tempdic["friends"] = zenFriends
    tempdic["zenFriendMap"] = zenFriendMap
    print "start " + str(tempdic["zenFriendMap"])
    #Set this model value for access at meditation completion
    request.user.get_profile().curFriends = zenFriends
    request.user.get_profile().save()
    #except Exception, e:
    #   response = HttpResponse(e)
    #   return response
    response = render_to_response('start.html',tempdic,context_instance=RequestContext(request))

    if len(zenFriendMap) > 0:
        response.set_cookie("friends",zenFriendMap)
        #print zenFriendMap
    return response

def meditate(request, time):
    tempdic = {}
    tempdic["time"] = time
    g = GeoIP()

    try:
        tempdic["sound"] = request.GET.get("s", 0)
        #Gather list of current meditators
        #Different meditation times are separate request.paths soo...
        #Gather meditation visitors manually, not with tracking template tag (which is request.path specific)
        #Also we want to scoop up geoip data for visualizing
        dudes = []
        co_list = []
        st_list = []
        #dude ->[country_code,region_code]
        meditators = Visitor.objects.active().filter(url__contains="/zen/")
        for dude in meditators:
            try:
                if dude.ip_address != '10.0.0.1':
                    ip_dat = g.city(dude.ip_address)
                    if ip_dat['country_code'] not in co_list:
                        co_list.append(ip_dat['country_code'])
                    if ip_dat['region'] not in st_list:
                        st_list.append(ip_dat['region'])
            except Exception, e:
                print 'visitor geoip error: ' + str(e)
                ip_dat['country_code'] = 'NA'
                ip_dat['region'] = 'NA'
            #Same format as zenFriendMap
            if ip_dat['country_code'] == None:
                ip_dat['country_code'] = ''
            if ip_dat['region'] == None:
                ip_dat['region'] = ' ?'
            dudes.append([ip_dat['country_code'].lower(),ip_dat['region'],dude.session_key])
    except Exception, e:
        print e

    social = True
    try:
        djangoUser = FacebookAccount.objects.get(user=request.user.pk)
        if "friends" in request.COOKIES:
            tempdic["zenFriendMap"] = request.COOKIES["friends"]
            #retrieving from COOKIES results in a str representation of the dictionary
            tempdic["zenFriendMap"] = ast.literal_eval(tempdic["zenFriendMap"]) 
        else:
            tempdic["zenFriendMap"] = {}
        

        #print djangoUser
    except Exception, e: #user is NOT authentiacted OR is authenticated, but does not have a social acct:
        social = False
        tempdic["zenFriendMap"] = {}
    
    try:
        #Remove visitors who are all ready counted in ZenFriendMap
        #boo O(n^2)
        print "friends: " + str(tempdic["zenFriendMap"])
        print "visitors: " + str(dudes)
        dudes2 = []
        for dude in dudes:
            add = True
            #if session key of visitor matches friend, don't double-count it
            if dude[2] == request.session.session_key:
                #dudes.remove(dude)
                #print "removed current user from visitors"
                continue
            for friend in tempdic["zenFriendMap"]:
                print str(dude[2]) + " "+ str(tempdic["zenFriendMap"][friend][4])
                #There seems to be a unicode equality test bug here.
                if str(dude[2]) == str(tempdic["zenFriendMap"][friend][4]):
                    #print "removed " + dude[2] + " from visitors"
                    #dudes.remove(dude)
                    add = False
            #If visitor not current user or one of user's friend
            if add:
                dudes2.append(dude)
        #print "dudes2: " + str(dudes2)
        tempdic["zenStrangerList"] = dudes2
        #print "dudes: " + str(dudes)
    except Exception, e:
        print "error: " + str(e)
        pass
        #print "meditate dude prune failure " + str(e)
    tempdic['meditators'] = dudes

    if not social:
        tempdic["friends"] = 0
        if request.user.is_authenticated(): #Non-social user
            #print "Meditate: Non-social user"
            request.user.get_profile().startMeditating(time)
            request.user.get_profile().save()
            return render_to_response('meditating.html',tempdic,context_instance=RequestContext(request))
        else:                             #Set cookie for acct creation
            response = render_to_response('meditating.html',tempdic,context_instance=RequestContext(request))
            response.set_cookie("time",time)
            return response

        
    
    request.user.get_profile().startMeditating(time)
    request.user.get_profile().save()
    #print request.user.get_profile().meditating
    tempdic["friends"] = request.user.get_profile().curFriends
    #print "meditate " + str(tempdic["zenFriendMap"])
    return render_to_response('meditating.html',tempdic,context_instance=RequestContext(request))


@login_required
def complete(request):
    if request.is_ajax():
        #print request.GET.get("time",0)
        response = HttpResponse("roger")
        try:
            time = request.GET.get("time",0)
        except Exception, e:
            print e
            response = HttpResponse(e)
            return response

        zenFriends = request.user.get_profile().curFriends
                #print zenFriends
                #sprint int(time)*(zenFriends+1)
        request.user.get_profile().addKarmaPts(int(time)*(zenFriends+1))
        request.user.get_profile().save()
        #print request.user.get_profile().karmaPts

        tz = TotalZen.objects.get(pk=1)
        tz.addMinutes(int(time))
        tz.save()

        try:
            if request.user.get_profile().fbStream:
                ''' DEBUG
                djangoUser = FacebookAccount.objects.get(user=request.user.pk)
                fbAccessToken = FacebookAccessToken.objects.get(account=request.user.pk)
                post_data = [('message','I just enjoyed '+str(time)+' minutes of zen and so can you.'),
                             ('name','Zen Together'),
                             ('link','http://www.zentogether.com'),
                             ('description','Meditate with friends and others around the world!'),
                             ('picture','http://www.zentogether.com/static/images/zt.gif'),
                             ('access_token',str(fbAccessToken.access_token))]     # a sequence of two element tuples
                #print post_data
                result = urllib2.urlopen('https://graph.facebook.com/'+str(djangoUser.social_id)+'/feed', urllib.urlencode(post_data))
                print "fbPost success"
                '''
                print 'fbPost disabled'
        except Exception, e:
            print "fbPost error: " + str(e)
            pass
    else:
        response = HttpResponse("nope")
    
    return response

@login_required
def reset(request):
    if request.is_ajax():
        #print request.GET.get("time",0)
        response = HttpResponse("roger")
        try:
            profile = request.user.get_profile()
            profile.meditating_start = datetime.datetime.now()
            profile.save()
        except Exception, e:
            response = HttpResponse(e)
            return response
    else:
        response = HttpResponse("nope")
    
    return response

@login_required
def exit(request):
    if request.is_ajax():
        print "exit"
        response = HttpResponse("roger")
        try:
            profile = request.user.get_profile()
            profile.meditating = False
            profile.save()
        except Exception, e:
            response = HttpResponse(e)
            return response
        #reset friendMap cookie set in start() for meditate()

    return response

@login_required
def savePrefs(request):
    if request.is_ajax():
        response = HttpResponse("roger")
        
        try:
            profile = request.user.get_profile()
            value = str(request.GET.get("fbStream",False))
            if value == "true":
                value = True
            else:
                value = False
            profile.fbStream = value
            profile.save()
            #print "PS: "+ str(request.user.get_profile().id)+" : "+ str(request.user.get_profile().fbStream)
        except Exception, e:
            print "SavePrefs ERR: " + str(e)
            response = HttpResponse(e)
    else:
        response = HttpResponse("nope")
    return response

@login_required
def profile(request):
    tempdic = {}
    profile = request.user.get_profile()

    # Credit account with meditation time if cookie set
    # The idea here is that allauth will redirect to /prorfile after signup/login
    # So a user would complete meditation (with cookie set by meditation view), login
    # as prompted at meditation end, be redirected to profile (HERE)
    if "time" in request.COOKIES:
        profile.addKarmaPts(request.COOKIES["time"])
        profile.save()

    #print "prof: " + str(profile.id)
    meditations = list(profile.meditations.all())
    meditations = meditations[len(meditations)-10:]
    meditations.reverse()

    tempdic["meditations"] = meditations
    try:
        djangoUser = FacebookAccount.objects.get(user=request.user.pk)
        #social = True
        fbAccessToken = FacebookAccessToken.objects.get(account=request.user.pk)
        #print 'https://graph.facebook.com/'+str(djangoUser.social_id)+'/permissions?access_token='+str(fbAccessToken)
        result = urllib2.urlopen('https://graph.facebook.com/'+str(djangoUser.social_id)+'/permissions?access_token='+str(fbAccessToken))
        data = json.load(result)
        try:
            fbStreamPerm = data["data"][0]["publish_stream"]
        except Exception, e:
            print e
            fbStreamPerm = 0
        #print "fb Perm read: " + str(fbStreamPerm)
    except Exception, e:
        fbStreamPerm = 0
        print e
        #social = False
    #print social
    try:
        tempdic["fbStreamPerm"] = fbStreamPerm
        #tempdic["social"] = social
        tempdic["fbStream"] = profile.fbStream
        tempdic["first_name"] = request.user.first_name
        tempdic["last_name"] = request.user.last_name
        tempdic["karmaPts"] = profile.karmaPts
        tempdic["numZen"] = profile.numZen
        #2011-12-02 17:17:47.452637     
        #%Y-%m-%d %H:%M:%f'
        #time is datetime obj
        lastZenDT = profile.lastZen
        if lastZenDT == datetime.datetime.strptime("20 Apr 00", "%d %b %y"):
            tempdic["hasZenned"] = False
        else:
            tempdic["hasZenned"] = True
        tempdic["lastZenTime"] = lastZenDT.strftime('%H:%M')
        lastZenMonth = lastZenDT.strftime('%b')
        lastZenDay = lastZenDT.strftime('%d')
        if len(lastZenDay) == 3 and lastZenDay[0] == "0":
            lastZenDay = lastZenDay[1:]
        tempdic["lastZenDate"] = lastZenMonth + " " + lastZenDay
    except Exception, e:
        print e
        tempdic["fbStream"] = None
        tempdic["first_name"] = None
        tempdic["last_name"] = None
        tempdic["karmaPts"] = None
        tempdic["numZen"] = None
        tempdic["lastZenDate"] = None
        tempdic["lastZenTime"] = None
        tempdic["hasZenned"] = None

    response = render_to_response('profile.html',tempdic,context_instance=RequestContext(request))
    # Delete stored time cookie. If it doesn't exist, this fails silently
    response.delete_cookie("time")
    return response
def geoip(request):
    g = GeoIP()
    #ip_dat = g.city(request.META['HTTP_X_REAL_IP'])
    #country = ip_dat['country_code']
    #state = ip_dat['region']
    #city = ip_dat['city']
    #for key,value in request.META:
    #   print str(key)+ ":  " + str(value)

    #print request.META
    #response = HttpResponse(str(country)+", "str(state)+", "+str(city))
    response = HttpResponse(request.META)
    return response 