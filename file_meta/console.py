import typer
from pathlib import Path
from file_meta.repo import Repo, QueryResult, uniqid, Comment

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

    fh = repo.file_helper(file_name)
    if fh.has_object_info():
        print("Tags")
        print(",".join(list(fh.tags)))
        print("Comments")
        #for comment in fh.comments.values():
            #print(comment)
        for comment in sorted(fh.comments.values(), key=lambda comment: comment["mtime"]):
            print( f"{comment['uid']} at {comment['mtime']}:")
            print( f"  {comment['content']}")

        print("Metas")
        for k in fh.metas.items():
            print(f"{k[0]}={k[1]}")

@app.command()
def meta( file_name : Path, meta_name : str, meta_value : str ):
    repo.file_helper(file_name).add_meta(meta_name, meta_value)
    print(f"Set meta {meta_name}={meta_value}")

@app.command()
def tag( file_name : Path, tags : list[str] ):
    fh = repo.file_helper(file_name)
    for tag in tags:
        fh.add_tag(tag)

    print(f"Add tag(s) {tags}")

@app.command()
def comment( file_name : Path, words : list[str] ):
    comment = " ".join(words)
    fh = repo.file_helper(file_name).add_comment(comment)
    print(f"Add comment {comment}")


@app.command()
def add( file_name: Path ):
    fh = repo.file_helper(file_name)
    status = fh.query()
    if status == QueryResult.NEW:
        fh.create_infos()
        print("Added")
    elif status == QueryResult.NEW_NAME:
        #detect move???
        fh.add_staging_info()
        print("Linked")
    elif status == QueryResult.DIRTY:
        fh.replace_infos()
        print("Replaced")
    else:
        print("Do nothing")


def run():
    app()
