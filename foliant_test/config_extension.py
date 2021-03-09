import os
from logging import getLogger
from importlib import import_module
from pathlib import Path


class ConfigExtensionTestFramework:
    _defaults = {
        'src_dir': Path('./src').expanduser(),
        'tmp_dir': Path('./__folianttmp__').expanduser()
    }

    def __init__(self, extension_name: str):
        try:
            parser_module = import_module(f'foliant.config.{extension_name}')
            self.parser = parser_module.Parser

        except ModuleNotFoundError:
            raise ModuleNotFoundError(f'Config extension {extension_name} is not installed')
        self.extension_name = extension_name
        self.project_path = Path('.')
        self.config_file_name = '_foliant.yml'

        self.config_path = self.project_path / self.config_file_name

        self.logger = getLogger('ConfigExtensionTestFramework')
        self.quiet = True

    @property
    def results(self):
        return self._results_dict

    def test_extension(self,
                       input_config: str,
                       expected_config: dict,
                       keep: bool = False):
        self._cleanup()
        try:
            self._generate_config(input_config)
            parser = self.parser(project_path=self.project_path,
                                 config_file_name=self.config_file_name,
                                 logger=self.logger,
                                 quiet=self.quiet)

            result = parser.parse()

            if result:
                self.compare_results(result, expected_config)
        finally:
            if not keep:
                self._cleanup()

    def _cleanup(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)

    def _generate_config(self, input_: str):
        with open(self.config_path, 'w', encoding='utf8') as f:
            f.write(input_)

    def compare_results(self, result: dict, expected_config: dict):
        expected = {**self._defaults, **expected_config}

        if result != expected:
            raise ResultsDifferError(
                'Parsed config differs from expected!\n'
                f'Result: {result}\n\n'
                f'Expected: {expected}'
            )


class ResultsDifferError(Exception):
    pass
