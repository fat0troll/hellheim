from django.conf.urls import patterns, include, url
from vms.views import machine_index, add_machine, edit_machine
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hellheim.views.home', name='home'),
    # url(r'^hellheim/', include('hellheim.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Virtual Machines UI
    url(r'^vms/(?P<pid>\w+)/edit', edit_machine),
    url(r'^vms/add', add_machine),
    url(r'^vms', machine_index),

    # Login and logout
    url(r'^login', login),
    url(r'^logout', logout),
)
