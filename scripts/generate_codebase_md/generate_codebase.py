import os
import argparse

# Set of possible Python file extensions for faster lookup
PYTHON_EXTENSIONS = {".py", ".yaml"}
BLACKLIST = {"venv", "scripts", ".git", "__pycache__", "logs"}


def collect_python_files(project_path):
    python_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if os.path.splitext(file)[1] in PYTHON_EXTENSIONS:
                full_path = os.path.join(root, file)
                python_files.append(full_path)
    return [[x for x in python_files if bk not in x] for bk in BLACKLIST][0]


def generate_project_structure(project_path):
    """
    Generates a string representing the directory structure of the project,
    including Python files, formatted for Markdown.
    """
    structure_lines = []
    for root, dirs, files in os.walk(project_path):
        level = root.replace(project_path, "").count(os.sep)
        indent = "    " * level
        folder_name = os.path.basename(root) or os.path.basename(project_path)
        print(folder_name)
        if folder_name in BLACKLIST:
            continue
        structure_lines.append(f"{indent}- **{folder_name}/**")
        for file in files:
            if os.path.splitext(file)[1] in PYTHON_EXTENSIONS:
                file_indent = "    " * (level + 1)
                structure_lines.append(f"{file_indent}- {file}")
    return "\n".join(structure_lines)


def create_markdown(python_files, output_file, project_structure):
    with open(output_file, "w", encoding="utf-8") as md_file:
        # Write the project structure at the beginning
        md_file.write("# Project Structure\n\n")
        md_file.write(project_structure)
        md_file.write("\n\n---\n\n")
        # Write the code from each file
        for file_path in python_files:
            header = f"## `{file_path}`\n\n"
            md_file.write(header)
            # if file_path.split(".")[-1] == ".py":
            md_file.write("```code\n")
            # if file_path.split(".")[-1] == ".yaml":
            #    md_file.write("```yaml\n")
            try:
                with open(file_path, "r", encoding="utf-8") as py_file:
                    content = py_file.read()
                    md_file.write(content)
            except Exception as e:
                md_file.write(f"# Error reading file {file_path}: {e}\n")
            md_file.write("\n```\n\n")
    print(f"Markdown file '{output_file}' has been created.")


def main():
    parser = argparse.ArgumentParser(
        description="Map Python project structure and collect code into a Markdown file."
    )
    parser.add_argument("project_path", help="Path to the Python project")
    parser.add_argument(
        "-o", "--output", default="project_code.md", help="Output Markdown or TXT file"
    )
    args = parser.parse_args()

    python_files = collect_python_files(args.project_path)
    # Sort the files for consistent ordering
    python_files.sort()
    # Generate the project structure
    project_structure = generate_project_structure(args.project_path)
    create_markdown(python_files, args.output, project_structure)


if __name__ == "__main__":
    main()
