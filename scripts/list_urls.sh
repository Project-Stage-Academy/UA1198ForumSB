#!/bin/bash

RED="\e[31m"
CYAN="\033[0;36m"
ENDCOLOR="\e[0m"

PYTHON=`which python`

pip show django-extensions &> /dev/null

if [[ "$?" != 0 ]]; then
    echo -e "${RED}[error] django-extensions is not installed${ENDCOLOR}"

    echo -e "${CYAN}[info] installing django-extensions${ENDCOLOR}"
    pip install django-extensions
fi

cd forum && $PYTHON manage.py shell -c 'from django.core.management import call_command; from django_extensions.management.commands.show_urls import Command; call_command(Command())'
