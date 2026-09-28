#!/usr/bin/env python3
"""confidence_label.schema.json geriye-dönük uyumluluk testleri (2026-09-27 nihai
inceleme F5). 4.1'de `out_of_scope_redirect` kaldırıldı ama `label_version` "1.0"
kaldı ve üst düzey `additionalProperties:false`; bu yüzden 4.0 etiketi taşıyan bu
alan artık şemayı geçersiz kılıyordu. Alan `deprecated:true` ile geri eklenir —
yeni çıktı bu alanı YAZMAZ, yalnız eski etiketlerin geçerliliği korunur.
"""
import json
import sys
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - ortamda yoksa atla
    jsonschema = None

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "skills" / "cureolex" / "schemas" / "confidence_label.schema.json"

with open(SCHEMA_PATH, encoding="utf-8") as fh:
    SCHEMA = json.load(fh)

BASE_LABEL = {
    "label_version": "1.0",
    "mode": "DRAFT",
    "combined_confidence": "MODERATE",
    "human_review_required": True,
    "self_disclosure": {
        "cureolex": {
            "version": "4.0.0",
            "mcp_unavailability_during_query": [],
            "uncertain_interpretations": [],
        },
        "medical_research": {"invoked": False},
    },
}


@unittest.skipIf(jsonschema is None, "jsonschema paketi kurulu değil")
class BackwardCompatTests(unittest.TestCase):
    def test_current_label_validates(self):
        jsonschema.validate(BASE_LABEL, SCHEMA)

    def test_4_0_style_label_with_out_of_scope_redirect_still_validates(self):
        """4.0'da üretilmiş, artık kullanımdan kalkmış alanı taşıyan bir etiket."""
        legacy = dict(BASE_LABEL)
        legacy["out_of_scope_redirect"] = ["x"]
        jsonschema.validate(legacy, SCHEMA)

    def test_out_of_scope_redirect_has_no_skill_name_enum(self):
        """Alan yalnız geriye-uyumluluk içindir — enum/skill adı taşımamalı."""
        prop = SCHEMA["properties"]["out_of_scope_redirect"]
        self.assertTrue(prop.get("deprecated"))
        self.assertEqual(prop["type"], "array")
        self.assertEqual(prop["items"], {"type": "string"})
        self.assertNotIn("enum", prop)


if __name__ == "__main__":
    unittest.main()
