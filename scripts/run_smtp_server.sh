#!/bin/bash

RED="\e[31m"
CYAN="\033[0;36m"
ENDCOLOR="\e[0m"

PYTHON=`which python`

pip show aiosmtpd &> /dev/null

if [[ "$?" != 0 ]]; then
    echo -e "${RED}[error] aiosmtpd is not installed${ENDCOLOR}"

    echo -e "${CYAN}[info] installing aiosmtpd${ENDCOLOR}"
    pip install aiosmtpd
fi

source `find ./ -name .env -type f | head -1`

echo -e "\n${CYAN}Starting aiosmtpd on $FORUM_EMAIL_HOST:$FORUM_EMAIL_PORT ${ENDCOLOR}"
$PYTHON -m aiosmtpd -n -l $FORUM_EMAIL_HOST:$FORUM_EMAIL_PORT
