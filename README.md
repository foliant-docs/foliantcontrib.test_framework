[![](https://img.shields.io/pypi/v/foliantcontrib.test_framework.svg)](https://pypi.org/project/foliantcontrib.test_framework/) [![](https://img.shields.io/github/v/tag/foliant-docs/foliantcontrib.test_framework.svg?label=GitHub)](https://github.com/foliant-docs/foliantcontrib.test_framework)

# Test framework

Foliant test framework is a tool which helps you test your Foliant extensions.
It is still under development and right now you can only test preprocessors and config extensions with it
using Preprocessor Test Framework and Configuration Extensions Test Framework.

## Preprocessor Test Framework

Preprocessor Test Framework is a class which allows you to quickly set up a simulated environment for preprocessor testing.
It runs a specific preprocessor just like Foliant core runs it, and compares the results with expected output.

### Usage

First, you need to initialize the framework by passing it a name of preprocessor you want to test.
Let's test the [includes](https://foliant-docs.github.io/docs/preprocessors/includes/) preprocessor in this example:

```python
from foliant_test.preprocessor import PreprocessorTestFramework
ptf = PreprocessorTestFramework('includes')
```

Now, to test the work of includes we need some source files. Source files are supplied in a mapping. We need to pass the framework both input source files and expected files.

Let's create a basic file structure with just two files, one of which includes the other:

```python
input_files = {
'first.md': '# First file\n\n<include src="second.md"></include>',
'second.md': 'Second file content'
}
```

Now let's create the expected mapping for these two files. What should be their contents after we apply the includes preprocessor?
_The expected files must have the same names as the corresponding input files.
Otherwise, an error will be thrown, even if the contents of the files are equal._

```python
expected_files = {
'first.md': '# First file\n\nSecond file content',
'second.md': 'Second file content'
}
```

All is left to do is to run the test:

```python
ptf.test_preprocessor(
input_mapping=input_files,
expected_mapping=expected_files
)
```

If you don't see any output, it means that everything went well and expected results were identical to the factual.

#### Adding options

To set up your preprocessor options, change the `options` attribute of the framework instance.

For example, let's test the work of includes' `extensions` option, which allows us to process different file types besides `.md`

```python
ptf.options = {'extensions': ['md', 'txt']}
input_files = {
    'first.txt': '# First file\n\n<include src="second.md"></include>',
    'second.md': 'Second file content'
}
expected_files = {
    'first.txt': '# First file\n\nSecond file content',
    'second.md': 'Second file content'
}
ptf.test_preprocessor(
    input_mapping=input_files,
    expected_mapping=expected_files
)
```

Apart from options, you can also change:

`config` attribute which represents the virtual `foliant.yml` dictionary;
`chapters` attribute, which holds the list of chapters,
`context` attribute which holds the whole preprocessor context.

#### Helper Functions For Input And Expected Mappings

It's ok to keep contents of test files in strings right inside your test modules, but when these strings grow big it's more convenient to keep them in separate files. `preprocessor` module exports two functions which help you manage those:

**unpack_file_dict**

`unpack_file_dict` turns dictionary of filenames into dictionary of these files' contents.

```python
from foliant_test.preprocessor import unpack_file_dict

file_dict = {
    'index.md': '/test_data/case1/index.md',  # paths should better be absolute
    'description.md': '/test_data/case1/description.md',
}
```

When you feed this dictionary to _unpack_file_dict_, it will replace paths to data files `'/test_data/case1/index.md'` 
and `'/test_data/case1/description.md'` with their contents:

```python
>>> unpack_file_dict(file_dict)
{
    'index.md': 'index md contents',
    'description.md': 'description md contents'
}
```

So you can pass the result straight to `input_mapping` or `expected_mapping` parameters:

```python
ptf.test_preprocessor(
    input_mapping=unpack_file_dict(file_dict),
    expected_mapping=unpack_file_dict(expected_file_dict)
)
```

**unpack_dir**

`unpack_dir` creates the whole mapping for you, based on the contents of supplied dir. It reads all files inside specified dir and puts them into a dictionary: `{<file_name>: <file_contents>}`. Note: `<file_name>` does not include a path, so `test_data/case1/index.md` will turn into `index.md`.

```python
from foliant_test.preprocessor import unpack_dir

input_dict = unpack_dir('/test_data/case1')  # paths should better be absolute
output_dict = unpack_dir('/test_data/case1_expected')
```

## Configuration Extension Test Framework

Configuration Extension Test Framework is a class which allows you to quickly set up simulated environment for testing config extensions. It parses the config just like Foliant core does it, and compares the results with expected output.

### Usage

First, you need to initialize the framework by passing it a name of extensions you want to test. Let's test the `path` builtin config extension in this example:

```python
from foliant_test.config_extension import ConfigExtensionTestFramework
ctf = ConfigExtensionTestFramework('path')
```

Now to test the work of `path` we need to supply a source config. The config is supplied in a YAML-string, as if it was a plain-text `foliant.yml` file.

The config string is supplied in `input_config` parameter, and is then compared to the expected config in `expected_config` parameter. Note that the latter is of type dict, because it's already parsed config.

```python
ctf.test_extension(
    input_config='mypath: !path README.md',
    expected_config={'mypath': '/usr/src/app/myproject/README.md'}
)

```

You can adjust the following parameters before testing the extension:

```python
ctf.project_path = Path('.')
ctf.config_file_name = '_foliant.yml'
ctf.quiet = True
```
