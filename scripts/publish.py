import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from python_git_wrapper import Repository  # type: ignore


class VersionHandler:
    def __init__(self, version_file: Path):
        if not version_file.is_file():
            raise FileNotFoundError("Invalid Version File")
        self.version_file = version_file
        self.file_content = version_file.read_text()
        match = re.search(r"__version__ *= *\"(\d)\.(\d)\.(\d)\"", self.file_content)
        if not match or len(match.groups()) != 3:
            raise LookupError("No version line on file")
        self.version_line = match[0]
        self.major: int = int(match[1])
        self.minor: int = int(match[2])
        self.build: int = int(match[3])

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.build}"

    def update_file(self) -> None:
        new_text = self.file_content.replace(
            self.version_line, f'__version__ = "{self.__str__()}"'
        )
        self.version_file.write_text(new_text)


class GitHandler:
    def __init__(self, git_path: Path):
        self.repo = Repository(path=str(git_path))

    def is_dirty(self) -> bool:
        status = self.repo.status()
        return status.modified or status.added or status.deleted or status.renamed or status.untracked

    def print_dirty(self) -> None:
        status = self.repo.status()
        for m in status.modified:
            print(f"{m} --- Modified")
        for a in status.added:
            print(f"{a} --- Added")
        for d in status.deleted:
            print(f"{d} --- Deleted ")
        for r in status.renamed:
            print(f"{r} --- Renamed")
        for u in status.untracked:
            print(f"{u} --- Untracked")

    def push_version(self, ver: VersionHandler) -> None:
        self.repo.commit(message=f"Publish New Package Version: {str(ver)}", add_files=True)
        self.repo.push()


if __name__ == "__main__":
    parser = ArgumentParser(prog="publish")
    parser.add_argument("--package", help="path to the package")
    parser.add_argument("--password", help="pypi password")
    args = parser.parse_args()

    if args.package:
        os.chdir(args.package)
    if args.password:
        os.putenv("FLIT_PASSWORD", args.password)

    git = GitHandler(git_path=Path('.'))
    if git.is_dirty():
        print("Git is dirty - please review the following files:")
        git.print_dirty()
        sys.exit(-1)

    package_init = Path("./fastapi_msal/__init__.py").resolve()
    version = VersionHandler(version_file=package_init)
    version.build += 1
    version.update_file()

    git.push_version(ver=version)

    completed = subprocess.run(
        ["flit", "publish"], text=True, stderr=subprocess.STDOUT, check=False
    )
    print(completed.stdout)
    sys.exit(completed.returncode)
