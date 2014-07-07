from django.db import models, connection, backend, transaction

SUPER_VOTE_COUNT = 6

TOP_SIX = 'top_six'
APPROVE = 'approve'
NOOP = 'no_opinion'
DISAPPROVE = 'disapprove'
DEEP_SIX = 'deep_six'

TOP_SIX_VALUE = 8
APPROVE_VALUE = 2
NOOP_VALUE = 0
DISAPPROVE_VALUE = -1
DEEP_SIX_VALUE = -4

VOTE_TYPES = {
  TOP_SIX : TOP_SIX_VALUE,
  APPROVE : APPROVE_VALUE,
  NOOP : NOOP_VALUE,
  DISAPPROVE : DISAPPROVE_VALUE,
  DEEP_SIX : DEEP_SIX_VALUE
}

INVERSE_VOTE_TYPES = {
  TOP_SIX_VALUE : TOP_SIX,
  APPROVE_VALUE : APPROVE,
  NOOP_VALUE : NOOP,
  DISAPPROVE_VALUE : DISAPPROVE,
  DEEP_SIX_VALUE : DEEP_SIX
}

class SuperVoteCounter(object):
  def __init__(self, alarm_count):
    self.alarm_count = alarm_count
    self.count = 0
  def increment(self):
    if self.count >= self.alarm_count:
      raise Http400
    self.count = self.count + 1

def quote_name(name):
  if name.startswith("`") and name.endswith("`"):
    return name
  return "`%s`" % name

class FundingPollVoteManager(models.Manager):
  
  @transaction.commit_on_success
  def save_fp_data_list(self, fporg, _funding_poll, _user, _org_vote_list):
    """ Should be a list of org_ids/vote_types """
    count = SuperVoteCounter(SUPER_VOTE_COUNT)
    
    def update_org(o,n):
      cursor = connection.cursor()
      
      table_name = quote_name(o._meta.db_table)
      total_v_column = quote_name("total_votes")
      v_type_column = quote_name(INVERSE_VOTE_TYPES[n])
      
      sql = "UPDATE %s SET %s=%s+%i, %s=%s+1 WHERE `id`=%i;" % (table_name,
                                                                total_v_column,
                                                                total_v_column, n,
                                                                v_type_column,
                                                                v_type_column,
                                                                o.id)
      
      cursor.execute(sql)
    def submit_data(l):
      org_id = l[0]
      vote_type = l[1]
      
      if vote_type == TOP_SIX or vote_type == DEEP_SIX:
        count.increment()
      
      _org = fporg.objects.get(id = org_id) 
      _vote_amount = VOTE_TYPES[vote_type]
      
      update_org(_org, _vote_amount)
      
      b = self.model()
      b.funding_poll = _funding_poll
      b.organization = _org
      b.voter = _user
      b.scalar = _vote_amount
      b.save()
    
    for d in _org_vote_list:
      submit_data((d, _org_vote_list[d]))
