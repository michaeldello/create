# CREATE

Configurable

Reusable

Extensible 

Automated

Tinkering

Executive

## Description
CREATE is a general purpose python executive for developing software.

This is a generic framework for allowing a developer to quickly iterate on their work, all in one step.

The executive is divided into stages, each with a particular objective for development, e.g., build, document, test, analyze. In each case, configuration files are read to decide how to proceed with execution. A simple way to think of this is a "CI/CD Lite" executive, whose configurable nature allows it to be as simple or as complex for personal software development automation.

## Features

### v0.1

- Default, basic guidance

### Planned/Future

- Proper logging
- Step/command execution options
- More granular error handling
- Parallelism
- Integrate AI

## Installation

TBD

## Usage

### Linux-y systems

Set your configuration (see Configuration section)

./go-create -c | --config

### Windows

(Currently doesn't support shebang)

python3 go-create.py -c | --config

## Configuration

Create a configuration under configs/ folder (or use the default, which is a basic guidance config)

## License

This software is open-source and available under the MIT License. You are free to contribute or report issues in the [GitHub repository](https://github.com/michaeldello/create).

## Feedback

If you have any questions, suggestions, or encounter issues, please don't hesitate to [open an issue](https://github.com/michaeldello/create/issues) on GitHub.

## Author

- [Michael Dello](https://github.com/michaeldello)
