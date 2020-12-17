# !/usr/bin/python
import subprocess

GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message', 'body']
GIT_LOG_FORMAT = ['%H', '%an', '%ae', '%ad', '%s', '%b']
GIT_LOG_FORMAT = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e'

p = subprocess.Popen('git log --format="%s"' % GIT_LOG_FORMAT, shell=True, stdout=subprocess.PIPE)
(log, _) = p.communicate()
log = log.decode(encoding='UTF-8')
log = log.strip('\x1e').split("\x1e")
log = [row.strip().split("\x1f") for row in log]
log = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in log]

# print(log)

for row in log:
    if row.setdefault('body', "NONE").find("\n"):
        changeIdSet = False
        for line in row['body'].split("\n"):
            if line.find('Change-Id:') != -1:
                changeIdStartStr = line.split('Change-Id: ')[1].strip()
                row['changeId'] = changeIdStartStr.split('\n')[0].strip()
                changeIdSet = True
                break
        if not changeIdSet:
            row['changeId'] = "NOT_FIND"
    else:
        row['changeId'] = "NONE"

for row in log:
    print(row['id'] + " - " + row.get('changeId'))
