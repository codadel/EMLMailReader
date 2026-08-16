# Work with addresses and groups

`From`, `Sender`, `ReplyTo`, `To`, `Cc`, and `Bcc` are `AddressList` objects.
They preserve top-level mailbox and group boundaries.

## Flatten participants

```python
for mailbox in message.To.Mailboxes:
    print(mailbox.DisplayName, mailbox.Email)
    print(mailbox.LocalPart, mailbox.Domain)
```

`Mailboxes` returns an immutable tuple containing direct and grouped mailboxes.

## Preserve group structure

```python
from EMLMailReader import AddressGroup

for item in message.To:
    if isinstance(item, AddressGroup):
        print("group", item.display_name)
        for mailbox in item.addresses:
            print(" member", mailbox.Email)
    else:
        print("mailbox", item.Email)
```

This distinction matters for values such as:

```text
Analytics: alice@example.com, bob@example.com; Undisclosed recipients:;
```

## Normalize or serialize

```python
normalized = message.To.to_header_value()
records = message.To.to_dict()
```

`to_dict()` emits ordered records with a `type` of `mailbox` or `group`.
Internationalized source values are marked on each `MailAddress` through
`IsInternationalized`.
