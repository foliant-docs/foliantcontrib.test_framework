import shutil
import re
from logging import getLogger
from importlib import import_module
from pathlib import Path, PosixPath
from unittest.util import _common_shorten_repr


def unpack_dir(input_dir: str or PosixPath, extensions: list = ['md']) -> dict:
    '''
    Search for file with extensions from `extensions` in the `input_dir` and
    pack them into the framework's input mapping format:
    {'file_name.md': '<file contents>'}

    :param input_dir: directory with source files to be packed into mapping.
    :param extensions: list of file extensions to be parsed inside input_dir.

    :returns: mapping ready to be fed into PreprocessorTestFramework.
    '''
    result = {}
    input_path = Path(input_dir)
    for extension in extensions:
        for file_path in input_path.rglob(f'*.{extension}'):
            file_key = str(file_path.relative_to(input_path))
            with open(file_path, encoding='utf8') as f:
                result[file_key] = f.read()
    return result


def unpack_file_dict(file_dict: dict) -> dict:
    '''
    Open each file in the file dict and replace it with its contents.

    :param file_dict: dictionary of following format:
                      {'source_name.md': 'data/file_name.md'}
                      where `source_name` is file name which will be given to
                      the PreprocessorTestFramework, `data/file_name.md` is local
                      file which should be unpacked.

    :returns: mapping ready to be fed into PreprocessorTestFramework:
              {'source_name.md': '<file contents>'}
    '''
    result = {}
    for file_key, file_path in file_dict.items():
        with open(file_path, encoding='utf8') as f:
            result[file_key] = f.read()
    return result


class PreprocessorTestFramework:
    config_defaults = {
        'src_dir': Path('./__src__'),
        'tmp_dir': Path('./__folianttmp__')
    }

    def __init__(self, preprocessor_name: str):
        try:
            preprocessor_module = import_module(f'foliant.preprocessors.{preprocessor_name}')
            self.preprocessor = preprocessor_module.Preprocessor

        except ModuleNotFoundError:
            raise ModuleNotFoundError(f'Preprocessor {preprocessor_name} is not installed')
        self.preprocessor_name = preprocessor_name
        self._options = {}
        self._chapters = []
        self._files = {}
        self._context = {
            'project_path': Path('.'),
            'config': {'preprocessors': [preprocessor_name], **self.config_defaults},
            'target': '',
            'backend': ''
        }
        self.logger = getLogger('PreprocessorTestFramework')
        self.quiet = True
        self.debug = False

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, val: dict):
        self._context = val

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, val):
        self._options = val
        preprocessor = {self.preprocessor_name: val} if val else self.preprocessor_name
        self._context['config']['preprocessors'] = [preprocessor]

    @property
    def chapters(self):
        return self._chapters

    @chapters.setter
    def chapters(self, val):
        self._chapters = val
        if val:
            self._context['config']['chapters'] = val
        else:
            if 'chapters' in self._context['config']:
                self._context['config'].pop('chapters')

    @property
    def config(self):
        return self._context['config']

    @config.setter
    def config(self, val):
        self._config = val
        self._context['config'] = {**self.config_defaults, **val}

    @property
    def results(self):
        return self._results_dict

    def _generate_working_dir(self):
        working_dir = Path(self._context['config']['tmp_dir'])
        for rel_path, content in self.source_dict.items():
            file_path = working_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf8') as f:
                f.write(content)

    def _generate_chapters(self):
        working_dir = Path(self._context['config']['tmp_dir'])
        chapters = []
        for chapter_path in working_dir.rglob('*.md'):
            rel_path = chapter_path.relative_to(working_dir)
            chapters.append(rel_path)
        self.chapters = chapters

    def _collect_results(self, normalize: bool = False):
        self._results_dict = {}
        working_dir = Path(self.context['config']['tmp_dir'])
        for markdown_file_path in working_dir.rglob('*.*'):
            file_key = str(markdown_file_path.relative_to(Path(working_dir)))
            with open(markdown_file_path, encoding='utf8') as f:
                content = f.read()
                if normalize:
                    content = self._normalize(content)
                self._results_dict[file_key] = content
        self._results_normalized = normalize

    def _normalize(self, markdown_content: str) -> str:
        '''Normalize the source Markdown content to simplify
        further operations: replace ``CRLF`` with ``LF``,
        remove excessive whitespace characters,
        provide trailing newline, etc.
        :param markdown_content: Source Markdown content
        :returns: Normalized Markdown content.

        Note: to avoid unnecessary empty line tuning we reduce 3 or more line
        breaks into 2.
        '''

        markdown_content = re.sub(r'^\ufeff', '', markdown_content)
        markdown_content = re.sub(r'\ufeff', '\u2060', markdown_content)
        markdown_content = re.sub(r'\r\n', '\n', markdown_content)
        markdown_content = re.sub(r'\r', '\n', markdown_content)
        markdown_content = re.sub(r'(?<=\S)$', '\n', markdown_content)
        markdown_content = re.sub(r'\t', '    ', markdown_content)
        markdown_content = re.sub(r'[ \n]+$', '\n', markdown_content)
        markdown_content = re.sub(r' +\n', '\n', markdown_content)
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

        return markdown_content

    def _cleanup(self):
        shutil.rmtree(self.context['config']['tmp_dir'], ignore_errors=True)
        shutil.rmtree(self.context['config']['src_dir'], ignore_errors=True)

    def test_preprocessor(self,
                          input_mapping: dict or None = None,
                          expected_mapping: dict or None = None,
                          keep: bool = False,
                          normalize: bool = True):
        self._cleanup()
        self.source_dict = {}
        if input_mapping:
            self.source_dict.update(input_mapping)
        self._generate_working_dir()
        self._generate_chapters()

        self.preprocessor(
            self.context,
            self.logger,
            self.quiet,
            self.debug,
            self._options
        ).apply()

        self._collect_results(normalize)
        if not keep:
            self._cleanup()

        expected = {}
        if expected_mapping:
            expected.update(expected_mapping)

        if expected:
            self.compare_results(expected)
            # print('ok!')

    def compare_results(self, expected: dict):
        if self._results_normalized:
            expected_ = {k: self._normalize(v) for k, v in expected.items()}
        else:
            expected_ = {**expected}

        if expected_.keys() != self.results.keys():
            raise ResultsDifferError(
                f'Expected file structure\n{list(expected_.keys())}\n'
                f'differs from resulting file structure {list(self.results.keys())}'
            )

        for e_file, e_content in expected.items():
            f1 = self._normalize(e_content)
            f2 = self.results[e_file]
            if self._normalize(e_content) != self.results[e_file]:
                raise ResultsDifferError(
                    f'File {e_file} contents differ from expected:\n'
                    '{}\n!=\n{}'.format(*_common_shorten_repr(f2, f1))
                )


class ResultsDifferError(Exception):
    pass
