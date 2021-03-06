#! /usr/bin/env python
"""Interface to the Dakota iterative systems analysis toolkit."""

import subprocess
import importlib
import types
import yaml
from .methods.vector_parameter_study import VectorParameterStudy
from . import methods_path


class Dakota(object):

    """Set up and run a Dakota experiment."""

    def __init__(self, method=None, **kwargs):
        """Create a new Dakota experiment.

        Called with no parameters, a Dakota experiment with basic
        defaults (a vector parameter study with the built-in
        `rosenbrock` example) is created. Use ``method`` to set the
        Dakota analysis method in a new experiment.

        Parameters
        ----------
        method : str
          The desired Dakota method (e.g., `vector_parameter_study`,
          `polynomial_chaos`, etc.) to use in an experiment.

        Examples
        --------
        Create a generic Dakota experiment:

        >>> d = Dakota()

        Create a vector parameter study experiment:

        >>> d = Dakota(method='vector_parameter_study')

        """
        self.input_file = 'dakota.in'
        self.output_file = 'dakota.out'

        if method is not None:
            _module = importlib.import_module(methods_path + method)
            _class = getattr(_module, _module.classname)
            self.method = _class(**kwargs)
        else:
            self.method = VectorParameterStudy()

    @classmethod
    def from_file_like(cls, file_like):
        """Create a Dakota instance from a file-like object.

        Parameters
        ----------
        file_like : file_like
            Input parameter file.

        Returns
        -------
        Dakota
            A new Dakota instance.

        """
        config = {}
        if isinstance(file_like, types.StringTypes):
            with open(file_like, 'r') as fp:
                config = yaml.load(fp.read())
        else:
            config = yaml.load(file_like)
        return cls(**config)

    def write_configuration_file(self, config_file=None):
        """Dump settings to a YAML configuration file.

        Parameters
        ----------
        config_file: str, optional
          A path/name for a new configuration file.

        Examples
        --------
        Make a configuration file for a vector parameter study
        experiment:

        >>> d = Dakota(method='vector_parameter_study')
        >>> d.write_configuration_file('config.yaml')

        """
        if config_file is not None:
            self.method.configuration_file = config_file
        props = self.method.__dict__.copy()
        for key in props:
            if key.startswith('_'):
                new_key = key.lstrip('_')
                props[new_key] = props.pop(key)
        with open(self.method.configuration_file, 'w') as fp:
            yaml.dump(props, fp, default_flow_style=False)

    def write_input_file(self, input_file=None):
        """Create a Dakota input file on the file system.

        Parameters
        ----------
        input_file: str, optional
          A path/name for a new Dakota input file.

        Examples
        --------
        Make an input file for a vector parameter study experiment:

        >>> d = Dakota(method='vector_parameter_study')
        >>> d.write_input_file()

        """
        if input_file is not None:
            self.input_file = input_file
        with open(self.input_file, 'w') as fp:
            fp.write(self.method.environment_block())
            fp.write(self.method.method_block())
            fp.write(self.method.variables_block())
            fp.write(self.method.interface_block())
            fp.write(self.method.responses_block())

    def run(self):
        """Run the Dakota experiment."""
        subprocess.check_output(['dakota',
                                 '-i', self.input_file,
                                 '-o', self.output_file],
                                stderr=subprocess.STDOUT)
