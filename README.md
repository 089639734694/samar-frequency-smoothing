# SAMAR — Penghalusan Frekuensi yang Mempertahankan Relasi Antartabel

Kode pendamping makalah IF6060 Kriptografi:
**"SAMAR: Penghalusan Frekuensi yang Mempertahankan Relasi Antartabel untuk
Melindungi Kolom Data Pribadi pada Basis Data Oracle"**

Muchammad Iqbal — 23525011 — Magister Informatika Opsi Cyber Security, STEI ITB

## Ringkasan

Enkripsi deterministik, blind index, dan masking konsisten semuanya
mempertahankan kesetaraan, dan karena itu semuanya mempertahankan histogram
frekuensi plaintext. Repositori ini mengukur kebocoran tersebut, lalu
mengusulkan dan mengevaluasi **SAMAR**, yang menurunkan pemilih homofon secara
deterministik dari pengenal entitas melalui HMAC berkunci sehingga histogram
menjadi rata **tanpa** merusak konsistensi antartabel.

## Peringatan data

Seluruh data bersifat **sintetis**. Jangan pernah menjalankan eksperimen ini
terhadap data pribadi yang sesungguhnya: yang dijalankan di sini adalah serangan
pemulihan data, sehingga memakai data riil akan bertentangan dengan argumen
makalahnya sendiri dan berpotensi melanggar UU No. 27 Tahun 2022.

## Struktur

```
src/
  schemes.py        enam skema: B0 plaintext, B1 masking konsisten,
                    B2 AES-SIV, B3 blind index HMAC, V1 homofonik acak, P SAMAR
  datagen.py        pembangkit data kepegawaian + penggajian sintetis
  attacks.py        A1 analisis frekuensi, A2 penugasan optimal,
                    A3 korelasi antarkolom, A4 lintas tabel
  experiment.py     eksperimen keamanan (rerata +- SB atas T percobaan)
  oracle_bench.py   pengukuran kinerja pada Oracle
  figures.py        pembangkit gambar makalah
  paper_content.py  seluruh isi prosa makalah
  build_paper.py    perakit berkas Word dari template IEEE
  smoke_test.py     uji cepat klaim inti
results/            CSV hasil, gambar, dan pratinjau PDF
config/             oracle.ini.contoh (salin jadi oracle.ini, jangan di-commit)
```

## Menjalankan

Butuh Python 64-bit dengan `numpy scipy cryptography python-docx`
(Python 32-bit tidak bisa: numpy/pandas tak lagi menyediakan wheel 32-bit).

```bash
python src/smoke_test.py                       # verifikasi klaim inti
python -c "import sys;sys.path.insert(0,'src');import experiment;experiment.main(T=20)"
python src/figures.py                          # gambar
python src/build_paper.py                      # berkas Word
```

### Pengukuran Oracle

```bash
cp config/oracle.ini.contoh config/oracle.ini   # lalu isi kredensial
python src/oracle_bench.py                      # ukur
python src/oracle_bench.py --cleanup            # hapus tabel uji
```

Gunakan **schema uji terpisah** dengan tabel sintetis. Skrip hanya membuat
tabel berawalan `SAMAR_` dan menghapusnya kembali; ia tidak pernah membaca
tabel aplikasi mana pun.

Bila basis datanya Oracle lama dengan password verifier usang, mode *thin*
akan gagal dengan `DPY-3015`. Pakai mode *thick* dengan Oracle Instant Client
64-bit dan panggil `oracledb.init_oracle_client(lib_dir=...)`.

## Hasil utama

| Temuan | Angka |
|---|---|
| Recovery analisis frekuensi, skema deterministik | 100% (agama, jenis kelamin, status kawin); 96,6% (golongan) |
| B0, B2, B3 identik satu sama lain | ya — pemetaan bijektif nilai→token |
| Recovery terhadap SAMAR | ≤ 1,9%, di bawah lantai tebak-terbanyak |
| Konsistensi antartabel | SAMAR 100% vs homofonik acak 9,6% |
| Biaya eksekusi Oracle | buffer gets = 119,4 + 1,962·k |
| Ekspansi kueri 196× | hanya 4,16× biaya |
| Keterbatasan: korelasi antarkolom | gaji terbuka memulihkan golongan 100% pada **semua** skema |

```powershell
$w = New-Object -ComObject Word.Application
$d = $w.Documents.Open("<path>\IEEE_template_makalah.doc", $false, $true)
$d.SaveAs2("<repo>\results\IEEE_template.docx", 16)
$d.Close($false); $w.Quit()
```
