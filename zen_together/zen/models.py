from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

class TotalZen(models.Model):
    total = models.IntegerField() #Total minutes meditated by all

    def addMinutes(self, minutes):
        self.total += minutes

    #def save(self):
    #   self.id=1
    #   super(TotalZen, self).save()

    #def delete(self):
    #   pass

    def __unicode__(self):
        return u"%d" % (self.total)

    class Admin:
        pass

class Meditation(models.Model):
    moment = models.DateTimeField() 
    place = models.CharField(max_length=255) #location of user via ip
    people = models.ManyToManyField(User, blank=True)
    duration = models.IntegerField()

    class Admin:
        pass

    def getDate(self):
        try:
            return self.moment.strftime('%b %d \'%y %z')
        except Exception, e:
            print e
            return "" 

    def __unicode__(self):
        return u"%s , %s, %s" % (str(self.moment).split(" ")[0], str(self.duration)+"m",str(len(self.people.all()))+" friends")

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    karmaPts = models.IntegerField() #Minutes meditated * friends meditated with
    numZen = models.IntegerField()   #Number of meditation sessions
    lastZen = models.DateTimeField() #DateTime of last meditation

    curFriends = models.IntegerField() #Cache # active fb friends for current session
                                       #TODO: Clear this variable on logout?
    curFriendUsers = models.ManyToManyField(User, related_name="curFriendsWith", blank=True)

    curLocation = models.CharField(max_length=255, blank=True)

    meditating = models.BooleanField()  # isMeditating boolean
    meditating_start = models.DateTimeField() #Meditation start datetime
    meditating_time = models.IntegerField() #Meditation length

    meditations = models.ManyToManyField(Meditation, blank=True)

    fbStream = models.BooleanField() #does user want to publish meditations to fb stream

    def addKarmaPts(self, points): #Called after a complete meditation session.
        self.numZen += 1    #account for the just-completed meditation
        self.karmaPts += int(points)
        self.lastZen = datetime.datetime.today()
        self.meditating = False
        try:
            print self.curFriendUsers.all()
            med = self.meditations.create(moment = datetime.datetime.today(),
                                    place = self.curLocation,
                                    duration = self.meditating_time)
            if len((self.curFriendUsers.all())) > 0:
                for friend in self.curFriendUsers.all():
                    med.people.add(friend)
                #med.save()
            #test = self.meditations(pk=med.pk).people.add(self.curFriendUsers.all())
        except Exception, e:
            print e

    def startMeditating(self, time): #Called before a meditation session.
        self.meditating_start = datetime.datetime.today() #Meditation start datetime
        self.meditating_time = time
        self.meditating = True

    def __unicode__(self):
        return u"%s - %s - %s - %s" % (self.user.username, self.karmaPts, self.numZen, self.lastZen)

    #class Admin:
    #   pass
    
#@receiver(post_save)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, 
                                   karmaPts=0, 
                                   numZen=0, 
                                   lastZen=datetime.datetime.strptime("20 Apr 00", "%d %b %y"), 
                                   curFriends = 0,
                                   meditating = False,
                                   meditating_start = datetime.datetime.strptime("20 Apr 00", "%d %b %y"),
                                   meditating_time = 0,
                                   fbStream = False,
                                   )

post_save.connect(create_user_profile, sender=User)
