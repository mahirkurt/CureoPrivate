# İş Portföy Hisse Senedi Fonu (TI2) — Karar-Destek Brifingi

## Yönetici Özeti
TI2, hisse senedi yoğun bir yatırım fonu olarak son bir yılda akranlarının üst dilimine yakın
bir riske-göre-düzeltilmiş getiri sergilemektedir (Sharpe ~1.4, kategori medyanı ~0.9; yıllık,
gün-sonu/EOD, as-of 2026-06-16). Buna karşılık son bir aylık geri çekilme akran ortalamasının
bir miktar üzerindedir; bu, görece üstünlüğün rejim duyarlı olduğunu gösterir.

## Fon Kimliği & Yapısı
İhraçcı/kurucu İş Portföy; kategori "Hisse Senedi Fonu"; portföy büyüklüğü ~3,8 milyar TL
(as-of 2026-06-16). Varlık dağılımında hisse senedi ağırlığı baskındır; kalan kısım ters repo
ve sınırlı dövizdedir. Toplam gider oranı (TER) akran medyanına yakındır.

## Risk/Getiri Profili
1 yıllık getiri ~%36,8 (nominal; yüksek enflasyon nedeniyle reel çerçevede daha mütevazıdır).
Yıllık volatilite akran bandının orta-üst kısmındadır; maksimum geri çekilme penceresi
tarihlendirilmiştir (as-of 2026-06-16). VaR(%95) ve CVaR değerleri kuyruk riskinin yönetilebilir
ancak ihmal edilemez olduğunu işaret eder.

## Benchmark & Makro Bağlam
Karşılaştırma ölçütü BIST 100'dür; fonun benchmark'a göre betası ~1'in üzerindedir. Mevcut
TCMB makro rejimi Nötr/Risk-Kapalı sınırında değerlendirilmektedir; hisse yoğun fonlar bu
ortamda rüzgârı önden alabilir.

## Akran Karşılaştırması
Kategori içinde Sharpe ve Sortino açısından üst çeyrekte; TER açısından medyana yakın
konumdadır. Tutarlılık (rolling getiri pozitifliği) orta düzeydedir.

## İzlenecekler & Riskler
Faiz/kur rejiminde sertleşme görece üstünlüğü zayıflatabilir; benchmark'a göre yüksek beta
aşağı hareketlerde daha derin geri çekilme anlamına gelir. Kurucu/yönetici tarafında açık bir
KAP duyurusu izlenmelidir.

## Kaynaklar
Getiri ve NAV serisi Borsa veri bağlayıcısından; varlık dağılımı ve gider oranı TEFAS
detay bağlayıcısından alınmıştır. Risk metrikleri deterministik kuant motoruyla yeniden
türetilmiştir. Tüm fiyat ve metrikler gün-sonu (EOD), as-of 2026-06-16.

## Feragat
Bu içerik yalnızca bilgilendirme ve karar-destek amaçlıdır; SPK yatırım danışmanlığı, portföy
yöneticiliği veya al/sat tavsiyesi niteliği taşımaz. Fon getirileri geçmişe dönük olup
gelecekteki getirinin garantisi değildir; NAV verileri gün-sonu (EOD) ve gecikmeli olabilir.
Yatırım kararları; kişinin kendi risk profili, bağımsız araştırması ve gerektiğinde SPK
lisanslı bir yatırım kuruluşuna/danışmanına danışılarak alınmalıdır.

<!-- RENDER:EXCLUDE-FROM-HERE -->
OPS: Borsa MCP get_fund_data x1 (native-first), fon-mcp get_allocation_snapshot/get_fund_costs x2; quant_engine deterministic=true (risk_adjusted/drawdown_var/monte_carlo)
PROV: [Borsa MCP / get_fund_data / 2026-06-16] · [fon-mcp / get_allocation_snapshot / 2026-06-16] · [fon-mcp / get_fund_costs / 2026-06-16] · [quant-analiz / risk_adjusted / Sharpe-v1]
VIZ: NAV-vs-XU100 çizgi · drawdown underwater · risk-getiri scatter (akran) · varlık-dağılım treemap
<!-- RENDER:EXCLUDE-TO-HERE -->

