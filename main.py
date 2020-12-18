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


def _red_log(message):
    return "\033[0;31m%s\033[0m" % message


def _green_log(message):
    return "\033[0;32m%s\033[0m" % message


def _yellow_log(message):
    return "\033[0;33m%s\033[0m" % message


def git_log(branch_name):
    git_commit_fields = [COMMIT_ID, COMMIT_AUTHOR_NAME, COMMIT_AUTHOR_EMAIL, COMMIT_DATE, COMMIT_MESSAGE, COMMIT_BODY]
    git_log_command = 'git --no-pager log ' + branch_name + ' --format="%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b%x1e"' + " --date=format:'%Y/%m/%d-%H:%M:%S'"
    # print(git_log_command)
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

print("branch " + _yellow_log(sys.argv[1]) + " have " + str(len(log1)) + " commits, " + "branch " + _yellow_log(
    sys.argv[2]) + " have " + str(len(log2)) + " commits.")

# IN changeId1, BUT NOT IN changeId2
diff_list = list(set(changeId1).difference(set(changeId2)))
# resort by git log
diff_list.sort(key=changeId1.index)
if len(diff_list) == 0:
    print(_green_log('All patches in branch ') + _yellow_log(sys.argv[1]) + _green_log(
        ' are already in branch ') + _yellow_log(sys.argv[2]))
else:
    if len(diff_list) == 1:
        print(_red_log("there is ") + str(len(diff_list)) + _red_log(" patch that belong ") + _yellow_log(
            sys.argv[1]) + _red_log(" is NOT in ") + _yellow_log(sys.argv[2]))
    else:
        print(_red_log("there are ") + str(len(diff_list)) + _red_log(" patches that belong ") + _yellow_log(
            sys.argv[1]) + _red_log(" are NOT in ") + _yellow_log(sys.argv[2]))
    for diff in diff_list:
        for row in log1:
            if row.get(COMMIT_CHANGE_ID) == diff:
                print(_yellow_log(row[COMMIT_ID]) + " " + row[COMMIT_DATE] + " " + row[COMMIT_MESSAGE])

# IN changeId2, BUT NOT IN changeId2
diff_list = list(set(changeId2).difference(set(changeId1)))
# resort by git log
diff_list.sort(key=changeId2.index)
if len(diff_list) == 0:
    print(_green_log('All patches in branch ') + _yellow_log(sys.argv[2]) + _green_log(
        ' are already in branch ') + _yellow_log(sys.argv[1]))
else:
    if len(diff_list) == 1:
        print(_red_log("there is ") + str(len(diff_list)) + _red_log(" patch that belong ") + _yellow_log(
            sys.argv[2]) + _red_log(" is NOT in ") + _yellow_log(sys.argv[1]))
    else:
        print(_red_log("there are ") + str(len(diff_list)) + _red_log(" patches that belong ") + _yellow_log(
            sys.argv[2]) + _red_log(" are NOT in ") + _yellow_log(sys.argv[1]))
    for diff in diff_list:
        for row in log2:
            if row.get(COMMIT_CHANGE_ID) == diff:
                print(_yellow_log(row[COMMIT_ID]) + " " + row[COMMIT_DATE] + " " + row[COMMIT_MESSAGE])
