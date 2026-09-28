# lex-sanitas mezar taşı

claude.ai hesabına senkronlu `lex-sanitas` skill'inin yerine yüklenecek emekli sürüm.
G10/G11 adlarının iki farklı anlamda kullanılmasını ve cureolex ile tetikleme
çakışmasını ortadan kaldırır.

**Ne zaman:** Faz C'den SONRA. Mevcut `lex-sanitas` içindeki `verify_output.py`
henüz cureolex'e taşınmadı; mezar taşı erken yüklenirse o doğrulayıcı Faz C'ye
kadar hiçbir yerde olmaz.

**Nasıl:**
1. Zip üret (worktree kökünden):
   `cd plugins/cureolex/docs/lex-sanitas-mezar-tasi && python3 -c "import shutil; shutil.make_archive('/tmp/lex-sanitas-mezar-tasi', 'zip', '.', 'lex-sanitas')"`
2. claude.ai → Settings → Capabilities → Skills: mevcut `lex-sanitas`'ı bu zip ile değiştir.
3. Yeni bir sohbette "sağlık mevzuatı taslağı" iste; lex-sanitas'ın çıktı üretmediğini,
   cureolex'e yönlendirdiğini doğrula.
