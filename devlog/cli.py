"""Command-line interface for devlog."""

import argparse
import sys

from . import __version__
from .store import LogStore


def build_parser():
    parser = argparse.ArgumentParser(
        prog="devlog",
        description="Minimal developer notes from the terminal.",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"devlog {__version__}"
    )
    parser.add_argument(
        "-d", "--dir",
        help="Path to devlog directory (default: ~/.devlog)",
    )

    sub = parser.add_subparsers(dest="command")

    # add
    add_p = sub.add_parser("add", help="Add a new note")
    add_p.add_argument("message", nargs="+", help="Note text")
    add_p.add_argument("-t", "--tag", action="append", default=[], help="Tag the note")

    # list
    list_p = sub.add_parser("list", aliases=["ls"], help="List recent notes")
    list_p.add_argument("-n", "--count", type=int, default=10, help="Number of notes")
    list_p.add_argument("-t", "--tag", help="Filter by tag")
    list_p.add_argument("--all", action="store_true", help="Show all notes")

    # search
    search_p = sub.add_parser("search", help="Search notes")
    search_p.add_argument("query", help="Search term")

    # tags
    sub.add_parser("tags", help="List all tags")

    # edit
    edit_p = sub.add_parser("edit", help="Edit a note by ID")
    edit_p.add_argument("note_id", help="Note ID (or prefix)")

    # delete
    del_p = sub.add_parser("delete", aliases=["rm"], help="Delete a note by ID")
    del_p.add_argument("note_id", help="Note ID (or prefix)")

    # export
    export_p = sub.add_parser("export", help="Export notes as JSON")
    export_p.add_argument("-o", "--output", help="Output file (default: stdout)")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    store = LogStore(base_dir=args.dir)

    if args.command == "add":
        text = " ".join(args.message)
        note = store.add(text, tags=args.tag)
        print(f"Added: {note['id'][:8]}")

    elif args.command in ("list", "ls"):
        count = None if args.all else args.count
        notes = store.list_notes(count=count, tag=args.tag)
        if not notes:
            print("No notes found.")
            return 0
        for note in notes:
            tags_str = ""
            if note.get("tags"):
                tags_str = " [" + ", ".join(note["tags"]) + "]"
            print(f"  {note['id'][:8]}  {note['date']}  {note['text']}{tags_str}")

    elif args.command == "search":
        results = store.search(args.query)
        if not results:
            print("No matches.")
            return 0
        for note in results:
            print(f"  {note['id'][:8]}  {note['date']}  {note['text']}")

    elif args.command == "tags":
        tags = store.list_tags()
        if not tags:
            print("No tags found.")
            return 0
        for tag, count in sorted(tags.items()):
            print(f"  {tag} ({count})")

    elif args.command == "edit":
        note = store.get_by_prefix(args.note_id)
        if not note:
            print(f"Note not found: {args.note_id}", file=sys.stderr)
            return 1
        new_text = _edit_in_editor(note["text"])
        if new_text is not None and new_text != note["text"]:
            store.update(note["id"], new_text)
            print(f"Updated: {note['id'][:8]}")
        else:
            print("No changes.")

    elif args.command in ("delete", "rm"):
        note = store.get_by_prefix(args.note_id)
        if not note:
            print(f"Note not found: {args.note_id}", file=sys.stderr)
            return 1
        store.delete(note["id"])
        print(f"Deleted: {note['id'][:8]}")

    elif args.command == "export":
        data = store.export_json()
        if args.output:
            with open(args.output, "w") as f:
                f.write(data)
            print(f"Exported to {args.output}")
        else:
            print(data)

    return 0


def _edit_in_editor(text):
    """Open text in $EDITOR for editing."""
    import os
    import tempfile

    editor = os.environ.get("EDITOR", "vi")
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(text)
        tmp_path = f.name

    try:
        ret = os.system(f'{editor} "{tmp_path}"')
        if ret != 0:
            return None
        with open(tmp_path) as f:
            return f.read()
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    sys.exit(main())
