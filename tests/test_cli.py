"""Tests for the CLI interface."""

import json

from devlog.cli import main


def test_add_and_list(tmp_path, capsys):
    d = str(tmp_path)
    main(["--dir", d, "add", "test note"])
    captured = capsys.readouterr()
    assert "Added:" in captured.out

    main(["--dir", d, "list"])
    captured = capsys.readouterr()
    assert "test note" in captured.out


def test_add_with_tags(tmp_path, capsys):
    d = str(tmp_path)
    main(["--dir", d, "add", "-t", "bug", "-t", "urgent", "fix login"])
    main(["--dir", d, "list"])
    captured = capsys.readouterr()
    assert "bug" in captured.out
    assert "urgent" in captured.out


def test_search(tmp_path, capsys):
    d = str(tmp_path)
    main(["--dir", d, "add", "hello world"])
    main(["--dir", d, "add", "goodbye world"])
    main(["--dir", d, "search", "hello"])
    captured = capsys.readouterr()
    assert "hello" in captured.out
    assert "goodbye" not in captured.out.split("hello")[-1]


def test_tags_command(tmp_path, capsys):
    d = str(tmp_path)
    main(["--dir", d, "add", "-t", "python", "note 1"])
    main(["--dir", d, "add", "-t", "python", "-t", "cli", "note 2"])
    main(["--dir", d, "tags"])
    captured = capsys.readouterr()
    assert "python (2)" in captured.out
    assert "cli (1)" in captured.out


def test_delete(tmp_path, capsys):
    d = str(tmp_path)
    main(["--dir", d, "add", "to delete"])
    captured = capsys.readouterr()
    note_id = captured.out.strip().split()[-1]

    main(["--dir", d, "delete", note_id])
    captured = capsys.readouterr()
    assert "Deleted:" in captured.out


def test_export(tmp_path, capsys):
    d = str(tmp_path)
    main(["--dir", d, "add", "exportable"])
    capsys.readouterr()  # clear add output
    main(["--dir", d, "export"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 1


def test_empty_list(tmp_path, capsys):
    d = str(tmp_path)
    main(["--dir", d, "list"])
    captured = capsys.readouterr()
    assert "No notes" in captured.out


def test_no_command(capsys):
    ret = main([])
    assert ret == 0
