import shutil
import os
from glob import glob
from pathlib import Path
from os import listdir
from os.path import isfile
import yaml
import re
import sys
import logging
import time
import chipwhisperer as cw
from datetime import datetime

import nbformat
import nbconvert
from nbconvert.preprocessors import ClearOutputPreprocessor
from nbconvert.exporters import NotebookExporter
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import RSTExporter, HTMLExporter
from nbparameterise import extract_parameters, parameter_values, replace_definitions, Parameter
from nbconvert.nbconvertapp import NbConvertBase
test_logger = logging.getLogger("ChipWhisperer Test")
test_logger.setLevel(logging.DEBUG)

script_path = os.path.abspath(__file__)
tests_dir, _ = os.path.split(script_path)
# set configuration options
RSTExporter.template_paths = ['.', tests_dir]
RSTExporter.extra_template_basedirs = [tests_dir, tests_dir+'/rst_extended']
RSTExporter.template_file = 'rst_extended.tpl'

# generate logger name from hw config id and short name
# make it so all the names line up and have the same length
def sname_to_log_name(hw_dict):
    sname:str = hw_dict['short name']
    if len(sname) < 11:
        sname = "_"*(11-len(sname)) + sname
    sname = "({})_".format(hw_dict['id']) + sname
    return sname

output = []

# helper functions for printing results/errors from notebook
def _get_outputs(nb):
    return [[i, cell] for i, cell in enumerate(nb.cells) if "outputs" in cell]

def _print_stderr(nb, logger=None):
    outputs = _get_outputs(nb)
    if logger is None:
        logger = test_logger
    printed_output = [[cell[0], output] for cell in outputs for output in cell[1]['outputs'] if
                      ('name' in output and output['name'] == 'stderr')]
    for out in printed_output:
        logger.warning("[{}]:\n{}".format(out[0], out[1]['text']))

def _print_stdout(nb, logger=None):
    if logger is None:
        logger = test_logger
    outputs = _get_outputs(nb)
    printed_output = [[cell[0], output] for cell in outputs for output in cell[1]['outputs'] if
                      ('name' in output and output['name'] == 'stdout')]
    for out in printed_output:
        logger.info("[{}]:\n{}".format(out[0], out[1]['text']))

def _print_tracebacks(errors, logger = None, config=None):
    # to escape ANSI sequences use regex
    if logger is None:
        logger = test_logger
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    if errors == []:
        logger.info("Passed all tests!")
    for error in errors:
        logger.info("Test failed in cell {}: {}: {}".format(error[0], error[1]['ename'], error[1]['evalue']))
        for lineno in range(len(error[1]['traceback'])):
            error[1]['traceback'][lineno] = ansi_escape.sub('', error[1]['traceback'][lineno])
            logger.log(60, error[1]['traceback'][lineno])


# Context manager for changing current working directory.
# with cd('/path/') as f:
#   directory specific stuff
class cd:
    """Context manager for changing current working directory.

    Args:
        path (str): The path to the directory to switch to.
    """
    def __init__(self, path):
        self.path = os.path.expanduser(path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.saved_path)

def put_all_kwargs_in_notebook(params, logger=None, **kwargs):
    if logger is None:
        logger = test_logger
    for kwarg in kwargs:
        in_params = False
        for p in params:
            if p.name == kwarg:
                in_params = True
        if in_params == False:
            logger.info(f"Inserting {kwarg}")
            params.append(Parameter(kwarg, str, kwargs[kwarg]))

# do the execution of the notebook
# also do any substiutions (scope hw location, PLATFORM, SS_VER, etc)
def execute_notebook(nb_path, serial_number=None, baud=None, hw_location=None, target_hw_location=None, allow_errors=True, SCOPETYPE='OPENADC', PLATFORM='CWLITEARM', SNAME="CWLITEARM", logger=None, **kwargs):
    """Execute a notebook via nbconvert and collect output.
       :returns (parsed nb object, execution errors)
    """
    notebook_dir, file_name = os.path.split(nb_path)
    real_path = Path(nb_path).absolute()
    if logger is None:
        logger=test_logger

    with open(real_path, encoding='utf-8') as nbfile:
        # replace variables in first block with passed in kwargs (from .yaml file)
        nb = nbformat.read(nbfile, as_version=4)

        orig_parameters = extract_parameters(nb)
        params = parameter_values(orig_parameters, SCOPETYPE=SCOPETYPE, PLATFORM=PLATFORM, **kwargs)
        kwargs['SCOPETYPE'] = SCOPETYPE
        kwargs['PLATFORM'] = PLATFORM
        put_all_kwargs_in_notebook(params, logger=logger, **kwargs)
        try:
            nb = replace_definitions(nb, params, execute=False)
        except:
            pass

        ep = ExecutePreprocessor(timeout=None, kernel_name='python3', allow_errors=allow_errors)

        # %run blocks can be run just fine through ExecutePreprocessor;
        # however, things like cw.scope() that we need to modify (to insert hw_location mostly)
        # are locked in another notebook

        # so we have to traverse the %run blocks and inline all the code
        if serial_number or baud or hw_location:
            ip = InLineCodePreprocessor(notebook_dir)
            # inline all code before doing any replacements
            nb, resources = ip.preprocess(nb, {})

        replacements = {}

        # do regex replacements for attaching specific devies
        # cw.scope() -> cw.scope(sn='<SN>')
        if serial_number:
            replacements.update({
                r'(cw|chipwhisperer)\.scope\(\)': r'\1.scope(sn=\'{}\')'.format(serial_number),
            })

        # cw.program_target(...) -> cw.program_target(..., baud=<BAUD>)
        if baud:
            replacements.update({
                r'(program_target\(.*)\)': r'\g<1>, baud={})'.format(baud)
            })

        # cw.scope() -> cw.scope(hw_location=<HW_LOCATION>)
        if hw_location:
            replacements.update({
                r'(cw|chipwhisperer)\.scope\(\)': r'\1.scope(hw_location={})'.format(hw_location),
            })

        # cw.target(...) -> cw.target(..., hw_location=<HW_LOCATION>)
        if target_hw_location:
            replacements.update({
                r'(cw|chipwhisperer)(\.target\()(.*,)(.*)(\))': r"\1\2\3\4, hw_location={}\5".format(target_hw_location)
            })

        # %matplotlib notebook won't show up in blank plots
        # so replace with %matplotlib inline for now
        replacements.update({'%matplotlib notebook' : '%matplotlib inline'})

        # complete all regex subtitutions
        if replacements:
            rp = RegexReplacePreprocessor(replacements)
            nb, resources = rp.preprocess(nb, {})

        # grab notebook resources
        if notebook_dir:
            with cd(notebook_dir):
                nb, resources = ep.preprocess(nb, {'metadata': {'path': './'}})
        else:
            nb, resources = ep.preprocess(nb, {'metadata': {'path': './'}})

        errors = [[i + 1, output] for i, cell in enumerate(nb.cells) if "outputs" in cell
                  for output in cell["outputs"] \
                  if output.output_type == "error"]

        export_kwargs = {
            'SCOPETYPE': SCOPETYPE,
            'PLATFORM': SNAME
        }

        return nb, errors, export_kwargs


# Takes a notebook node and exports it to ReST and HTML
def export_notebook(nb, nb_path, output_dir, SCOPETYPE=None, PLATFORM=None, logger=None):
    """Takes a notebook node and exports it to ReST and HTML

    Args:
        nb (notebook): The notebook returned by execute_notebook.
        nb_path (str): Path to intput notebook file. Used to generate the
            name of the output file.
        output_dir (str): The output directory for the ReST and HTML file.
        SCOPETYPE (str): Used to generate the output file name.
        PLATFORM (str): Used to generate the output file name.
    """

    if not logger:
        logger = test_logger

    # Modify name of output notebook, figure out final directory,
    # move images so that they appear in the .html, etc

    # Objective is to put final tutorials in
    # ~/chipwhisperer/tutorials/<PLATFORM>/<LAB_NAME>.html

    logger.info("Exporting {}".format(nb_path))
    # test_logger.info("Exporting {}".format(nb_path))

    # extract lab name
    notebook_dir, file_name = os.path.split(nb_path)
    lab_name, ext = os.path.splitext(file_name)

    # ~/chipwhisperer/tutorials + <PLATFORM> + lab name
    base_path = os.path.join(output_dir, PLATFORM, lab_name)
    logger.info("Base path: {}".format(base_path))

    # add rst/html extension
    rst_path = os.path.abspath(base_path + '.rst')
    html_path = os.path.abspath(base_path + '.html')

    test_logger.info("Writing to {}".format(rst_path))
    test_logger.info("Writing to {}".format(html_path))
    logger.info("Writing to {}".format(rst_path))
    logger.info("Writing to {}".format(html_path))

    # copy images to final directory for .html file
    # just do a dumb copy where we grab notebook_dir/img/*

    ebp = EscapeBacktickPreprocessor()

    # export finished notebook to RST and HTML
    rst_ready_nb, _ = ebp.preprocess(nb, {})
    logger.info("Here 1, rst_path = {}".format(rst_path))
    try:
        rst_file = open(rst_path, 'w', encoding='utf-8')
        try:
            rst_exporter = RSTExporter()
            body, res = rst_exporter.from_notebook_node(rst_ready_nb, resources=
                {'unique_key': 'img/'})
            file_names = res['outputs'].keys()

            # copy over images from notebook
            # only works with rst file
            for name in file_names:
                img_path = os.path.join(output_dir, PLATFORM, name)
                with open(img_path, 'wb') as f:
                    f.write(res['outputs'][name])
                    logger.info('writing to '+ img_path)


            rst_file.write(body)
            logger.info('Wrote to: '+ rst_path)
            test_logger.info('Wrote to: '+ rst_path)
        except Exception as e:
            test_logger.error("Exception {} when writing {}".format(str(e), rst_path))
    except Exception as e:
        test_logger.error("Exception {} when writing {}".format(str(e), rst_path))

    with open(html_path, 'w', encoding='utf-8') as html_file:
        logger.info('Wrote to: '+ html_path)
        html_exporter = HTMLExporter()

        body, res = html_exporter.from_notebook_node(nb)

        html_file.write(body)

    test_logger.info("Copying over images")
    for image_path in glob(os.path.join(notebook_dir, "img", "*")):
        _, image_name = os.path.split(image_path)
        outpath = os.path.join(output_dir, PLATFORM, "img", image_name)
        test_logger.info("Copying {} to {}".format(image_path, outpath))
        shutil.copyfile(image_path, outpath)
    test_logger.info("Done")

def test_notebook(nb_path, output_dir, serial_number=None, export=True, allow_errors=True, print_first_traceback_only=True, print_stdout=False, print_stderr=False,
                  allowable_exceptions=None, baud=None, hw_location=None, logger=None, **kwargs):
    # reset output for next test

    # TODO: clean this up
    output[:] = list() # probably just remove this
    passed = False
    if logger is None:
        logger = test_logger
    logger.info("Testing: {}:...".format(os.path.abspath(nb_path)))
    logger.info("with {}.".format(kwargs))
    if serial_number:
        logger.info('on device with serial number {}.'.format(serial_number))
    elif hw_location:
        logger.info('on device at {}'.format(hw_location))
    else:
        logger.info('No serial number specified... only bad if more than one device attached.')

    # run notebook and record runtime
    t_a = datetime.now()
    nb, errors, export_kwargs = execute_notebook(nb_path, serial_number, hw_location=hw_location, allow_errors=allow_errors, allowable_exceptions=allowable_exceptions, baud=baud, logger=logger, **kwargs)
    dt = datetime.now() - t_a

    if not errors:
        logger.info("PASSED")
        passed = True
        export_notebook(nb, nb_path, output_dir, **export_kwargs, logger=logger)
    else:
        logger.warning("FAILED:")
        passed = False
        #note: print_tracebacks changes errors, should change at some point
        if print_first_traceback_only:
            _print_tracebacks([error for i, error in enumerate(errors) if i == 0],logger=logger)
        else:
            _print_tracebacks(errors,logger=logger)
        export_notebook(nb, nb_path, output_dir, **export_kwargs, logger=logger)

    if print_stdout:
        _print_stdout(nb, logger)
    if print_stderr:
        _print_stderr(nb, logger)

    logger.info("\n")
    if errors != []:
        errors = [error[1]['traceback'] for error in errors],



    result = {
        'passed': passed,
        'errors': errors,
        'run time': '{}:{:02d}'.format(dt.seconds//60, dt.seconds % 60)
    }

    return passed, '\n'.join(output), result

# clear cell output in notebook and insert kwargs. Useful for clearing notebooks before pushing to github
def clear_notebook(path, kwargs={"SCOPETYPE": "OPENADC", "PLATFORM": "CWLITEARM", "VERSION": "HARDWARE"}):
    real_path = Path(path)
    body = ""
    with open(real_path, "r", encoding="utf-8") as nbfile:
        nb = nbformat.read(nbfile, as_version=4)

        # special case: if the top block isn't a parameter block, nbparameterise will:
        #   * error out if invalid python syntax
        #   * replace code with a parameter block (whatever we passed in with kwargs, including an empty block)
        # so if no parameters being changed, don't run nbparameterise
        if len(kwargs) > 0:
            orig_parameters = extract_parameters(nb)
            params = parameter_values(orig_parameters, **kwargs)
            new_nb = replace_definitions(nb, params, execute=False)
        else:
            new_nb = nb
        co = ClearOutputPreprocessor()

        exporter = NotebookExporter()
        node, resources = co.preprocess(new_nb, {'metadata': {'path': './'}})
        body, resources = exporter.from_notebook_node(node, resources)
    with open(real_path, "w", encoding="utf-8") as nbfile:
        nbfile.write(body)

# apply clear_notebook() to an entire directory. default_list and blacklist are regex
def clear_outputs_in_dir(dirpath, default_list=r".*\.ipynb$", blacklist=r"^Lab.*", kwargs={"SCOPETYPE": "OPENADC", "PLATFORM": "CWLITEARM", "VERSION": "HARDWARE"}):
    notebook_files = [dirpath + "/" + f for f in listdir(dirpath) if isfile(dirpath + "/" + f) and re.search(default_list, f) and not re.search(blacklist, f)]

    for file in notebook_files:
        _builtin_print("Clearing {}".format(file))
        clear_notebook(file, kwargs)

def load_configuration(path):
    """Load the yaml configuration file for the tutorials.

    Args:
        path (str): The path to the configuration file.

    Returns:
        (tuple) Length two tuple (tutorials (dict), connected_hardware (dict))
    """
    with open(path, 'r') as config_file:
        config = yaml.full_load(config_file)
    tutorials = config['tutorials']
    connected_hardware = config['connected']
    return tutorials, connected_hardware

def matching_connected_configuration(config, connected):
    """
    Args:
        config (dict): With at least keys: scope, and target.
        connected (list): List of connected hardware configurations.
            Each configuration is a dict with at least scope, and target
            as keys.

    Returns:
        tuple: (bool, dict) Whether a match was found, and second the matching attached
         configuration. Returns False and None if matching connected device was not found.
    """
    check_keys = [
        'scope',
        'target'
    ]

    for connected_config in connected:
        check = [config[key] == connected_config[key] for key in check_keys]
        if all(check):
            connected = connected_config
            return True, connected
    return False, None

# escape ` and _ since they cause issues with rst
# may not be necessary?
class EscapeBacktickPreprocessor(nbconvert.preprocessors.Preprocessor):
    def __init__(self, **kw):
        super().__init__(**kw)

    def preprocess_cell(self, cell, resources, index):
        if cell['cell_type'] == 'code':
            outputs = cell['outputs']
            for output in outputs:
                if 'name' in output:
                    output['text'] = output['text'].replace('`', '\\`')
                    output['text'] = output['text'].replace('_', '\\_')
                    #output['text'] = output['text'].replace(':', '\\:')
        return cell, resources

class RegexReplacePreprocessor(nbconvert.preprocessors.Preprocessor):
    """Preprocessor for replacing matched regex strings in nb cells

    Each regex will be used and replaced by the replacement in the repl iterable.
    Pairs of regex, and replacement strings are selected by index.

    Args:
        replacements (dict): A dictionary with regex strings as keys and replacement
            strings as values.
    Returns:
        notebook, resources: The modified notebook, and resources with all replacements applied.
    """

    def __init__(self, replacements, **kw):
        try:
            self.replacement_pairs = [(re.compile(regex), repl) for regex, repl in replacements.items()]
        except re.error as e:
            test_logger.error('One of the regex compile failed, invalid regex.')
            sys.exit(0)
        super().__init__(**kw)

    def preprocess_cell(self, cell, resources, index):
        if cell['cell_type'] == 'code':
            for p, repl in self.replacement_pairs:
                cell['source'] = re.sub(p, repl, cell['source'])
        return cell, resources

class InLineCodePreprocessor(nbconvert.preprocessors.Preprocessor):
    """Preprocessor that in lines code instead of using %run in nb.

    The %run command is not ideal for regex replacing code because
    the notebooks are external and not accesible with a preprocessor.
    This preprocessor takes any %run notebook.ipynb instance in a cell
    exports the externel notebook to python code and in lines that code
    into the cell before returning this cell.

    This preprocessor should be run before the RegexReplacePreProcessor
    so all instances in external notebooks that are now inline are also
    processed.


    TODO: This needs to handle nested run blocks and indented run blocks - DONE

    Args:
        notebook_dir (str): The path to the directory containing all the
            notebooks. Used to resolve the relative paths used by the
            %run command.

    Returns:
        notebook, resources: The modified notebook, and resources with all
            instances of the %run command in lined.
    """

    def __init__(self, notebook_dir, **kwargs):
        self.notebook_dir = notebook_dir
        super().__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        if cell['cell_type'] == 'code':
            while ('%run' in cell['source']) or ("run_line_magic('run'" in cell['source']):
                # to deal with other notebooks being called from the source notebook
                # find the notebooks and export to python code and replace
                # the current cell source code with that python code before
                # replacing instances of cw.scope()
                def regex_replace(p):
                    # external_notebooks = re.findall(p, cell['source'])

                    run_line = re.search(p, cell['source'])
                    if not run_line:
                        return
                    run_position = run_line.start()
                    num_tabs = 0
                    num_spaces = 0
                    x = cell['source']
                    while True:
                        if cell['source'][run_position-1] == '\t':
                            num_tabs += 1
                        elif cell['source'][run_position-1] == " ":
                            num_spaces += 1
                        else:
                            break

                        run_position -= 1

                    # for full_match, ext_nb in external_notebooks:
                    full_match = run_line.group()
                    ext_nb = run_line.group(2)
                    # print(run_line.group(1))
                    # print(run_line.group(2))
                    ext_nb_path = os.path.join(self.notebook_dir, ext_nb)
                    ext_nb_node = nbformat.read(ext_nb_path, as_version=4)
                    python_exporter = nbconvert.exporters.PythonExporter()
                    python_code, _ = python_exporter.from_notebook_node(ext_nb_node)
                    python_code = " " * num_spaces + "\t" * num_tabs + python_code.replace("\n", "\n{}{}".format(" " * num_spaces, "\t" * num_tabs))
                    # print(str(num_spaces), str(num_tabs))
                    cell['source'] = cell['source'].replace(full_match, '\n{}\n'.format(python_code))
                p = re.compile(r"(%run\s*[\"']?(.*\.ipynb)[\"']?)")
                regex_replace(p)
                p = re.compile(r"(get_ipython\(\)\.run_line_magic\('run'\, \'\"(.*\.ipynb)\"\'\))")
                regex_replace(p)

            p2 = re.compile(r"(get_ipython\(\)\.run_cell_magic\('bash', '.*?', '(.*?)'\))", flags=re.DOTALL)
            run_line = re.finditer(p2, cell['source'])
            # print(run_line)
            for match in run_line:
                # print(match.start())
                run_position = match.start()
                num_tabs = 0
                num_spaces = 0
                x = cell['source']
                while True:
                    if cell['source'][run_position-1] == '\t':
                        num_tabs += 1
                    elif cell['source'][run_position-1] == " ":
                        num_spaces += 1
                    else:
                        break

                    run_position -= 1

                # for full_match, ext_nb in external_notebooks:
                full_match = match.group(1)
                shell_cmd = match.group(2)
                space_tab = " " * num_spaces + "\t" * num_tabs
                a = cell['source'].replace(full_match, f'try:\n{space_tab}    {full_match}\n{space_tab}except:\n{space_tab}    x=open("/tmp/tmp.txt").read(); print(x); raise OSError(x)\n')
                a = a.replace(shell_cmd, shell_cmd + " &> /tmp/tmp.txt")
                cell['source'] = a

        return cell, resources

# function to run all notebooks for a given hardware configuration
# select hardware via hw_id (i.e. 0 runs hw configuration 0, 1 runs hw configuration 1, and so on)
def run_test_hw_config(hw_id, cw_dir, config, hw_location=None, target_hw_location=None, logger=None, output_dir=None):
    if logger is None:
        logger = test_logger

    tutorials, connected_hardware = load_configuration(config)
    summary = {'failed': 0, 'run': 0}
    hw_settings = connected_hardware[hw_id]
    if hw_settings['enabled'] is False:
        return "", {"enabled": False}, hw_id

    nb_dir = os.path.join(cw_dir, 'jupyter')
    if not output_dir:
        output_dir = os.path.join(cw_dir, 'tutorials')
    tests = {}

    for nb in tutorials.keys():
        for test_config in tutorials[nb]['configurations']:
            # if this hardware is in the notebook's hardware list
            if hw_id in test_config['ids']:

                # grab hw specific info from yaml file
                kwargs = {
                    'SCOPETYPE': hw_settings['scope'],
                    'PLATFORM': hw_settings['target'],
                    'CRYPTO_TARGET': hw_settings['firmware'],
                    'VERSION': hw_settings['tutorial type'],
                    'SS_VER': test_config['ssver'],
                    'SNAME': hw_settings['short name']

                }

                path = os.path.join(nb_dir, nb)
                nb_short = str(nb).split('/')[-1].split(' -')[0]
                hw_kwargs = hw_settings.get('kwargs')
                logger.info("HW kwargs: {}".format(hw_kwargs))
                if hw_kwargs:
                    kwargs.update(hw_kwargs)

                tutorial_kwargs = test_config.get('kwargs')
                if tutorial_kwargs:
                    kwargs.update(tutorial_kwargs)

                logger.info("\nTesting {} with {} ({})".format(nb, hw_id, kwargs))
                logger.log(60, "Running {}".format(nb_short))
                passed, output, result_dict = test_notebook(hw_location=hw_location, target_hw_location=target_hw_location, nb_path=path, output_dir=output_dir, logger=logger, **kwargs)
                if not passed:
                    summary['failed'] += 1
                summary['run'] += 1
                header = " {} {} in {} min\n".format("Passed" if passed else "Failed", nb_short, result_dict['run time'])
                logger.log(60, header)
                lab_dir, lab_file = os.path.split(nb)
                lab_name, ext = os.path.splitext(lab_file)
                logger.info("Lab name: {}".format(lab_name))
                tests[lab_name] = result_dict

            else:
                pass # we don't need to test this hardware on this tutorial
        

    time.sleep(0.5)
    logger.info("\n-----------------\nFinished test run\n-----------------\n")
    logger.log(60, "Finished all tests")
    return summary, tests, hw_id

# main function for running tests on all hardware
# runs tests for each hardware concurrently
def run_tests(cw_dir, config, results_path=None, output_dir=None):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    if not results_path:
        results_path = "./"
    
    # create the many loggers we use for tests
    results_handler = logging.FileHandler(results_path + "/testing.log")
    test_logger.addHandler(results_handler)

    # global summary file that takes output from all test loggers
    global_fmt = logging.Formatter("%(asctime)s||%(name)s||%(message)s", "%H:%M")
    global_sum_handler =  logging.FileHandler(results_path + "/sum_test.log")
    global_sum_handler.setFormatter(global_fmt)
    global_sum_handler.setLevel(60)

    test_logger.addHandler(global_sum_handler)

    # load yaml file
    tutorials, connected_hardware = load_configuration(config)

    num_hardware = len(connected_hardware)
    hw_locations = []
    target_hw_locations = []
    loggers = []

    nb_dir = os.path.join(cw_dir, 'jupyter')
    if output_dir is None:
        output_dir = os.path.join(cw_dir, 'tutorials')

    # make sure all the notebooks we have to test actually exist (catch typos)
    wrong_paths = ""
    for nb in tutorials.keys():
        path = os.path.join(nb_dir, nb)
        test_logger.info("Checking that {} in {} exists...".format(nb, nb_dir))
        if not (os.path.exists(path)):
            wrong_paths += " " + path

    if wrong_paths != "":
        raise FileNotFoundError("Incorrect paths: {}".format(wrong_paths))

    # create loggers for each test hardware
    def create_logger(i):
        # set up logging for tests

        # short name used for id
        sname = sname_to_log_name(connected_hardware[i])
        full_fmt = logging.Formatter("%(asctime)s||%(levelname)s||%(lineno)d||%(message)s", "%y-%m-%d %H:%M:%S")
        full_handle = logging.FileHandler(results_path + "/test_{}.log".format(sname))
        full_handle.setFormatter(full_fmt)
        full_handle.setLevel(logging.NOTSET)

        sum_fmt = logging.Formatter("%(asctime)s||%(message)s", "%H:%M")
        sum_handle = logging.FileHandler(results_path + "/sum_test_{}.log".format(sname))
        sum_handle.setFormatter(sum_fmt)
        sum_handle.setLevel(60)

        cur = logging.getLogger("{} Logger".format(sname))

        cur.setLevel(logging.NOTSET)
        cur.addHandler(full_handle)
        cur.addHandler(sum_handle)
        cur.addHandler(global_sum_handler)
        return cur
    
    # grab scope hw location and target hw location if needed
    # also swap to MPSSE mode if required, since doing that changes hw_location due to reenumeration
    # also update firmware if required
    def setup_HW(conf: dict, i: int):
        test_logger.info("Setting up conf {}".format(str(conf)))
        target_name = conf["short name"]
        if target_name is None and (conf.get('tutorial type') == "SIMULATED"):
            target_name = "SIMULATED"

        # make tutorial output folder
        target_folder = os.path.join(output_dir, target_name)
        test_logger.info("Making folder {}".format(target_folder))
        slocation = None
        tlocation = None

        try:
            os.mkdir(target_folder)
        except FileExistsError as e:
            pass
        except Exception as e:
            test_logger.info("Making folder {} failed err {}".format(target_folder, str(e)))

        # copy the images from input to output directory
        # keeping them in the same relative directory
        image_input_dir = os.path.join(nb_dir, 'img')
        image_output_dir = os.path.join(target_folder, 'img')

        if not os.path.isdir(image_output_dir):
            os.mkdir(image_output_dir)

        test_logger.info('Copying over image files...')
        for image_path in glob(os.path.join(image_input_dir, '*')):
            _, image_name = os.path.split(image_path)
            shutil.copyfile(image_path, os.path.join(image_output_dir, image_name))
        test_logger.info('Done')

        # get target hw_location
        if not conf.get('target serial number') is None:
            if conf['target'] == "CW305":
                target_type =  cw.targets.CW305
            elif conf['target'] == "CW310":
                target_type =  cw.targets.CW310
            else:
                raise ValueError("Invalid target type ")
            target = cw.target(None, target_type, sn=str(conf['target serial number']))

            # update firmware if new one available
            if target.latest_fw_str > target.fw_version_str:
                target.upgrade_firmware()
                time.sleep(5)
                target = cw.target(None, target_type, sn=conf['target serial number'])
                test_logger.info("Upgraded target firmware for device {}".format(i))

            tlocation = target._getNAEUSB().hw_location()
            test_logger.info("Found target device {} at {}".format(i, tlocation))
            target.dis()

        # get scope hw_location
        if not conf.get('serial number') is None:
            scope = cw.scope(force=True, sn=str(conf['serial number']))

            #update firmware if new one available
            if scope.latest_fw_str > scope.fw_version_str:
                scope.upgrade_firmware()
                time.sleep(5)
                scope = cw.scope(force=True, sn=str(conf['serial number']))
                test_logger.info("Upgraded firmware for device {}".format(i))
            else:
                test_logger.info("Device {} up to date".format(i))

            # swap to MPSSE mode if required
            if conf.get('MPSSE') is True:
                scope.enable_MPSSE()
                time.sleep(5)
                scope = cw.scope(force=True, sn=str(conf['serial number']))
                test_logger.info("Changing device {} to MPSSE mode".format(i))

            test_logger.info("MPSSE enabled = {}".format(scope._getNAEUSB().is_MPSSE_enabled()))
            slocation = scope._getNAEUSB().hw_location()
            test_logger.info("Found device {} at {}".format(i, slocation))
            scope.dis()
        return slocation, tlocation

    for i in range(num_hardware):
        loggers.append(create_logger(i))
        s, t = setup_HW(connected_hardware[i], i)
        hw_locations.append(s)
        target_hw_locations.append(t)


    # Run each on of the tutorials with each supported hardware
    # configuration for that tutorial and export the output
    # to the output directory.

    # to keep track of test name and output for email
    tests = {}

    # to keep track of number of fails/run
    summary = {}
    summary['all'] = {}
    summary['all']['failed'] = 0
    summary['all']['run'] = 0
    results = []
    test_logger.info("num hw: {}".format(num_hardware))
    results_data = {}
    with ProcessPoolExecutor(max_workers=num_hardware) as nb_pool:
        test_future = {nb_pool.submit(run_test_hw_config, i, cw_dir, config, hw_locations[i], target_hw_locations[i], loggers[i], output_dir): i for i in range(num_hardware)}
        for future in as_completed(test_future):
            hw_summary, hw_tests, hw_id = future.result()
            sname = sname_to_log_name(connected_hardware[hw_id])
            results_data[sname] = hw_tests
            # summary[str(index)]['failed'] += hw_summary['failed']
            # summary[str(index)]['run'] += hw_summary['run']

            # tests
            # tests.update(hw_tests)
    
    test_logger.log(60, "Finished all tests, writing results.yaml...")

    test_logger.info("\nResults data: {}\n".format(str(results_data)))
    # output_dir = os.path.join(cw_dir, 'tutorials')

    # write results to a yaml file
    with open(os.path.join(results_path, "results.yaml"), "w+") as f:
        test_logger.info("Writing to {}".format(results_path + 'results.yaml'))
        yaml.dump(results_data, f, default_flow_style=False)
    with open(os.path.join(output_dir, "results.yaml"), "w+") as f:
        test_logger.info("Writing to {}".format(output_dir + 'results.yaml'))
        yaml.dump(results_data, f, default_flow_style=False)
    try:
        shutil.rmtree('projects')
    except FileNotFoundError:
        pass

    return summary, tests

if __name__ == '__main__':
    script, cw_dir, config_file_path, results_path, tutorial_path = sys.argv
    run_tests(cw_dir, config_file_path, results_path, tutorial_path)
    # run_tests()

