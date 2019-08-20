from datetime import datetime
import subprocess
from subprocess import PIPE
import shlex
import sys
import os
import logging
from datetime import datetime
from time import sleep
from importlib import util

from mail import send_mail, create_email_contents


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


ACTIVATE_VENV = '. /home/cwtests/.virtualenvs/tests/bin/activate'
ACTIVATE_VENV_PYTHON = '/home/cwtests/.virtualenvs/tests/bin/activate_this.py'


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
    jupyter_dir = os.path.join(cw_dir, 'jupyter')
    jupyter_test_dir = os.path.join(jupyter_dir, 'tests')
    test_script = os.path.join(jupyter_test_dir, 'tutorials.py')

    # wipe virtual environment
    cmd = '{} && pip freeze | xargs pip uninstall -y'.format(ACTIVATE_VENV)
    out1, err1 = execute_command(cmd, cw_dir, shell=True)

    install_cw = '{} && python -m pip install .'.format(ACTIVATE_VENV)
    out2, err2 = execute_command(install_cw, cw_dir, shell=True)

    install_jupyter = '{} && python -m pip install -r requirements.txt'.format(ACTIVATE_VENV)
    out3, err3 = execute_command(install_jupyter, jupyter_dir, shell=True)

    # activate virtualenvironment
    with open(ACTIVATE_VENV_PYTHON, 'r') as f:
        exec(f.read(), dict(__file__=ACTIVATE_VENV_PYTHON))

    # make sure the tutorials.run_tests function is available
    spec = util.spec_from_file_location("tutorials", os.path.join(jupyter_test_dir, 'tutorials.py'))
    tutorials = util.module_from_spec(spec)
    spec.loader.exec_module(tutorials)

    summary, tests = eval('tutorials.run_tests("tutorials.yaml")', {'run_tests': run_tests, '__name__': '__main__'})

    tests[cmd] = 'Stdout:\n{}\nStderr:{}\n'.format(out1, err1)
    tests[install_cw] = 'Stdout:\n{}\nStderr:{}\n'.format(out2, err2)
    tests[install_jupyter] = 'Stdout:\n{}\nStderr:{}\n'.format(out3, err3)

    return summary, tests


def server_time():
    time, err = execute_command('date +"%A, %b %d, %Y %H:%M:%S %Z"', '/')
    return time


def local_time():
    return datetime.now()


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
        summary = None
        tests = None
        if self.should_check_repo():
            # check for update from remote
            changes_pulled = update_from_remote(self.cw_dir)
            commit = checked_out_commit(self.cw_dir)
            if changes_pulled:
                # run the tests on newest changes
                logging.info('running tests at {}'.format(local_time()))
                self.last_test_start_time = local_time()
                self.last_test_time_pretty = server_time()
                summary, tests = run_tests(cw_dir, self.config_file)
                self.hours_tested_today.append(self.last_test_start_time.day)
        else:
            pass

        if self.last_test_start_time:
            day_finished = local_time().day
            day_started = self.last_test_start_time.day
            if day_finished > day_started:
                self.hours_tested_today = list()

        if summary and tests:
            return self.last_test_time_pretty, commit, summary, tests
        else:
            return None


def create_summaries(summary, tests):
    summaries = []
    title = ''

    for key, value in summary:
        failed = value['failed']
        run = value['run']
        passed = run - failed

        if key == 'all':
            title = '{} Failed, {} Passed, {} Run'.format(failed, passed, run)
        else:
            summaries.append('{}: {} Failed, {} Passed, {} Run'.format(key, failed, passed, run))

    return title, summaries, tests


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
            time, commit, summary, tests = test_results
            title, summaries, tests = create_summaries(summary, tests)

            jinja_context = {
                'title': title,
                'tests': tests,
                'summaries': summaries,
            }

            email_contents = create_email_contents(jinja_context)
            subject = 'ChipWhisperer Test Results {}'.format(time)
            send_mail(from_email, to_emails, subject, email_contents)
        sleep(100)


if __name__ == '__main__':
    logging.info('server time is {}'.format(server_time()))
    script, cw_dir, config_file = sys.argv
    main(cw_dir, config_file)
