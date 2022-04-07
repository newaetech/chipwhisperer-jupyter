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
import usb1
from pathlib import Path

#from mail import send_mail, create_email_contents

std_hanlder = logging.StreamHandler(sys.stdout)

nb_handler = logging.FileHandler("results/nb.log")
nb_logger = logging.getLogger("notebooks")
nb_logger.setLevel(logging.DEBUG)
nb_logger.addHandler(nb_handler)
nb_logger.addHandler(std_hanlder)

cmd_handler = logging.FileHandler("results/cmd.log")
cmd_logger = logging.getLogger("commands")
cmd_logger.setLevel(logging.DEBUG)
cmd_logger.addHandler(cmd_handler)
cmd_logger.addHandler(std_hanlder)

run_handler = logging.FileHandler("results/run.log")
run_logger = logging.getLogger("runtime")
run_logger.setLevel(logging.DEBUG)
run_logger.addHandler(run_handler)
run_logger.addHandler(std_hanlder)

# os.environ.setdefault

# fix logging inside docker container
logging.basicConfig(filename="results/log.txt", encoding='utf-8', level=logging.DEBUG)
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
    cmd_logger.debug('executing "{}" in "{}" with shell={}'.format(command, directory, shell))
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
        cmd_logger.debug('stdout: \n"{}"\n'.format(stdout))
    if stderr:
        cmd_logger.error('stderr: \n"{}"\n'.format(stderr))

    return stdout, stderr


def update_from_remote(directory):
    updated = False
    out, err = execute_command('git pull --rebase', directory)

    # check if there was any updates to remote repository
    if os.environ.get('CHECK_GIT') == "NO":
        updated = True
        run_logger.debug('\nskipping git check\n')
    elif 'Already up to date.' not in out:
        run_logger.debug('\ngit not up to date, running test. out: {}\n'.format(out))
        updated = True


    # Always update the jupyter submodule
    out, err = execute_command('git submodule update --init jupyter', directory)

    if updated:
        run_logger.info('pulled new changes to repository')
    else:
        run_logger.info('repository already up to date')

    return updated


def checked_out_commit(directory):
    command = 'git rev-parse $(git branch | grep \* | cut -d " " -f2)'
    checked_out_hash, err = execute_command(command, directory, shell=True)
    return checked_out_hash


def run_tests(cw_dir, config_file):
    jupyter_dir = os.path.join(cw_dir, 'jupyter')
    jupyter_test_dir = os.path.join(jupyter_dir, 'tests')
    test_script = os.path.join(jupyter_test_dir, 'tutorials.py')

    # # wipe virtual environment
    cmd = '{} && pip freeze | xargs pip uninstall -y'.format(ACTIVATE_VENV)
    # out1, err1 = execute_command(cmd, cw_dir, shell=True)

    install_cw = '{} && python -m pip install .'.format(ACTIVATE_VENV)
    # out2, err2 = execute_command(install_cw, cw_dir, shell=True)

    install_jupyter = '{} && python -m pip install -r requirements.txt'.format(ACTIVATE_VENV)
    # out3, err3 = execute_command(install_jupyter, jupyter_dir, shell=True)

    # # activate virtualenvironment
    # with open(ACTIVATE_VENV_PYTHON, 'r') as f:
    #     exec(f.read(), dict(__file__=ACTIVATE_VENV_PYTHON))

    # make sure the tutorials.run_tests function is available
    path = os.path.join(jupyter_test_dir, 'tutorials.py')
    spec = util.spec_from_file_location("tutorials", os.path.join(jupyter_test_dir, path))
    tutorials = util.module_from_spec(spec)
    spec.loader.exec_module(tutorials)

    cur_date = local_time()
    cur_date_formatted = '{}-{}-{}:{}'.format(cur_date.year, 
        cur_date.month, cur_date.day, cur_date.hour)
    result_path = Path(os.getcwd(), "results", cur_date_formatted)

    result_path.mkdir(0o777, exist_ok=True)
    os.chmod(str(result_path), 0o777) ## need to do this for some reason to get correct permissions
    #result_path = Path(os.getcwd(), "results")

    if not config_file:
        config_path = os.path.abspath(os.path.join(cw_dir, '..', 'tests.yaml'))
    else:
        config_path = config_file

    cwd = os.getcwd()
    os.chdir(jupyter_test_dir)
    sys.modules['tutorials'] = tutorials
    summary, tests = eval('tutorials.run_tests("{}", "{}", "{}")'.format(cw_dir, config_path, result_path), {'tutorials': tutorials, '__name__': '__main__'})
    os.chdir(cwd)

    #tests[cmd] = 'Stdout:\n{}\nStderr:{}\n'.format(out1, err1)
    #tests[install_cw] = 'Stdout:\n{}\nStderr:{}\n'.format(out2, err2)
    #tests[install_jupyter] = 'Stdout:\n{}\nStderr:{}\n'.format(out3, err3)

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
        #return True
        if (self.testing_hours == "always") or (self.testing_hours == "once"):
            run_logger.info("Skipping hour check")
            return True
        h = local_time().hour
        if h in self.testing_hours and h not in self.hours_tested_today:
            run_logger.info("Hour check fine, can run test: {} in {}".format(h, self.testing_hours))
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
                run_logger.info('running tests at {}'.format(local_time()))
                #reset_usb()
                self.last_test_start_time = local_time()
                self.last_test_time_pretty = server_time()
                summary, tests = run_tests(cw_dir, self.config_file)
                if self.testing_hours == "once":
                    sys.exit()
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

    for key, value in summary.items():
        failed = value['failed']
        run = value['run']
        passed = run - failed

        if key == 'all':
            title = '{} Failed, {} Passed, {} Run'.format(failed, passed, run)
        else:
            summaries.append('{}: {} Failed, {} Passed, {} Run'.format(key, failed, passed, run))

    return title, summaries, tests


def sort_by_failed(tests):
    failed = {}
    passed = {}
    build = {}
    for key in tests.keys():
        if key.startswith('PASSED'):
            passed[key] = tests[key]
        elif key.startswith('FAILED'):
            failed[key] = tests[key]
        else:
            build[key] = tests[key]
    result = {}
    result.update(failed)
    result.update(passed)
    result.update(build)
    return result


def main(chipwhisperer_dir, config_file):
    #   required_env_variables = [
    #       'TO_EMAILS',
    #       'FROM_EMAIL',
    #       'SENDGRID_API_KEY',
    #       'HOURS',
    #   ]

    #   env_vars = os.environ.keys()

    #   env_var_exists = [var in env_vars for var in required_env_variables]

    #   if not all(env_var_exists):
    #       logging.error('not all required environment variables were given: {}'.format(required_env_variables))
    #       sys.exit()

    # process the environmental variables
    # some come in as command seperated lists
    #   to_emails_env = os.environ.get('TO_EMAILS')
    #   to_emails = [email.strip() for email in to_emails_env.strip().split(',') if email.strip()]
    #   from_email = os.environ.get('FROM_EMAIL').strip()
    hours_env = os.environ.get('HOURS')
    if (hours_env == "always") or (hours_env == "once"):
        hours = hours_env
    else:
        hours = [int(h.strip()) for h in hours_env.strip().split(',') if h.strip()]

    run_logger.info("Running test server with Hours = {}".format(hours))

    tester = Tester(chipwhisperer_dir, config_file, hours)

    while True:
        test_results = tester.run()
        if test_results:
            time, commit, summary, tests = test_results
            title, summaries, tests = create_summaries(summary, tests)

            tests = sort_by_failed(tests)

            jinja_context = {
                'title': title,
                'commit': commit,
                'summaries': summaries,
                'tests': tests,
            }
            HOME = os.environ.get('HOME')
            with open(HOME + "/results/results.txt", "w", encoding='utf-8') as f:
                for k in jinja_context:
                    if k == 'tests':
                        f.write('tests:')
                        for ktest in jinja_context[k]:
                            f.write('     {}'.format(ktest))
                    else:
                        f.write('{}: {}'.format(k, jinja_context[k]))
                f.write(str(jinja_context))

            #email_contents = create_email_contents(jinja_context)
            subject = 'ChipWhisperer Test Results {}'.format(time)
            #send_mail(from_email, to_emails, subject, email_contents)
        sleep(100)


def reset_usb():
    ## linux only
    with usb1.USBContext() as ctx:
        cw_list = [dev for dev in ctx.getDeviceIterator() if dev.getVendorID() == 0x2b3e]
        for dev in cw_list:
            subprocess.run(["./usbreset", "/dev/bus/usb/{:03d}/{:03d}".format(dev.getBusNumber(), \
                dev.getDeviceAddress())])

    sleep(5)

if __name__ == '__main__':
    run_logger.info('server time is {}'.format(server_time()))
    script, cw_dir, config_file = sys.argv
    main(cw_dir, config_file)
