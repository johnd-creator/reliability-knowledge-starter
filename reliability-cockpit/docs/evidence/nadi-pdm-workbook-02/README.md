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
| bc-irregular-axis-dark-1440.png | `18da43ab55f805383e8e15c19450cb133af36f29c7a96622bc26661d55f7668a` |
| bc-irregular-axis-dark-1920.png | `80aec4c90bb2a092f9c17faff316c423176d3e18d711d3e9eaac60e279653aab` |
| bc-irregular-axis-light-1440.png | `56c635fdd764c6f8149aabd6405f9cdfd9612beb78c68c4bab559a951953edf5` |
| bc-irregular-axis-light-1920.png | `ec7af598fb9e4e76ceca30ddb0e3ecec5f3bcd3db442c711bdbdf9763aa8bc7e` |
| boiler-five-axis-dark-1440.png | `3901829823991059e3f88e88be02d856365c6534f916a5041312f00074e97356` |
| boiler-five-axis-dark-1920.png | `06f6f775153dd3d31923ab7a6a162ef4ba58c54d38b8d56d86d9a79f6da8e1d8` |
| boiler-five-axis-light-1440.png | `2e81c1873e1499ecdddd4ec1ab9b7c0661d071b0b6cacce30a93c79cb8f2c8aa` |
| boiler-five-axis-light-1920.png | `0f626e8decc37a19c8b94020df0bda5730e60ebce08035214200ae638d60ed18` |
| boiler-three-point-rms-dark-1440.png | `8c4a29d1344a30492716a244c559541e4e3da1b6ecbf9ae5ca5448d56d88207b` |
| boiler-three-point-rms-dark-1920.png | `268d9ddcc45bf747ccb7770998e5836e50c2453ad6fd381eaf05277c3038d64b` |
| boiler-three-point-rms-light-1440.png | `89dddc2ffc609c510f428613ee3f0f3a23e681556b5a4e9579f868fba0c8c493` |
| boiler-three-point-rms-light-1920.png | `eb97e7220314fc58f932122722dd026f84a60910c77fb815d268142f9eb06054` |
| candidate-dictionary.json | `a3db0a58ca54339e122190f61d4bba35d0eec10f0954c49fba19ede564841fb9` |
| cep-bearing-cbm-dark-1440.png | `6716824af73ca80c011025459a03efdb55b6f9f3f10657743fe9529ebf741f8a` |
| cep-bearing-cbm-dark-1920.png | `b331c1ca6822895de4dec54d0e3f6849c86bf0b6cd80405f1b0b7529dfc61fae` |
| cep-bearing-cbm-light-1440.png | `9c114929a574aae9fbea7d58e36c2438fba6650522aa0e48f2d98e2a0ceefbe2` |
| cep-bearing-cbm-light-1920.png | `c176dcf2d9d28c4627c62700f7ad0748faeacb9090fb0ac5921c189881436711` |
| cep-ir-window-dark-1440.png | `a49d7b31cfbd73cecb4235a6aa751bb08fb9f8336ff492998afb3c36f9bd735e` |
| cep-ir-window-dark-1920.png | `96eb89e71f2b146cb71ad56d46194050c1ba8250e40faf74814ea3a6ea3cffd8` |
| cep-ir-window-light-1440.png | `3ef5e0376deb03d0579d70ab5b370db0f704e02d86e909decaad39690c5eecd6` |
| cep-ir-window-light-1920.png | `625014bf1737aa61271b4ec3ccb75e12871f8cf64ec9a9499a126e86f3aa1014` |
| results.json | `e5413119562790e97b2fde350ecfb2f85359dc2bd7cc8ec3f30f0776f1160472` |
| source-inventory.json | `e1a2c0b282711051944aa34a458f9bb6409fd07b47568e3e7f2f6c84b33bd1f8` |
| turbine-four-point-dark-1440.png | `28c4679f4b17ed59ab37966be1bcdc1ce67ee0cd2976daf4c6bef77ec6a37a55` |
| turbine-four-point-dark-1920.png | `36db86735debacac20a86783e95abd31f46e06de4c94204dd1efdce2c4ac63fe` |
| turbine-four-point-light-1440.png | `32f35270a092aef9cafbe9adb64cefd6adcab78552c093ec60262e1048a6b849` |
| turbine-four-point-light-1920.png | `a94285b046e1a8942f150a8c9e0ef7728c9fc680de58be9760cf725b3a4ff598` |
