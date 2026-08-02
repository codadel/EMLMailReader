# Inspect ordered and repeated headers

`HeaderCollection` behaves like a sequence of `HeaderField` occurrences and
also provides case-insensitive lookup.

```python
# Last decoded Subject value, or None.
subject = message.Headers.get("subject")

# Every Received value in source order, without encoded-word decoding.
received = message.Headers.get_all("Received", decoded=False)

# Complete structured occurrences.
for field in message.Headers.occurrences("X-Tracking-ID"):
    print(field.index, field.raw_name, field.raw_value)
```

## Choose the appropriate representation

| Property | Use |
| --- | --- |
| `raw_value` | Preserve folded source text |
| `unfolded_value` | Inspect source semantics without folding |
| `decoded_value` | Work with interpreted Unicode text |
| `syntax_status` | Separate current, obsolete, and invalid syntax |

Do not convert all headers into a normal dictionary when duplicate values or
source order matter. Use `Headers.to_list()` for a JSON-compatible ordered
representation.

Structured projections such as `Date`, `MessageID`, `ResentBlocks`, and
`TraceBlocks` complement the header collection; they do not replace it.
