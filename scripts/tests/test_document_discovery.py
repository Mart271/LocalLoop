"""Repository validation must include source docs and exclude downloaded development tools."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_docs
import validate_mermaid


class DocumentDiscovery(unittest.TestCase):
    def test_source_and_spike_docs_are_checked_but_vendor_docs_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            included = {root / "README.md", root / "docs/design.md", root / "spikes/README.md"}
            excluded = {root / ".localloop-dev/actionlint/docs/broken.md",
                        root / "apps/desktop/node_modules/package/README.md",
                        root / "spikes/xlsx/target/build/README.md"}
            for path in included | excluded:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("[bad link](missing.md)\n", encoding="utf-8")
            with patch.object(check_docs, "REPO_ROOT", root):
                self.assertEqual(set(check_docs.markdown_files()), included)
            self.assertEqual(set(validate_mermaid.iter_markdown_files([root])), included)


if __name__ == "__main__":
    unittest.main()
