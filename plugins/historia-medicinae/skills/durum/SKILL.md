---
name: durum
description: "historia-medicinae filo sağlık kontrolü — 25 wire'lı server, 3 companion ve 3 delegasyonun bağlantı/anahtar durumunu raporlar, G0 kapsam manifestosu iskeletini üretir. Kullanın: 'connector'larım çalışıyor mu', 'filo durumu', 'hangi anahtarlar eksik', 'neden sonuç alamıyorum', 'doctor', 'preflight' sorularında."
argument-hint: "[--live: canlı MCP initialize denemesi]"
allowed-tools: Read, Bash, Glob
disable-model-invocation: false
---

# Filo Durumu

## 1. Statik kontrol

`scripts/historia_doctor.py` çalıştır:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/historia_doctor.py"
```

Bu betik `fleet.lock.json`'ı okur (üretilmiş türev; `fleet.yaml` tek gerçek kaynaktır) ve
her server için **bant · anahtar env adı · env'de var mı** raporlar. Ağ gerektirmez.

`--live` verilirse anahtarı bulunan server'lara streamable HTTP MCP `initialize` → `initialized`
zinciri denenir.

## 2. Raporlanacaklar

- Bant bazında bağlı/eksik sayısı (akademik çekirdek · birincil kaynak · tam-metin · yasama ·
  terminoloji/epi · Türkiye · web · substrat).
- **Kritik eksikler ve sonucu:**
  - `PUBMED_MCP_API_KEY` yok → MeSH K01.400 dönem-kilitli arama **yapılamaz** (kapsam kaybı).
  - `OTTOMAN_ARCHIVES_MCP_API_KEY` yok → dijitalleştirilmiş birincil kaynağa programatik
    erişim **kapanır**.
  - `OPENALEX_MCP_API_KEY` yok → beşeri bilimler literatürü ve atıf-grafı ekol haritası kaybolur.
- **Kalıcı bloklar** (anahtarla çözülmez, ölçülmüş): LoC manifest 403 · NLM Akamai bot kapısı ·
  Perseus/Scaife CTS ölü · HathiTrust tam-metin 403 · Europeana anahtarı sunucuda yok ·
  BHL anahtarı yok.
- **Delegasyonlar:** `vekayinuvis` / `evidentia` / `sci-audit` kurulu mu.
- **Oturum:** `devlet-arsivleri` için `devarsiv_session_status` (bağlıysa).

## 3. Çıktı

Bant başlıklı kompakt tablo + "şu an ne yapılabilir / ne yapılamaz" iki satırlık özet.
Sayı uydurma: betiğin döndürdüğünü aktar.
