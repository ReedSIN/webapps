from webapps.generic.models import *
from webapps.fundingpoll.models import *
from webapps.finance.models import *
from webapps.elections.models import *

def clearBallots(username):
    "Deletes all the ballots for a give user. Useful for testing."
    # get the Sinuser object
    user = SinUser.objects.get(username = username)
    # get a list of their ballots
    ballots = Ballot.objects.filter(voter = user)
    # go through list and delete the ballots
    for ballot in ballots:
        ballot.delete()
