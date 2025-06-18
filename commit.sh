#!/bin/bash

OLD_EMAIL="adityasinghw84it@gmail.com"
CORRECT_NAME="Aditya Singh"
CORRECT_EMAIL="aditya.s@tsquaredc.com"

git filter-branch --env-filter '
if [ "$GIT_COMMITTER_EMAIL" = "'"$OLD_EMAIL"'" ]
then
    export GIT_COMMITTER_NAME="'"$CORRECT_NAME"'"
    export GIT_COMMITTER_EMAIL="'"$CORRECT_EMAIL"'"
fi
if [ "$GIT_AUTHOR_EMAIL" = "'"$OLD_EMAIL"'" ]
then
    export GIT_AUTHOR_NAME="'"$CORRECT_NAME"'"
    export GIT_AUTHOR_EMAIL="'"$CORRECT_EMAIL"'"
fi
' --tag-name-filter cat -- --branches --tags
