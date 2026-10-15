# WORKBOOK-02 — Evidence kandidat tersanitasi

Seluruh screenshot adalah komponen aktual dengan request diintersepsi dan fixture **DEMO / QA SINTETIS**. Bukan live HTTPS3000, bukan data workbook asli, bukan engineer UAT. Nilai 0 pada screenshot sengaja diisi sebagai uji nol sintetis; semua nilai template awal UNKNOWN/null.

- [Inventaris 177 worksheet](source-inventory.json) · 65 signature struktur, bukan 65 konfigurasi engineering yang disetujui.
- [Kamus 42 field baru dan lineage](candidate-dictionary.json) · 39 DIRECT, 3 AMBIGUOUS; sembilan DIRECT lama tetap pada evidence WORKBOOK-01.
- [169 pemeriksaan browser](results.json) · mencakup 92 pemeriksaan existing.

| Profil | Light 1440 | Light 1920 | Dark 1440 | Dark 1920 |
|---|---|---|---|---|
| bc-irregular-axis | [light 1440](bc-irregular-axis-light-1440.png) | [light 1920](bc-irregular-axis-light-1920.png) | [dark 1440](bc-irregular-axis-dark-1440.png) | [dark 1920](bc-irregular-axis-dark-1920.png) |
| boiler-five-axis | [light 1440](boiler-five-axis-light-1440.png) | [light 1920](boiler-five-axis-light-1920.png) | [dark 1440](boiler-five-axis-dark-1440.png) | [dark 1920](boiler-five-axis-dark-1920.png) |
| boiler-three-point-rms | [light 1440](boiler-three-point-rms-light-1440.png) | [light 1920](boiler-three-point-rms-light-1920.png) | [dark 1440](boiler-three-point-rms-dark-1440.png) | [dark 1920](boiler-three-point-rms-dark-1920.png) |
| cep-bearing-cbm | [light 1440](cep-bearing-cbm-light-1440.png) | [light 1920](cep-bearing-cbm-light-1920.png) | [dark 1440](cep-bearing-cbm-dark-1440.png) | [dark 1920](cep-bearing-cbm-dark-1920.png) |
| cep-ir-window | [light 1440](cep-ir-window-light-1440.png) | [light 1920](cep-ir-window-light-1920.png) | [dark 1440](cep-ir-window-dark-1440.png) | [dark 1920](cep-ir-window-dark-1920.png) |
| turbine-four-point | [light 1440](turbine-four-point-light-1440.png) | [light 1920](turbine-four-point-light-1920.png) | [dark 1440](turbine-four-point-dark-1440.png) | [dark 1920](turbine-four-point-dark-1920.png) |

## Integritas artefak

| File | SHA256 |
|---|---|
| bc-irregular-axis-dark-1440.png | `c354315d08bc6c04a7af43b69a78a8503ecdd95b7bc798e0717e9b82453169a1` |
| bc-irregular-axis-dark-1920.png | `4184525d36a3743b2f7392b670cf5948c55a5c3bab55d0f502f32dec45c5d8b4` |
| bc-irregular-axis-light-1440.png | `23b1925840b1e9bf440f73958cc71e4350bb5a7405873b99c3c1b43137fb272c` |
| bc-irregular-axis-light-1920.png | `6059a7412b8c9188aafe7c964397fb59158ce824796deb6c235779acf9da7d23` |
| boiler-five-axis-dark-1440.png | `2088e4f518e4466f67260d5a6ce4d958575dd9aa074167bc9a44f641df51e095` |
| boiler-five-axis-dark-1920.png | `377270268674ae5d8e7602c3ecad4e62530594742d4b1374a247743443af7824` |
| boiler-five-axis-light-1440.png | `ff48b92c0e1f7153db7284cfe44310009c02ab118df204a8f927e20ca56501a0` |
| boiler-five-axis-light-1920.png | `978cf150984e31c73faab268da669a6642d351daf9adc907e9016f1bf59dc72e` |
| boiler-three-point-rms-dark-1440.png | `624566295f854da822e232b317d81de43bcde58a1e45255cd96e614a17e0c642` |
| boiler-three-point-rms-dark-1920.png | `6f3a0b1be1ae3854c5e9418e36ee1339db11da4d4e4463a350be5d76ed72f7d3` |
| boiler-three-point-rms-light-1440.png | `3e0049ebb3424dcbfcadadf80c6d37de2a792e1e4042cb8162aeb992f1883da6` |
| boiler-three-point-rms-light-1920.png | `ba409716003086cc962e9e121e3a1dd2235fc6a5dd1329cb0b01c115e40e871d` |
| candidate-dictionary.json | `651daa29b8d4c8ebf469953d6c5f12dc1dfe051e6aaed7c6d8d264ca38477a7a` |
| cep-bearing-cbm-dark-1440.png | `6716824af73ca80c011025459a03efdb55b6f9f3f10657743fe9529ebf741f8a` |
| cep-bearing-cbm-dark-1920.png | `b331c1ca6822895de4dec54d0e3f6849c86bf0b6cd80405f1b0b7529dfc61fae` |
| cep-bearing-cbm-light-1440.png | `9c114929a574aae9fbea7d58e36c2438fba6650522aa0e48f2d98e2a0ceefbe2` |
| cep-bearing-cbm-light-1920.png | `c176dcf2d9d28c4627c62700f7ad0748faeacb9090fb0ac5921c189881436711` |
| cep-ir-window-dark-1440.png | `a49d7b31cfbd73cecb4235a6aa751bb08fb9f8336ff492998afb3c36f9bd735e` |
| cep-ir-window-dark-1920.png | `96eb89e71f2b146cb71ad56d46194050c1ba8250e40faf74814ea3a6ea3cffd8` |
| cep-ir-window-light-1440.png | `3ef5e0376deb03d0579d70ab5b370db0f704e02d86e909decaad39690c5eecd6` |
| cep-ir-window-light-1920.png | `625014bf1737aa61271b4ec3ccb75e12871f8cf64ec9a9499a126e86f3aa1014` |
| results.json | `7260e3d4eb872cd274f453448706aa01f143aeafe7e7311c687c2499af2caa7f` |
| source-inventory.json | `e1a2c0b282711051944aa34a458f9bb6409fd07b47568e3e7f2f6c84b33bd1f8` |
| turbine-four-point-dark-1440.png | `4e397c4207d4e25a285b54157108b8419a03ca68b80138150afdff9ab884da08` |
| turbine-four-point-dark-1920.png | `8fb46f3435810a70d6a9c66f8b89f6d01a3c5e45aaa9508f3f887ffd147d8b0d` |
| turbine-four-point-light-1440.png | `28c76b6e0078dec56aef752b3269619968ef1f242b9afe016c27172c34a1807a` |
| turbine-four-point-light-1920.png | `670c060ef5b94dc870565a90a618378f582eefd730dba1867a941696ec728866` |
