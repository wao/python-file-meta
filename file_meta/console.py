import typer
from pathlib import Path
from file_meta.repo import Repo, QueryResult

repo = Repo(Path("~/.local/file_meta").expanduser())

def old_main( file_name: Path ):
    if not file_name.is_file():
        print(f"{file_name} is not a file, can't handle")
        exit(0)

def status( file_name: Path ):
    status = repo.query(file_name)
    if status == QueryResult.NEW:
        print("New file")
    elif status == QueryResult.NEW_NAME:
        print("New name for old file")
    elif status == QueryResult.DIRTY:
        print("Dirty file")
    elif status == QueryResult.SAME:
        print("Same file")


def run():
    typer.run(status)
