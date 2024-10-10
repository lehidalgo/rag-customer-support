# Python Project to Markdown

This script scans a Python project directory, generates a Markdown file containing the project structure, and includes the source code of all `.py` files.

## Features

- Recursively scans the given project directory for Python files.
- Ignores blacklisted directories such as `venv`.
- Generates a Markdown file that lists the project structure, including Python files, and includes their code in the same file.
- The output file can be customized, with a default name of `project_code.md`.

## Usage

### Prerequisites

- Python 3.x

### Installation

Clone the repository or download the script, and ensure Python 3.x is installed.

### Running the Script

To run the script, use the following command:

```bash
python generate_codebase.py <project_path> -o <output_file>
```

- <project_path>: The root directory of your Python project.
- -o <output_file> (optional): The output Markdown file name. Defaults to project_code.md.


### Example:

```bash
python generate_codebase.py ../ -o project_codebase.md
```

This will generate a Markdown file with the project structure and the content of all Python files under the specified directory.

#### Arguments
project_path: The path to the root of the Python project.
-o / --output: (Optional) The name of the output Markdown file. Defaults to project_code.md.
