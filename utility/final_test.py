# This file tests the STV code.  

from webapps.generic.models import *
from webapps.elections.models import *

#Candidate sinusers
jacob = SinUser.objects.get(username="jmenick")
eleanor = SinUser.objects.get(username="eparment")
lisa = SinUser.objects.get(username="lfrueh")
brett = SinUser.objects.get(username="bbeutell")

#Voter sinusers
annam = SinUser.objects.get(username="swansons")
john = SinUser.objects.get(username="jiselin")
ali = SinUser.objects.get(username="alryan")
alejandro = SinUser.objects.get(username="achavezl")
timo = SinUser.objects.get(username="tdelgado")
jason = SinUser.objects.get(username="jinx")
theo = SinUser.objects.get(last_name="Sangenitto")
klein = SinUser.objects.get(username="kleinj")

#Create Election
posi = raw_input('What is the name of the position?: ----->    ')
e = Election(position=posi, numSeatsInitial=2)
e.save()

#Make the Candidate Objects
jacob_candidate = Candidate(person = jacob, election = e)
jacob_candidate.save()
eleanor_candidate = Candidate(person = eleanor, election = e)
eleanor_candidate.save()
lisa_candidate = Candidate(person = lisa, election = e)
lisa_candidate.save()
brett_candidate = Candidate(person = brett, election = e)
brett_candidate.save()

e.candidatesCurrent = Candidate.objects.filter(election=e)
e.save()

#Make the Ballot objects
annam_ballot = Ballot(election = e, voter = annam)
annam_ballot.save()
john_ballot = Ballot(election = e, voter = john)
john_ballot.save()
ali_ballot = Ballot(election = e, voter = ali)
ali_ballot.save()
alejandro_ballot = Ballot(election = e, voter = alejandro)
alejandro_ballot.save()
timo_ballot = Ballot(election = e, voter = timo)
timo_ballot.save()
jason_ballot = Ballot(election = e, voter = jason)
jason_ballot.save()

#Populate ballots with Votes.

# Annam's ballot first
an_vote_jacob = Vote(parent_ballot = annam_ballot, vote = jacob_candidate)
an_vote_jacob.save()
an_vote_eleanor = Vote(parent_ballot = annam_ballot, vote = eleanor_candidate)
an_vote_eleanor.save()
an_vote_brett = Vote(parent_ballot = annam_ballot, vote = brett_candidate)
an_vote_brett.save()
an_vote_lisa = Vote(parent_ballot = annam_ballot, vote = lisa_candidate)
an_vote_lisa.save()

an_vote_jacob.next = an_vote_eleanor
an_vote_jacob.save()
an_vote_eleanor.prev = an_vote_jacob
an_vote_eleanor.save()
an_vote_eleanor.next = an_vote_brett
an_vote_brett.prev = an_vote_eleanor
an_vote_brett.next = an_vote_lisa
an_vote_lisa.prev = an_vote_brett

an_vote_jacob.save()
an_vote_eleanor.save()
an_vote_brett.save()
an_vote_lisa.save()

annam_ballot.first = an_vote_jacob
annam_ballot.save()
annam_ballot.first.save()
annam_ballot.first.next.save()
annam_ballot.last = an_vote_lisa
annam_ballot.save()

#John's Ballot
john_vote_jacob = Vote(parent_ballot = john_ballot, vote = jacob_candidate)
john_vote_jacob.save()
john_vote_eleanor = Vote(parent_ballot = john_ballot, vote = eleanor_candidate)
john_vote_eleanor.save()
john_vote_brett = Vote(parent_ballot = john_ballot, vote = brett_candidate)
john_vote_brett.save()
john_vote_lisa = Vote(parent_ballot = john_ballot, vote = lisa_candidate)
john_vote_lisa.save()

john_vote_jacob.next = john_vote_eleanor
john_vote_eleanor.prev = john_vote_jacob
john_vote_eleanor.next = john_vote_brett
john_vote_brett.prev = john_vote_eleanor
john_vote_brett.next = john_vote_lisa
john_vote_lisa.prev = john_vote_brett


john_vote_jacob.save()
john_vote_eleanor.save()
john_vote_brett.save()
john_vote_lisa.save()

john_ballot.first = john_vote_jacob
john_ballot.last = john_vote_lisa
john_ballot.save()

#Ali's Ballot
ali_vote_jacob = Vote(parent_ballot = ali_ballot, vote = jacob_candidate)
ali_vote_jacob.save()
ali_vote_eleanor = Vote(parent_ballot = ali_ballot, vote = eleanor_candidate)
ali_vote_eleanor.save()
ali_vote_brett = Vote(parent_ballot = ali_ballot, vote = brett_candidate)
ali_vote_brett.save()
ali_vote_lisa = Vote(parent_ballot = ali_ballot, vote = lisa_candidate)
ali_vote_lisa.save()

ali_vote_jacob.next = ali_vote_eleanor
ali_vote_eleanor.prev = ali_vote_jacob
ali_vote_eleanor.next = ali_vote_brett
ali_vote_brett.prev = ali_vote_eleanor
ali_vote_brett.next = ali_vote_lisa
ali_vote_lisa.prev = ali_vote_brett

ali_vote_jacob.save()
ali_vote_eleanor.save()
ali_vote_brett.save()
ali_vote_lisa.save()

ali_ballot.first = ali_vote_jacob
ali_ballot.last = ali_vote_lisa
ali_ballot.save()

#Alejandro's Ballot
ale_vote_jacob = Vote(parent_ballot = alejandro_ballot, vote = jacob_candidate)
ale_vote_jacob.save()
ale_vote_eleanor = Vote(parent_ballot = alejandro_ballot, vote = eleanor_candidate)
ale_vote_eleanor.save()
ale_vote_brett = Vote(parent_ballot = alejandro_ballot, vote = brett_candidate)
ale_vote_brett.save()
ale_vote_lisa = Vote(parent_ballot = alejandro_ballot, vote = lisa_candidate)
ale_vote_lisa.save()

ale_vote_jacob.next = ale_vote_eleanor
ale_vote_eleanor.prev = ale_vote_jacob
ale_vote_eleanor.next = ale_vote_brett
ale_vote_brett.prev = ale_vote_eleanor
ale_vote_brett.next = ale_vote_lisa
ale_vote_lisa.prev = ale_vote_brett

ale_vote_jacob.save()
ale_vote_eleanor.save()
ale_vote_brett.save()
ale_vote_lisa.save()

alejandro_ballot.first = ale_vote_jacob
alejandro_ballot.last = ale_vote_lisa
alejandro_ballot.save()


#Timo's Ballot
timo_vote_jacob = Vote(parent_ballot = timo_ballot, vote = jacob_candidate)
timo_vote_jacob.save()
timo_vote_eleanor = Vote(parent_ballot = timo_ballot, vote = eleanor_candidate)
timo_vote_eleanor.save()
timo_vote_brett = Vote(parent_ballot = timo_ballot, vote = brett_candidate)
timo_vote_brett.save()
timo_vote_lisa = Vote(parent_ballot = timo_ballot, vote = lisa_candidate)
timo_vote_lisa.save()

timo_vote_jacob.next = timo_vote_eleanor
timo_vote_eleanor.prev = timo_vote_jacob
timo_vote_eleanor.next = timo_vote_brett
timo_vote_brett.prev = timo_vote_eleanor
timo_vote_brett.next = timo_vote_lisa
timo_vote_lisa.prev = timo_vote_brett

timo_vote_jacob.save()
timo_vote_eleanor.save()
timo_vote_brett.save()
timo_vote_lisa.save()

timo_ballot.first = timo_vote_jacob
timo_ballot.last = timo_vote_lisa
timo_ballot.save()

#Jason's Vote
jason_vote_jacob = Vote(parent_ballot = jason_ballot, vote = jacob_candidate)
jason_vote_jacob.save()
jason_vote_eleanor = Vote(parent_ballot = jason_ballot, vote = eleanor_candidate)
jason_vote_eleanor.save()
jason_vote_brett = Vote(parent_ballot = jason_ballot, vote = brett_candidate)
jason_vote_brett.save()
jason_vote_lisa = Vote(parent_ballot = jason_ballot, vote = lisa_candidate)
jason_vote_lisa.save()

jason_vote_brett.next = jason_vote_lisa
jason_vote_lisa.prev = jason_vote_brett
jason_vote_lisa.next = jason_vote_eleanor
jason_vote_eleanor.prev = jason_vote_lisa
jason_vote_eleanor.next = jason_vote_jacob
jason_vote_jacob.prev = jason_vote_eleanor


jason_vote_jacob.save()
jason_vote_eleanor.save()
jason_vote_brett.save()
jason_vote_lisa.save()

jason_ballot.first = jason_vote_brett
jason_ballot.last = jason_vote_jacob
jason_ballot.save()

print e.execute_STV()


 
