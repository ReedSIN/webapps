from webapps.elections.models import *

sen = Election.objects.get(id=21)
cs = sen.candidate_set.all()

counts = {}

for c in cs:
    counts[c.person.username] = {}
    vs = c.vote_set.all()
    for v in vs:
        try:
            counts[c.person.username][v.get_position()] += 1
        except:
            counts[c.person.username][v.get_position()] = 1            
        
      

