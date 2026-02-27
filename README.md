# devlog

Minimal CLI for developer notes and journaling from the terminal.

## Install

```bash
pip install -e .
```

## Usage

```bash
# Add a note
devlog add "fixed the timezone bug in the parser"

# Add with tags
devlog add -t bug -t python "off-by-one in date calculation"

# List recent notes
devlog list
devlog list -n 20
devlog list --tag bug

# Search
devlog search "timezone"

# View all tags
devlog tags

# Edit a note (opens $EDITOR)
devlog edit a1b2c3d4

# Delete
devlog delete a1b2c3d4

# Export as JSON
devlog export
devlog export -o backup.json
```

## Storage

Notes are stored as JSON in `~/.devlog/notes.json`. Override with `--dir`.

## License

MIT
