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


def _red_log(msg):
    return _color_log('31', msg)


def _green_log(msg):
    return _color_log('32', msg)


def _yellow_log(msg):
    return _color_log('33', msg)


def _color_log(color, msg):
    return "\033[0;%sm%s\033[0m" % (color, msg)


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


def git_log_with_diff_change_ids(branch):
    git_logs = git_log(branch)
    diff_change_ids = []
    for row in git_logs:
        if row.get(COMMIT_CHANGE_ID) != 'NOT_FIND':
            diff_change_ids.append(row.get(COMMIT_CHANGE_ID))
    return git_logs, diff_change_ids


(branch1_git_logs, br1_change_ids) = git_log_with_diff_change_ids(sys.argv[1])

(branch2_git_logs, br2_change_ids) = git_log_with_diff_change_ids(sys.argv[2])

print("branch " + _yellow_log(sys.argv[1]) + " have " + str(
    len(branch1_git_logs)) + " commits, " + "branch " + _yellow_log(
    sys.argv[2]) + " have " + str(len(branch2_git_logs)) + " commits.")


def _print_diff_patch(git_logs, change_id_list):
    for change_id in change_id_list:
        for log in git_logs:
            if log.get(COMMIT_CHANGE_ID) == change_id:
                print(_yellow_log(log[COMMIT_ID]) + "  " + log[COMMIT_DATE] + "  " + log[COMMIT_AUTHOR_EMAIL] + "\t " +
                      log[COMMIT_MESSAGE])


def print_diff(branch1, br1_git_logs, br1_change_ids, branch2, br2_git_logs, br2_change_ids):
    # IN br1_git_logs, BUT NOT IN br2_change_ids
    diff_change_ids = list(set(br1_change_ids).difference(set(br2_change_ids)))
    # resort by br1_change_ids
    diff_change_ids.sort(key=br1_change_ids.index)
    diff_len = len(diff_change_ids)
    if diff_len == 0:
        print(_green_log('All patches in branch ') + _yellow_log(branch1) + _green_log(
            ' are already in branch ') + _yellow_log(branch2))
    else:
        there_ = "there is " if (diff_len == 1) else "there are "
        patch_ = " patch that belong " if (diff_len == 1) else " patches that belong "
        not_ = " is NOT in " if (diff_len == 1) else " are NOT in "
        print(_red_log(there_) + str(diff_len) + _red_log(patch_)
              + _yellow_log(branch1) + _red_log(not_) + _yellow_log(branch2))
        _print_diff_patch(br1_git_logs, diff_change_ids)


print_diff(sys.argv[1], branch1_git_logs, br1_change_ids, sys.argv[2], branch2_git_logs, br2_change_ids)

print_diff(sys.argv[2], branch2_git_logs, br2_change_ids, sys.argv[1], branch1_git_logs, br1_change_ids)
