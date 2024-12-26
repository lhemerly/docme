import os
import tempfile
import sys
import ast
from git import Repo

def clone_repo(git_url, clone_dir):
    print(f"Cloning {git_url} into {clone_dir}...")
    Repo.clone_from(git_url, clone_dir)
    print("Repository cloned successfully.")

def extract_docstrings(file_path):
    """
    Extract docstrings from a Python file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    docstrings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node)
            if docstring:
                name = node.name if hasattr(node, "name") else "<module>"
                docstrings.append((file_path, name, docstring))
    return docstrings

def traverse_and_parse(repo_dir, output_file):
    """
    Traverse the docs repo and parse all .md files
    (excluding Sphinx placeholder .md files that contain ```{toctree}).
    """
    with open(output_file, "w", encoding="utf-8") as out_f:
        for root, _, files in os.walk(repo_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_dir)

                # .md
                if file.endswith(".md"):
                    # Check if it has a Sphinx toctree directive
                    with open(file_path, "r", encoding="utf-8") as check_f:
                        content = check_f.read()
                        if "```{toctree}" in content:
                            # Skip these "index" or "toctree" placeholders
                            continue

                    print(f"Reading {file_path}...")
                    out_f.write(f"File: {relative_path}\n")
                    out_f.write(content)
                    out_f.write("\n\n")

def parse_docstrings(library_repo_dir, output_file):
    """
    Parse all Python files in the library repo and extract docstrings.
    """
    with open(output_file, "w", encoding="utf-8") as out_f:
        for root, _, files in os.walk(library_repo_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    print(f"Extracting docstrings from {file_path}...")
                    docstrings = extract_docstrings(file_path)
                    for file_path, name, docstring in docstrings:
                        out_f.write(f"File: {file_path}\n")
                        out_f.write(f"Function/Class: {name}\n")
                        out_f.write(f"Docstring:\n{docstring}\n\n")

    print(f"Docstrings extracted and saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <github_docs_url> <github_library_url>")
        sys.exit(1)

    docs_git_url = sys.argv[1]
    library_git_url = sys.argv[2]

    with tempfile.TemporaryDirectory() as temp_dir:
        docs_dir = os.path.join(temp_dir, "docs_repo")
        lib_dir = os.path.join(temp_dir, "library_repo")

        try:
            # 1) Clone both repos
            clone_repo(docs_git_url, docs_dir)
            clone_repo(library_git_url, lib_dir)

            # 2) Parse the manual docs (md)
            manual_docs_output_file = os.path.join(temp_dir, "manual_docs.txt")
            traverse_and_parse(docs_dir, manual_docs_output_file)

            # 3) Parse the docstrings from the library code
            docstrings_output_file = os.path.join(temp_dir, "docstrings.txt")
            parse_docstrings(lib_dir, docstrings_output_file)

            # 4) Combine them into a single final file
            final_output_file = "combined_output.md"  # or .txt, your choice
            with open(final_output_file, "w", encoding="utf-8") as out_f:
                out_f.write("# Manual `.md` Documentation\n\n")
                with open(manual_docs_output_file, "r", encoding="utf-8") as f:
                    out_f.write(f.read())

                out_f.write("# Auto-Extracted Docstrings\n\n")
                with open(docstrings_output_file, "r", encoding="utf-8") as f:
                    out_f.write(f.read())

            print(f"Final merged file with everything: {final_output_file}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
