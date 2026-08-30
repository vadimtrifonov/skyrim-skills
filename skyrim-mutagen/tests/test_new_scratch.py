import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "new_scratch.py"
WRITE_SMOKE = Path(__file__).resolve().parent / "fixtures" / "WriteSmoke.cs"


class NewScratchTests(unittest.TestCase):
    def assert_process(self, command, *, env=None, returncode=0, timeout=120):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
            check=False,
        )
        rendered = subprocess.list2cmdline([str(part) for part in command])
        self.assertEqual(
            result.returncode,
            returncode,
            f"command: {rendered}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def create_scratch(self, task_name, mutagen_root):
        env = os.environ.copy()
        env["MUTAGEN_ROOT"] = str(mutagen_root)
        result = self.assert_process(
            [sys.executable, str(SCRIPT), task_name],
            env=env,
        )
        output = Path(result.stdout.strip())
        self.addCleanup(shutil.rmtree, output, ignore_errors=True)
        return output

    def test_scaffold_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            mutagen = Path(temporary) / "Mutagen"
            project = mutagen / "Mutagen.Bethesda.Skyrim" / "Mutagen.Bethesda.Skyrim.csproj"
            project.parent.mkdir(parents=True)
            project.write_text("<Project />", encoding="utf-8")
            output = self.create_scratch("Record Audit", mutagen)

        self.assertTrue(output.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.assertTrue(output.name.startswith("skyrim-mutagen-record-audit-"))
        self.assertEqual(
            sorted(path.name for path in output.iterdir()),
            ["Program.cs", "Scratch.csproj"],
        )

    @unittest.skipUnless(
        os.environ.get("SKYRIM_MUTAGEN_INTEGRATION") == "1",
        "set SKYRIM_MUTAGEN_INTEGRATION=1 to build the generated project",
    )
    def test_generated_projects_build_and_run(self):
        dotnet = shutil.which("dotnet")
        self.assertIsNotNone(dotnet, "dotnet is unavailable")
        self.assertIn("MUTAGEN_ROOT", os.environ)

        output = self.create_scratch("integration", os.environ["MUTAGEN_ROOT"])
        project = output / "Scratch.csproj"

        self.assert_process(
            [dotnet, "build", str(project), "--nologo", "-clp:ErrorsOnly"],
            timeout=600,
        )
        usage = self.assert_process(
            [dotnet, "run", "--no-build", "--project", str(project)],
            returncode=2,
        )
        self.assertIn("Usage: Scratch", usage.stderr)

        (output / "Program.cs").write_text(
            WRITE_SMOKE.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.assert_process(
            [dotnet, "build", str(project), "--nologo", "-clp:ErrorsOnly"],
            timeout=600,
        )
        write = self.assert_process(
            [
                dotnet,
                "run",
                "--no-build",
                "--project",
                str(project),
                "--",
                str(output),
            ]
        )
        self.assertIn("write smoke passed", write.stdout)


if __name__ == "__main__":
    unittest.main()
