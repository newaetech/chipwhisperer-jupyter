import shutil
import os
from glob import glob
from pathlib import Path
from os import listdir
from os.path import isfile, join
import yaml
import re
import sys

import nbformat
import nbconvert
from nbconvert.preprocessors import ClearOutputPreprocessor
from nbconvert.exporters import NotebookExporter
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import RSTExporter
from nbparameterise import extract_parameters, parameter_values, replace_definitions
from nbconvert.nbconvertapp import NbConvertBase

script_path = os.path.abspath(__file__)
tests_dir, _ = os.path.split(script_path)
# set configuration options
RSTExporter.template_path = [tests_dir]
RSTExporter.template_file = 'rst_extended.tpl'
NbConvertBase.display_data_priority = [
    'application/vnd.jupyter.widget-state+json',
    'application/vnd.jupyter.widget-view+json',
    'application/javascript',
    'application/vnd.bokehjs_exec.v0+json',
    'text/html',
    'text/markdown',
    'image/svg+xml',
    'text/latex',
    'image/png',
    'image/jpeg',
    'text/plain'
]


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


def execute_notebook(nb_path, serial_number, allow_errors=True, SCOPETYPE='OPENADC', PLATFORM='CWLITEARM', **kwargs):
    """Execute a notebook via nbconvert and collect output.
       :returns (parsed nb object, execution errors)
    """
    notebook_dir, file_name = os.path.split(nb_path)
    real_path = Path(nb_path).absolute()

    with open(real_path) as nbfile:
        nb = nbformat.read(nbfile, as_version=4)
        orig_parameters = extract_parameters(nb)
        params = parameter_values(orig_parameters, SCOPETYPE=SCOPETYPE, PLATFORM=PLATFORM, **kwargs)
        nb = replace_definitions(nb, params, execute=False)

        ep = ExecutePreprocessor(timeout=None, kernel_name='python3', allow_errors=allow_errors)

        replacements = {
            r'cw.scope(\(\))': 'cw.scope(sn=\'{}\')'.format(serial_number),
            r'chipwhisperer.scope()': 'chipwhisperer.scope(sn=\'{}\')'.format(serial_number)
        }
        rp = RegexReplacePreprocessor(replacements)
        ip = InLineCodePreprocessor(notebook_dir)

        if serial_number:
            # inline all code before putting in serial
            # numbers
            nb, resources = ip.preprocess(nb, {})
            # add serial number to the cw.scope calls
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


def export_notebook(nb, nb_path, output_dir, SCOPETYPE=None, PLATFORM=None):
    """Takes a notebook node and exports it to ReST.

    Args:
        nb (notebook): The notebook returned by execute_notebook.
        nb_path (str): Path to intput notebook file. Used to generate the
            name of the output file.
        output_dir (str): The output directory for the ReST file.
        SCOPETYPE (str): Used to generate the output file name.
        PLATFORM (str): Used to generate the output file name.
    """
    notebook_dir, file_name = os.path.split(nb_path)
    file_name_root, _ = os.path.splitext(file_name)
    rst_path = os.path.join(output_dir, file_name_root + "-{}-{}".format(SCOPETYPE, PLATFORM) + ".rst")
    rst_path = os.path.abspath(rst_path)

    with open(rst_path, "w", encoding='utf-8') as rst_file:
        rst_exporter = RSTExporter()

        body, res = rst_exporter.from_notebook_node(nb)

        rst_file.write(body)
        print('Wrote to:', rst_path)


def _print_tracebacks(errors):
    if errors == []:
        print("Passed all tests!")
    for error in errors:
        print("Test failed in cell {}: {}: {}".format(error[0], error[1]['ename'], error[1]['evalue']))
        for line in error[1]['traceback']:
            print(line)


def _get_outputs(nb):
    return [[i, cell] for i, cell in enumerate(nb.cells) if "outputs" in cell]


def _print_stderr(nb):
    outputs = _get_outputs(nb)
    printed_output = [[cell[0], output] for cell in outputs for output in cell[1]['outputs'] if
                      ('name' in output and output['name'] == 'stderr')]
    for out in printed_output:
        print("[{}]:\n{}".format(out[0], out[1]['text']))


def _print_stdout(nb):
    outputs = _get_outputs(nb)
    printed_output = [[cell[0], output] for cell in outputs for output in cell[1]['outputs'] if
                      ('name' in output and output['name'] == 'stdout')]
    for out in printed_output:
        print("[{}]:\n{}".format(out[0], out[1]['text']))


def test_notebook(nb_path, output_dir, serial_number, export=True, allow_errors=True, print_first_traceback_only=True, print_stdout=False, print_stderr=False,
                  allowable_exceptions=None, **kwargs):
    print()
    print("Testing: {}:...".format(os.path.abspath(nb_path)))
    print("with {}.".format(kwargs))
    if serial_number:
        print('on device with serial number {}.'.format(serial_number))
    else:
        print('No serial number specified... only bad if more than one device attached.')
    nb, errors, export_kwargs = execute_notebook(nb_path, serial_number, allow_errors=allow_errors, allowable_exceptions=allowable_exceptions, **kwargs)
    if not errors:
        print("PASSED")
        if export:
            export_notebook(nb, nb_path, output_dir, **export_kwargs)
    else:
        if allowable_exceptions:
            error_is_acceptable = [error[1]['ename'] in allowable_exceptions for error in errors]
            if all(error_is_acceptable):
                print("PASSED with expected errors")
                for error in errors:
                    print(error[1]['ename'], ':', error[1]['evalue'])
                if export:
                    export_notebook(nb, nb_path, output_dir, **export_kwargs)
            else:
                print("FAILED:")
                if print_first_traceback_only:
                    _print_tracebacks([error for i, error in enumerate(errors) if i == 0])
                else:
                    _print_tracebacks(errors)
        else:
            print("FAILED:")
            if print_first_traceback_only:
                _print_tracebacks([error for i, error in enumerate(errors) if i == 0])
            else:
                _print_tracebacks(errors)
    if print_stdout:
        _print_stdout(nb)
    if print_stderr:
        _print_stderr(nb)


def clear_notebook(path):
    real_path = Path(path)
    body = ""
    with open(real_path, "r", encoding="utf-8") as nbfile:
        nb = nbformat.read(nbfile, as_version=4)
        orig_parameters = extract_parameters(nb)
        params = parameter_values(orig_parameters, SCOPETYPE="OPENADC", PLATFORM="CWLITEARM")
        new_nb = replace_definitions(nb, params, execute=False)
        co = ClearOutputPreprocessor()

        exporter = NotebookExporter()
        node, resources = co.preprocess(new_nb, {'metadata': {'path': './'}})
        body, resources = exporter.from_notebook_node(node, resources)
    with open(real_path, "w", encoding="utf-8") as nbfile:
        nbfile.write(body)


def clear_outputs_in_dir(dirpath):
    filter_list = ["Test_Notebook.ipynb", "PA_TVLA_1-Performing_TVLA_Testing_for_Crypto_Validation.ipynb",
                   "PA_Profiling_1_Template_Attacks_HW_Assumption.ipynb", "PA_Intro_3-Measuring_SNR_of_Target.ipynb",
                   "PA_HW_CW305.ipynb", "PA_CPA_4-Hardware_Crypto_Attack.ipynb", "Helpful_Code_Blocks.ipynb",
                   "!!Suggested_Completion_Order!!.ipynb", "Fault_4-AES_Differential_Fault_Analysis_Attacks.ipynb"]
    notebook_files = [f for f in listdir("./") if
                      (isfile(join("./", f)) and f.endswith(".ipynb") and f not in filter_list)]
    for file in notebook_files:
        print("Clearing {}".format(file))
        clear_notebook(file)


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
        tuple: (bool, string) Whether a match was found, and second the serial number
        of the hardware device connected matching the configuration. Returns False and
        None if matching connected device was not found.
    """
    check_keys = [
        'scope',
        'target'
    ]

    for connected_config in connected:
        check = [config[key] == connected_config[key] for key in check_keys]
        if all(check):
            sn = connected_config.get('serial number')
            return True, sn
    return False, None


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
            print('One of the regex compile failed, invalid regex.')
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

    Args:
        notebook_dir (str): The path to the directory containing all the
            notebooks. Used to resolve the relative paths used by the
            %run command.

    Returns:
        notebook, resources: The modified notebook, and resources with all
            instances of the %run command in lined.
    """

    def __init__(self, notebook_dir, **kwargs):
        self.notebook_dir = nb_dir
        super().__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        if cell['cell_type'] == 'code':
            if '%run' in cell['source']:
                # to deal with other notebooks being called from the source notebook
                # find the notebooks and export to python code and replace
                # the current cell source code with that python code before
                # replacing instances of cw.scope()
                p = re.compile(r"%run\s*[\"']?(.*\.ipynb)[\"']?")
                python_code_list = []
                external_notebooks = re.findall(p, cell['source'])
                for ext_nb in external_notebooks:
                    ext_nb_path = os.path.join(self.notebook_dir, ext_nb)
                    ext_nb_node = nbformat.read(ext_nb_path, as_version=4)
                    python_exporter = nbconvert.exporters.PythonExporter()
                    python_code, _ = python_exporter.from_notebook_node(ext_nb_node)
                    python_code_list.append(python_code)

                cell['source'] = '\n'.join(python_code_list)

        return cell, resources


if __name__ == '__main__':
    script, config_file_path = sys.argv
    tutorials, connected_hardware = load_configuration(config_file_path)

    nb_dir = '..'
    output_dir = '../../tutorials/'

    # copy the images from input to output directory
    # keeping them in the same relative directory
    image_input_dir = os.path.join(nb_dir, 'img')
    image_output_dir = os.path.join(output_dir, 'img')

    if not os.path.isdir(image_output_dir):
        os.mkdir(image_output_dir)

    print('Copying over image files...', end='')
    for image_path in glob(os.path.join(image_input_dir, '*')):
        _, image_name = os.path.split(image_path)
        shutil.copyfile(image_path, os.path.join(image_output_dir, image_name))
    print('Done')

    # Run each on of the tutorials with each supported hardware
    # configuration for that tutorial and export the output
    # to the output directory.
    for nb in tutorials.keys():
        for test_config in tutorials[nb]['configurations']:
            match, serial_number = matching_connected_configuration(test_config, connected_hardware)
            if match:
                path = os.path.join(nb_dir, nb)

                kwargs = {
                    'SCOPETYPE': test_config['scope'],
                    'PLATFORM': test_config['target'],
                    'CRYPTO_TARGET': test_config['firmware'],
                }

                extra_kwargs = tutorials[nb].get('kwargs')
                if extra_kwargs:
                    kwargs.update(extra_kwargs)

                test_notebook(nb_path=path, output_dir=output_dir, serial_number=serial_number, **kwargs)

    # clean up the projects created by running the tutorial notebooks.
    try:
        shutil.rmtree('projects')
    except FileNotFoundError:
        pass