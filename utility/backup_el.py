from webapps.elections.models import *
import csv

O_FILE = "/home/bbeutell/senate_backup.csv"

el = Election.objects.get(id=21)
bs = el.ballot_set.all()

HEADER = []

with open(O_FILE,'w+') as csvf:
    wrt = csv.writer(csvf, delimiter=",")
    for b in bs:
        TO_WRITE = []
        TO_WRITE.append(b.voter.username)
        y = b.first
        while (y is not None):
            TO_WRITE.append((y.vote.person.username,y.get_position()))
            y = y.next
        wrt.writerow(TO_WRITE)
