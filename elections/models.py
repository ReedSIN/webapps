from __future__ import division
from datetime import datetime
from django import forms
from django.db import models
from django.db.models import Q, Max, Min, Avg
from webapps.generic.models import *
import ast
import random
import csv

numStudents = 5
''' Is this number stored anywhere? the total number of SinUsers is like 2300. 
This is relevant because quorum for the election is calculated by taking one quarter of the number of currently enrolled students. 
'''

class Candidate(models.Model):
    person = models.ForeignKey(SinUser)
    election = models.ForeignKey("Election", related_name ="candidate_set")
    num_first_place = models.IntegerField(default=0)
    num_second_place = models.IntegerField(default=0)
     # This is a float because allowing for fractions of votes makes transferring surplus votes much easier. 
#    first_name = models.CharField(max_length = 30,blank=True,null=True)
#    last_name = models.CharField(max_length = 30,blank=True,null=True)
#    major = models.CharField(max_length = 40,blank=True,null=True)
#    class_year = models.CharField(max_length = 15,blank=True,null=True)
#    blurb = models.CharField(max_length = 140,blank=True,null=True,)
#    photo = models.URLField(blank=True,null=True)
#    preferred_pron = models.CharField(max_length = 30,blank=True,null=True)
#    numVotesList = ListField() # This will keep track of the number of votes a candidate receives in each round for testing/accounting purposes. 
#    isWinnerCurrent = models.BooleanField(default=False)
#    isOutCurrent = models.BooleanField(default=False)
#    isWinnerList = ListField(blank=True,null=True)

    def __unicode__(self):
        return u'%s' %(self.person.username)

class Vote(models.Model):
    parent_ballot = models.ForeignKey("Ballot")
    vote = models.ForeignKey("Candidate", related_name ="vote_set")
    next = models.ForeignKey("Vote", null=True, related_name="prev_vote", on_delete = models.SET_NULL)
    prev = models.ForeignKey("Vote", null=True, related_name="next_vote", on_delete = models.SET_NULL)
    first_round = models.IntegerField(null=True,blank=True)
    same_as_prev = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' %(self.vote.person.username)

    # Call this ONLY on the first round of the election
    def set_first_round(self):
        ''' 
        Sets a first_round attribute.
        For debugging reasons.
        '''
        self.first_round = self.get_position()
        pass

    def get_position(self):
        ''' Returns position within the linked list '''
        ''' must account for whether linked votes have same ranking '''
        current = self

        if current.prev is None:
            return 1
        else:
            if current.same_as_prev:
                return current.prev.get_position()
            else:
                return 1 + current.prev.get_position()


class Ballot(models.Model):
    election = models.ForeignKey("Election", related_name = "ballot_set")
    voter = models.ForeignKey(SinUser, related_name= "ballot_set")
#    voteRecord = ListField(null=True,blank=True)
#    hasVoted = models.BooleanField(default=False)
    first = models.ForeignKey(Vote, null=True, blank=True, related_name="first_voter_set")
    last = models.ForeignKey(Vote, null=True, blank=True, related_name="last_voter_set")
    def __unicode__(self):
        list = [str(self.voter.username)+" --> "]
        y = self.first
        i = 1
        while y is not None: 
            list.append(str(i) +": " + str(y))
            y = y.next
            i += 1
        return u'%s' %(list)

    def insertAtEnd(self,vote):
        vote.prev = self.last
        vote.next = None
        self.last.next = vote
        self.last = vote

    def removeFirst(self):
        if self.first == self.last:
            self.first = None
            self.last = None
            self.save()
        elif self.first.next is not None: 
            self.first.next.prev = None
            self.first.next.save()
            self.first = self.first.next
            self.save()

    def removeLast(self):
        if self.first == self.last:
            self.first = None
            self.last = None
            self.save()
        elif self.last.prev is not None: 
            self.last.prev.next = None
            self.last.prev.save()
            self.last = self.last.prev
            self.save()

    def removeCandidate(self, c):
        if self.first is not None:
            y = self.first
            while y.vote != c and y.next is not None:
                y = y.next
            if y.vote == c:
                if self.first == self.last:
                    self.first = None
                    self.last = None
                    self.save()
                elif self.first.vote == c and self.first != self.last:
                    self.removeFirst()
                    self.save()
                elif self.last is not None and self.last.vote == c and self.first != self.last:
                    self.removeLast()
                    self.save()
                elif y.next is not None and y.prev is not None: 
                    y.next.prev = y.prev
                    y.next.save()
                    y.prev.next = y.next
                    y.prev.save()
        

    def retFirst(self):
        if self.first is not None:
            return self.first.vote

    
class Election(models.Model):

    position = models.CharField(max_length = 50)
    candidatesInitial = models.ManyToManyField(Candidate,null=True,blank=True, related_name="running_set")
    candidatesCurrent = models.ManyToManyField(Candidate,related_name="elections_in",null=True,blank=True)
    ballotsInitial = models.ManyToManyField(Ballot,null=True,blank=True, related_name="tha_election")
    ballotsCurrent = models.ManyToManyField(Ballot, null=True,blank=True, related_name="still_movin")
    numSeatsInitial = models.IntegerField(null=True,blank=True,default=1)
    numSeatsCurrent = models.IntegerField(null=True,blank=True,default=1)
    quorum = models.IntegerField(null=True,blank=True)
    threshold = models.IntegerField(null=True,blank=True)
    numRounds = models.IntegerField(default=0)
    winners = models.ManyToManyField(Candidate, related_name="elections_won",null=True,blank=True)
    record = models.CharField(max_length = 2000, null=True,blank=True)

#    startDateTime = models.DateTimeField(null=True,blank=True)
#    endDateTime = models.DateTimeField(null=True,blank=True)
#    candidatesList = ListField(null=True,blank=True)
#    numVotesInitial = models.IntegerField(default=0)
#    numVotesCurrent = models.IntegerField(default=0)
#    numVotesList = ListField(null=True,blank=True)
#    thresholdList = ListField(null=True,blank=True)
#    meets_quorum = models.BooleanField(default=False)


    def __unicode__(self):
        return u'%s' %(self.position)

    """ Below are helper functions. """
    
    def calculate_quorum(self):
        self.quorum = int(round(numStudents/4))
        self.save()
        return self.quorum

    def calculate_threshold(self, balls):
        return int(round(balls.count()/(self.numSeatsInitial + 1))) + 1

    def tabulate_first_place(self, balls):
        for candidate in self.candidatesCurrent.all():
            candidate.num_first_place = 0
            candidate.save()
        for ballot in balls: 
            if ballot.first is not None:
                choice = ballot.first
                choice.vote.num_first_place +=1
                choice.vote.save()
                while choice.next is not None and choice.next.same_as_prev == True:
                    choice = choice.next
                    choice.vote.num_first_place += 1
                    choice.save()

# If something fucks up, put this code above, removing everything below
# the line "if ballot.first is not None:"
#
#            first_choice = ballot.retFirst()
#            if first_choice is not None:
#                first_choice.num_first_place += 1
#                first_choice.save()
#                if ballot.first.next is not None:
#                    if ballot.first.next.same_as_prev == True:
#                        equal = ballot.first.next.vote
#                        equal.num_first_place += 1
#                        equal.save()
    
    def redistribute_first_place(self, from_cand, balls):
        relevant_ballots = balls.filter(first__vote = from_cand)
        numSurplus = from_cand.num_first_place - self.threshold
        # randomly sample keepers from relevant ballots
        rbl = list(relevant_ballots)
        random_indices = sorted(random.sample(range(len(rbl)-1), numSurplus))
        random_ballots = [rbl[i] for i in random_indices]
        list_of_ids = [b.id for b in random_ballots]
        keepers = relevant_ballots.filter(pk__in = list_of_ids)
        deleters = relevant_ballots.exclude(pk__in = list_of_ids)
        for d in deleters: 
            self.ballotsCurrent.remove(d)
            self.save()
        for b in self.ballotsCurrent.all():
            b.removeCandidate(c = from_cand)
            b.save()
        self.candidatesCurrent.remove(from_cand)
        self.save()
        
    def determine_loser(self):
        least_votes = self.candidatesCurrent.aggregate(min_votes=Min('num_first_place'))['min_votes']
        worst_cands = self.candidatesCurrent.filter(num_first_place = least_votes)
        #randomly pick one of the worst candidates to call the loser
        wcl = list(worst_cands)
        random_index = sorted(random.sample(xrange(len(wcl)),1))[0]
        loser_id = wcl[random_index].id
        loser = Candidate.objects.get(id=loser_id)
        return loser

    def delete_loser(self, loser):
        for b in self.ballotsCurrent.all():
            b.removeCandidate(c = loser)
            b.save()
        self.candidatesCurrent.remove(loser)
        self.save()

    def print_winners(self):
        string = ""
        for winner in self.winners.all():
             string = string + str(winner) +", "
        return string
            

    def execute_STV(self):
        startingCandidates = Candidate.objects.filter(election = self)
        startingBallots = Ballot.objects.filter(election=self)
        startingNumSeats = self.numSeatsInitial
        winners = self.winners
        quorum = self.calculate_quorum()
        numRounds = 0

        # Create files for data dumpage for summary. 
        transcript_path = "election%stranscript.txt" % (self.id)
        csv_path = "election%s.csv" % (self.id)

        trans_file = open(transcript_path, 'w+')
        csv_file = open(csv_path, 'wb')
        csv_writer = csv.writer(csv_file, delimiter=',')

        posi = str(self.position)
        now = str(datetime.now())
        trans_file.write('%s \n' %(posi))
        trans_file.write('%s \n' % (now))
        csv_writer.writerow(['Round','Candidate','NumFirst'])

        self.candidatesInitial = startingCandidates
        self.ballotsInitial = startingBallots
        self.record = ""
        self.save()
        if (startingBallots.count() < quorum):
            self.record += "QUORUM NOT MET.  "
            trans_file.write('QUUROM NOT MET. \n')
        else: 
            self.record += "QUORUM IS MET. RESULTS FOLLOW.  "
            trans_file.write('QUOROM IS MET. RESULTS FOLLOW. ')
            self.candidatesCurrent = startingCandidates
            self.ballotsCurrent = startingBallots
            self.numSeatsCurrent = startingNumSeats
            self.save()
            self.threshold = self.calculate_threshold(balls = self.ballotsCurrent)
            self.save()
            while (self.candidatesCurrent.count() > self.numSeatsCurrent):
                self.tabulate_first_place(balls = self.ballotsCurrent.all())
                self.save()
                print self.numRounds
                for b in self.ballotsCurrent.all():
                    print b
                for c in self.candidatesCurrent.all():
                    print "%s : %s" %(c,c.num_first_place)
                    csv_writer.writerow([self.numRounds, c, c.num_first_place])
                self.numRounds += 1
                self.save()
                self.record += "round %s:  "  %(self.numRounds)
                trans_file.write('Round %s: \n' %(self.numRounds))
                winner_this_round = False
                for candy in self.candidatesCurrent.all():
                    if candy.num_first_place >= self.threshold:
                        winner_this_round = True
                        self.winners.add(candy)
                        self.save()
                        self.numSeatsCurrent = self.numSeatsCurrent - 1
                        self.save()
                        if candy.num_first_place > self.threshold:
                            self.redistribute_first_place(from_cand = candy,balls = self.ballotsCurrent)
                        self.record += "%s wins.  " %(candy)
                        trans_file.write('%s wins. \n \n' %(candy))
                        self.save()
                if not winner_this_round == True:
                    self.record += "No winner this round.  "
                    trans_file.write('No winner this round. \n')
                    self.save()
                    loser = self.determine_loser()
                    self.delete_loser(loser)
                    self.record += "%s loses this round.  " %(loser)
                    self.save()
                    trans_file.write('%s eliminated. \n \n' % (loser))
            for winner in self.candidatesCurrent.all():
                self.winners.add(winner)
                self.save()
        self.record += "In short, the winners are %s" %(str(self.print_winners()))
        trans_file.write('In short, the winners are: \n \n')
        for winner in self.winners.all():
            trans_file.write('%s \n' %(str(winner)))
        trans_file.close()
        csv_file.close()
        return self.record
                        

                    
            
            
            
        
                
                
                    
                        
                
                
                
               
        
        

        
