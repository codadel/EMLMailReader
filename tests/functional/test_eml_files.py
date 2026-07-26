from pathlib import Path

import pytest

from EMLMailReader import MailReader


pytestmark = pytest.mark.functional

EML_DIRECTORY = Path(__file__).parent / "assets" / "eml-files"
CASES = (
    (
        "Test-Email-One.eml",
        "Chris made appointment with Kenyon to prepare for deposition",
        "mk.balaji@gmail.com",
        "text/plain",
        0,
        0,
        0,
    ),
    (
        "Test-Email-Two.eml",
        "Fracassa call 11/1",
        "ted.chadwick@gmail.com",
        "text/plain",
        0,
        0,
        0,
    ),
    (
        "Test-Email-Three.eml",
        "document checklist for 189 Beavertail Rd",
        "ted.chadwick@gmail.com",
        "multipart/mixed",
        4,
        3,
        0,
    ),
    (
        "Test-Email-Four.eml",
        "View your Microsoft 365 Business Basic invoice",
        "microsoft-noreply@microsoft.com",
        "multipart/mixed",
        2,
        1,
        0,
    ),
    (
        "Test-Email-Five.eml",
        "Test-Email-5",
        "maheshkumaar.balaji@outlook.com",
        "multipart/mixed",
        2,
        1,
        0,
    ),
    (
        "Test-Email-Six.eml",
        "Test Email 6 - Sent via Gmail web",
        "maheshkumaar.balaji@gmail.com",
        "multipart/alternative",
        2,
        0,
        0,
    ),
    (
        "Test-Email-Seven.eml",
        "Re: Test Email 6 - Sent via Gmail web",
        "maheshkumaar.balaji@mkbdgs.com",
        "multipart/alternative",
        2,
        0,
        0,
    ),
    (
        "Test-Email-Eight.eml",
        "Test Mail 8 - Sent from Apple Mail",
        "maheshkumaar.balaji@gmail.com",
        "multipart/related",
        2,
        0,
        1,
    ),
)


@pytest.mark.parametrize(
    (
        "filename",
        "subject",
        "from_address",
        "media_type",
        "child_count",
        "attachment_count",
        "inline_count",
    ),
    CASES,
    ids=[case[0].removesuffix(".eml") for case in CASES],
)
def test_real_eml_files_parse_into_expected_message_tree(
    filename,
    subject,
    from_address,
    media_type,
    child_count,
    attachment_count,
    inline_count,
):
    message = MailReader().get_email(str(EML_DIRECTORY / filename))

    assert message is not None
    assert message.Subject == subject
    assert message.From.Mailboxes[0].Email == from_address
    assert message.ContentType.MediaType == media_type
    assert len(message.Children) == child_count
    assert len(message.Attachments) == attachment_count
    assert len(message.InlineResources) == inline_count
    assert message.RawSource
    assert not any(item.severity.value == "error" for item in message.Diagnostics)
