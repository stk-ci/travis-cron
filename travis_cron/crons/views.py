# Create your views here.

from crons.models import Entry, Cronjob
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins

def index(request):
    entry_list = Entry.objects.exclude(travis_token = '').order_by('sub_date')
    cron_list = Cronjob.objects.all()
    return render_to_response('crons_index.html',
                              { 'entry_list': entry_list, 'cron_list': cron_list },
                              context_instance=RequestContext(request))

def new(request):
    try:
        entry = Entry(gh_project = request.POST['gh_project'],
                      cronjob = Cronjob.objects.get(pk=request.POST['cronjob']),
                      #github_user = request.POST['github_user'],
                      travis_token = '',
                      #repository_owner_name = request.POST['repository_owner_name'],
                      motivation = request.POST['motivation'],
                      special_requests = request.POST['special_requests'])
        entry.full_clean()
        entry.save()

        mail_message = "%s - %s\n\n%s\n\nSpecial requests:\n%s\n" % (entry.gh_project, entry.cronjob.description, 
                                                                     entry.motivation, entry.special_requests or 'None :)')
        mail_admins('New entry!', mail_message)

        return HttpResponseRedirect(reverse('crons.views.index'))

    except KeyError:
        error_message = 'Something went wrong.'

    except ValidationError as e:
        if '__all__' in e.message_dict:
            error_message = ' '.join(e.message_dict['__all__'])
        else:
            error_message = ' '.join(map(lambda pair: ': '.join((pair[0], pair[1][0])), e.message_dict.items())) # TODO, fa schifo

    entry_list = Entry.objects.all().order_by('sub_date')
    cron_list = Cronjob.objects.all()
    return render_to_response('crons_index.html',
                              { 'entry_list': entry_list, 'cron_list': cron_list,
                              'error_message': error_message },
                              context_instance=RequestContext(request))
