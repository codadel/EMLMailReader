import unittest

from EMLMailReader import FileMissingError, FolderNotAvailableError


class TestCustomExceptions(unittest.TestCase):
    def test_file_missing_error_mentions_path(self):
        error = FileMissingError("/missing/message.eml")
        try:
            raise error
        except FileMissingError as caught:
            self.assertIn("/missing/message.eml", str(caught))

    def test_folder_not_available_error_mentions_path(self):
        error = FolderNotAvailableError("/missing/output")
        try:
            raise error
        except FolderNotAvailableError as caught:
            self.assertIn("/missing/output", str(caught))


if __name__ == "__main__":
    unittest.main()
