# !/usr/bin/python
import subprocess
import sys

COMMIT_BODY = 'body'
COMMIT_ID = 'id'
COMMIT_AUTHOR_NAME = 'author_name'
COMMIT_AUTHOR_EMAIL = 'author_email'
COMMIT_DATE = 'date'
COMMIT_MESSAGE = 'message'
COMMIT_CHANGE_ID = 'change_id'


def git_log(branch_name):
    git_commit_fields = [COMMIT_ID, COMMIT_AUTHOR_NAME, COMMIT_AUTHOR_EMAIL, COMMIT_DATE, COMMIT_MESSAGE, COMMIT_BODY]
    git_log_command = 'git --no-pager log ' + branch_name + ' --format="%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b%x1e"'
    print(git_log_command)
    p = subprocess.Popen(git_log_command, shell=True, stdout=subprocess.PIPE)
    (logs, _) = p.communicate()
    logs = logs.decode(encoding='UTF-8')
    logs = logs.strip('\x1e').split("\x1e")
    logs = [log_str.strip().split("\x1f") for log_str in logs]
    logs = [dict(zip(git_commit_fields, log_str)) for log_str in logs]

    for one_log in logs:
        if one_log.setdefault(COMMIT_BODY, "NONE").find("\n"):
            change_id_set = False
            for line in one_log[COMMIT_BODY].split("\n"):
                if line.find('Change-Id:') != -1:
                    change_id_start_str = line.split('Change-Id: ')[1].strip()
                    one_log[COMMIT_CHANGE_ID] = change_id_start_str.split('\n')[0].strip()
                    change_id_set = True
                    break
            if not change_id_set:
                one_log[COMMIT_CHANGE_ID] = "NOT_FIND"
        else:
            one_log[COMMIT_CHANGE_ID] = "NONE"

    # for row in log:
    #     print(row[COMMIT_ID] + " - " + row.get(COMMIT_CHANGE_ID))
    return logs


log1 = git_log(sys.argv[1])
changeId1 = []
for row in log1:
    if row.get(COMMIT_CHANGE_ID) != 'NOT_FIND':
        changeId1.append(row.get(COMMIT_CHANGE_ID))

log2 = git_log(sys.argv[2])
changeId2 = []
for row in log2:
    if row.get(COMMIT_CHANGE_ID) != 'NOT_FIND':
        changeId2.append(row.get(COMMIT_CHANGE_ID))
print(len(changeId2))

diff_list = list(set(changeId1).difference(set(changeId2)))
# print (diff_list)

print("                               commit id" + " - " + "changeId                        ")
for diff in diff_list:
    for row in log1:
        if row.get(COMMIT_CHANGE_ID) == diff:
            print(row[COMMIT_ID] + " - " + row[COMMIT_CHANGE_ID])
