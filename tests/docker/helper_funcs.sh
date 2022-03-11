#!/bin/bash
# requires bash

# builds docker test image
build_test () {
cd ~/chipwhisperer/jupyter/tests/docker
docker build . -t cw-testing-server
cd -
}

# runs docker test image with a bunch of command line args
run_test () {
        local POSITIONAL_ARGS=()
        local RUN_HOURS
        local CHECK_GIT
        local SENDGRID_KEY
        local FROM_EMAIL
        local TO_EMAILS
        local USAGE="Usage: run_test [-h|--help] [-H|--hours hours] [--emails sendgrid_api_key from_email to_emails] [--no-check-git]"

        while [[ $# -gt 0 ]]; do
                case $1 in
                        -h|--help)
                                echo $USAGE
                                return
                                ;;
                        -H|--hours)
                                RUN_HOURS="$2"
                                shift
                                shift
                                ;;
                        --emails)
                                local EMAIL_ARGS=()
                                shift
                                while [[ "$1" != "-"* && "$1" != "" ]]; do
                                        EMAIL_ARGS+=("$1")
                                        shift
                                done

                                if [[ ${#EMAIL_ARGS} -lt 3 ]]; then
                                        echo "Missing args for --emails"
                                        echo "$USAGE"
                                        return 1
                                fi

                                SENDGRID_KEY="${EMAIL_ARGS[0]}"
                                FROM_EMAIL="${EMAIL_ARGS[1]}"
                                unset 'EMAIL_ARGS[0]'
                                unset 'EMAIL_ARGS[1]'

                                TO_EMAILS="${EMAIL_ARGS[@]}"
                                ;;
                        --no-check-git)
                                CHECK_GIT="NO"
                                shift
                                shift
                                ;;
                        -*|--*)
                                echo "Unknown option $1"
                                return 1
                                ;;
                        *)
                                POSITIONAL_ARGS+=("$1")
                                shift
                                ;;
                esac
        done

        #echo "$SENDGRID_KEY"
        #echo "$FROM_EMAIL"
        #echo "$TO_EMAILS"

        if [ -z $RUN_HOURS ]; then
                #echo "Default run hours"
                RUN_HOURS="4, 8, 12, 16, 20"
        fi

        if [ -z $CHECK_GIT ]; then
                #echo "Check git"
                CHECK_GIT="YES"
        fi

        #echo "RUN_HOURS=$RUN_HOURS"
        #echo "CHECK_GIT=$CHECK_GIT"

    docker system prune -f
    rm -rf ~/results/*
    docker run -d --privileged \
        -v /dev:/dev \
        -v $HOME/tutorials/:/home/cwtests/chipwhisperer/tutorials \
        -v $HOME/results/:/home/cwtests/results \
        -e TO_EMAILS="$TO_EMAILS" \
        -e FROM_EMAIL="$FROM_EMAIL" \
        -e SENDGRID_API_KEY="$SENDGRID_KEY" \
        -e HOURS="$RUN_HOURS" \
        -e CHECK_GIT="$CHECK_GIT" \
        cw-testing-server
}

# attach to test image
attach_test () {
        docker exec -it $1 /bin/bash
}