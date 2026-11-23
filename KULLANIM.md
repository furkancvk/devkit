# devkit: kullanım kılavuzu

Bu kılavuz, kitin takılı olduğu bir repoda Claude Code ile çalışan geliştirici içindir. Kiti kuran ve güncelleyen kişi için ayrıntı [README.md](README.md) dosyasındadır.

## Kit nedir

Kit, Claude Code'a nasıl çalışacağını öğreten bir skill takımıdır. Skill'ler bu repoda durur; ürün reposunda yalnız `.claude/settings.json` içinde kite işaret eden iki ayar vardır. Bir repoda kit takılıysa o repoda açtığın her Claude oturumu skill'leri görür.

Üç paket vardır:

| Paket | Ne getirir | Hangi repolarda |
| --- | --- | --- |
| `superpowers` | Süreç: tasarım, plan, test önce, hata ayıklama, bitirmeden doğrulama | hepsinde |
| `core` | Sorgulama, devir, alt ajan politikası, repo kurulumu | hepsinde |
| `ui` | Arayüz tasarımı ve tarayıcıda sınama | arayüzü olan repolarda |

## İlk kurulum (kişi başına, repo başına bir kez)

Gerekenler: Claude Code kurulu ve giriş yapılmış; git; Python 3.9 ya da üstü. Windows'ta Git for Windows kurulu olmalı.

Aşağıdaki komutlar macOS ve Linux içindir. Windows'ta `bin/kit.py` yerine `py -3 bin\kit.py` yaz.

1. Kit reposunu klonla: `git clone https://github.com/furkancvk/devkit`
2. Çalışacağın repo için plugin'leri indir:

   ```bash
   bin/kit.py install ~/code/my-app
   ```

3. O repoda `claude` aç ve klasöre güven sorusunu onayla. Güvenilmeyen klasörde repodaki ayarlar yüklenmez.
4. Kontrol et:

   ```bash
   bin/kit.py status ~/code/my-app
   ```

   Claude Code içinde `/plugin` yazınca `core` ve `superpowers` açık görünmelidir.

`install` repoda dosya değiştirmez. Çalıştırdıktan sonra `git status` bir fark gösteriyorsa commit etme, haber ver.

## Günlük kullanım

Çoğu skill kendiliğinden devreye girer; sen işi anlatırsın, Claude uygun skill'i seçer ve "şu skill'i şunun için kullanıyorum" diye söyler. Üç skill yalnız sen çağırınca çalışır (aşağıda "Elle çağrılanlar").

### Yeni özellik ya da davranış değişikliği

1. **Tasarım.** Claude koda girmeden önce ne istediğini sorar, iki üç yaklaşım sunar, seçtiğini kısa bir tasarım belgesine yazar: `docs/superpowers/specs/YYYY-AA-GG-<konu>-design.md`. Sen onaylamadan devam etmez.
2. **Plan.** Onaylı tasarımı küçük görevlere böler: `docs/superpowers/plans/YYYY-AA-GG-<özellik>.md`. Her görevde dosya yolları, test ve doğrulama adımı yazar.
3. **Uygulama.** "Başla" dediğinde planı görev görev yürütür. Önce başarısız testi yazar, sonra kodu. Görev aralarında kendi işini gözden geçirir.
4. **Bitirme.** Testleri çalıştırır ve ne yapacağını sana sorar: yerelde birleştirmek ya da push edip PR açmak gibi seçenekler sunar.

Claude ayrı bir çalışma kopyası (worktree) açmak isterse önce sorar. İstemiyorsan hayır de; çalıştığın dalda devam eder.

### Hata

"Şu bozuk" dediğinde Claude düzeltme önermeden önce nedeni arar: hatayı tekrarlar, kanıt toplar, kök nedeni bulur, sonra düzeltir. Tahminle yama atmaz.

### Küçük iş

Tek dosyalık düzeltme, yazım hatası, yorum ya da ad değişikliği için tasarım ve plan aşaması atlanır. Bu, her reponun `AGENTS.md` dosyasındaki ekip kuralıdır. Claude yine de süreci başlatırsa "bu küçük iş, doğrudan yap" demen yeter.

### "Bitti" demeden önce

Claude işi bitmiş saymadan önce reponun doğrulama komutunu çalıştırır ve çıktısını gösterir. Komut her reponun `AGENTS.md` dosyasında "Verify" satırında yazar (örneğin `npm run verify`); Windows, macOS ve Linux'ta aynı biçimde çalışır.

Çıktıyı görmeden "geçti" diyorsa ya da komutu çalıştırmadıysa, çalıştırmasını iste. Komut kırmızıysa iş bitmemiştir.

### İşi bırakırken

Anlamlı bir iş bitince Claude `docs/PROGRESS.md` dosyasını günceller: ne yapıldı, ne açık kaldı, sıradaki adım. Bu dosyanın başı her yeni oturumun başında Claude'a kendiliğinden gösterilir; yani dün nerede kaldığınızı anlatmana gerek kalmaz. Dosyayı kısa tut, en önemli durum en üstte dursun. Oturumu başka birine ya da yeni bir oturuma devredeceksen `/core:handoff` çağır.

## Elle çağrılanlar

Bu üçü yalnız sen yazınca çalışır.

| Komut | Ne zaman | Ne yapar |
| --- | --- | --- |
| `/core:grill-me` | Bir planı ya da kararı uygulamadan önce sınamak istediğinde | Seni tur tur sorgular. Her turda numaralı sorular sorar ve her soruya kendi önerdiği cevabı yazar. Sen "anlaştık" diyene kadar koda başlamaz |
| `/core:handoff <sonraki oturum ne için>` | Oturumu devrederken | Konuşmayı bir devir belgesine çevirir. Belgeyi işletim sisteminin geçici klasörüne yazar, repoya değil. Parola ve kişisel veriyi çıkarır |
| `/core:repo-setup` | Kit bir repoya ilk takıldığında, bir kez | `AGENTS.md`, `CLAUDE.md` ve `docs/PROGRESS.md` dosyalarını şablondan kurar, reponun doğrulama komutunu tanımlar, gizli dosyaları (`.env` gibi) Claude'un okumasına kapatır ve riskli kod alanları için yola bağlı kural önerir. Var olan notları İngilizceye çevirerek taşır. Commit atmaz, farkı gösterir |

## Kendiliğinden çalışanlar

### superpowers

| Skill | Ne zaman devreye girer |
| --- | --- |
| `brainstorming` | Yeni bir şey yapılacakken, koddan önce |
| `writing-plans` | Onaylı tasarım varken, koddan önce |
| `subagent-driven-development` | Plan, her görev için ayrı alt ajanla yürütülürken |
| `executing-plans` | Plan aynı oturumda, alt ajansız yürütülürken |
| `test-driven-development` | Özellik ya da hata düzeltmesi yazılırken |
| `systematic-debugging` | Hata, kırmızı test ya da beklenmeyen davranışta |
| `verification-before-completion` | "Bitti", "düzeldi", "geçti" demeden önce |
| `requesting-code-review` | Görev ya da özellik tamamlanınca |
| `receiving-code-review` | İnceleme geri bildirimi geldiğinde |
| `using-git-worktrees` | İş ayrı bir çalışma kopyası gerektirdiğinde (önce sorar) |
| `finishing-a-development-branch` | Uygulama bitip testler geçtiğinde |
| `dispatching-parallel-agents` | Birbirinden bağımsız iki ya da daha çok iş olduğunda |
| `writing-skills` | Yeni skill yazılırken (kit bakımı) |
| `diagnosing-superpowers` | Bir oturum kötü gittiğinde nedenini ararken |
| `using-superpowers` | Her oturumun başında; diğerlerini devreye sokan kural budur |

### core

| Skill | Ne zaman devreye girer |
| --- | --- |
| `fable-orchestration` | Claude alt ajan açarken. Zor işi Opus'a, basit işi Sonnet'e, toplu veri temizliğini Haiku'ya verir ve her çağrıda modeli açıkça yazar |
| `grilling` | `/core:grill-me` bunu çağırır; "beni sorgula" dediğinde de devreye girer |

### ui

| Skill | Ne zaman devreye girer |
| --- | --- |
| `frontend-design` | Yeni arayüz kurulurken ya da var olan yeniden biçimlenirken |
| `webapp-testing` | Yerelde çalışan web uygulaması tarayıcıda sınanırken (Playwright; ekran görüntüsü, konsol kaydı) |

Reponun kendi tasarım belgesi varsa (`docs/design/`) o belge `frontend-design`'ın genel önerilerinden önce gelir.

## Ekip kuralları

Kit takılı her repoda `AGENTS.md` içinde aynı kısa kural listesi bulunur; Claude her oturumda bunları okur. Özeti:

- Yalnız isteneni yapar; fazladan özellik, seçenek ve soyutlama eklemez.
- Yalnız gereken satırları değiştirir; komşu kodu yeniden biçimlendirmez ya da "iyileştirmez".
- Değişikliği küçük tutar: dal ve PR başına tek konu.
- "Bitti" demeden önce doğrulama komutunu çalıştırır; testi geçirmek için testi zayıflatmaz.
- Geri alınması zor işten önce durup sorar: yıkıcı migration, veri ya da dal silme, geçmişi yeniden yazma, yetki modelini değiştirme, dış sözleşmeyi bozma.
- Yeni bağımlılık eklerken ne için olduğunu söyler, bakımına ve lisansına bakar.
- Sen istemedikçe worktree açmaz; iş birleşince planı siler.
- Parola, anahtar ve kişisel veriyi depoya ya da ayar dosyasına yazmaz.

Bir kurala uymadığını görürsen hatırlat; aynı şey tekrarlanıyorsa "Geri besleme" bölümüne bak.

## Süreci ayarlamak

Öncelik sırası şöyledir: senin o anki isteğin ve reponun `AGENTS.md` dosyası, skill'lerin önüne geçer. Bu superpowers'ın kendi kuralıdır.

- **Tek seferlik:** Sohbette söyle. "Plan yazma, doğrudan yap", "bu iş için test önce kuralını atla".
- **Repo için kalıcı:** `AGENTS.md` dosyasının repo bölümüne yaz. Örnek: "Bu repoda worktree açma."
- **Bütün repolar için:** `AGENTS.md` içindeki "Ekip kuralları" bölümü kit şablonundan gelir. Onu repoda değiştirme; kit bakımcısına söyle.

## Dil

Ajanın okuduğu dosyalar İngilizcedir: `AGENTS.md`, `docs/PROGRESS.md`, tasarım ve plan belgeleri, skill'ler. Sen Claude ile Türkçe konuşursun, o da sana Türkçe cevap verir. Ürün kullanıcısına görünen metin ürünün dilinde kalır.

Alan terimleri çevrilmez. Ürüne ya da sektöre özgü, İngilizce olmayan sözcüklerin kodda hangi ada karşılık geldiği `AGENTS.md` içindeki "Domain terms" bölümünde yazar. Yeni bir terim çıktığında oraya ekle; yoksa her oturum onu başka türlü çevirir.

## Geri besleme

Kit, kullanıldıkça düzeltilirse iyileşir. Kural basit:

- Claude aynı hatayı **ikinci kez** yaparsa: reponun `AGENTS.md` dosyasına bir satırlık kural yaz. Hata bütün repolarda olabilecek türdense kit bakımcısına söyle; ekip kurallarına girer.
- **Üçüncü kez** yaparsa yazılı kural yetmiyor demektir: lint kuralına, teste ya da CI adımına çevrilir.
- Bir oturum kötü gittiyse (iş tekrarlandı, plan yok sayıldı, çok uzun sürdü) kapatmadan önce Claude'a "superpowers bu oturumda neyi yanlış yaptı, incele" de ve çıkan sonucu kit bakımcısına ilet.
- Bir skill sana sürekli ayak bağı oluyorsa kendi makinende kapatıp geçme; söyle. Sende sorun olan başkasında da oluyordur.

Kitte yapılan her değişiklik `CHANGELOG.md` dosyasına yazılır.

## Kapatmak

Yalnız kendi makinende, yalnız bu repoda kapatmak için repoya dokunma. `.claude/settings.local.json` dosyasına yaz (bu dosya depoya girmez):

```json
{ "enabledPlugins": { "superpowers@devkit": false } }
```

Bir paketi repodan herkes için çıkarmak ekip kararıdır:

```bash
bin/kit.py unplug ~/code/my-app --packages ui
```

## Token kullanımı

Limiti dolduran şey yazılan kod değil, her adımda bütün konuşmanın yeniden okunmasıdır. Konuşma ne kadar uzun ve kalabalıksa her adım o kadar pahalıdır. Bu kitin çıktığı ekipte ölçülen bir haftada harcamanın yaklaşık beşte dördü bağlamı 200 bin token'ı aşmış adımlardan, benzer bir pay da repo yerine bir üst klasörde açılan oturumlardan geldi. Kendi durumunu `bin/usage.py` ile ölçebilirsin.

### Oturumu reponun içinde aç

```bash
cd ~/code/my-app
claude
```

Bir üst klasörde açma. Orada açılan oturum birkaç repoyu birden gezer, reponun `AGENTS.md` dosyasını ve kitini görmez, bağlamı gereksiz büyür. İki repoda birden iş yapacaksan iki ayrı oturum aç.

### `/clear`: bir iş, bir oturum

`/clear` konuşmayı sıfırlar. Kendiliğinden çalışmaz, sen yazarsın.

Ne zaman:

- Bir iş bitti ve ilgisiz başka bir işe geçiyorsun.
- Aynı oturumda saatlerdir çalışıyorsun ve Claude eski şeyleri karıştırmaya başladı.
- `/context` yazdığında bağlamın büyük kısmı dolmuş görünüyor.

Nasıl:

1. İş yarımsa önce "ilerlemeyi `docs/PROGRESS.md` dosyasına yaz" de. Değişiklikleri commit et ya da en azından kaydedildiğinden emin ol.
2. `/clear` yaz.
3. Yeni işi anlat. Claude nerede kaldığını bilir: `docs/PROGRESS.md` dosyasının başı temizlikten sonra da kendiliğinden yeniden gösterilir.

Ne zaman yapma: bir işin ortasındaysan ve Claude'un aklındaki ayrıntı henüz hiçbir dosyaya yazılmadıysa. O durumda `/compact <neye odaklansın>` kullan; konuşmayı özetleyerek küçültür, işi bırakmaz. Örnek: `/compact ödeme dışa aktarma hatası ve denenen çözümler`.

### Claude'un kendiliğinden yaptıkları

Bunlar ekip kurallarında ve `fable-orchestration` içinde yazılı; senin bir şey yapman gerekmez, ama uymadığını görürsen hatırlat:

- **Alt ajana tek iş.** Ana oturum her alt ajana tek bir iş verir. Alt ajan işi bitince rapor edip kapanır; iş büyürse ya da bağlamı yaklaşık 200 bin token'ı geçerse durup rapor eder, kalan iş yeni bir alt ajana verilir.
- **Model seçimi.** Arama, okuma ve özet işleri Sonnet'e, toplu veri temizliği Haiku'ya, zor işler Opus'a gider.
- **Kısa çıktı.** Test ve derleme komutları başarıda birkaç satır, hatada ayrıntı basar. Claude bütün bir günlüğü ya da dosyayı ekrana dökmez, gereken kısmı okur.

### Ölçmek

```bash
bin/usage.py --days 7
```

Son günlerin kullanımını modele, ana oturum ve alt ajan ayrımına, bağlam büyüklüğüne ve projeye göre gösterir. Yalnız kendi makinendeki kayıtları okur, hiçbir yere göndermez. Dolar rakamı liste fiyatıyla bir tahmindir; payları karşılaştırmak ve bir değişikliğin öncesi ile sonrasına bakmak içindir.

### Kitin kendi maliyeti

Kit takılıyken her oturuma yaklaşık 1.300 token eklenir (skill adları ve açıklamaları; `claude plugin details` tahmini). Buna `docs/PROGRESS.md` dosyasının başı da eklenir (en çok 80 satır ya da 4.000 karakter). Bir skill çalıştığında kendi metni yüklenir: `brainstorming` yaklaşık 5.400, `subagent-driven-development` yaklaşık 7.000 token. Asıl maliyet sürecin kendisidir: tasarım, plan ve alt ajanlı uygulama küçük bir işte gereksiz uzun sürer. Küçük işte süreci atlatmanın nedeni budur.

## Sorun giderme

| Belirti | Bak |
| --- | --- |
| Skill'ler oturumda görünmüyor | `bin/kit.py status <repo>`. Paket "not plugged" görünüyorsa repo kite bağlanmamıştır. "on" görünüyorsa `bin/kit.py install <repo>` çalıştır, klasöre güvendiğinden emin ol, oturumu yeniden aç |
| `Plugin ... not found in marketplace` | Kit bu makinede kayıtlı değil ya da eski. `bin/kit.py install <repo>`, olmazsa `claude plugin marketplace update devkit` |
| Kit güncellendi ama eski skill çalışıyor | `claude plugin marketplace update devkit`, ardından `claude plugin update core@devkit`. Yeni oturum aç |
| Claude her küçük işte plan yazıyor | "Bu küçük iş, doğrudan yap" de. Sürekli oluyorsa reponun `AGENTS.md` dosyasında ekip kuralları bölümü var mı bak |
| Claude doğrulamadan "bitti" diyor | Reponun `AGENTS.md` dosyasında "Verify" satırı dolu mu bak. Yoksa `/core:repo-setup` çağır |
| Bir oturum saçmaladı, neden bilmek istiyorsun | Claude'a "superpowers bu oturumda neyi yanlış yaptı, incele" de |

## Bilinen sınırlar

- Kit yalnız Claude Code'da çalışır. Codex bu paketleri görmez; Codex yalnız `AGENTS.md` dosyasını okur.
- Skill'lerin devreye girmesi kesin değildir. Model seçer; superpowers bu seçimi güçlü biçimde zorlar ama garanti etmez. Kesin olması gereken kontrol CI'da durur.
- Kit kendiliğinden güncellenmez. Yeni sürümü sen çekersin.
- Kit Windows, macOS ve Linux için yazıldı ama yalnız Linux'ta sınandı. Windows'ta oturum başı hook'u Git for Windows ile gelen `bash`'i kullanır (superpowers ile aynı sarmalayıcı); `bash` bulunamazsa sessizce atlanır, kitin geri kalanı çalışır.
