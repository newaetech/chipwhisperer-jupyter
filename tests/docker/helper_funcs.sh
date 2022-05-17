#!/bin/bash
# requires bash

build_test () {
        cd ~/chipwhisperer/jupyter/tests/docker
        docker build . -t cw-testing-server
        cd -
}

run_test () {
	local POSITIONAL_ARGS=()
	local RUN_HOURS
	local CHECK_GIT
	local SENDGRID_KEY
	local FROM_EMAIL
	local TO_EMAILS
	local CLEAR_RESULTS
	local USAGE="Usage: run_test [-h|--help] [-H|--hours hours] [--emails sendgrid_api_key from_email to_emails] [--no-check-git] [--no-clear]"

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

				SENDGRID_KEY=${EMAIL_ARGS[0]}
				FROM_EMAIL=${EMAIL_ARGS[1]}
				unset 'EMAIL_ARGS[0]'
				unset 'EMAIL_ARGS[1]'

				TO_EMAILS=${EMAIL_ARGS[@]}
				;;
			--no-check-git)
				CHECK_GIT="NO"
				shift
				;;
			--no-clear)
				CLEAR_RESULTS="YES"
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
		RUN_HOURS="always"
	fi

	if [ -z $CHECK_GIT ]; then
		#echo "Check git"
		CHECK_GIT="YES"
	fi

	#echo "RUN_HOURS=$RUN_HOURS"
	#echo "CHECK_GIT=$CHECK_GIT"

	docker system prune -f
	if [ -n $CLEAR_RESULTS ]; then
		rm -rf ~/results/*
	fi

	CURRENT_TEST_ID=$(docker run -d --privileged \
	    -v /dev:/dev \
	    -v $HOME/tutorials/:/home/cwtests/chipwhisperer/tutorials \
	    -v $HOME/results/:/home/cwtests/results \
	    -e TO_EMAILS="$TO_EMAILS" \
	    -e FROM_EMAIL="$FROM_EMAIL" \
	    -e SENDGRID_API_KEY="$SENDGRID_KEY" \
	    -e HOURS="$RUN_HOURS" \
	    -e CHECK_GIT="$CHECK_GIT" \
	    cw-testing-server)
	export CURRENT_TEST_ID
	echo $CURRENT_TEST_ID

    #-e HOURS="6, 10, 14, 18, 21, 22, 23" \
}

kill_test() {
	docker kill $CURRENT_TEST_ID
}

set_jupyter_ssh () {
	cd ~/chipwhisperer/jupyter/
	git remote set-url origin git@github.com:newaetech/chipwhisperer-jupyter.git
	cd -

}

set_jupyter_git() {
	cd ~/chipwhisperer/jupyter/
	git remote set-url origin https://github.com/newaetech/chipwhisperer-jupyter.git
	cd -
}

attach_test () {
	docker exec -it $CURRENT_TEST_ID /bin/bash
}

log_test () {
	docker logs $CURRENT_TEST_ID
}

list_chipwhisperers () {
	lsusb -v -d 2b3e: 2> /dev/null | egrep "(iSerial)|(idProduct)"
}

alias ccat='clear; cat'

monitor_log () {
	while [ 1 ]; do ccat $1; docker ps; sleep 1; done
}

monitor_summary() {
	monitor_log sum_test.log
}

monitor_finished() {
	while [ 1 ]; do ccat sum_test.log | grep "Finished all tests"; docker ps; sleep 1; done
}
if [ -z $CURRENT_TEST_ID ]; then
	CURRENT_TEST_ID=$(docker ps -q)
	export CURRENT_TEST_ID
fi

go_docker() {
	cd ~/chipwhisperer/jupyter/tests/docker
}

go_results() {
	cd ~/results
}