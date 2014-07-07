
FUCKS = []

with open("/var/django/webapps/utility/not_yet_revoted.txt") as rdr:
    for line in rdr:
        i = line.find("@")
        FUCKS.append(line[:i])


