# anamnesis-indexer

anamnesis-mcp'nin **GraphRAG global araması** için çevrimdışı Leiden topluluk tespiti.

## Neden ayrı bir paket

`anamnesis-mcp/BUILD-BRIEF.md` §5, global aramayı **bilinçli olarak sevk etmemişti**: topluluk
tespiti istek-kapsamlı bir Worker'ın işi değildir ve özetlemeyi Worker içindeki zayıf bir modele
yaptırmak, kanıt substratına güvenilmez metin sokardı. O gerekçe hâlâ geçerli, bu yüzden iş üçe
bölündü ve **hiçbir yerde yaklaşık bir şey yapılmıyor**:

| Katman | Nerede | Ne yapar |
|---|---|---|
| Depolama + servis | Worker (`community.ts`) | Bölümlemeyi saklar ve sunar. Burada kümeleme YOK. |
| Bölümleme | **bu paket**, HP systemd timer | Gerçek Leiden. Saf graf matematiği — dil modeli yok, dolayısıyla yaklaşıklanacak bir şey de yok. |
| Özetleme | Orkestratör (Claude), `community_summarize` | `upsert_triples` ile aynı doktrin. |

Bir topluluğun özeti yoksa `global_query` bunu **söyler** (`summary_status:"absent"`) ve üye
listesini döndürür — özet uydurmaz.

## Akış

```
graph_export(collection) → Leiden (level 0) → toplulaştır → Leiden (level 1) → upsert_communities
```

Seviye 1 yalnız gerçekten bir şey birleştirdiğinde yazılır; kaba bir topluluk daima ince
toplulukların **birleşimidir** (yeniden dilimlenmesi değil) — hiyerarşiyi hiyerarşi yapan budur.

## Kapsam

Hedef korpuslar `ANAMNESIS_INDEX_COLLECTIONS` ile **açıkça** sayılır. "Tüm koleksiyonları listele"
diye bir araç yoktur ve bu paket öyle bir araç istemez: başka kiracıların çalışma setlerini
saymak, 2026-09-07 denetiminin kapattığı çapraz-koleksiyon sızıntısının ta kendisi olurdu.
Yalnız dayanıklı (`lib`) korpuslar anlamlıdır — scratch bir oturum boyu yaşar ve reaper'a gider.

## Kurulum (HP)

```bash
rsync -az --delete --exclude .venv --exclude .env --exclude __pycache__ \
  plugins/evidentia/self-host/anamnesis-indexer/ hp-ai-node:~/anamnesis-indexer/
ssh hp-ai-node 'cd ~/anamnesis-indexer && ~/.local/bin/uv sync'
# .env'i .env.example'dan doldur (anahtar Doppler'dan), sonra:
ssh hp-ai-node 'sudo cp ~/anamnesis-indexer/deploy/anamnesis-indexer.{service,timer} /etc/systemd/system/ \
  && sudo systemctl daemon-reload && sudo systemctl enable --now anamnesis-indexer.timer'
```

Elle koşum: `sudo systemctl start anamnesis-indexer` · Günlük: `journalctl -u anamnesis-indexer -n 50`

## Test

```bash
uv sync --extra dev && uv run pytest -q && uv run ruff check .
```

Ölçülen davranış testlerle sabitlenmiştir: zayıf bağlı iki üçgen iki topluluğa ayrılır, üyeler
graf indeksleri değil orijinal düğüm id'leridir, yalnız topluluk-içi kenarlar sayılır, sabit
tohumda sonuç deterministiktir, boş graf çökmez, bilinmeyen düğüme işaret eden kenar gecelik
koşumu düşürmez ve seviye 1 daima seviye 0'ın birleşimidir.
