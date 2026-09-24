# edupedia 1.1.0 — claude.ai kurulumu

claude.ai'da hook, alt-ajan ve komut yoktur; bütün derinlik `tedy` orkestratöründedir. Gerekenler: özel bağlayıcı ekleyebilen bir plan ve TEDY aile listesindeki tam yetkili Google hesabı.

## 1. Eski skill paketini kaldırın

1.0.0 öncesinde yüklenmiş bir edupedia skill paketi varsa claude.ai skill listesinden silin; yerel üretim talimatı taşır ve yeni akışla çelişir.

## 2. Skill paketini üretin ve yükleyin

```bash
python3 plugins/edupedia/scripts/build_surfaces.py --zip
# → plugins/edupedia/dist/edupedia-claude-ai.zip  (kökte edupedia/SKILL.md)
```

claude.ai → Ayarlar → Yetenekler (Capabilities) → Skills → Upload → zip'i seçin → `edupedia` skill'ini etkinleştirin.

## 3. Bağlayıcıyı ekleyin

Ayarlar → Connectors → Add custom connector → ad `TEDY edupedia`, URL `https://mcp.tedy.online/mcp` → Add → Connect → Google girişi → onay sayfasında geri-çağırma adresinin `https://claude.ai/api/mcp/auth_callback` (ya da `https://claude.com/api/mcp/auth_callback`) olduğunu doğrulayın → Onayla.

## 4. Kullanım

Sohbette bağlayıcıyı ve skill'i açın. Örnek: "Işık'ın yaklaşan fen sınavı için QUIZ modunda edupedia modülü hazırla." Model `edupedia_rehber` ile başlar, `edupedia_derle` ile derler ve `edupedia_yayinla` sonrası tedy.online bağlantısını verir.

## 5. Ne geçer, ne geçmez

| Claude Code | claude.ai |
|---|---|
| SessionStart preflight | yok — model `edupedia_durum` ile kontrol eder |
| Beş komut | yok — aynı akış doğal dil istekleriyle |
| `edupedia` skill'i | aynı talimat (zip) |
| `tedy` araçları, 18 kapı, yayın | aynı (sunucu tarafı) |
