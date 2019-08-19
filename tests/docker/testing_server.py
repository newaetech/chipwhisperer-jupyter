from datetime import datetime
import subprocess
from subprocess import PIPE
import shlex
import sys
import os
import logging
from datetime import datetime
from time import sleep

from mail import send_mail


# fix logging inside docker container
root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)

# check for debuging
debug = os.environ.get('DEBUG')
if debug:
    root.setLevel(logging.DEBUG)
else:
    root.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def execute_command(command, directory, shell=False):
    logging.debug('executing "{}" in "{}" with shell={}'.format(command, directory, shell))
    if shell:
        process = subprocess.Popen(command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            cwd=directory,
            shell=True)
    else:
        commands = shlex.split(command)
        process = subprocess.Popen(commands,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            cwd=directory)

    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode('utf-8').strip(), stderr.decode('utf-8').strip()

    if stdout:
        logging.debug('stdout: \n"{}"'.format(stdout))
    if stderr:
        logging.error('stderr: \n"{}"'.format(stderr))

    return stdout, stderr


def update_from_remote(directory):
    updated = False
    out, err = execute_command('git pull --rebase', directory)

    # check if there was any updates to remote repository
    if 'Already up to date.' not in out:
        updated = True

    # Always update the jupyter submodule
    out, err = execute_command('git submodule update --init jupyter', directory)

    if updated:
        logging.info('pulled new changes to repository')
    else:
        logging.info('repository already up to date')

    return updated


def checked_out_commit(directory):
    command = 'git rev-parse $(git branch | grep \* | cut -d " " -f2)'
    checked_out_hash, err = execute_command(command, directory, shell=True)
    return checked_out_hash


def run_tests(cw_dir, config_file):
    jupyter_test_dir = os.path.join(cw_dir, 'jupyter', 'tests')
    test_script = os.path.join(jupyter_test_dir, 'tutorials.py')
    out1, err1 = execute_command('python3 -m pip install .', cw_dir)
    out2, err2 = execute_command('python3 -m pip install -r requirements.txt', jupyter_test_dir)
    out3, err3 = execute_command('python3 {} {}'.format(test_script, config_file), jupyter_test_dir)
    return '\n\n'.join([out1, out2, out3]), '\n\n'.join([err1, err2, err3])


def server_time():
    time, err = execute_command('date +"%A, %b %d, %Y %H:%M:%S %Z"', '/')
    return time


def local_time():
    return datetime.now()


def create_email_contents(date, commit, test_output):
    contents = '{}\n\nChecked out commit {}\n\n{}'.format(date, commit, test_output)
    return contents


class Tester:

    def __init__(self, chipwhisperer_dir, config_file, testing_hours=(6, 10, 14, 18)):
        self.hours_tested_today = list()
        self.testing_hours = testing_hours
        self.last_test_start_time = None
        self.cw_dir = chipwhisperer_dir
        self.config_file = config_file

    def should_check_repo(self):
        h = local_time().hour
        if h in self.testing_hours and h not in self.hours_tested_today:
            return True
        else:
            return False

    def run(self):
        results = ''
        if self.should_check_repo():
            # check for update from remote
            changes_pulled = update_from_remote(self.cw_dir)
            commit = checked_out_commit(self.cw_dir)
            if changes_pulled:
                # run the tests on newest changes
                logging.info('running tests at {}'.format(local_time()))
                self.last_test_start_time = local_time()
                self.last_test_time_pretty = server_time()
                results, err = run_tests(cw_dir, self.config_file)
                self.hours_tested_today.append(self.last_test_start_time.day)
        else:
            pass

        if self.last_test_start_time:
            day_finished = local_time().day
            day_started = self.last_test_start_time.day
            if day_finished > day_started:
                self.hours_tested_today = list()

        if results:
            return self.last_test_time_pretty, commit, results, err
        else:
            return None


def main(chipwhisperer_dir, config_file):
    required_env_variables = [
        'TO_EMAILS',
        'FROM_EMAIL',
        'SENDGRID_API_KEY',
        'HOURS',
    ]

    env_vars = os.environ.keys()

    env_var_exists = [var in env_vars for var in required_env_variables]

    if not all(env_var_exists):
        logging.error('not all required environment variables were given: {}'.format(required_env_variables))
        sys.exit()

    # process the environmental variables
    # some come in as command seperated lists
    to_emails_env = os.environ.get('TO_EMAILS')
    to_emails = [email.strip() for email in to_emails_env.strip().split(',') if email.strip()]
    from_email = os.environ.get('FROM_EMAIL').strip()
    hours_env = os.environ.get('HOURS')
    hours = [int(h.strip()) for h in hours_env.strip().split(',') if h.strip()]

    tester = Tester(chipwhisperer_dir, config_file, hours)

    while True:
        test_results = tester.run()
        if test_results:
            time, commit, out, err = test_results
            email_contents = create_email_contents(time, commit, out)
            subject = 'ChipWhisperer Test Results {}'.format(time)
            send_mail(from_email, to_emails, subject, email_contents)
        sleep(100)


if __name__ == '__main__':
    logging.info('server time is {}'.format(server_time()))
    script, cw_dir, config_file = sys.argv
    main(cw_dir, config_file)
