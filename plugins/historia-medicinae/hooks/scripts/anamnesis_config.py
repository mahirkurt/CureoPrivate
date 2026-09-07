#!/usr/bin/env python3
"""historia-medicinae — Anamnesis kimliği.

Bu dosya plugin'e ÖZGÜdür; yanındaki `anamnesis_{run,guard,ledger,lifecycle}.py`
ise `tools/fleetkit/vendor/anamnesis/` içindeki kanonik kopyanın BAYT-ÖZDEŞ
vendor'lanmış hâlidir. Davranış değişikliği kanonik dosyaya yazılır ve
`python3 tools/fleetkit/vendor.py` ile dağıtılır; kimlik buraya yazılır.

Neden vendor, neden import değil: plugin'ler marketplace'ten TEK DİZİN olarak
kurulur, repo kökündeki paylaşılan kod kurulu kopyaya gitmez.
"""
from __future__ import annotations

import re

PLUGIN_ID = "histmed"
PLUGIN_LABEL = "historia-medicinae"
KIND = "run"
PREFIX_HEAD = "hmrun:"
LEDGER_NAME = "anamnesis-histmed.json"
ENV_PREFIX = "HISTMED_ANAMNESIS"
GUARD_OFF = "histmed-anamnesis.off"

#: Mesajlarda gösterilen kanonik doc_id örneği (yalnız insan okuru içindir).
DOC_ID_EXAMPLE = "doi/pmid/wellcome/devarsiv/yoktez"

# Flagship / :start yeni bir çalışma seti açar. Alt komutlar oturum
# koleksiyonunu paylaşır ki mod-arası önbellek tutsun.
NEW_RUN_RE = re.compile(r"(?:^|\s)/historia-medicinae(?:\:start)?(?:\s|$)", re.IGNORECASE)
