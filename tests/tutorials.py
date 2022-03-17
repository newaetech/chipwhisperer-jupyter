import shutil
import os
from glob import glob
from pathlib import Path
from os import listdir
import os
from os.path import isfile, join
import yaml
import re
import sys
from pprint import pprint
import logging
import time
import chipwhisperer as cw

import nbformat
import nbconvert
from nbconvert.preprocessors import ClearOutputPreprocessor
from nbconvert.exporters import NotebookExporter
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import RSTExporter, HTMLExporter
from nbparameterise import extract_parameters, parameter_values, replace_definitions, Parameter
from nbconvert.nbconvertapp import NbConvertBase

# results_path = os.environ.get('CW_TEST_RESULT_PATH')
# if not results_path:
#     results_path = "./"

from functools import partial
import builtins

#test_handler = logging.FileHandler(results_path + "test_log.txt")
test_logger = logging.getLogger("ChipWhisperer Test")
test_logger.setLevel(logging.DEBUG)
#test_logger.addHandler(test_handler)

script_path = os.path.abspath(__file__)
tests_dir, _ = os.path.split(script_path)
# set configuration options
RSTExporter.template_paths = ['.', tests_dir]
# RSTExporter.extra_template_basedirs = [tests_dir, tests_dir+'/rst_extended']
RSTExporter.template_file = 'rst_extended.tpl'
# NbConvertBase.display_data_priority = [
#     'application/vnd.jupyter.widget-state+json',
#     'application/vnd.jupyter.widget-view+json',
#     'application/javascript',
#     'application/vnd.bokehjs_exec.v0+json',
#     'text/html',
#     'text/markdown',
#     'image/svg+xml',
#     'text/latex',
#     'image/png',
#     'image/jpeg',
#     'text/plain'
# ]


output = []

_builtin_print = print
def print(*args, **kwargs):
    """Overwrite print to allow recording of output."""
    builtins.print(*args, flush=True, **kwargs)
    output.append(' '.join(args))


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
            logger.debug(f"Inserting {kwarg}")
            params.append(Parameter(kwarg, str, kwargs[kwarg]))

def execute_notebook(nb_path, serial_number=None, baud=None, hw_location=None, allow_errors=True, SCOPETYPE='OPENADC', PLATFORM='CWLITEARM', logger=None, **kwargs):
    """Execute a notebook via nbconvert and collect output.
       :returns (parsed nb object, execution errors)
    """
    notebook_dir, file_name = os.path.split(nb_path)
    real_path = Path(nb_path).absolute()
    if logger is None:
        logger=test_logger

    with open(real_path, encoding='utf-8') as nbfile:
        nb = nbformat.read(nbfile, as_version=4)

        orig_parameters = extract_parameters(nb)
        params = parameter_values(orig_parameters, SCOPETYPE=SCOPETYPE, PLATFORM=PLATFORM, **kwargs)
        kwargs['SCOPETYPE'] = SCOPETYPE
        kwargs['PLATFORM'] = PLATFORM
        put_all_kwargs_in_notebook(params, logger=logger, **kwargs)
        nb = replace_definitions(nb, params, execute=False)

        ep = ExecutePreprocessor(timeout=None, kernel_name='python3', allow_errors=allow_errors)

        if serial_number or baud or hw_location:
            ip = InLineCodePreprocessor(notebook_dir)
            # inline all code before doing any replacements
            nb, resources = ip.preprocess(nb, {})

        replacements = {}

        if hw_location and serial_number:
            print("Make error for this later")

        if serial_number:
            replacements.update({
                r'cw.scope(\(\))': 'cw.scope(sn=\'{}\')'.format(serial_number),
                r'chipwhisperer.scope()': 'chipwhisperer.scope(sn=\'{}\')'.format(serial_number)
            })

        if baud:
            # replacements.update({
            #     r'program_target\(((?:[\w=\+/*\s]+\s*,\s*)*[\w=+/*]+)': r"program_target(\g<1>, baud=38400"
            # })
            replacements.update({
                r'(program_target\(.*)\)': r'\g<1>, baud={})'.format(baud)
            })

        if hw_location:
            replacements.update({
                r'cw.scope(\(\))': 'cw.scope(hw_location={})'.format(hw_location),
                r'chipwhisperer.scope()': 'chipwhisperer.scope(hw_location={})'.format(hw_location)
            })

        # %matplotlib notebook won't show up in blank plots
        # so replace with %matplotlib inline for now
        replacements.update({'%matplotlib notebook' : '%matplotlib inline'})

        # complete all regex subtitutions
        if replacements:
            rp = RegexReplacePreprocessor(replacements)
            nb, resources = rp.preprocess(nb, {})

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
            'PLATFORM': PLATFORM
        }

        return nb, errors, export_kwargs


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
    notebook_dir, file_name = os.path.split(nb_path)

    #need to make sure course is in rst file name
    notebook_dir = notebook_dir.replace(r'\\', '_').replace('../', '').replace('/', '_')
    file_name_root, _ = os.path.splitext(notebook_dir + '_' + file_name)
    base_path = os.path.join(output_dir, file_name_root + '-{}-{}'.format(SCOPETYPE, PLATFORM))
    rst_path = os.path.abspath(base_path + '.rst')
    html_path = os.path.abspath(base_path + '.html')



    #   class EscapeBacktickPreprocessor(nbconvert.preprocessors.Preprocessor):

    ebp = EscapeBacktickPreprocessor()

    rst_ready_nb, _ = ebp.preprocess(nb, {})
    with open(rst_path, 'w', encoding='utf-8') as rst_file:
        rst_exporter = RSTExporter()


        body, res = rst_exporter.from_notebook_node(rst_ready_nb, resources={'unique_key': 'img/{}-{}-{}'.format(SCOPETYPE, PLATFORM, file_name_root).replace(' ', '')})
        file_names = res['outputs'].keys()
        for name in file_names:
            with open(os.path.join(output_dir, name), 'wb') as f:
                f.write(res['outputs'][name])
                test_logger.info('writing to '+ name)
            #print(res['outputs'][name])


        rst_file.write(body)
        logger.info('Wrote to: '+ rst_path)

        ## need resources

    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_exporter = HTMLExporter()

        body, res = html_exporter.from_notebook_node(nb)

        html_file.write(body)
        logger.info('Wrote to: '+ html_path)


def _print_tracebacks(errors, logger = None, config=None):
    # to escape ANSI sequences use regex
    if logger is None:
        logger = test_logger
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    if errors == []:
        logger.info("Passed all tests!")
    for error in errors:
        logger.warning("Test failed in cell {}: {}: {}".format(error[0], error[1]['ename'], error[1]['evalue']))
        for line in error[1]['traceback']:
            logger.warning(ansi_escape.sub('', line))


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


def test_notebook(nb_path, output_dir, serial_number=None, export=True, allow_errors=True, print_first_traceback_only=True, print_stdout=False, print_stderr=False,
                  allowable_exceptions=None, baud=None, hw_location=None, logger=None, **kwargs):
    # reset output for next test
    output[:] = list()
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
        logger.debug('No serial number specified... only bad if more than one device attached.')
    nb, errors, export_kwargs = execute_notebook(nb_path, serial_number, hw_location=hw_location, allow_errors=allow_errors, allowable_exceptions=allowable_exceptions, baud=baud, logger=logger, **kwargs)
    if not errors:
        logger.info("PASSED")
        passed = True
        if export:
            export_notebook(nb, nb_path, output_dir, **export_kwargs, logger=logger)
    else:
        if allowable_exceptions:
            error_is_acceptable = [error[1]['ename'] in allowable_exceptions for error in errors]
            if all(error_is_acceptable):
                logger.info("PASSED with expected errors")
                passed = True
                for error in errors:
                    logger.info(error[1]['ename']+ ':'+ error[1]['evalue'])
                if export:
                    export_notebook(nb, nb_path, output_dir, **export_kwargs, logger=logger)
            else:
                logger.warning("FAILED {} config {}:".format(nb_path, kwargs))
                passed = False
                if print_first_traceback_only:
                    _print_tracebacks([error for i, error in enumerate(errors) if i == 0], logger=logger)
                else:
                    _print_tracebacks(errors, logger=logger)
        else:
            logger.warning("FAILED:")
            passed = False
            if print_first_traceback_only:
                _print_tracebacks([error for i, error in enumerate(errors) if i == 0],logger=logger)
            else:
                _print_tracebacks(errors,logger=logger)
            export_notebook(nb, nb_path, output_dir, **export_kwargs, logger=logger)
    if print_stdout:
        _print_stdout(nb, logger)
    if print_stderr:
        _print_stderr(nb, logger)

    logger.debug("\n")
    return passed, '\n'.join(output)


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
                # print(run_line.group(1))
                # print(run_line.group(2))
                space_tab = " " * num_spaces + "\t" * num_tabs
                a = cell['source'].replace(full_match, f'try:\n{space_tab}    {full_match}\n{space_tab}except:\n{space_tab}    x=open("/tmp/tmp.txt").read(); print(x); raise OSError(x)\n')
                a = a.replace(shell_cmd, shell_cmd + " &> /tmp/tmp.txt")
                cell['source'] = a
                # print(a)
                # python_code = " " * num_spaces + "\t" * num_tabs + python_code.replace("\n", "\n{}{}".format(" " * num_spaces, "\t" * num_tabs))
                # print(str(num_spaces), str(num_tabs))
                # cell['source'] = cell['source'].replace(full_match, '\n{}\n'.format(python_code))

        return cell, resources

#need to separate into separate functions to multiprocess
def run_test_hw_config(id, cw_dir, config, hw_location=None, logger=None):
    tutorials, connected_hardware = load_configuration(config)
    summary = {'failed': 0, 'run': 0}
    hw_settings = connected_hardware[id]

    nb_dir = os.path.join(cw_dir, 'jupyter')
    output_dir = os.path.join(cw_dir, 'tutorials')
    tests = {}
    if logger is None:
        logger = test_logger
    # if not hw_settings['enabled']:
    #     return summary, tests

    # TODO: grab HW configuration settings

    for nb in tutorials.keys():
        for test_config in tutorials[nb]['configurations']:
            # run the test
            if id in test_config['ids']:
                kwargs = {
                    'SCOPETYPE': hw_settings['scope'],
                    'PLATFORM': hw_settings['target'],
                    'CRYPTO_TARGET': hw_settings['firmware'],
                    # 'serial_number': hw_settings.get('serial number'),
                    'VERSION': hw_settings['tutorial type'],
                    'SS_VER': test_config['ssver']

                }

                path = os.path.join(nb_dir, nb)
                hw_kwargs = hw_settings.get('kwargs')
                logger.debug("HW kwargs: {}".format(hw_kwargs))
                if hw_kwargs:
                    kwargs.update(hw_kwargs)

                tutorial_kwargs = test_config.get('kwargs')
                if tutorial_kwargs:
                    kwargs.update(tutorial_kwargs)

                logger.debug("\nTesting {} with {} ({})".format(nb, id, kwargs))
                passed, output = test_notebook(hw_location=hw_location, nb_path=path, output_dir=output_dir, logger=logger, **kwargs)
                if not passed:
                    summary['failed'] += 1
                summary['run'] += 1
                header = "{} {} with config {}\n".format("Passed" if passed else "Failed", nb, id)
                tests[header] = output
            else:
                pass # we don't need to test this hardware on this tutorial

    time.sleep(0.5)
    logger.debug("\n-----------------\nFinished test run\n-----------------\n")
    return summary, tests

def run_tests(cw_dir, config, results_path=None):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    if not results_path:
        results_path = "./"
    
    results_handler = logging.FileHandler(results_path + "/testing.log")
    test_logger.addHandler(results_handler)
    tutorials, connected_hardware = load_configuration(config)

    num_hardware = len(connected_hardware)
    hw_locations = []
    loggers = []
    handlers = []
    for i in range(num_hardware):
        handlers.append(logging.FileHandler(results_path + "/test_{}.log".format(i)))
        loggers.append(logging.getLogger("Test Logger {}".format(i)))
        cur = loggers[i]
        cur.setLevel(logging.DEBUG)
        cur.addHandler(handlers[i])

        if connected_hardware[i].get('serial number') is None:
            hw_locations.append(None)
            continue
        scope = cw.scope(sn=str(connected_hardware[i]['serial number']))
        if scope.latest_fw_str > scope.fw_version_str:
            scope.upgrade_firmware()
            time.sleep(5)
            scope = cw.scope(sn=str(connected_hardware[i]['serial number']))
            test_logger.info("Upgraded firmware for device {}".format(i))
        else:
            test_logger.info("Device {} up to date")

        hw_locations.append((scope._getNAEUSB().usbtx.device.getBusNumber(),\
            scope._getNAEUSB().usbtx.device.getDeviceAddress()))
        test_logger.info("Found device {} at {}".format(i, hw_locations[i]))
        scope.dis()
        #hw_locations.appe

    nb_dir = os.path.join(cw_dir, 'jupyter')
    output_dir = os.path.join(cw_dir, 'tutorials')

    # copy the images from input to output directory
    # keeping them in the same relative directory
    image_input_dir = os.path.join(nb_dir, 'img')
    image_output_dir = os.path.join(output_dir, 'img')

    if not os.path.isdir(image_output_dir):
        os.mkdir(image_output_dir)

    test_logger.info('Copying over image files...')
    for image_path in glob(os.path.join(image_input_dir, '*')):
        _, image_name = os.path.split(image_path)
        shutil.copyfile(image_path, os.path.join(image_output_dir, image_name))
    test_logger.info('Done')

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
    with ProcessPoolExecutor(max_workers=num_hardware) as nb_pool:
        test_future = {nb_pool.submit(run_test_hw_config, i, cw_dir, config, hw_locations[i], loggers[i]): i for i in range(num_hardware)}
        for future in as_completed(test_future):
            hw_summary, hw_tests = future.result()
            summary['all']['failed'] += hw_summary['failed']
            summary['all']['run'] += hw_summary['run']
            index = test_future[future]
            summary[str(index)] = {'failed': hw_summary['failed'], 'run': hw_summary['run']}
            # summary[str(index)]['failed'] += hw_summary['failed']
            # summary[str(index)]['run'] += hw_summary['run']
            tests.update(hw_tests)

            with open("config_{}_log.txt".format(index), 'w') as f:
                for header in hw_tests:
                    f.write("Test {}, output:\n{}".format(header, hw_tests[header]))

        # for i in range(num_hardware):
        #     test_logger.debug("Running hw")
        #     results.append(nb_pool.apply_async(run_test_hw_config, args=(i, config)))

        # try:
        #     for index, result in enumerate(results):
                # hw_summary, hw_tests = result.get()
                # summary['all']['failed'] += hw_summary['failed']
                # summary['all']['run'] += hw_summary['run']
                # summary[str(index)] = {'failed': hw_summary['failed'], 'run': hw_summary['run']}
                # # summary[str(index)]['failed'] += hw_summary['failed']
                # # summary[str(index)]['run'] += hw_summary['run']
                # tests.update(hw_tests)

                # with open("config_{}_log.txt".format(index), 'w') as f:
                #     for header in hw_tests:
                #         f.write("Test {}, output:\n{}".format(header, hw_tests[header]))
        # except Exception as e:
        #     nb_pool.terminate()
        #     test_logger.error(e)

    try:
        shutil.rmtree('projects')
    except FileNotFoundError:
        pass

    return summary, tests

if __name__ == '__main__':
    script, config_file_path = sys.argv
    run_tests(config_file_path)
