#!/bin/bash

if [ -z "$(git branch -al "$1")" ]
then
   echo "Branch name: $1 not exists."
   exit
fi

if [ -z "$(git branch -al "$2")" ]
then
   echo "Branch name: $2 not exists."
   exit
fi

parojet_path=$(pwd)
#echo "${parojet_path}"

git --no-pager log "$1"| grep "Change-Id:" | cut -d ' ' -f 6 > "${parojet_path}"/"$1".gitlog
git --no-pager log "$2"| grep "Change-Id:" | cut -d ' ' -f 6 > "${parojet_path}"/"$2".gitlog
echo "|=========================================================|"
echo "| diff  branch  $1..$2"
echo "| <:  $1  -YES" " $2  -NO"
echo "| >:  $1  -NO"  " $2  -YES"
echo "|=========================================================|"
diff "${parojet_path}"/"$1".gitlog "${parojet_path}"/"$2".gitlog
rm -f "${parojet_path}"/"$1".gitlog "${parojet_path}"/"$2".gitlog