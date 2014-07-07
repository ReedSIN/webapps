from webapps.elections.models import *

sen = Election.objects.get(id=21)
sbs = sen.ballot_set.all()
me = SinUser.objects.get(username="bbeutell")
