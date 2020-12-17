# !/usr/bin/python
import subprocess
import sys

def git_log(str):
    GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message', 'body']
    GIT_LOG_FORMAT = ['%H', '%an', '%ae', '%ad', '%s', '%b']
    GIT_LOG_FORMAT = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e'

    print(str)
    git_command = 'git log ' + str + ' --format="%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b%x1e"'
    print(git_command)
    p = subprocess.Popen(git_command, shell=True, stdout=subprocess.PIPE)
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

    # for row in log:
    #     print(row['id'] + " - " + row.get('changeId'))
    return log

log1 = git_log(sys.argv[1])
changeId1 = []
for row in log1:
    if row.get('changeId') != 'NOT_FIND':
        changeId1.append(row.get('changeId'))

print(len(changeId1))

log2 = git_log(sys.argv[2])
changeId2 = []
for row in log2:
    if row.get('changeId') != 'NOT_FIND':
        changeId2.append(row.get('changeId'))
print(len(changeId2))

diff_list = list(set(changeId1).difference(set(changeId2)))
# print (diff_list)

print("                               commit id" + " - " + "changeId                        ")
for diff in diff_list:
    for row in log1:
        if row.get('changeId') == diff:
            print(row['id'] + " - " + row['changeId'])