#!/usr/bin/env python3
import os
import re
import argparse
import sys


def is_readonly_path(path):
    """
    Checks if the given path is a system critical or read-only directory.

    Parameters:
        path (str): The path to check.

    Returns:
        bool: True if the path is read-only or system critical, False otherwise.
    """
    # Common system directories to prevent writing into
    system_dirs = [
        "/",
        "/bin",
        "/boot",
        "/dev",
        "/etc",
        "/home",
        "/lib",
        "/lib64",
        "/media",
        "/mnt",
        "/opt",
        "/proc",
        "/root",
        "/run",
        "/sbin",
        "/srv",
        "/sys",
        "/tmp",
        "/usr",
        "/var",
    ]

    abs_path = os.path.abspath(path)
    for sys_dir in system_dirs:
        if abs_path == sys_dir or abs_path.startswith(sys_dir + os.sep):
            return True
    return False


def create_project_structure(structure_str: str, target_path: str):
    """
    Creates directories and files based on a tree-like structure string.

    Parameters:
        structure_str (str): The tree-like string representing the project structure.
        target_path (str): The path where the project structure will be created.
    """
    # Validate target_path is writable and not a system directory
    if is_readonly_path(target_path):
        print(
            f"Error: Target path '{target_path}' is a system directory or read-only. Please choose a writable directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.access(target_path, os.W_OK):
        print(f"Error: Target path '{target_path}' is not writable.", file=sys.stderr)
        sys.exit(1)

    # Ensure the target path exists
    try:
        os.makedirs(target_path, exist_ok=True)
        print(f"Target directory ensured: {target_path}")
    except Exception as e:
        print(f"Error creating target directory '{target_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Split the structure string into lines
    lines = structure_str.strip().splitlines()

    # Stack to keep track of the current path based on depth
    # stack[0] = target_path
    stack = [os.path.abspath(target_path)]

    for line_number, line in enumerate(lines, start=1):
        # Ignore empty lines
        if not line.strip():
            continue

        original_line = line  # Keep the original line for debugging

        # Determine the depth by counting leading indentations
        # Each '│   ' or '    ' counts as one indentation level
        depth = 0
        while line.startswith("│   ") or line.startswith("    "):
            depth += 1
            line = line[4:]

        # Remove the tree branch characters like '├── ' or '└── '
        name = re.sub(r"^[├└]──\s*", "", line).rstrip()

        # Debugging statements
        print(f"Processing Line {line_number}: '{original_line}'")
        print(f"Determined Depth: {depth}")
        print(f"Extracted Name: '{name}'")
        print(f"Current Path Stack: {stack}")

        # Determine if it's a directory or a file
        if name.endswith("/"):
            # It's a directory
            dir_name = name.rstrip("/")
            # Parent directory is at current depth
            if depth >= len(stack):
                print(
                    f"Error: Depth {depth} exceeds stack size {len(stack)}. Using last directory in stack as parent."
                )
                parent_dir = stack[-1]
            else:
                parent_dir = stack[depth]
            current_dir = os.path.join(parent_dir, dir_name)
            # Create the directory
            try:
                os.makedirs(current_dir, exist_ok=True)
                print(f"Created directory: {current_dir}")
            except Exception as e:
                print(
                    f"Failed to create directory '{current_dir}': {e}", file=sys.stderr
                )
                continue  # Skip adding to stack if directory creation failed
            # Update the stack
            if depth + 1 < len(stack):
                stack[depth + 1] = current_dir
                stack = stack[: depth + 2]
            else:
                stack.append(current_dir)
        else:
            # It's a file
            file_name = name
            # Parent directory is at current depth
            if depth >= len(stack):
                print(
                    f"Error: Depth {depth} exceeds stack size {len(stack)}. Using last directory in stack as parent."
                )
                parent_dir = stack[-1]
            else:
                parent_dir = stack[depth]
            file_path = os.path.join(parent_dir, file_name)
            # Create the file
            try:
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        pass  # Create an empty file
                    print(f"Created file: {file_path}")
                else:
                    print(f"File already exists: {file_path}")
            except Exception as e:
                print(f"Failed to create file '{file_path}': {e}", file=sys.stderr)

    print("Project structure creation completed.")


def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Create a Python project structure from a tree-like structure file."
    )
    parser.add_argument(
        "structure_file",
        type=str,
        help="Path to the file containing the project structure.",
    )
    parser.add_argument(
        "target_path",
        type=str,
        help="Path where the project structure will be created.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output."
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Read the structure string from the file
    try:
        with open(args.structure_file, "r", encoding="utf-8") as f:
            structure_str = f.read()
        if not structure_str.strip():
            print(
                f"Error: The structure file '{args.structure_file}' is empty.",
                file=sys.stderr,
            )
            sys.exit(1)
    except FileNotFoundError:
        print(
            f"Error: The structure file '{args.structure_file}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(
            f"Error reading structure file '{args.structure_file}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create the project structure
    create_project_structure(structure_str, args.target_path)


if __name__ == "__main__":
    main()
