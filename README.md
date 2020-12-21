[![](https://img.shields.io/pypi/v/foliantcontrib.test_framework.svg)](https://pypi.org/project/foliantcontrib.test_framework/) [![](https://img.shields.io/github/v/tag/foliant-docs/foliantcontrib.test_framework.svg?label=GitHub)](https://github.com/foliant-docs/foliantcontrib.test_framework)

# Test framework

Foliant test framework is a tool which helps you test your Foliant extensions. It is still under development and right now you can only test preprocessors with it using Preprocessor Test Framework.

## Preprocessor Test Framework

Preprocessor Test Framework is a class which allows you to quickly set up simulated environment for preprocessor testing. It runs a specific preprocessor just like Foliant core runs it, and the compares the results with expected results.

### Usage

First you need to initialize the framework by passing it a name of preprocessor you want to test. Let's test the [includes](https://foliant-docs.github.io/docs/preprocessors/includes/) preprocessor in this example:

```python
>>> from foliant_test.preprocessor import PreprocessorTestFramework
>>> ptf = PreprocessorTestFramework('includes')

```

Now to test the work of includes we need some source files. Source files are supplied in a mapping. We need to pass the framework both input source files and expected files.

Let's create a basic file structure with just two files, one of which includes the other:

```python
>>> input_files = {
...     'first.md': '# First file\n\n<include src="second.md"></include>',
...     'second.md': 'Second file content'
... }

```

Now let's create the expected mapping for these two files. What should be their contents after we apply the includes preprocessor?

```python
>>> expected_files = {
...     'first.md': '# First file\n\nSecond file content',
...     'second.md': 'Second file content'
... }

```

All is left to do is to run the test:

```python
>>> ptf.test_preprocessor(
...     input_mapping=input_files,
...     expected_mapping=expected_files
... )

```

If you don't see any output, it means that everything went well and expected results were identical to the factual.

#### Adding options

To set up your preprocessor options, change the `options` attribute of the framework instance.

For example, let's test the work of includes' `extensions` option, which allows us to process different file types besides `.md`

```python
>>> ptf.options = {'extensions': ['md', 'txt']}
>>> input_files = {
...     'first.txt': '# First file\n\n<include src="second.md"></include>',
...     'second.md': 'Second file content'
... }
>>> expected_files = {
...     'first.txt': '# First file\n\nSecond file content',
...     'second.md': 'Second file content'
... }
>>> ptf.test_preprocessor(
...     input_mapping=input_files,
...     expected_mapping=expected_files
... )

```

Apart from options you can also change:

`config` attribute which represents the virtual `foliant.yml` dictionary;
`chapters` attribute, which holds the list of chapters,
`context` attribute which holds the whole preprocessor context.
