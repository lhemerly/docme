import os
import sys
import tempfile
from git import Repo


def clone_repo(git_url, clone_dir):
    """
    Clone a GitHub repository to a specified directory.

    Args:
        git_url (str): The URL of the GitHub repository.
        clone_dir (str): The directory to clone the repository into.
    """
    print(f"Cloning {git_url} into {clone_dir}...")
    Repo.clone_from(git_url, clone_dir)
    print("Repository cloned successfully.")


def parse_rst(file_path):
    """
    Read an .rst file and return its content as is.

    Args:
        file_path (str): The path to the .rst file.

    Returns:
        str: The content of the .rst file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_md(file_path):
    """
    Read a Markdown file and return its content as is.

    Args:
        file_path (str): The path to the Markdown file.

    Returns:
        str: The content of the Markdown file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def traverse_and_parse(repo_dir, output_file):
    """
    Traverse the repository and parse all .rst and .md files.

    Args:
        repo_dir (str): The directory of the cloned repository.
        output_file (str): The file to write the combined content to.
    """
    with open(output_file, "w", encoding="utf-8") as out_f:
        for root, _, files in os.walk(repo_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_dir)
                if file.endswith(".rst"):
                    print(f"Reading {file_path}...")
                    out_f.write(f"File: {relative_path}\n")
                    out_f.write(parse_rst(file_path))
                    out_f.write("\n\n")
                elif file.endswith(".md"):
                    print(f"Reading {file_path}...")
                    out_f.write(f"File: {relative_path}\n")
                    out_f.write(parse_md(file_path))
                    out_f.write("\n\n")
    print(f"Output written to {output_file}")


def main():
    """
    Main function to clone a GitHub repository and parse its documentation files.

    Usage:
        python script.py <github_repo_url>
    """
    if len(sys.argv) != 2:
        print("Usage: python script.py <github_repo_url>")
        sys.exit(1)

    git_url = sys.argv[1]
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            clone_repo(git_url, temp_dir)
            output_file = "output.txt"
            traverse_and_parse(temp_dir, output_file)
            print(f"Combined documentation saved to {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
