import csv
from webapps.elections.models import *

O_FILE1 = '/home/bbeutell/senate_ballots_s14.csv'

e = Election.objects.get(id=21)
sbs = e.ballot_set.all()

with open(O_FILE,'w+') as csvf:
    wrt = csv.writer(csvf,delimiter=",")
    for b in sbs:
        TO_WRITE = []
        y = b.first
        while y is not None:
            tw = '[' + str(y.vote) + ' | ' + str(y.get_position()) +']'
            TO_WRITE.append(tw)
            y = y.next
    
        wrt.writerow(TO_WRITE)
