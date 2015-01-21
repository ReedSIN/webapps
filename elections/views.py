import os, sys

from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import date, datetime
from django.core.exceptions import ObjectDoesNotExist

from webapps.generic.models import *
from webapps.generic.views import *
from webapps.generic.errors import *

from webapps.elections.models import *

import demjson
import sys

"""

-- Jacob Menick
-- March 2014

Heeerre, we gooooo

"""

VALID_FACTORS = [
    'student'
]

ADMIN_FACTORS = [
    'admin',
   'elections'
]

#
# NOTE: Requesting Context automagically grants you use of the user variable in templates
# (I think) -BB

#
# Helper functions (shorthand for recurring Django queries):
#

def get_elects():
    return Election.objects.all()

def get_cands(e):
    return e.candidate_set.all()

def has_user_voted(e,user):
    return e.ballot_set.filter(voter=user).exists()

def get_toVote_hasVoted(es,user):

    # These will be returned as a tuple
    es_toVote   = []
    es_hasVoted = []

    for e in es:
        # check if the user is in a ballot set for a given election
        has_voted = has_user_voted(e,user)
        # assign eleciton to proper array
        es_hasVoted.append(e) if has_voted else es_toVote.append(e)

    return (es_toVote, es_hasVoted)



#############################
### THE ACTUAL VIEW FUNKS ###

def index(request):
    

    # ------ JM on 11/16 -----------
    # this block should only allow voting in the 
    # correct date window, but I didn't really test it very thoroughly so 
    # I'm just going to comment it out and end voting manually. 
    startVote = date(2014, 12, 9)
    endVote = date(2014, 12, 14)
    today = date.today()

    if (today < startVote) or (today > endVote):
        authenticate(request, ADMIN_FACTORS)
    else:
        authenticate(request, VALID_FACTORS)

#    authenticate(request, ADMIN_FACTORS)
   # ------ end JM 11/16 -----------

    # Assigns array of elections user hasn't and has voted in (respectively)
    elections_toVote, elections_hasVoted = get_toVote_hasVoted(get_elects(),request.user)

    template_args = {
        'elections_toVote'  : elections_toVote,
        'elections_hasVoted': elections_hasVoted,
    }

    return render_to_response('elections/home.html',template_args,context_instance=RequestContext(request))

def vote(request,identifier,validate_error=""):

    authenticate(request, VALID_FACTORS)
    jacob = SinUser.objects.get(username="jmenick")

    try:
        election = Election.objects.get(id=identifier)
    except:
        raise Http404

    has_voted = has_user_voted(election,request.user)
    if request.user == jacob:
        has_voted = False

    if has_voted:
        html = '''
<h1>You have already voted in this election</h1>
<p>Return to the <a href="http://sin.reed.edu/webapps/elections/">elections home</a> to vote in other elections.</p>
'''
        return HttpResponse(html)

    # Get only the original canidates, not those added as write-ins
    candidates = election.candidatesInitial.all()
    candidate_count = len(candidates)  # This will give a max on the html input for ranking

    template_args = {
        'election'       : election,
        'has_voted'      : has_voted,
        'candidates'     : candidates,
        'candidate_count': candidate_count,
        'validate_error' : validate_error
    }

    return render_to_response('elections/vote.html',template_args,context_instance=RequestContext(request))

def submit_vote(request,identifier):
    authenticate(request,VALID_FACTORS)

    if request.method != 'POST':
        raise Http404
    try:
        election = Election.objects.get(id=identifier) # this is also stored in the query string
    except:
        raise Http404

    # Kick them out if they have voted
    if has_user_voted(election,request.user):
        html = '''
<h1>You have already voted in this election</h1>
<p>Return to the <a href="http://sin.reed.edu/webapps/elections/">elections home</a> to vote in other elections.</p>
'''
        return HttpResponse(html)

    # Grab the query
    query = demjson.decode(request.POST['query_string'])
    print >>sys.stderr, query

    # Grab votes from the query
    # NOTE: This will not contain any votes with ranks equal to ''
    vote_array = query['votes']

    print >> sys.stderr, "query 0 %s" % str(query)
    print >> sys.stderr, "vote_array 0 %s" % str(vote_array)

    #-------------------ALEX EDITS HERE------------------------

    # 1. check if the voter voted and wants to contribute to quorum
    didVote = query['didVote']
    bQuorum = query['bQuorum']


    # 2. update quorum
    if bQuorum == True:
        election.increment_quorum()
        election.save()

    # 3. If the voter didn't vote, return thanks voter
    if didVote == False:
        # Create an emtpy ballot
        # This should not effect the election, but the number of ballots
        # are used to calulate quorum in execute_STV()
        bal = Ballot(voter=request.user, election=election)
        bal.save()
        template_args = {
            'vote_success': True,
        }
        return render_to_response('elections/thanks_voter.html',template_args,context_instance=RequestContext(request))

    # 3. If the voter voted, sort their votes using election sort
    for fillslot in range(len(vote_array)-1,0,-1):
        positionOfMax=0
        for location in range(1,fillslot+1):
            # Recall: each element of array is dictionary
            if vote_array[location]['rank'] > vote_array[positionOfMax]['rank']:
                positionOfMax = location

        temp = vote_array[fillslot]
        vote_array[fillslot] = vote_array[positionOfMax]
        vote_array[positionOfMax] = temp

    # Now, we have a vote_array sorted by rank from highest pref to lowest pref
    bal = Ballot(voter=request.user,election=election)
    bal.save()

    # verts will hold the votes we construct in the first for loop
    verts = []

    # This creates and saves the votes for the ballot
    # They MUST be saved first for next and prev assignments to work

    #for i in range(0,len(vote_array)):
    i = 0
    vote_array_initial_length = len(vote_array)
    while i < len(vote_array):
        print >>sys.stderr, 'Current index: %d, array length: %d' %(i, vote_array_initial_length)
        # check if candidate is a write in. If they are, they need to validated.
        isWritein = vote_array[i]['isWritein']
        if isWritein:
            try:
                can = None
                candidates = election.candidate_set.all()
                for c in candidates:
                    if c.person.username == vote_array[i]['candidate']:
                        can = c
                if can is None:
                    # attempt to validate new candidate, throws exception
                    can_su = SinUser.objects.get(username= vote_array[i]['candidate'])
                    # create a new candidate for the writein
                    can = Candidate(person=can_su, election=election)
                    can.save()
            except:
                vote_array.pop(i)
                # Redirect back to page with error
                continue
        else:
            can_su = SinUser.objects.get(username= vote_array[i]['candidate'])
            can = Candidate.objects.get(person=can_su, election= election)

        vt = Vote(parent_ballot= bal, vote= can)
        vt.save()
        verts.append(vt)

        if (i == 0):
            bal.first = vt
        if (i == len(vote_array) - 1):
            bal.last = vt
        i += 1

    # This goes through verts and ties the votes together
    # The range takes len(verts)-1 since we reason about the last index through i+1
    for i in range(0,len(verts)-1):
        verts[i].next = verts[i+1]
        verts[i+1].prev = verts[i]
        r1 = vote_array[i]['rank']
        r2 = vote_array[i+1]['rank']
        if (r1 == r2):
            verts[i+1].same_as_prev = True
        verts[i].save()
        verts[i+1].save()

    # Last loop through the votes, I promise
    for v in verts:
        v.set_first_round() # This records the rank in the first round
        v.save()            # And, of course, we save

    print >> sys.stderr, "fiddin, to save %s" % str(bal)
    bal.save()
    template_args = {
        'vote_success'       : True,
    }

    return render_to_response('elections/thanks_voter.html',template_args,context_instance=RequestContext(request))

def re_vote(request):
    authenticate(request,VALID_FACTORS)

    el = Election.objects.get(id=21)
    candidates = get_cands(el)
    candidate_count = len(candidates)  # This will give a max on the html input for ranking
    template_args = {
        'election'       : el,
        'candidates'     : candidates,
        'candidate_count': candidate_count,
    }
    return render_to_response('elections/re_vote.html',template_args,context_instance=RequestContext(request))

def check_username(request):
    "Checks the validity of a give username"
    # Gets the username from the URL
    username = request.GET.get('username','')
    valid = False
    try:
        if SinUser.objects.get(username = username):
            valid = True
    except:
        valid = False
    # Respond with boolean
    return HttpResponse(str(valid), content_type="text/plain")

def re_submit_vote(request):
    authenticate(request,VALID_FACTORS)

    if request.method != 'POST':
        raise Http404

    election = Election.objects.get(id=21)

    # Delete their old ballot :'(
    try:
        old_user_ballot = election.ballot_set.get(voter=request.user)
        old_user_ballot.delete()
    except:
        pass

    # Grab the query
    query = demjson.decode(request.POST['query_string'])
    # Grab votes from the query
    vote_array = query['votes']  # NOTE: This, in theory, will not contain any votes with ranks equal to ''

    # Selection sort on the vote_array
    # thanks be to interactivepython.org
    for fillslot in range(len(vote_array)-1,0,-1):
        positionOfMax=0
        for location in range(1,fillslot+1):
            # Recall: each element of array is dictionary
            if int(vote_array[location]['rank']) > int(vote_array[positionOfMax]['rank']):
                positionOfMax = location

        temp = vote_array[fillslot]
        vote_array[fillslot] = vote_array[positionOfMax]
        vote_array[positionOfMax] = temp
    # end selection sort

    # Now, we have a vote_array sorted by rank from highest pref to lowest pref
    bal = Ballot(voter=request.user,election=election)  # new ballot
    bal.save()
    # verts will hold the votes we construct in the first for loop
    verts = []
    # This creates and saves the votes for the ballot
    # They MUST be saved first for next and prev assignments to work
    for i in range(0,len(vote_array)):
        # Who da candidate?
        can_su = SinUser.objects.get(username= vote_array[i]['candidate'])
        can = Candidate.objects.get(person= can_su, election= election)
        # Construct the vote
        vt = Vote(parent_ballot= bal, vote= can)
        vt.save()
        # Append to the verts array (preserves order)
        verts.append(vt)
        # Assign the appropriate first and last votes
        if (i == 0):
            bal.first = vt
        if (i == len(vote_array) - 1):
            bal.last = vt

    # This goes through verts and ties the votes together
    # The range takes len(verts)-1 since we reason about the last index through i+1
    for i in range(0,len(verts)-1):
        verts[i].next = verts[i+1]
        verts[i+1].prev = verts[i]
        r1 = int(vote_array[i]['rank'])
        r2 = int(vote_array[i+1]['rank'])
        if (r1 == r2):
            verts[i+1].same_as_prev = True

    # Last loop through the votes, I promise
    for v in verts:
        v.set_first_round() # This records the rank in the first round
        v.save()            # And, of course, we save

    # Last step
    bal.save()

    vote_success = True  # Triggers a success message

    template_args = {
        'vote_success'       : vote_success,
    }

    return render_to_response('elections/thanks_voter.html',template_args,context_instance=RequestContext(request))




def vote_mockup(request):

    authenticate(request, VALID_FACTORS)
    has_voted = None # Controls display of page?
    # GET or POST ?

    template_args = {
        'user': request.user
    }

    return render_to_response('elections/vote_mockup.html',template_args,context_instance=RequestContext(request))


def results_mockup(request):

    authenticate(request, VALID_FACTORS)

    # Grab all (current) elections
    elections = None # Placeholder

    template_args = {
        'elections': elections,
        'user': request.user
    }

    return render_to_response('elections/results_mockup.html',template_args,context_instance=RequestContext(request))

def admin_index(request):

    authenticate(request, ADMIN_FACTORS)
    # Do they have other specific view permissions?

    # Is it POST or GET?

    # Grab all (current) elections
    elections = None # Placeholder

    template_args = {
        'elections' : elections,
        'user': request.user
    }

    return render_to_response('elections/admin_index.html',template_args,context_instance=RequestContext(request))

def create_election(request):

    authenticate(request, ADMIN_FACTORS)

    # GET or POST?
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data



    template_args = {
        'user': request.user
    }

    return render_to_response('elections/create_election.html',template_args,context_instance=RequestContext(request))

def thanks(request):
    authenticate(request, ADMIN_FACTORS)

    template_args = {
        'user': request.user,
    }

    return render_to_response('elections/thanks.html',template_args,context_instance=RequestContext(request))

def deleted(request):
    authenticate(request, ADMIN_FACTORS)

    template_args = {
        'user': request.user,
    }

    return render_to_response('elections/deleted.html',template_args,context_instance=RequestContext(request))
'''
#def delete_election(request,identifier):
    authenticate(request, ADMIN_FACTORS)

    relevant_election = Election.objects.get(id=identifier)
    relevant_election.delete()

    template_args = {
        'user': request.user,
    }

    return HttpResponseRedirect('/elections/admin/deleted/',template_args,context_instance=RequestContext(request))
'''
