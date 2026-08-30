import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "new_scratch.py"
SPEC = importlib.util.spec_from_file_location("new_scratch", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NewScratchTests(unittest.TestCase):
    def test_task_slug(self):
        self.assertEqual(MODULE.task_slug("USSEP 4.3.9 audit"), "ussep-4-3-9-audit")
        with self.assertRaises(ValueError):
            MODULE.task_slug("---")

    def test_create_project(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mutagen = root / "Mutagen"
            project = mutagen / "Mutagen.Bethesda.Skyrim" / "Mutagen.Bethesda.Skyrim.csproj"
            project.parent.mkdir(parents=True)
            project.write_text("<Project />", encoding="utf-8")
            output = root / "scratch"

            with patch.dict(os.environ, {"MUTAGEN_ROOT": str(mutagen)}):
                result = MODULE.create_project("Record Audit", output)

            self.assertEqual(result, output)
            self.assertEqual(
                sorted(path.name for path in output.iterdir()),
                ["Program.cs", "Scratch.csproj"],
            )

    def test_existing_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mutagen = root / "Mutagen"
            project = mutagen / "Mutagen.Bethesda.Skyrim" / "Mutagen.Bethesda.Skyrim.csproj"
            project.parent.mkdir(parents=True)
            project.write_text("<Project />", encoding="utf-8")
            output = root / "existing"
            output.mkdir()

            with patch.dict(os.environ, {"MUTAGEN_ROOT": str(mutagen)}):
                with self.assertRaises(FileExistsError):
                    MODULE.create_project("test", output)


if __name__ == "__main__":
    unittest.main()
