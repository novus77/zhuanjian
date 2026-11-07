import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from repository_archive import check, snapshot, update


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "docs").mkdir()
        (self.root / "models").mkdir()
        (self.root / ".gitignore").write_text("Library/\n*.blend1\n")
        (self.root / ".gitattributes").write_text("*.glb filter=lfs diff=lfs merge=lfs -text\n")

    def test_records_real_source_bytes_and_lfs_storage(self):
        (self.root / "models/chair.glb").write_bytes(b"real-model-bytes")
        entry = next(item for item in snapshot(self.root)["files"] if item["path"] == "models/chair.glb")
        self.assertEqual(entry["sha256"], hashlib.sha256(b"real-model-bytes").hexdigest())
        self.assertEqual(entry["size"], 16)
        self.assertEqual(entry["storage"], "git-lfs")

    def test_pointer_checkout_matches_original_model_identity(self):
        model = self.root / "models/chair.glb"
        model.write_bytes(b"real-model-bytes")
        expected = snapshot(self.root)
        digest = hashlib.sha256(b"real-model-bytes").hexdigest()
        model.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:" + digest + "\nsize 16\n")
        self.assertEqual(snapshot(self.root), expected)

    def test_ignored_caches_and_backup_files_are_excluded(self):
        (self.root / "Library").mkdir()
        (self.root / "Library/cache.bin").write_bytes(b"cache")
        (self.root / "models/chair.blend1").write_bytes(b"backup")
        self.assertFalse(any(item["path"].startswith("Library/") or item["path"].endswith("blend1")
                             for item in snapshot(self.root)["files"]))

    def test_changed_asset_requires_catalog_refresh(self):
        model = self.root / "models/chair.glb"
        model.write_bytes(b"first")
        update(self.root)
        check(self.root)
        model.write_bytes(b"second")
        with self.assertRaisesRegex(ValueError, "catalog is stale"):
            check(self.root)

    def test_new_content_and_deleted_sources_require_refresh(self):
        source = self.root / "models/chair.glb"
        source.write_bytes(b"first")
        update(self.root)
        source.unlink()
        (self.root / "docs/process.md").write_text("Production progress")
        with self.assertRaisesRegex(ValueError, "catalog is stale"):
            check(self.root)
        update(self.root)
        check(self.root)

    def test_generation_is_deterministic_and_catalog_does_not_index_itself(self):
        (self.root / "docs/process.md").write_text("Production progress")
        update(self.root)
        first = (self.root / "docs/archive-manifest.json").read_bytes()
        update(self.root)
        self.assertEqual((self.root / "docs/archive-manifest.json").read_bytes(), first)
        paths = [item["path"] for item in json.loads(first)["files"]]
        self.assertNotIn("docs/archive-manifest.json", paths)
        self.assertNotIn("docs/asset-catalog.md", paths)


if __name__ == "__main__":
    unittest.main()
