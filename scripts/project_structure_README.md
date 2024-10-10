# Project Structure Generator

This Python script generates a project structure from a tree-like structure string defined in a file. It reads a specified file containing the structure and creates directories and files as outlined in that file.

## Features

- Create a project directory and file structure based on a tree-like diagram format.
- Automatically generate nested directories and files.
- Command-line interface for easy usage.

## Usage

To use this script, you need to provide a file containing the project structure and a target path where the structure will be created.

### Running the Script

The script requires Python 3.x. Run the script from the command line with the following options:

```bash
python3 scripts/project_structure.py scripts/proj_template.txt ./ --verbose
```

<structure_file>: The path to the file containing the project structure (tree-like string).
<target_path>: The directory where the project structure will be created.
--verbose or -v: (Optional) Enable verbose output to see detailed information about the process.

Example
Suppose you have a file structure.txt with the following content:

```
MyProject/
├── .git/
├── __pycache__/
├── main.py
├── module/
│   ├── __init__.py
│   ├── utils.py
│   └── tests/
│       └── test_utils.py
└── venv/
```


Run the script like this:

```bash
python3 project_structure.py project_structure.txt /path/to/create/project --verbose
```

