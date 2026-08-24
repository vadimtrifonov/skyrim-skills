import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from get_record import RecordLookupError, get_record
from list_records import list_records


class RecordToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "Test.spriggit"
        self.write_json("RecordData.json", {"ModKey": "Test.esp"})
        self.write_json(
            "Quests/TestQuest.json",
            {
                "FormKey": "000001:Test.esp",
                "EditorID": "TestQuest",
                "MajorRecordFlagsRaw": 32,
            },
        )
        self.write_json(
            "Cells/0/0/TestCell/RecordData.json",
            {
                "FormKey": "000100:Skyrim.esm",
                "EditorID": "TestCell",
                "Persistent": [
                    {
                        "MutagenObjectType": "PlacedObject",
                        "FormKey": "000002:Test.esp",
                        "EditorID": "TestReference",
                        "Base": "000001:Test.esp",
                    }
                ],
                "NavigationMeshes": [
                    {
                        "FormKey": "000200:Skyrim.esm",
                    }
                ],
                "LinkedRecord": "000002:Test.esp",
            },
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_json(self, relative_path: str, value: object) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_list_records_keeps_normalized_output(self) -> None:
        records = list_records(self.root)
        self.assertEqual(
            [(item["type"], item["formKey"]) for item in records],
            [
                ("Cell", "000100:Skyrim.esm"),
                ("NavigationMesh", "000200:Skyrim.esm"),
                ("PlacedObject", "000002:Test.esp"),
                ("Quest", "000001:Test.esp"),
            ],
        )
        quest = next(item for item in records if item["type"] == "Quest")
        self.assertEqual(quest["kind"], "new")
        self.assertTrue(quest["deleted"])

    def test_gets_top_level_and_embedded_records(self) -> None:
        top_level = get_record(self.root, "000001:test.ESP")
        self.assertEqual(top_level["source"], "Quests/TestQuest.json")
        self.assertEqual(top_level["path"], [])
        self.assertEqual(top_level["record"]["EditorID"], "TestQuest")

        embedded = get_record(self.root, "000002:Test.esp")
        self.assertEqual(embedded["source"], "Cells/0/0/TestCell/RecordData.json")
        self.assertEqual(embedded["path"], ["Persistent", 0])
        self.assertEqual(embedded["record"]["EditorID"], "TestReference")

    def test_rejects_invalid_or_missing_form_keys(self) -> None:
        with self.assertRaisesRegex(RecordLookupError, "invalid FormKey"):
            get_record(self.root, "TestQuest")
        with self.assertRaisesRegex(RecordLookupError, "record not found"):
            get_record(self.root, "FFFFFF:Test.esp")

    def test_rejects_duplicate_records(self) -> None:
        self.write_json(
            "Quests/Duplicate.json",
            {
                "FormKey": "000001:Test.esp",
                "EditorID": "Duplicate",
            },
        )
        with self.assertRaisesRegex(RecordLookupError, "multiple records found"):
            get_record(self.root, "000001:Test.esp")


if __name__ == "__main__":
    unittest.main()
