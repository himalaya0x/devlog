"""Tests for the LogStore backend."""

import json
import os
import tempfile

import pytest

from devlog.store import LogStore


@pytest.fixture
def tmp_store(tmp_path):
    return LogStore(base_dir=str(tmp_path))


def test_add_note(tmp_store):
    note = tmp_store.add("hello world")
    assert note["text"] == "hello world"
    assert len(note["id"]) == 12
    assert note["tags"] == []


def test_add_with_tags(tmp_store):
    note = tmp_store.add("tagged note", tags=["python", "debug"])
    assert note["tags"] == ["python", "debug"]


def test_list_notes(tmp_store):
    tmp_store.add("first")
    tmp_store.add("second")
    tmp_store.add("third")
    notes = tmp_store.list_notes()
    assert len(notes) == 3
    assert notes[0]["text"] == "third"  # most recent first


def test_list_with_count(tmp_store):
    for i in range(5):
        tmp_store.add(f"note {i}")
    notes = tmp_store.list_notes(count=3)
    assert len(notes) == 3


def test_list_filter_by_tag(tmp_store):
    tmp_store.add("no tag")
    tmp_store.add("has tag", tags=["important"])
    tmp_store.add("also tagged", tags=["important", "bug"])
    notes = tmp_store.list_notes(tag="important")
    assert len(notes) == 2


def test_search(tmp_store):
    tmp_store.add("fix the login bug")
    tmp_store.add("update readme")
    tmp_store.add("another bug fix")
    results = tmp_store.search("bug")
    assert len(results) == 2


def test_search_by_tag(tmp_store):
    tmp_store.add("some note", tags=["refactor"])
    results = tmp_store.search("refactor")
    assert len(results) == 1


def test_list_tags(tmp_store):
    tmp_store.add("a", tags=["python"])
    tmp_store.add("b", tags=["python", "cli"])
    tmp_store.add("c", tags=["cli"])
    tags = tmp_store.list_tags()
    assert tags["python"] == 2
    assert tags["cli"] == 2


def test_get_by_prefix(tmp_store):
    note = tmp_store.add("findable note")
    found = tmp_store.get_by_prefix(note["id"][:4])
    assert found["id"] == note["id"]


def test_get_by_prefix_not_found(tmp_store):
    assert tmp_store.get_by_prefix("nonexistent") is None


def test_update(tmp_store):
    note = tmp_store.add("original text")
    tmp_store.update(note["id"], "updated text")
    found = tmp_store.get_by_prefix(note["id"][:4])
    assert found["text"] == "updated text"
    assert "modified" in found


def test_delete(tmp_store):
    note = tmp_store.add("to delete")
    tmp_store.add("to keep")
    tmp_store.delete(note["id"])
    notes = tmp_store.list_notes()
    assert len(notes) == 1
    assert notes[0]["text"] == "to keep"


def test_export_json(tmp_store):
    tmp_store.add("exportable")
    data = tmp_store.export_json()
    parsed = json.loads(data)
    assert len(parsed) == 1
    assert parsed[0]["text"] == "exportable"


def test_empty_store(tmp_store):
    assert tmp_store.list_notes() == []
    assert tmp_store.search("anything") == []
    assert tmp_store.list_tags() == {}
