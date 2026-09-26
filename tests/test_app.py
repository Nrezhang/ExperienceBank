import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
import app


class HandlerTests(unittest.TestCase):
    @patch("app._table")
    def test_create_item(self, table):
        table.return_value = MagicMock()
        result = app.handler(
            {"routeKey": "POST /api/items", "body": json.dumps({"title": "First idea"})},
            None,
        )
        self.assertEqual(result["statusCode"], 201)
        self.assertEqual(json.loads(result["body"])["title"], "First idea")
        table.return_value.put_item.assert_called_once()

    @patch("app._table")
    def test_rejects_blank_title(self, table):
        result = app.handler(
            {"routeKey": "POST /api/items", "body": json.dumps({"title": "  "})},
            None,
        )
        self.assertEqual(result["statusCode"], 400)
        table.assert_not_called()

    @patch("app._table")
    def test_lists_newest_first(self, table):
        table.return_value.scan.return_value = {
            "Items": [
                {"id": "old", "title": "Old", "createdAt": "2026-01-01"},
                {"id": "new", "title": "New", "createdAt": "2026-02-01"},
            ]
        }
        result = app.handler({"routeKey": "GET /api/items"}, None)
        self.assertEqual(json.loads(result["body"])["items"][0]["id"], "new")


if __name__ == "__main__":
    unittest.main()
