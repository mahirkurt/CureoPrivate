# GoDaddy MCP Integration — Live Domain Verification Protocol

> **On-demand load.** Brief'te .com domain önceliği belirtilirse, ya da finalist listesi belirlendiyse ve canlı domain doğrulaması gerekiyorsa yüklenir. Bu dosya, GoDaddy MCP üzerinden **gerçek-zamanlı domain müsaitlik kontrolü** ve **alternatif öneri** iş akışını tanımlar.

---

## Felsefe

`domain_recon.py` heuristic'tir — **gerçek müsaitlik bilgisi vermez**, sadece tahmin yapar. Modern marka isimlendirme süreçlerinde bu yeterli değildir; `.com` evreninin %99'u tükendiği için **canlı sorgulama** kritik karar girdisidir. GoDaddy MCP iki API çağrısı sunar:

| MCP Tool | İşlev | Brand-Maker Kullanımı |
|---|---|---|
| `check_domain` | Belirli bir domain'in müsait olup olmadığını + fiyatı döner | Her finalist için **.com** birinci öncelik (sonra .ai, .io) |
| `suggest_domains` | Bir kelime/tema verildiğinde GoDaddy'nin önerdiği müsait alternatifler | `.com` müsait değilse hazır alternatifler |

---

## Sert Kural: `.com` Önceliği

Skill bu protokolü uygularken aşağıdaki **bağlayıcı önceliği** kullanır:

### Tier 1: `.com` (Mutlak öncelik)

`.com` müsait olan finalistler **her durumda diğerlerine tercih edilir**. Sebep:
- Domain ekuitisinin %90'ı `.com`'dadır (Verisign 2024 raporu)
- Kullanıcılar adres çubuğuna otomatik `.com` ekler (browser autocomplete davranışı)
- Trademark hukuk pratiğinde `.com` ownership "first to market" sinyali sayılır
- Investor/B2B ortamında `.com` olmayan markalar "second-tier" algısı yaratır
- Yeniden satış değeri: `.com` premium domain piyasasında 10-100x değer farkı oluşturur

### Tier 2: `.ai` (AI/ML startup için kabul edilir)

Yalnızca brief'te AI/ML/LLM/data-intelligence sektörü açıkça geçiyorsa, `.com` müsait değil ise `.ai` ikinci tercih edilir.

### Tier 3: `.io` (Tech/dev tool için kabul edilir)

Geliştirici-odaklı tool için fallback. **Asla** B2C consumer marka için önerilmez.

### Tier 4: Hiçbiri (`.co`, `.app`, `.xyz`, vd.)

Bu TLD'ler **finalist düşürme nedeni**dir. Bir finalistin yalnızca tier 4 TLD'si müsaitse o finalist **elenir** ve yerine alternatif aday üretilir.

---

## İş Akışı (3-Stage Live Verification)

### Stage 1: Birincil .com Kontrolü (Zorunlu)

Her finalist için sırayla:

```
mcp call → GoDaddy:check_domain
  domain: "{finalist}.com"
```

Üç olası sonuç:

| Sonuç | Eylem |
|---|---|
| **available: true** | ✓ Finalist .com'u rezervasyona hazır. Tier 1 onay. |
| **available: false** | ↓ Stage 2'ye geç (alternatif TLD kontrolü) |
| **API error / timeout** | `domain_recon.py` heuristic skoruna düş + manuel doğrulama URL üret |

### Stage 2: Alternatif TLD Kontrolü (.com müsait değilse)

```
mcp call → GoDaddy:check_domain
  domain: "{finalist}.ai"
mcp call → GoDaddy:check_domain
  domain: "{finalist}.io"
```

Karar matrisi:

| .com | .ai | .io | Brief profili | Karar |
|---|---|---|---|---|
| ✗ | ✓ | ✓/✗ | AI/ML startup | `.ai` ile finalist OK; raporda `.com` premium piyasa değerlendirmesi notu |
| ✗ | ✗ | ✓ | Tech/dev tool | `.io` ile finalist OK; B2C marka ise **elenir** |
| ✗ | ✗ | ✗ | Herhangi | **Eleme** veya Stage 3 |

### Stage 3: GoDaddy `suggest_domains` ile Alternatif Aday Toplama

Tüm primary TLD'ler dolu ise, GoDaddy'nin kendi öneri motoru çağrılır:

```
mcp call → GoDaddy:suggest_domains
  query: "{finalist}"
  limit: 10
```

GoDaddy genelde şu kalıpları sunar:
- `get{finalist}.com`, `try{finalist}.com`, `use{finalist}.com`
- `{finalist}hq.com`, `{finalist}app.com`, `{finalist}labs.com`
- `{finalist}.{alt-tld}` (xyz, online, tech)

Alternatif `.com` kalıpları (ör. `get{finalist}.com`) **kabul edilebilir** — bu kalıp 2020+ Tech ekosisteminde standart hale geldi (getbento.com, tryclay.com, withvalor.com). Yine de raporda **trade-off açıkça yazılır**: brand surface biraz uzar, marka mesajında "get/try" ön ek brand bilincine alınır.

---

## Çıktı Formatı

GoDaddy MCP çıktıları rapora şu yapıda işlenir:

### Per-Finalist Domain Block

```markdown
**[FİNALİST]** — Live Domain Verification

| TLD | Durum | Fiyat (USD/yıl) | Aksiyon |
|---|---|---|---|
| .com | ✓ Müsait | $11.99 | **REZERVE ET** (öncelik 1) |
| .ai | ✓ Müsait | $89.99 | İkincil rezervasyon önerilir |
| .io | ✗ Alınmış | — | — |

**Stage 3 (Müsait değilse) — GoDaddy alternatif önerileri:**
- get[finalist].com — $11.99 ✓
- try[finalist].com — $11.99 ✓
- [finalist]hq.com — $11.99 ✓
```

---

## Toplu Tarama Örneği (Mental Pseudocode)

5 finalist için tek-pas iş akışı:

```python
# Pseudo-code (gerçek MCP call'ları skill execution time'da)
finalists = ["Pythia", "Cohera", "Veridya", "Luminera", "Stratera"]

for name in finalists:
    # Stage 1: Birincil .com
    com_result = mcp_call("GoDaddy:check_domain", domain=f"{name}.com")
    if com_result["available"]:
        rapor[name] = {"primary": ".com", "tier": 1, "rezerve_et": True}
        continue

    # Stage 2: AI/Tech alternatives
    ai_result = mcp_call("GoDaddy:check_domain", domain=f"{name}.ai")
    io_result = mcp_call("GoDaddy:check_domain", domain=f"{name}.io")

    if brief_sektor == "AI" and ai_result["available"]:
        rapor[name] = {"primary": ".ai", "tier": 2, "com_premium_buy": True}
    elif brief_sektor == "tech" and io_result["available"]:
        rapor[name] = {"primary": ".io", "tier": 3, "com_premium_buy": True}
    else:
        # Stage 3: GoDaddy alternative suggestions
        suggestions = mcp_call("GoDaddy:suggest_domains", query=name, limit=10)
        rapor[name] = {"primary": "alternative", "tier": 4,
                       "alternatives": suggestions, "consider_elimination": True}
```

---

## [v2.1] İki-Kaynak Doğrulama Zorunluluğu (uzman-denetim düzeltmesi A)

Denetim, skill'in `auronza.com` ve `nortanza.com`'u **"müsait (standart)"** raporladığını buldu; ikisi de **DOLU**. Kök neden: heuristic bir **tahmin**di ama **hüküm** gibi kullanıldı. v2.1 kuralı:

> **Hiçbir alan adı TEK sinyalle "müsait" raporlanmaz.** Müsaitlik hükmü **canlı ikinci kaynak** gerektirir. `domain_recon.py` artık gerçek bir canlı doğrulayıcıdır: **RDAP (birincil, HTTPS)** → **WHOIS (port 43, ikincil)**. Karar mantığı:
> - herhangi bir canlı kaynak **kayıt** döndürürse → `confirmed_taken` (DOLU)
> - **iki** bağımsız kaynak boş derse → `confirmed_available` (yalnız o zaman "MÜSAİT")
> - **tek** kaynak boş derse → `provisional_available` ("müsait" YAZMA — ikinci kaynak gerekli)
> - hiç kaynak erişilemezse (offline) → `unverified` ("doğrulanamadı" — asla "müsait")

GoDaddy MCP **birincil canlı kaynak** olmaya devam eder; `domain_recon.py` RDAP+WHOIS ise **fallback ikinci-kaynak katmanı**dır ve artık heuristic değil canlıdır. GoDaddy MCP + RDAP birlikte iki-kaynak `confirmed` üretir.

Her domain sonucu **doğrulama-durumu + kaynak(lar) + UTC zaman damgası** taşır (bkz. `output-template.md` §4.1).

---

## Hata İşleme ve Fallback

GoDaddy MCP bağlı değil veya etkinleştirilmemişse:

1. **Fallback 1 (v2.1 — canlı):** `domain_recon.py` **RDAP + WHOIS iki-kaynak** doğrulaması yapar; heuristic yalnız "rekabet seviyesi" bağlamı için gösterilir, **müsaitlik hükmü değildir**.
2. **Fallback 2**: Manuel doğrulama URL'leri (Namecheap/Domainr/Instant/RDAP) rapora yazılır.
3. **Raporda explicit şeffaflık**: canlı kaynak erişilemediyse durum `unverified` olarak damgalanır — **asla iyimser "müsait" varsayımı yok**.

Brief'te kullanıcı GoDaddy MCP'yi etkinleştirmek isterse:
> *"GoDaddy MCP'nin canlı domain doğrulaması yapabilmesi için Settings → Connectors → GoDaddy 'Enable in chat' onayı verin. Sonraki marka isimlendirme görevlerinde otomatik olarak kullanılacaktır."*

---

## Maliyet ve Sınırlama Değerlendirmeleri

| Boyut | Değer | Kullanım Tavsiyesi |
|---|---|---|
| Rate limit | GoDaddy API tier'a göre değişir (Free tier: 60 req/min) | 5-7 finalist × 3 TLD = 15-21 call → free tier içinde rahat |
| Latency | Her call ~200-500ms | Toplam 5-10 saniye için skill bekler |
| Pricing data accuracy | Anlık, GoDaddy fiyatlandırmasıyla senkron | Diğer registrar'larda fiyat değişebilir; bilgi amaçlı kullanılır |
| Trademark check | **YAPMAZ** — sadece domain müsaitliği | Trademark için ayrı USPTO/EUIPO/TÜRKPATENT akışı gerekli |

---

## Strateji İçin GoDaddy MCP Yeri

| Önceki Mimari (v1.1) | Yeni Mimari (v1.2 ile) |
|---|---|
| `domain_recon.py` heuristic skor üretir; manuel doğrulama URL'si verir | GoDaddy MCP **canlı sorgu** yapar; heuristic yalnızca MCP yoksa devreye girer |
| Müşteri her finalist için 5-6 URL'yi tek tek tıklamak zorunda | Skill çıktısında doğrudan ✓/✗ + fiyat + alternatif görür |
| Karar süresi: 1-2 saat manuel | Karar süresi: 1-2 dakika anlık |

---

## Skill Disiplini Özeti

1. **GoDaddy MCP varsa, ÖNCE o kullanılır** — `domain_recon.py` heuristic'i ikincil hale gelir
2. **`.com` mutlak öncelik** — diğer TLD'ler ancak `.com` müsait değilse değerlendirilir
3. **`.com` müsait olan finalist diğerlerine tercih edilir** — eşitse SMILE skoru karar verir
4. **Trade-off raporlanır** — alternatif TLD veya alternatif kalıp seçildiğinde rationale yazılır
5. **MCP yoksa fallback şeffaf** — heuristic + manuel URL listesi sunulur

---

## Kaynaklar

- GoDaddy Domains API: https://developer.godaddy.com/doc/endpoint/domains
- GoDaddy MCP server: https://api.godaddy.com/v1/domains/mcp
- Verisign 2024 Domain Industry Brief: TLD pazar payı
- ICANN gTLD policy: https://www.icann.org/resources/pages/gtld-policy
