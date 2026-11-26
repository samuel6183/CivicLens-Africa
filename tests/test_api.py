import os
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.ingest import world_bank
from backend.store import search

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"CIVICLENS_DB":self.temp.name+"/test.sqlite3"})
        self.env.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.temp.cleanup()

    def test_empty_and_health(self):
        self.assertEqual(self.client.get("/api/health").json(), {"status":"ok"})
        self.assertEqual(self.client.get("/api/search").json()["total"],0)
        self.assertEqual(self.client.get("/api/search?limit=101").status_code,422)
        self.assertEqual(self.client.get("/records.html").status_code,200)

    def test_import_search_dedup(self):
        def fixture(url):
            return [{},[{"date":"2020","countryiso3code":"KEN","value":1.25},
                        {"date":"2021","countryiso3code":"KEN","value":None}]]
        self.assertEqual(world_bank(fixture),3)
        world_bank(fixture)
        self.assertEqual(search()["total"],3)
        self.assertEqual(self.client.get("/api/search?q=inflation").json()["total"],1)
        self.assertEqual(self.client.get("/api/search?q=%27").json()["total"],0)
        series = self.client.get("/api/series?indicator=FP.CPI.TOTL.ZG").json()
        self.assertEqual(series["observations"][0]["value"],1.25)

if __name__=="__main__":
    unittest.main()
