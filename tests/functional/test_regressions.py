"""Regression tests for EML files attached to resolved issues."""

from hashlib import sha256
from pathlib import Path

import pytest

from EMLMailReader import MailReader


pytestmark = pytest.mark.functional

REGRESSION_DIRECTORY = Path(__file__).parent / "regressions"
ISSUE_3_SOURCE = REGRESSION_DIRECTORY / "issue-3-body-and-attachment.eml"
ISSUE_3_SOURCE_SHA256 = (
    "87a6069217b8f6dca7a991384f4d9414549c12a13bf1bddabf5c0de4b960dd86"
)
ISSUE_3_BODY = "This email has both body text and an attachment\r\n"


def test_issue_3_preserves_body_when_attachment_follows():
    """Keep the body when parsing the exact EML reported in GitHub issue #3."""
    source = ISSUE_3_SOURCE.read_bytes()

    assert sha256(source).hexdigest() == ISSUE_3_SOURCE_SHA256

    message = MailReader().get_email(str(ISSUE_3_SOURCE))

    assert message is not None
    assert message.RawSource == source
    assert message.Subject == "An Email with a body and an attachment"
    assert message.Body == ISSUE_3_BODY
    assert message.TextBody == ISSUE_3_BODY
    assert message.HtmlBody == ""
    assert len(message.Children) == 2
    assert len(message.Attachments) == 1

    attachment = message.Attachments[0]
    assert attachment.Name == "find_x_lol.jpg"
    assert attachment.ContentType.MediaType == "image/jpeg"
    assert attachment.IsAttachment
    assert not any(
        diagnostic.severity.value == "error"
        for diagnostic in message.Diagnostics
    )
