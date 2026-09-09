#!/usr/bin/env python3
"""vekayinuvis — Anamnesis kimliği.

Bu dosya plugin'e ÖZGÜdür; yanındaki `anamnesis_{run,guard,ledger,lifecycle}.py`
ise `tools/fleetkit/vendor/anamnesis/` içindeki kanonik kopyanın BAYT-ÖZDEŞ
vendor'lanmış hâlidir. Davranış değişikliği kanonik dosyaya yazılır ve
`python3 tools/fleetkit/vendor.py` ile dağıtılır; kimlik buraya yazılır.

Neden vendor, neden import değil: plugin'ler marketplace'ten TEK DİZİN olarak
kurulur, repo kökündeki paylaşılan kod kurulu kopyaya gitmez.
"""
from __future__ import annotations

import re

PLUGIN_ID = "vekayinuvis"
PLUGIN_LABEL = "vekayinuvis"
KIND = "run"
PREFIX_HEAD = "vkrun:"
LEDGER_NAME = "anamnesis-vekayinuvis.json"
ENV_PREFIX = "VEKAYI_ANAMNESIS"
GUARD_OFF = "vekayinuvis-anamnesis.off"

#: Mesajlarda gösterilen kanonik doc_id örneği (yalnız insan okuru içindir).
DOC_ID_EXAMPLE = "devarsiv:/yoktez:/doi:/iiif:"

# Flagship / :start yeni bir çalışma seti açar. Alt komutlar oturum
# koleksiyonunu paylaşır ki mod-arası önbellek tutsun.
NEW_RUN_RE = re.compile(r"(?:^|\s)/vekayinuvis(?:\:start)?(?:\s|$)", re.IGNORECASE)
