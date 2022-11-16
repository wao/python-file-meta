import typer
from pathlib import Path
from file_meta.repo import Repo, QueryResult, uniqid

app = typer.Typer()

repo = Repo(Path("~/.local/file_meta").expanduser())

@app.command()
def old_main( file_name: Path ):
    if not file_name.is_file():
        print(f"{file_name} is not a file, can't handle")
        exit(0)

@app.command()
def status( file_name: Path ):
    s = None
    status = repo.query(file_name)
    if status == QueryResult.NEW:
        s = "?"
    elif status == QueryResult.NEW_NAME:
        s = "+"
    elif status == QueryResult.DIRTY:
        s = "M"
    elif status == QueryResult.SAME:
        s = "S" 

    if s:
        print(f"{s}   {file_name}")

@app.command()
def add( file_name: Path ):
    fh = repo.file_helper(file_name)
    status = fh.query()
    if status == QueryResult.NEW:
        fh.create_infos()
    elif status == QueryResult.NEW_NAME:
        #detect move???
        fh.add_staging_info()
    elif status == QueryResult.DIRTY:
        fh.update_infos()


def run():
    app()
