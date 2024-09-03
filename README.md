# Pick

**pick** is a more powerful alternative to `head`/`tail`/`cat`/`tac`/... to pick lines from a text file.

## Usage

```
Python-like list-subscription expression, but 1-based!
    cat ... | pick 1            # pick the first line
    cat ... | pick -1           # pick the last line
    cat ... | pick :            # pick all lines
    cat ... | pick ::           # pick all lines
    cat ... | pick 2:           # pick all lines except the first line
    cat ... | pick :-1          # pick all lines except the last line
    cat ... | pick ::-1         # pick all lines (in reverse order)
    cat ... | pick 3:1:-1       # pick the first 3 lines (in reverse order)
    cat ... | pick ::2          # pick every other line
    ... (and more)

Dash-split range expression:
    cat ... | pick 1-3          # pick the first 3 lines
    cat ... | pick 5-10         # pick the 5th to 10th lines
    cat ... | pick 10-1         # pick the 10th to 1st lines (in reverse order)

Comma-split mixed expression:
    cat ... | pick 1,3::,5-7    # pick the 1st, then all except the first two, then the 5th to 7th lines
```

## License

[MIT](./LICENSE) License.
