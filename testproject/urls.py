from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

def example2(request):
    from django.contrib import messages
    messages.add_message(request, messages.SUCCESS, 'Successfully rendered requirements!')
    return direct_to_template(request, template='example2/example2.html')

urlpatterns = patterns('',
    url(r'^example1/$', direct_to_template, {'template': 'example1/example1.html'}),
    url(r'^example2/$', example2),
    url(r'^example3/$', direct_to_template, {'template': 'example3/example3.html'}),
)
