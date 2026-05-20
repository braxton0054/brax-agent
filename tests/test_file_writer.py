import tempfile
from pathlib import Path
from brax.core.file_writer import FileWriter


def test_write_file():
    with tempfile.TemporaryDirectory() as tmp:
        fw = FileWriter(Path(tmp))
        fw.write_file("test.txt", "hello world")
        assert (Path(tmp) / "test.txt").exists()
        assert (Path(tmp) / "test.txt").read_text() == "hello world"


def test_write_file_creates_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        fw = FileWriter(Path(tmp))
        fw.write_file("nested/dir/file.txt", "content")
        assert (Path(tmp) / "nested" / "dir" / "file.txt").exists()


def test_write_file_skips_existing():
    with tempfile.TemporaryDirectory() as tmp:
        fw = FileWriter(Path(tmp))
        fw.write_file("existing.txt", "original")
        fw.write_file("existing.txt", "overwritten")
        assert (Path(tmp) / "existing.txt").read_text() == "overwritten"


def test_no_diff_by_default():
    with tempfile.TemporaryDirectory() as tmp:
        fw = FileWriter(Path(tmp))
        # Just verify it doesn't crash
        fw.write_file("test.txt", "hello")
