# Pemetaan input NK ke PI Collector

Kandidat berikut berasal dari registry verified/ok. Kesamaan nama belum membuktikan kesesuaian dengan fitur training. Seluruh pemetaan awal berstatus unknown dan belum digunakan untuk prediksi otomatis.

| Fitur | Kandidat yang tersedia | Catatan |
|---|---|---|
|Gross Load|BSR.GEN ACTIVE POWER 1; BSR.GEN ACTIVE POWER 2; BSR.GEN ACTIVE POWER 3; BSR1.Generator Gross Capacity rev|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|PS|BSR_UATAACTIVEPOWER.REAL; BSR_UATBACTIVEPOWER.REAL|PS = pemakaian sendiri (konfirmasi pengguna). Tag dan satuan W/MW belum dikonfirmasi; kandidat daya auxiliary tidak otomatis dipakai atau dijumlahkan.|
|Coal flow|Total Coal Flow; Total Coal Flow Edited; Total Coal Flow|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|SFC||Belum ada pemetaan atau rumus yang disetujui; tidak dihitung otomatis.|
|Main Steam Press|BSR.MAIN STEAM HEAD PRE1; BSR.MAIN STEAM HEAD PRE2; BSR.MAIN STEAM HEAD PRE3|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|Main Steam Temp|BSR.MAIN STEAM TEMP|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|Main Steam Flow|BSR.MAIN STEAM FLOW|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|Economizer Inlet Temp||Belum ada kandidat yang dapat dipastikan dari nama registry; perlu discovery terarah.|
|APH A In O2|BSR.APH A IN FLUE GAS O2 1; BSR.APH A IN FLUE GAS O2 2; BSR.APH A IN FLUE GAS O2 3|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|APH A in flue gas temp|BSR.APH A OTL FLUE GAS TEMP 1; BSR.APH A OTL FLUE GAS TEMP 2; BSR.APH A OTL FLUE GAS TEMP 3|Registry menyebut outlet; fitur training menyebut inlet. Jangan disamakan tanpa bukti.|
|Condensor Vacuum|BSR.CONDENSER A VACCUM; BSR.CONDENSER B VACCUM|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|Feedwater Flow|Final Feedwater Flow|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
|Total Air Flow|BSR.TOTAL AIRFLOW|Perlu konfirmasi atribut, satuan sumber dan satuan training.|
