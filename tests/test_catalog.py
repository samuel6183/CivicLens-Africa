import json
import unittest
import tempfile
import os
from unittest.mock import patch
from pathlib import Path
from backend.ingest import import_documents
from backend.store import search

class CatalogTests(unittest.TestCase):
    def test_catalog(self):
        path=Path("frontend/documents.json")
        rows=json.loads(path.read_text())
        self.assertEqual(len(rows),6)
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ,{"CIVICLENS_DB":tmp+"/test.sqlite3"}):
                self.assertEqual(import_documents(path),6)
                import_documents(path)
                self.assertEqual(search()["total"],6)
                self.assertEqual(search(q="economic survey")["total"],2)
