from django.conf.urls.defaults import patterns, include, url
import settings
import os

#from allauth.account.views import logout
#from allauth.socialaccount.views import login_cancelled, login_error
#from allauth.facebook.views import login as facebook_login

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'zen.views.home', name='home'),
    # url(r'^zen_together/', include('zen_together.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^about/$', 'zen.views.about'),
    url(r'^zen/$', 'zen.views.start'),
    url(r'^zen/go/(\d{1,2})/$', 'zen.views.meditate'),
    url(r'^zen/complete/$', 'zen.views.complete'),
    url(r'^zen/reset/$', 'zen.views.reset'),
    url(r'^zen/exit/$', 'zen.views.exit'),
    url(r'^zen/savePrefs/$', 'zen.views.savePrefs'),
    #url(r'^avatar/', include('avatar.urls')),
    url(r'^tracking/', include('tracking.urls')),
    url(r'^geoip/', 'zen.views.geoip'),
    url(r'^profile/', 'zen.views.profile'),
    #url(r'^logout/', 'zen.views.logout'),

    #url(r'^login/facebook/$', facebook_login, name="facebook_login"),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':os.path.join(os.path.dirname(__file__),'static/')}),
    url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,}),
)