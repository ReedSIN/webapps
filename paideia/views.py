from datetime import datetime
import time

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

from webapps.generic.views import *
from webapps.generic.models import SinUser
from webapps.paideia.models import *

import demjson


VALID_FACTORS = [
  'admin',
  'student',
]

CZARS = [
  'mkincaid',
  'muldavin',
  'raon',
]

DAYS = ['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
VERBOSE_DAYS = ['Sat, Jan 16', 'Sun, Jan 17', 'Mon, Jan 18', 'Tue, Jan 19', 'Wed, Jan 20', 'Thu, Jan 21', 'Fri, Jan 22', 'Sat, Jan 23', 'Sun, Jan 24']
BEGIN_DATE = 16
END_DATE = 25
BEGIN_HOUR = 1
END_HOUR = 25

HOURS = []

for i in range(BEGIN_HOUR, END_HOUR):
  hour = i%24
  if hour >= 12:
    antepost = "pm"
  else:
    antepost = "am"
  hour = hour % 12
  if (hour == 0):
    hour = 12
  HOURS.append(str(hour) + ":00 " + antepost)




def index(request):
  if request.META['REMOTE_USER'] not in CZARS:
    admin = False
    teacher = is_teacher(request)
  else:
    admin = True
    teacher = False

  template_args = {
    "days" : DAYS,
    "vdays" : VERBOSE_DAYS,
    "hours" : HOURS,
    "admin" : admin,
    "teacher" : teacher
  }
    
  return render_to_response('paideia/index.phtml', template_args, context_instance=RequestContext(request))

def alum_index(request):
  template_args = {
    "days" : DAYS,
    "vdays" : VERBOSE_DAYS,
    "hours" : HOURS,
    "admin" : False,
    "teacher" : False
  }

  return render_to_response('paideia/index.phtml', template_args, context_instance=RequestContext(request))

def add_page(request):
  if request.META['REMOTE_USER'] not in CZARS:
    authenticate(request, VALID_FACTORS)
    czar = False
    teacher = is_teacher(request)
  else:
    czar = True
    teacher = False

  if not teacher and not czar:
    return HttpResponseRedirect('/webapps/paideia/')

  template_args = {
    "days" : DAYS,
    "vdays" : VERBOSE_DAYS,
    "hours" : HOURS,
    "admin" : czar,
    "teacher" : teacher,
  }

  return render_to_response("paideia/add.phtml", template_args, context_instance=RequestContext(request))

def edit_page(request):
  if request.META['REMOTE_USER'] not in CZARS:
    authenticate(request, VALID_FACTORS)
    czar = False
    teacher = is_teacher(request)
  else:
    czar = True
    teacher = False

  if not teacher:
    return HttpResponseRedirect('/webapps/paideia/')

  student = SinUser.objects.get(username=request.META['REMOTE_USER'])
  classes = PaideiaClass.objects.all().filter(teacher=student).order_by('time')

  template_args = {
    "classes" : classes,
    "days" : DAYS,
    "vdays" : VERBOSE_DAYS,
    "hours" : HOURS,
    "admin" : czar,
    "teacher" : teacher
  }

  return render_to_response("paideia/edit.phtml", template_args, context_instance=RequestContext(request))

def search_page(request):
  if request.META['REMOTE_USER'] not in CZARS:
    czar = False
    teacher = is_teacher(request)
  else:
    czar = True
    teacher = False

  results = PaideiaClass.objects.none()

  try:
    terms = request.GET['q']

    if terms.lower() == 'notes' and czar:
      results = PaideiaClass.objects.all().filter(notes__gt=' ')
    else:
      terms = terms.split()
      for term in terms:
        termTitles = PaideiaClass.objects.all().filter(name__icontains=term)
        termDescriptions = PaideiaClass.objects.all().filter(description__icontains=term)
        termTeachers = PaideiaClass.objects.all().filter(teacher_name__icontains=term)
  
        results = results | termTitles | termDescriptions | termTeachers

        if czar:
          termNotes = PaideiaClass.objects.all().filter(notes__icontains=term)
          results = results | termNotes

      results = results.order_by('name')
      
  except MultiValueDictKeyError:
    results = PaideiaClass.objects.none()
    
  template_args = {
    "results" : results,
    "admin" : czar,
    "teacher" : teacher
  }

  return render_to_response("paideia/search.phtml", template_args, context_instance=RequestContext(request))

def admin_page(request):
  if request.META['REMOTE_USER'] not in CZARS:
    return HttpResponseRedirect('/webapps/paideia/')

  try:
    uid = request.POST['uid']
  except:
    uid = ''

  try:
    if len(uid) > 0:
      teacher = SinUser.objects.get(username__iexact=uid)
      if Teacher.objects.all().filter(user=teacher).count() > 0:
        result = '<span class="okay">' + teacher.first_name + ' ' + teacher.last_name + ' is already a Teacher.</span>'
      else:
        nt = Teacher()
        nt.user = teacher
        nt.name = teacher.last_name + " " + teacher.first_name
        nt.save()
        result = '<span class="okay">' + teacher.first_name + ' ' + teacher.last_name + ' is now a Teacher.</span>'
    else:
      result = ''
  except:
    result = '<span class="error"> User "' + uid + '" not found in the system!</span>'

  teachers = Teacher.objects.all()

  template_args = {
    "admin" : True,
    "result" : result,
    "teachers" : teachers
  }

  return render_to_response("paideia/admin.phtml", template_args, context_instance=RequestContext(request))


def is_teacher(request):
  uid = request.META['REMOTE_USER']
  try:
    student = SinUser.objects.get(username=uid)
  except:
    return False
  
  try:
    teacher = Teacher.objects.get(user=student)
    return True
  except:
    return False



# Class Registration, Editing, and Deletion Methods #
#####################################################

def register_class(request):
  if request.META['REMOTE_USER'] not in CZARS:
    authenticate(request, VALID_FACTORS)
    czar = False
    if not is_teacher(request):
      return HttpResponseRedirect("/webapps/paideia/")
  else:
    czar = True

  newclass = PaideiaClass()
  newclass.name = request.POST['name']
  newclass.location = request.POST['location']
  newclass.description = convertLineBreaks(request.POST['description'])
  newclass.teacher = SinUser.objects.get(username=request.META['REMOTE_USER'])
  if not czar:
    newclass.teacher_name = str(newclass.teacher)
  else:
    if len(request.POST['teacher'].strip()) > 0:
      newclass.teacher_name = request.POST['teacher'].strip()
  
  hour = int(request.POST['hour'])
  day = int(request.POST['day'])
  if hour == 24:
    hour = 0
    day += 1
  newclass.time = datetime(2010, 1, day, hour)
  newclass.length = int(request.POST['length'])

  endhour = hour + newclass.length;
  if endhour >= 24:
    endhour = endhour % 24
    day += 1
  newclass.end = datetime(2010, 1, day, endhour)

  try:
    fblink = request.POST['fbevent']
    if fblink.find('facebook.com/home.php#/event.php') != -1 or fblink.find('facebook.com/event.php?eid') != -1:
      newclass.fbevent = fblink
    else:
      newclass.fbevent = ''
  except:
    newclass.fbevent = ''

  if not czar:
    newclass.notes = '';
  else:
    newclass.notes = convertLineBreaks(request.POST['notes'])

  newclass.save()

  return HttpResponseRedirect("/webapps/paideia/")
 
def edit_class(request):
  if request.META['REMOTE_USER'] not in CZARS:
    authenticate(request, VALID_FACTORS)
    czar = False
    if not is_teacher(request):
      # those who try to circumvent the system get rickrolled
      return HttpResponseRedirect('http://www.youtube.com/watch?v=oHg5SJYRHA0')
  else:
    czar = True

  pclass = PaideiaClass.objects.get(id=int(request.POST['cid']))  
  pclass.name = request.POST['name-edit']
  if czar:
    pclass.teacher_name = request.POST['teacher-edit']
    pclass.notes = convertLineBreaks(request.POST['notes-edit'])
  else:
    student = SinUser.objects.get(username=request.META['REMOTE_USER'])
    if pclass.teacher != student:
      return HttpResponseRedirect('/webapps/paideia/')

  pclass.description = convertLineBreaks(request.POST['description-edit'])
  
  if czar:
    pclass.location = request.POST['location-edit']
  
    hour = int(request.POST['hour-edit'])
    day = int(request.POST['day-edit'])
    if hour == 24:
      hour = 0
      day += 1
    pclass.time = datetime(2010, 1, day, hour)
    pclass.length = int(request.POST['length-edit'])
  
    endhour = hour + pclass.length;
    if endhour >= 24:
      endhour = endhour % 24
      day += 1
    pclass.end = datetime(2010, 1, day, endhour)

  try:
    fblink = request.POST['fbevent-edit']
    if fblink.find('facebook.com/home.php#/event.php') != -1 or fblink.find('facebook.com/event.php?eid') != -1:
      pclass.fbevent = fblink
    else:
      pclass.fbevent = ''
  except:
    pclass.fbevent = ''

  pclass.save()

  if czar:
    return HttpResponse(str(pclass.id) + "|" + ajax_search_result(pclass.id), mimetype='text/plain')
  else:
    return HttpResponseRedirect("/webapps/paideia/")

def delete_class(request):
  if request.META['REMOTE_USER'] not in CZARS:
    authenticate(request, VALID_FACTORS)
    czar = False
  else:
    czar = True

  pclass = PaideiaClass.objects.get(id=int(request.POST['cid']))
  user = SinUser.objects.get(username=request.META['REMOTE_USER'])

  if user == pclass.teacher or czar:
    pclass.delete()
    return HttpResponse('', mimetype='text/plain')
  else:
    return HttpResponse('Naughty naughty!', mimetype='text/plain')



# AJAX Information Injection Methods #
######################################
# for stuff like class listings, class descriptions, injected forms on the edit page, etc.

def class_count(request):
  counts = ""

  for hour in range(BEGIN_HOUR, END_HOUR):
    for day in range(BEGIN_DATE, END_DATE):
      # make classes scheduled at midnight appear in the 12:00 am block of previous day,
      # since that's how most people's minds work
      if hour == 24:
        hour_fix = 0
        day_fix = day+1
        block_fix = datetime(2010, 1, day_fix, (hour_fix))
        counts += str(len(PaideiaClass.objects.all().filter(time=block_fix))) + ","
        continue

      block = datetime(2010, 1, day, (hour%24))
      counts += str(len(PaideiaClass.objects.all().filter(time=block))) + ","

  return HttpResponse(counts[0:-1], mimetype='text/plain')

def listing(request):
  start = time.clock()

  day = int(request.POST['day'])
  daydate = datetime(2010, 1, day)

  response = "";
  response += "<span class=\"dayHeader\">" + daydate.strftime("%A, %B %d") + "</span><br><br>";

  noClasses = True

  for i in range(BEGIN_HOUR, END_HOUR):
    # treat midnight as part of the previous day
    hour = i
    if (hour == 24):
      hour = 0;
      day += 1;
    
    # find all the classes for this hour
    currentHour = datetime(2010, 1, day, hour)
    classes = PaideiaClass.objects.all().filter(time=currentHour)

    if len(classes) == 0:
      continue
    else:
      noClasses = False
    
    # if there are some, print out the time
    response += "<div class=\"listing\" id=\"v-jan-" + str(day) + "-" + str(hour) + "\">";
    if hour >= 12:
      antepost = "pm"
    else:
      antepost = "am"
    hour = hour % 12
    if (hour == 0):
      hour = 12
    response += "<div class=\"listingHour\">" + str(hour) + ":00 " + antepost + "</div>"

    # and then print out title & teacher name for each class found
    for c in classes:
      response += "<div class=\"listingInfo\">"
      response += "<span class=\"title\"><a href=\"javascript:moreInfo(" + str(c.id) + ")\">" + c.name + "</a></span><br>"
      response += c.teacher_name + "<br>"
      response += str(hour) + ":00 " + antepost + "-"

      endhour = (i + c.length) % 24
      if (endhour >= 12):
        endantepost = "pm"
      else:
        endantepost = "pm"
      endhour = endhour % 12
      if (endhour == 0):
        endhour = 12
      response += str(endhour) + ":00 " + endantepost
      response += ", " + c.location

      response += "<div class=\"listingDescription spacing\" id=\"d-" + str(c.id) + "\"></div> </div>"

    response += "</div>"

  if noClasses:
    response += "There are no classes listed for this day."

  end = time.clock();

  # make sure that at least 500 ms have passed since we got the request,
  # so that the slideup animation has time to finish
  while end-start < 0.5: 
    end = time.clock()
    
  return HttpResponse(response, mimetype='text/html')

# this is used to reload a class's information on the search page, after a czar
# makes changes to it. this is all done through ajax so they can edit multiple
# classes without having to search individually for each one
def ajax_search_result(cid):
  if request.META['REMOTE_USER'] not in CZARS:
    return ""

  pclass = PaideiaClass.objects.get(id=cid)
  id = str(pclass.id)

  response = '<span class="title"><a href="javascript:moreInfo(' + id + ')">' + pclass.name + '</a></span> '
  response += '(<a href="javascript:czarEdit(' + id + ')"><span id="edit-' + id + '">edit</span></a>) '
  response += '(<a href="javascript:deleteClass(' + id + ', \'' + pclass.name + '\')">delete</a>)<br>'
  response += pclass.teacher_name + '<br>' + pclass.time.strftime('%A, %b %d, %I:00')  
  if pclass.time.hour < 12:
    response += ' am - '
  else:
    response += ' pm - '
  response += pclass.end.strftime('%I:00')
  if pclass.end.hour < 12:
    response += ' am, '
  else:
    response += ' pm, '
  response += pclass.location

  response += '<span id="{{ class.id }}-notes" style="font-weight: bold;">'
  if len(pclass.notes.strip()) > 0:
    response += '<br><br>Notes:<span style="font-weight: normal;"> ' + pclass.notes + '</span>'
  response += '</span>'
  
  response += '<div class="listingDescription" style="display: none;" id="d-' + id + '"></div><div class="statusDiv" id="sd-' + id + '"></div><div class="editFormDiv" id="efd-' + id + '"></div>'

  return response


def description(request):
  class_id = int(request.POST['cid'])

  pclass = PaideiaClass.objects.get(id=class_id)

  response = str(class_id) + "|"
  response += pclass.description 
  if len(pclass.fbevent) > 0:
    response += "<p><a href=\"" + pclass.fbevent + "\">Facebook Event for this class</a>.</p>"

  response += "<a href=\"javascript:moreInfo(" + str(class_id) + ")\">(x)</a><br>"

  return HttpResponse(response, mimetype='text/plain')

def ajax_edit_form(request):
  if request.META['REMOTE_USER'] not in CZARS:
    authenticate(request, VALID_FACTORS)
    czar = False
  else:
    czar = True

  cid = request.POST['cid']
  pclass = PaideiaClass.objects.get(id=int(cid))

  response = cid + "|"
  response += '<br><form action="/webapps/paideia/edit_class" id="ajaxForm" onsubmit="return validate_edit(this)" method="post"><div class="formTitle">Title:</div><input type="text" name="name-edit" id="name" size="50">'
  if czar:
    response += '<div class="formTitle">Teacher:</div><input type="text" name="teacher-edit" id="teacher" size="50">'
    response += '<div id="timeSelect"><div class="formTitle">Time:</div>Starts at<select id="hour" name="hour-edit"> <option value="1">1:00 am</option> <option value="2">2:00 am</option> <option value="3">3:00 am</option> <option value="4">4:00 am</option> <option value="5">5:00 am</option> <option value="6">6:00 am</option> <option value="7">7:00 am</option> <option value="8">8:00 am</option> <option value="9">9:00 am</option><option value="10">10:00 am</option><option value="11">11:00 am</option><option value="12">12:00 pm</option><option value="13">1:00 pm</option><option value="14">2:00 pm</option><option value="15">3:00 pm</option><option value="16">4:00 pm</option><option value="17">5:00 pm</option><option value="18">6:00 pm</option><option value="19">7:00 pm</option><option value="20">8:00 pm</option><option value="21">9:00 pm</option><option value="22">10:00 pm</option><option value="23">11:00 pm</option><option value="24">12:00 am</option></select> on <select id="day" name="day-edit"><option value="16">Sat, Jan 16</option><option value="17">Sun, Jan 17</option><option value="18">Mon, Jan 18</option><option value="19">Tue, Jan 19</option><option value="20">Wed, Jan 20</option><option value="21">Thu, Jan 21</option><option value="22">Fri, Jan 22</option><option value="23">Sat, Jan 23</option><option value="24">Sun, Jan 24</option></select>, lasts for <input type="text" id="length" name="length-edit" size="1" maxlength="1"> hour(s).</div><div class="formTitle">Location:</div><input type="text" id="location" name="location-edit" size="50">'
    
  response += '<div class="formTitle">Facebook Event URL : <span style="color: gray;">Optional</span></div> <input type="text" id="fbevent" name="fbevent-edit" size="50"><br><div class="formTitle">Description:</div><textarea id="description" name="description-edit" cols="49" rows="7"></textarea><br>'
  
  if czar:
    response += '<div class="formTitle">Notes:</div><textarea id="notes" name="notes-edit" cols="49" rows="7"></textarea><br>'

  response += '<div class="formTitle"><input type="hidden" name="cid" id="classID" value="'+cid+'"><input type="submit" value="Edit Class"></div></form>|'
  response += pclass.name + "|"
  response += pclass.fbevent + "|"
  textdescription = (pclass.description).replace("<br>","\r\n")
  response += textdescription
  if czar:
    response += "|" + pclass.time.strftime('%H')
    response += "|" +  pclass.time.strftime('%d')
    response += "|" +  str(pclass.length)
    response += "|" +  pclass.location 
    response += "|" + pclass.teacher_name 
    response += "|" + (pclass.notes).replace("<br>","\r\n")

  return HttpResponse(response, mimetype="text/plain")





def convertLineBreaks(desc):
  desc.replace("|","")
  lines = desc.splitlines()

  converted = ""
  for line in lines:
    converted += line + "<br>"

  return converted[0:-4]
