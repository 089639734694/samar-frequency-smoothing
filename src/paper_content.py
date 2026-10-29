"""
paper_content.py - Seluruh isi prosa makalah, terpisah dari kode pembangun
dokumen agar mudah disunting tanpa menyentuh logika format.

Konvensi penanda:
  ("H1", teks)        judul bagian  (otomatis dinomori I, II, III, ...)
  ("H2", teks)        subbagian     (otomatis dinomori A, B, C, ... per bagian)
  ("P",  teks)        paragraf isi
  ("EQ", teks)        persamaan (rata tengah, bernomor manual di teks)
  ("TBL", kunci)      sisipkan tabel dengan kunci tsb dari TABEL
  ("FIG", kunci)      sisipkan gambar dengan kunci tsb dari GAMBAR
  ("LIST", [a, b])    daftar bernomor
"""

JUDUL = ("SAMAR: Penghalusan Frekuensi yang Mempertahankan Relasi "
         "Antartabel untuk Melindungi Kolom Data Pribadi pada Basis Data Oracle")

PENULIS = "Muchammad Iqbal - 23525011"
AFILIASI = [
    "Program Studi Magister Informatika Opsi Cyber Security",
    "Sekolah Teknik Elektro dan Informatika",
    "Institut Teknologi Bandung, Jl. Ganesha 10 Bandung 40132, Indonesia",
]
EMAIL = "23525011@std.stei.itb.ac.id, muchammad.iqbal@gmail.com"

ABSTRAK = (
    "Abstrak—Kolom data pribadi pada basis data korporasi kerap harus tetap "
    "dapat dicari dan di-JOIN, sehingga organisasi memakai transformasi yang "
    "mempertahankan kesetaraan: enkripsi deterministik, blind index, atau "
    "masking konsisten. Makalah ini menunjukkan bahwa ketiganya, walau "
    "dipasarkan sebagai kontrol yang berbeda, memiliki kebocoran yang identik "
    "secara terukur. Pada eksperimen 20 percobaan atas data kepegawaian "
    "sintetis, analisis frekuensi memulihkan 100% nilai kolom agama, jenis "
    "kelamin, dan status kawin, serta 96,6% kolom golongan, dengan angka yang "
    "sama persis untuk enkripsi deterministik AES-SIV maupun blind index HMAC. "
    "Mitigasi yang ada di literatur, yaitu penghalusan frekuensi homofonik, "
    "meratakan histogram tetapi memilih homofon secara acak per baris sehingga "
    "konsistensi antartabel runtuh ke 2,1% dan salinan non-produksi kehilangan "
    "kegunaannya. Makalah ini mengusulkan SAMAR (Smoothing Antifrekuensi "
    "Mempertahankan Asosiasi Relasional), yang menurunkan pemilih "
    "homofon secara deterministik dari pengenal entitas melalui HMAC berkunci. "
    "SAMAR menekan recovery rate ke paling tinggi 1,9%, di bawah lantai tebak-"
    "terbanyak, sambil mempertahankan konsistensi antartabel 100%. Pengukuran "
    "pada basis data Oracle 12c menunjukkan biaya ekspansi kueri jauh lebih "
    "murah daripada dugaan model naif: buffer gets per eksekusi tumbuh menurut "
    "119,4 + 1,962k, sehingga ekspansi 196 kali hanya berbiaya 4,16 kali. "
    "Eksperimen juga menemukan bahwa penghalusan frekuensi tidak melindungi "
    "terhadap korelasi antarkolom; kolom gaji yang dibiarkan terbuka tetap "
    "memulihkan golongan 100%, sehingga kolom kuasi-pengenal yang berkorelasi "
    "wajib ikut ditangani."
)

KATA_KUNCI = ("Kata Kunci—analisis frekuensi, blind index, data masking, "
              "enkripsi deterministik, pelindungan data pribadi, "
              "penghalusan frekuensi")

ISI = [
    # =====================================================================
    ("H1", "PENDAHULUAN"),
    ("H2", "Latar Belakang"),
    ("P",
     "Basis data aplikasi korporasi menyimpan data pribadi dalam jumlah besar: "
     "nomor induk pegawai, nama, golongan jabatan, agama, status perkawinan, "
     "dan nominal penghasilan. Undang-Undang Nomor 27 Tahun 2022 tentang "
     "Pelindungan Data Pribadi [1] mewajibkan pengendali data menerapkan "
     "langkah teknis untuk melindungi data tersebut, dan menempatkan data "
     "keuangan pribadi sebagai data yang bersifat spesifik sehingga menuntut "
     "perlindungan lebih ketat."),
    ("P",
     "Kendalanya, perlindungan itu tidak boleh mematikan fungsi basis data. "
     "Aplikasi tetap harus dapat menjalankan pencarian kesetaraan seperti "
     "WHERE golongan = ? dan tetap harus dapat menggabungkan tabel melalui "
     "JOIN. Enkripsi acak seperti AES-GCM memberi kerahasiaan terkuat, tetapi "
     "ciphertext yang berbeda untuk plaintext yang sama membuat kedua operasi "
     "itu mustahil dijalankan oleh mesin basis data. Enkripsi transparan pada "
     "tingkat penyimpanan seperti Transparent Data Encryption [2] menjawab "
     "persoalan lain, yaitu pencurian berkas data atau cadangan, tetapi tidak "
     "memberi perlindungan apa pun terhadap pihak yang memiliki akses SQL yang "
     "sah, termasuk pengembang, administrator basis data, dan vendor."),
    ("P",
     "Karena itu praktik di lapangan jatuh pada kelas transformasi yang "
     "mempertahankan kesetaraan, yaitu transformasi dengan sifat bahwa "
     "plaintext yang sama selalu menghasilkan keluaran yang sama. Tiga bentuk "
     "yang paling lazim adalah enkripsi deterministik [3], blind index berbasis "
     "HMAC [4] pada tingkat aplikasi, dan masking konsisten pada lingkungan "
     "non-produksi [5]. Dua yang pertama dipandang sebagai kontrol kriptografi, "
     "sedangkan yang ketiga dipandang sebagai kontrol tata kelola data. Ketiga "
     "pendekatan itu dibahas dalam literatur dan panduan yang berbeda, dan "
     "lazimnya ditangani oleh unit kerja yang berbeda pula."),
    ("P",
     "Masking konsisten layak mendapat perhatian khusus. Masking baru berguna "
     "bila konsisten: satu nilai yang sama harus menjadi nilai tersamar yang "
     "sama di seluruh tabel, sebab bila tidak, JOIN antartabel rusak dan "
     "salinan non-produksi tidak dapat dipakai menguji apa pun. Begitu sebuah "
     "transformasi bersifat konsisten, ia mempertahankan distribusi frekuensi "
     "nilai aslinya, dan di situlah kerentanannya terletak."),
    ("H2", "Persoalan yang Dibahas"),
    ("P",
     "Penyerang yang memegang salinan statis kolom tersamar tidak perlu "
     "memecahkan kriptografi apa pun. Ia cukup menghitung berapa kali setiap "
     "nilai tersamar muncul, lalu mencocokkan peringkat frekuensi itu dengan "
     "distribusi publik yang ia ketahui. Naveed, Kamara, dan Wright [6] "
     "menunjukkan bahwa serangan semacam ini memulihkan atribut rekam medis "
     "terenkripsi deterministik pada lebih dari 60% catatan di lebih dari 60% "
     "rumah sakit yang diuji. Lacharite dan Paterson [7] mengusulkan "
     "penghalusan frekuensi berbasis penyandian homofonik sebagai mitigasinya, "
     "yaitu satu plaintext dipetakan ke beberapa ciphertext agar histogramnya "
     "rata."),
    ("P",
     "Namun mitigasi tersebut memilih homofon secara acak untuk setiap baris. "
     "Akibatnya nilai yang sama milik entitas yang sama menghasilkan token yang "
     "berbeda di tabel yang berbeda, sehingga justru merusak konsistensi "
     "antartabel yang menjadi alasan masking dan enkripsi deterministik dipakai "
     "sejak awal. Dengan kata lain, mitigasi yang tersedia di literatur tidak "
     "dapat diterapkan pada kasus yang paling banyak membutuhkannya."),
    ("H2", "Kontribusi"),
    ("P", "Kontribusi makalah ini adalah sebagai berikut."),
    ("LIST", [
        "Evaluasi empiris terpadu yang memperlakukan enkripsi deterministik, "
        "blind index, dan masking konsisten sebagai satu kelas transformasi di "
        "bawah satu model penyerang yang sama, sehingga kebocoran keduanya "
        "dapat dibandingkan secara langsung. Sepanjang penelusuran penulis, "
        "masking konsisten sebagai kontrol tata kelola belum pernah diukur "
        "secara kuantitatif dengan cara ini.",
        "Rancangan SAMAR (Smoothing Antifrekuensi Mempertahankan Asosiasi "
        "Relasional), yaitu penghalusan frekuensi yang pemilih homofonnya "
        "diturunkan secara deterministik dari pengenal entitas melalui HMAC "
        "berkunci, sehingga meratakan histogram tanpa mengorbankan konsistensi "
        "antartabel.",
        "Serangan lintas tabel yang mengagregasi frekuensi token dari dua tabel "
        "yang berbagi atribut, beserta buktinya bahwa serangan ini memperkuat "
        "pemulihan pada skema deterministik tetapi tidak memperoleh apa pun "
        "terhadap SAMAR.",
        "Pengukuran biaya ekspansi kueri pada basis data Oracle 12c "
        "sesungguhnya memakai metrik internal basis data, yang menjawab "
        "pertanyaan terbuka pada [7] mengenai kelayakan praktis penghalusan "
        "frekuensi.",
        "Temuan bahwa penghalusan frekuensi tidak melindungi terhadap korelasi "
        "antarkolom, beserta rekomendasi penanganannya.",
    ]),
    ("P",
     "Bagian II memuat tinjauan pustaka. Bagian III memaparkan model sistem dan "
     "model ancaman. Bagian IV menjelaskan rancangan SAMAR dan Bagian V "
     "implementasinya. Bagian VI menyajikan eksperimen dan hasil, Bagian VII "
     "membahas temuan dan keterbatasan, Bagian VIII memuat tautan kode sumber, "
     "dan Bagian IX menutup makalah."),

    # =====================================================================
    ("H1", "TINJAUAN PUSTAKA"),
    ("H2", "Enkripsi Deterministik dan Enkripsi yang Mempertahankan Sifat"),
    ("P",
     "Bellare, Boldyreva, dan O'Neill [3] memformalkan enkripsi deterministik "
     "dan menunjukkan bahwa skema semacam itu tidak mungkin memenuhi keamanan "
     "semantik, karena kesetaraan ciphertext dengan sendirinya membocorkan "
     "kesetaraan plaintext. Keamanan terbaik yang dapat dicapai adalah bagi "
     "plaintext berentropi tinggi. AES-SIV [8], [9] adalah realisasi praktis "
     "enkripsi deterministik terautentikasi yang dipakai luas, dan menjadi "
     "salah satu pembanding pada makalah ini."),
    ("P",
     "CryptDB [10] mempopulerkan penggunaan enkripsi yang mempertahankan sifat "
     "di dalam basis data agar kueri dapat dijalankan langsung atas ciphertext. "
     "Pendekatan itu memicu rangkaian penelitian mengenai kebocoran yang "
     "melekat padanya."),
    ("H2", "Serangan Inferensi dan Leakage-Abuse"),
    ("P",
     "Naveed, Kamara, dan Wright [6] menunjukkan bahwa kolom terenkripsi "
     "deterministik dapat dipulihkan hanya dengan analisis frekuensi dan data "
     "bantu publik, serta memperkenalkan varian berbasis optimasi penugasan. "
     "Grubbs dan rekan [11] memperluasnya ke enkripsi yang mengungkap urutan, "
     "sedangkan Bindschaedler dan rekan [12] mengkaji sejauh mana inferensi "
     "semacam itu berhasil pada konfigurasi yang lebih realistis. Kellaris dan "
     "rekan [13] menunjukkan serangan generik atas basis data teralihdaya. "
     "Rangkaian karya tersebut mapan pada sisi serangan, dan makalah ini tidak "
     "mengklaim kebaruan di sana; serangan dipakai sebagai alat ukur."),
    ("H2", "Penghalusan Frekuensi"),
    ("P",
     "Lacharite dan Paterson [7] mengusulkan frequency-smoothing encryption, "
     "yang meminjam penyandian homofonik dari kriptografi klasik: nilai v "
     "memperoleh sejumlah homofon sebanding dengan frekuensinya, sehingga "
     "histogram ciphertext menjadi mendekati seragam. Makalah tersebut "
     "menyatakan bahwa satu kueri kesetaraan harus dijalankan sekali untuk "
     "setiap homofon, dan menilai dampaknya masih dapat dikelola, tetapi tidak "
     "mengukurnya pada mesin basis data relasional. Grubbs dan rekan [14] "
     "kemudian mengembangkan PANCAKE, yang meratakan frekuensi akses pada "
     "penyimpanan kunci-nilai, bukan frekuensi nilai pada kolom relasional."),
    ("P",
     "Kedua karya tersebut memilih homofon secara acak per operasi. Pada "
     "penyimpanan kunci-nilai hal itu tidak menimbulkan masalah, tetapi pada "
     "basis data relasional yang mengandalkan konsistensi antartabel, pemilihan "
     "acak merusak sifat yang justru dibutuhkan. Celah inilah yang diisi SAMAR."),
    ("H2", "Masking dan Pseudonimisasi sebagai Kontrol Tata Kelola"),
    ("P",
     "ENISA [15] mencatat bahwa pembedaan pseudonim dimungkinkan hanya dengan "
     "melakukan analisis frekuensi atas pseudonim yang teramati, dan bahwa "
     "sebagian pengenal memang lebih sering muncul daripada yang lain. NIST SP "
     "800-188 [16] menganjurkan agar risiko identifikasi ulang diukur setelah "
     "transformasi dilakukan, bukan diasumsikan hilang. Panduan produk masking "
     "[5] menyediakan mode deterministik agar konsistensi antartabel terjaga, "
     "dan menganjurkan kolam nilai pengganti yang besar untuk mengurangi "
     "keterdugaan. Peringatan-peringatan tersebut bersifat kualitatif dan belum "
     "disertai pengukuran, sehingga besaran risikonya tidak diketahui praktisi."),
    ("H2", "Celah Penelitian"),
    ("P",
     "Dari tinjauan di atas, tiga celah dapat diidentifikasi. Pertama, kebocoran "
     "masking konsisten diperingatkan tetapi tidak pernah diukur, dan tidak "
     "pernah dibandingkan langsung dengan enkripsi deterministik di bawah satu "
     "model penyerang. Kedua, mitigasi penghalusan frekuensi yang tersedia "
     "merusak konsistensi antartabel sehingga tidak dapat dipakai pada "
     "lingkungan relasional. Ketiga, biaya ekspansi kueri yang ditimbulkan "
     "penghalusan frekuensi belum pernah diukur pada basis data relasional "
     "produksi. Makalah ini menutup ketiganya."),

    # =====================================================================
    ("H1", "MODEL SISTEM DAN MODEL ANCAMAN"),
    ("H2", "Model Sistem"),
    ("P",
     "Sistem yang dimodelkan adalah basis data relasional korporasi berisi "
     "sekurang-kurangnya dua tabel yang berbagi atribut sensitif: tabel entitas "
     "dengan satu baris per entitas, dan tabel transaksi dengan banyak baris "
     "per entitas. Pada studi kasus makalah ini, tabel entitas adalah tabel "
     "pegawai dan tabel transaksi adalah riwayat penggajian bulanan. Atribut "
     "sensitif pada kedua tabel harus tetap dapat dicari melalui kueri "
     "kesetaraan dan harus konsisten antartabel."),
    ("P",
     "Kunci kriptografis dipegang aplikasi dan diasumsikan tidak bocor ke "
     "penyerang. Transformasi dilakukan pada tingkat aplikasi sebelum data "
     "ditulis, sehingga mesin basis data tidak pernah memegang kunci. Gambar 1 "
     "merangkum model sistem beserta posisi penyerang yang dibahas."),
    ("FIG", "sistem"),
    ("H2", "Model Penyerang"),
    ("P",
     "Penyerang bersifat snapshot dan semi-jujur: ia memperoleh salinan statis "
     "kolom tersamar beserta kolom lain yang tidak disamarkan, tetapi tidak "
     "memegang kunci dan tidak mengubah data. Tabel I merangkum tiga posisi "
     "penyerang yang dimodelkan."),
    ("TBL", "model_penyerang"),
    ("P",
     "Pada ketiga posisi tersebut, penyerang diasumsikan memegang distribusi "
     "bantu publik per kolom yang berkorelasi baik dengan distribusi "
     "sesungguhnya tetapi tidak identik dengannya, sesuai asumsi yang dipakai "
     "pada [6]. Di luar cakupan makalah ini adalah penyerang yang memegang "
     "kunci, penyerang aktif yang mengubah data, serta serangan terhadap "
     "lapisan jaringan dan sistem operasi."),
    ("H2", "Sifat yang Ditargetkan"),
    ("P",
     "Skema yang memadai harus memenuhi sifat keamanan sekaligus sifat "
     "fungsional. Sifat keamanan: S1, ketahanan terhadap analisis frekuensi, "
     "yaitu histogram token tidak boleh mencerminkan histogram plaintext. "
     "Sifat fungsional: R1, kueri kesetaraan tetap dapat dijalankan oleh mesin "
     "basis data; R2, konsistensi antartabel, yaitu atribut satu entitas harus "
     "menghasilkan token yang sama di setiap tabel; dan R3, biaya penyimpanan "
     "dan eksekusi tetap dalam batas yang praktis. Tabel II memperlihatkan "
     "bahwa tidak satu pun skema yang ada memenuhi S1, R1, dan R2 sekaligus."),
    ("TBL", "sifat_skema"),

    # =====================================================================
    ("H1", "RANCANGAN SKEMA SAMAR"),
    ("H2", "Notasi dan Kuota Homofon"),
    ("P",
     "Misalkan kolom sensitif memiliki domain nilai V dan tabel memuat n baris. "
     "Frekuensi nilai v dinyatakan sebagai f(v). Parameter sistem adalah target "
     "t, yaitu jumlah baris yang diharapkan ditanggung setiap homofon. Kuota "
     "homofon bagi nilai v ditetapkan sebagai"),
    ("EQ", "k(v) = maks(1, bulat(f(v) / t))  (1)"),
    ("P",
     "Nilai yang jarang memperoleh k(v) = 1 sehingga tidak menanggung biaya "
     "ekspansi sama sekali, sedangkan nilai yang umum memperoleh kuota besar. "
     "Karena setiap homofon diharapkan menanggung sekitar t baris, histogram "
     "token menjadi mendekati seragam tanpa bergantung pada seberapa condong "
     "distribusi aslinya."),
    ("H2", "Konstruksi"),
    ("P",
     "SAMAR memakai dua kunci yang saling bebas: kunci token K dan kunci "
     "pemilih K sub s. Himpunan homofon bagi nilai v dibentuk sebagai"),
    ("EQ", "T(v, j) = trunc16(HMAC-SHA256(K, v ‖ j)),  0 ≤ j < k(v)  (2)"),
    ("P",
     "Inti rancangan terletak pada cara memilih j. Berbeda dengan penghalusan "
     "frekuensi konvensional yang mengambil j secara acak, SAMAR menurunkannya "
     "secara deterministik dari pengenal entitas e pada baris tersebut:"),
    ("EQ", "j = HMAC-SHA256(K sub s, e ‖ v) mod k(v)  (3)"),
    ("P",
     "Token akhir yang disimpan pada kolom adalah T(v, j). Pengenal entitas e "
     "adalah atribut yang sudah ada pada setiap tabel, misalnya nomor induk "
     "pegawai, sehingga tidak diperlukan kolom tambahan. Gambar 2 merangkum "
     "seluruh alur pembentukan token ini."),
    ("FIG", "konstruksi"),
    ("H2", "Mengapa Konsistensi Antartabel Terjaga"),
    ("P",
     "Persamaan (3) hanya bergantung pada e dan v. Karena atribut seorang "
     "pegawai bernilai sama di tabel pegawai maupun di tabel penggajian, "
     "pemilih j yang dihasilkan pun sama, sehingga token yang tersimpan "
     "identik. Dengan demikian JOIN dan pemeriksaan silang antartabel tetap "
     "bekerja persis seperti pada data plaintext. Sebaliknya, dua pegawai "
     "berbeda yang kebetulan bergolongan sama akan memperoleh j yang berbeda "
     "karena e-nya berbeda, sehingga keduanya tersebar ke homofon yang berbeda "
     "dan histogram tetap rata. Inilah pemisahan yang menjadi inti kontribusi: "
     "keacakan yang dibutuhkan untuk meratakan frekuensi diambil dari "
     "keragaman antarentitas, bukan dari pembangkit bilangan acak."),
    ("P",
     "Pemilih j tidak dapat dihitung penyerang walaupun e terlihat jelas di "
     "tabel, sebab perhitungannya memerlukan K sub s. Dari sudut pandang "
     "penyerang, penugasan entitas ke homofon tidak dapat dibedakan dari "
     "penugasan acak."),
    ("H2", "Kueri Kesetaraan dan Ekspansi"),
    ("P",
     "Untuk mencari nilai v, aplikasi membangkitkan seluruh k(v) homofon lalu "
     "menyusun predikat IN atas himpunan tersebut. Hasilnya tepat, tanpa false "
     "positive maupun false negative, sebab himpunan homofon suatu nilai tidak "
     "beririsan dengan himpunan homofon nilai lain. Faktor ekspansi kueri "
     "terbobot didefinisikan sebagai rerata jumlah token per kueri bila peluang "
     "mengueri suatu nilai sebanding dengan frekuensinya:"),
    ("EQ", "k̄ = ( Σ f(v) · k(v) ) / n  (4)"),
    ("P",
     "Agregasi seperti GROUP BY atas kolom tersamar menghasilkan k(v) kelompok "
     "untuk setiap nilai, sehingga aplikasi perlu melipatnya kembali memakai "
     "peta token-ke-nilai yang hanya dimiliki pemegang kunci. Konsekuensi ini "
     "dibahas pada Bagian VII."),
    ("H2", "Analisis Keamanan Informal"),
    ("P",
     "Ketahanan terhadap analisis frekuensi (S1) bersumber dari dua hal. "
     "Pertama, menurut (1) setiap homofon menanggung sekitar t baris sehingga "
     "frekuensi token tidak lagi mencerminkan f(v). Kedua, menurut (3) "
     "penugasan entitas ke homofon ditentukan HMAC berkunci, sehingga penyerang "
     "tidak dapat mengelompokkan kembali homofon milik satu nilai. Agar dapat "
     "memulihkan pengelompokan itu, penyerang harus membedakan keluaran HMAC "
     "dari fungsi acak, yang berarti mematahkan HMAC-SHA256 [4]."),
    ("P",
     "Perlu ditegaskan bahwa SAMAR hanya menangani kebocoran dari histogram "
     "kolom yang bersangkutan. Ia tidak menangani kebocoran dari kolom lain "
     "yang berkorelasi, tidak menangani kebocoran pola akses, dan tidak "
     "menangani penyerang yang memegang kunci. Keterbatasan pertama terbukti "
     "signifikan pada eksperimen dan dibahas tersendiri pada Bagian VII."),

    # =====================================================================
    ("H1", "IMPLEMENTASI"),
    ("H2", "Lingkungan dan Pustaka"),
    ("P",
     "Seluruh skema diimplementasikan dalam Python 3.13 dengan pustaka "
     "cryptography [17] untuk AES-SIV dan AES-GCM, serta modul hmac dan "
     "hashlib pustaka standar untuk HMAC-SHA256. Pengukuran kinerja dilakukan "
     "terhadap basis data Oracle Database 12c Enterprise Edition 12.1.0.2 "
     "melalui pustaka python-oracledb [18] pada mode thick. Analisis serangan "
     "memakai NumPy dan SciPy, dengan penugasan optimal diselesaikan memakai "
     "algoritme Hungarian [19] melalui implementasi linear_sum_assignment."),
    ("H2", "Skema yang Dibandingkan"),
    ("P",
     "Enam skema dibandingkan. B0 adalah plaintext sebagai kontrol. B1 adalah "
     "masking konsisten yang memetakan nilai ke kolam nilai palsu melalui "
     "SHA-256, meniru mode deterministik perkakas masking komersial, dengan "
     "kolam berukuran tiga kali domain sesuai anjuran [5]. B2 adalah enkripsi "
     "deterministik AES-SIV 256 bit. B3 adalah pola tingkat aplikasi berupa "
     "AES-GCM acak pada kolom data disertai blind index HMAC-SHA256 terpotong "
     "32 bit. V1 adalah varian ablasi berupa penghalusan frekuensi homofonik "
     "dengan pemilihan homofon acak per baris, mewakili [7]. P adalah SAMAR. "
     "V1 dan P memakai target t yang sama agar faktor ekspansinya setara dan "
     "perbandingannya adil."),
    ("H2", "Data Sintetis dan Etika Data"),
    ("P",
     "Seluruh data yang dipakai bersifat sintetis dan dibangkitkan secara "
     "terprogram. Tidak satu baris pun berasal dari sistem produksi atau dari "
     "salinannya. Keputusan ini bukan sekadar kemudahan: eksperimen yang "
     "dilaporkan adalah serangan pemulihan data pribadi, sehingga menjalankannya "
     "atas data pribadi yang sesungguhnya akan bertentangan dengan argumen "
     "makalah ini sendiri dan berpotensi melanggar [1]. Serangan yang diuji "
     "hanya memerlukan distribusi yang realistis, bukan identitas orang per "
     "orang."),
    ("P",
     "Tabel pegawai memuat kolom nomor induk, jenis kelamin, golongan, agama, "
     "status kawin, unit kerja, dan gaji pokok. Tabel transaksi memuat dua "
     "belas baris penggajian bulanan per pegawai yang membawa ulang kolom "
     "golongan dan unit kerja. Bobot distribusi tiap kolom dipilih agar condong "
     "menyerupai karakteristik data kepegawaian, misalnya satu golongan "
     "menguasai sekitar 30% populasi dan satu kategori agama sekitar 84%. Gaji "
     "pokok dibangkitkan berkorelasi kuat dengan golongan disertai derau "
     "relatif, sehingga perannya sebagai kuasi-pengenal dapat diuji."),

    # =====================================================================
    ("H1", "EKSPERIMEN DAN HASIL"),
    ("H2", "Rancangan Eksperimen"),
    ("P",
     "Eksperimen keamanan dijalankan sebanyak 20 percobaan, masing-masing "
     "dengan seed berbeda sehingga data, kunci, dan distribusi bantu "
     "dibangkitkan ulang. Setiap percobaan memakai 20.000 pegawai dan 240.000 "
     "baris transaksi. Metrik utamanya adalah recovery rate, yaitu proporsi "
     "baris yang nilai aslinya berhasil ditebak penyerang. Sebagai pembanding "
     "dilaporkan pula lantai tebak-terbanyak, yaitu hasil yang diperoleh "
     "penyerang yang mengabaikan token dan menebak nilai paling umum untuk "
     "semua baris. Empat serangan diuji: A1 analisis frekuensi dengan "
     "pencocokan peringkat, A2 penugasan optimal atas histogram, A3 korelasi "
     "antarkolom yang memulihkan golongan melalui gaji pokok, dan A4 serangan "
     "lintas tabel yang mengagregasi frekuensi token dari tabel pegawai dan "
     "tabel transaksi."),
    ("P",
     "Eksperimen kinerja dijalankan terhadap Oracle 12c dengan 100.000 baris "
     "per skema. Tabel dan indeks uji dibuat pada skema dan tablespace "
     "terpisah, lalu dihapus setelah diukur. Latensi wall-clock dilaporkan "
     "sebagai konteks, tetapi metrik utamanya adalah buffer gets per eksekusi "
     "yang dibaca dari tampilan V$SQL, sebab pengukuran wall-clock terhadap "
     "basis data jarak jauh didominasi waktu pulang-pergi jaringan dan tidak "
     "mencerminkan biaya eksekusi."),
    ("H2", "Hasil Keamanan"),
    ("P",
     "Tabel III menyajikan recovery rate serangan A1 dan A2. Temuan pertama dan "
     "paling pokok: B0, B2, dan B3 menghasilkan angka yang identik, bukan "
     "sekadar berdekatan. Hal itu bukan kebetulan. Ketiganya adalah pemetaan "
     "bijektif dari nilai ke token, sehingga histogram tokennya merupakan "
     "permutasi histogram plaintext dan analisis frekuensi memperlakukan "
     "ketiganya sama persis. Dengan kata lain, mengganti masking dengan "
     "enkripsi deterministik AES-SIV 256 bit, atau dengan blind index HMAC, "
     "sama sekali tidak mengurangi kebocoran frekuensi."),
    ("TBL", "hasil_a1a2"),
    ("P",
     "Kolom berkardinalitas rendah dipulihkan seluruhnya: agama, jenis kelamin, "
     "dan status kawin mencapai 100,0% tanpa simpangan. Golongan mencapai 96,6% "
     "dengan simpangan baku 12,9 poin, yang berasal dari percobaan ketika derau "
     "pada distribusi bantu menukar peringkat dua golongan yang frekuensinya "
     "berdekatan. Unit kerja dengan kardinalitas 20 dipulihkan 79,3%, lebih "
     "rendah karena ekornya rapat sehingga lebih peka terhadap derau."),
    ("P",
     "Masking konsisten (B1) memperoleh angka yang sedikit lebih rendah, "
     "misalnya 43,6% pada unit kerja. Penyebabnya bukan perlindungan yang lebih "
     "baik, melainkan tabrakan substitusi: beberapa nilai berbeda terpetakan ke "
     "nilai palsu yang sama meskipun kolam penggantinya sudah tiga kali ukuran "
     "domain. Pada eksperimen, delapan golongan menyusut menjadi tujuh nilai "
     "tersamar. Jadi masking konsisten tidak hanya membocorkan frekuensi, "
     "tetapi juga diam-diam menggabungkan dua nilai berbeda menjadi satu dan "
     "merusak integritas data tanpa peringatan."),
    ("P",
     "Kedua skema homofonik, V1 dan SAMAR, menekan recovery rate ke paling "
     "tinggi 1,9%. Angka ini berada jauh di bawah lantai tebak-terbanyak, yang "
     "berarti penyerang tidak memperoleh informasi apa pun dari token; "
     "mengikuti hasil analisis frekuensi justru lebih buruk daripada "
     "mengabaikannya. Gambar 3 memperlihatkan sumber perbedaannya: pangsa token "
     "terbanyak turun dari 29,9% pada skema deterministik menjadi 0,29% pada "
     "SAMAR."),
    ("FIG", "gbr1"),
    ("P",
     "Tabel IV menyajikan serangan lintas tabel A4. Penambahan 240.000 baris "
     "transaksi mempertajam estimasi frekuensi penyerang sehingga serangan atas "
     "skema deterministik tetap berhasil pada tingkat yang sama, sedangkan "
     "SAMAR tetap bertahan pada 1,5% dan 1,6%. Hal ini penting karena SAMAR "
     "mempertahankan konsistensi antartabel, yaitu justru sifat yang "
     "dieksploitasi serangan ini, namun tetap tidak membocorkan apa pun. V1 "
     "memang menunjukkan angka rendah pada tabel yang sama, tetapi angka itu "
     "tidak bermakna secara operasional sebab V1 tidak mampu menyediakan "
     "konsistensi antartabel sehingga skenario dua tabel tidak dapat "
     "dijalankan di atasnya."),
    ("TBL", "hasil_a4"),
    ("H2", "Hasil Fungsional"),
    ("P",
     "Tabel V menguji sifat R2 secara langsung dengan menghitung proporsi "
     "entitas yang memperoleh token sama ketika atribut yang sama ditransformasi "
     "pada dua tabel. Skema deterministik dan SAMAR mencapai 100%. V1 hanya "
     "mencapai 2,1%, dan angka itu bukan anomali melainkan konsekuensi "
     "langsung rancangannya: dengan 401 token untuk delapan nilai, yaitu "
     "rerata sekitar lima puluh homofon per nilai, peluang dua tabel memilih "
     "homofon yang sama memang sekitar seperlima puluh. Konsekuensinya hampir "
     "setiap pegawai akan tercatat bergolongan berbeda antara tabel pegawai "
     "dan tabel penggajian, sehingga salinan non-produksi tidak dapat dipakai "
     "menguji logika bisnis apa pun yang memeriksa silang kedua tabel. "
     "Perhatikan pula bahwa makin kuat perataan frekuensi yang dituntut, makin "
     "banyak homofon yang diperlukan, dan makin parah pula kerusakan "
     "konsistensi pada V1; kedua tujuan itu saling bertentangan secara "
     "langsung pada rancangannya."),
    ("TBL", "hasil_fungsional"),
    ("H2", "Hasil Kinerja pada Oracle"),
    ("P",
     "Tabel VI menyajikan hasil pengukuran pada Oracle 12c. Pada target t = 250 "
     "yang menghasilkan faktor ekspansi terbobot 78,59, SAMAR memerlukan 273,4 "
     "buffer gets per eksekusi dibanding 50,1 pada plaintext, yaitu 5,5 kali. "
     "Perbandingan itu jauh lebih kecil daripada dugaan model naif yang "
     "menganggap biaya tumbuh sebanding dengan jumlah homofon. Indeks SAMAR "
     "berukuran 5 MB dibanding 3 MB pada plaintext; perbedaan ini terutama "
     "berasal dari panjang token heksadesimal, sebagaimana terlihat dari "
     "AES-SIV yang tokennya paling panjang dan indeksnya paling besar, yaitu "
     "7 MB dengan 153,2 buffer gets, padahal faktor ekspansinya hanya satu."),
    ("TBL", "hasil_oracle"),
    ("P",
     "Throughput INSERT SAMAR mencapai 72.170 baris per detik atau sekitar 76% "
     "dari plaintext. V1 hanya mencapai 31.633 baris per detik karena "
     "memerlukan pengambilan bilangan acak kriptografis untuk setiap baris, "
     "sedangkan SAMAR cukup menghitung satu HMAC. Perbedaan ini bersifat "
     "implementatif, bukan mendasar, tetapi tetap menguntungkan SAMAR pada "
     "beban muat data besar."),
    ("H2", "Sapuan Parameter"),
    ("P",
     "Gambar 4 menyajikan hubungan antara faktor ekspansi dan biaya eksekusi "
     "pada rentang k dari 1 hingga 196,2. Hubungannya linear dengan kemiringan "
     "kecil:"),
    ("EQ", "buffer gets = 119,4 + 1,962 · k̄  (5)"),
    ("P",
     "Setiap homofon tambahan hanya berbiaya sekitar dua logical read, sehingga "
     "ekspansi kueri 196 kali hanya menaikkan biaya 4,16 kali. Penyebabnya "
     "adalah setiap homofon tambahan dieksekusi sebagai index range scan yang "
     "berbagi blok root dan branch indeks yang sudah berada di buffer cache, "
     "sehingga hanya blok daun yang benar-benar perlu dibaca tambahan. Waktu "
     "CPU menunjukkan pola serupa, naik dari 1.125 menjadi 1.855 mikrodetik per "
     "eksekusi atau 1,65 kali untuk rentang ekspansi yang sama. Temuan ini "
     "menjawab pertanyaan terbuka pada [7]: pada indeks B-tree nyata, biaya "
     "ekspansi kueri jauh lebih murah daripada yang diperkirakan model "
     "pengulangan kueri."),
    ("FIG", "gbr2"),
    ("P",
     "Gambar 5 merangkum seluruh hasil keamanan untuk kolom golongan. Tiga dari "
     "empat serangan runtuh terhadap SAMAR, sedangkan satu serangan tidak."),
    ("FIG", "gbr3"),

    # =====================================================================
    ("H1", "DISKUSI"),
    ("H2", "Penghalusan Frekuensi Tidak Melindungi dari Korelasi Antarkolom"),
    ("P",
     "Serangan A3 berhasil memulihkan golongan 100% pada seluruh skema, "
     "termasuk V1 dan SAMAR. Temuan ini perlu dinyatakan terus terang karena "
     "membatasi klaim makalah ini. Penyebabnya bukan kelemahan pada penghalusan "
     "frekuensi itu sendiri, melainkan kenyataan bahwa kolom gaji pokok "
     "dibiarkan terbuka demi kebutuhan analitik. Penyerang cukup menghitung "
     "rata-rata gaji pada baris yang bertoken sama, lalu mencocokkannya dengan "
     "acuan gaji publik per golongan. Seberapa pun rata histogram tokennya, "
     "pemetaan token ke nilai tetap terungkap."),
    ("P",
     "Menarik bahwa satu-satunya skema yang tidak dipulihkan sepenuhnya pada "
     "A3 adalah masking konsisten, dengan 74,1%. Penyebabnya justru cacatnya "
     "sendiri: tabrakan substitusi menggabungkan beberapa golongan sehingga "
     "rata-rata gaji per token menjadi campuran dan pencocokan acuan meleset. "
     "Perlindungan yang berasal dari kerusakan integritas data jelas bukan "
     "perlindungan yang dapat diandalkan."),
    ("P",
     "Implikasi praktisnya tegas: melindungi kolom kategorikal saja tidak "
     "memadai. Kolom numerik yang berkorelasi kuat dengannya harus ikut "
     "ditangani, misalnya dengan membulatkannya ke dalam ember yang cukup lebar "
     "sehingga tidak lagi menunjuk satu golongan, atau dengan mengenkripsinya "
     "secara acak bila kueri kesetaraan atasnya memang tidak dibutuhkan. "
     "Pendekatan pengelompokan semacam ini sejalan dengan prinsip k-anonymity "
     "[20] dan dengan anjuran pengukuran risiko identifikasi ulang pada [16]."),
    ("H2", "Panduan Pemilihan Parameter"),
    ("P",
     "Gabungan (5) dan hasil keamanan memberi panduan yang dapat langsung "
     "dipakai. Karena recovery rate sudah runtuh ke sekitar 1% bahkan pada "
     "faktor ekspansi sekitar 10, dan karena biaya tumbuh linear dengan "
     "kemiringan kecil, praktisi tidak perlu memilih k yang besar. Target t "
     "yang menghasilkan k terbobot pada kisaran 10 hingga 40 sudah memberi "
     "perlindungan penuh terhadap analisis frekuensi dengan tambahan biaya "
     "eksekusi di bawah 1,7 kali plaintext. Nilai k yang lebih besar "
     "memperbanyak kardinalitas indeks dan memperberat agregasi tanpa manfaat "
     "keamanan tambahan yang terukur."),
    ("H2", "Keterbatasan"),
    ("LIST", [
        "Kuota homofon pada (1) dihitung dari distribusi yang berlaku saat "
        "transformasi dilakukan. Bila distribusi bergeser jauh seiring waktu, "
        "kuota menjadi usang dan perataan histogram memburuk, sehingga "
        "diperlukan perhitungan ulang beserta transformasi ulang kolom.",
        "Agregasi GROUP BY atas kolom tersamar menghasilkan k(v) kelompok per "
        "nilai dan harus dilipat kembali oleh aplikasi pemegang kunci, sehingga "
        "pelaporan langsung dari basis data tanpa aplikasi tidak lagi mungkin.",
        "SAMAR tidak menangani kebocoran pola akses maupun kebocoran volume "
        "hasil kueri, yang menjadi ranah karya seperti [14].",
        "Pengukuran kinerja dilakukan pada satu instans Oracle 12c dengan satu "
        "konfigurasi indeks dan satu ukuran tabel; angka absolutnya bergantung "
        "pada perangkat keras dan konfigurasi, meskipun bentuk hubungan linear "
        "pada (5) diharapkan tetap berlaku.",
        "Evaluasi memakai data sintetis. Distribusi dipilih agar menyerupai "
        "data kepegawaian, tetapi tidak divalidasi terhadap data riil mana pun.",
    ]),

    # =====================================================================
    ("H1", "KODE SUMBER"),
    ("P",
     "Seluruh implementasi skema, pembangkit data sintetis, modul serangan, "
     "dan skrip pengukuran tersedia agar eksperimen dapat dijalankan ulang. "
     "Repositori memuat petunjuk instalasi, daftar dependensi, dan skrip untuk "
     "menghasilkan kembali seluruh tabel dan gambar pada makalah ini."),
    ("P", "Kode sumber: https://github.com/<akun>/samar-frequency-smoothing"),

    # =====================================================================
    ("H1", "KESIMPULAN"),
    ("P",
     "Makalah ini menunjukkan bahwa enkripsi deterministik, blind index, dan "
     "masking konsisten memiliki kebocoran frekuensi yang identik secara "
     "terukur, meskipun ketiganya dipandang sebagai kontrol yang berbeda dan "
     "dikelola oleh pihak yang berbeda. Pada eksperimen 20 percobaan, analisis "
     "frekuensi memulihkan 100% nilai kolom agama, jenis kelamin, dan status "
     "kawin, serta 96,6% kolom golongan, dengan angka yang sama persis untuk "
     "ketiga pendekatan tersebut. Organisasi yang mengganti masking dengan "
     "enkripsi deterministik karena menganggapnya lebih kuat secara kriptografis "
     "sesungguhnya tidak memperoleh pengurangan kebocoran sama sekali."),
    ("P",
     "SAMAR menutup celah tersebut dengan menurunkan pemilih homofon secara "
     "deterministik dari pengenal entitas melalui HMAC berkunci, sehingga "
     "keacakan yang dibutuhkan untuk meratakan histogram diambil dari keragaman "
     "antarentitas alih-alih dari pembangkit bilangan acak. Dengan cara itu "
     "SAMAR menekan recovery rate ke paling tinggi 1,9%, yaitu di bawah lantai "
     "tebak-terbanyak, sambil mempertahankan konsistensi antartabel 100%, "
     "sedangkan penghalusan frekuensi konvensional hanya mencapai 2,1% pada "
     "sifat yang sama. Pengukuran pada Oracle 12c menunjukkan biaya yang "
     "praktis: buffer gets per eksekusi tumbuh menurut 119,4 + 1,962k, sehingga "
     "ekspansi kueri 196 kali hanya berbiaya 4,16 kali, dan faktor ekspansi "
     "pada kisaran 10 hingga 40 sudah memadai."),
    ("P",
     "Temuan yang sama pentingnya bersifat membatasi: penghalusan frekuensi "
     "tidak melindungi terhadap korelasi antarkolom. Kolom gaji yang dibiarkan "
     "terbuka tetap memulihkan golongan 100% pada seluruh skema, termasuk "
     "SAMAR. Melindungi kolom kategorikal saja karena itu tidak memadai, dan "
     "kolom kuasi-pengenal yang berkorelasi wajib ikut ditangani."),
    ("P",
     "Penelitian lanjutan dapat mencakup pemutakhiran kuota homofon secara "
     "inkremental tanpa transformasi ulang menyeluruh, penanganan terpadu "
     "terhadap kebocoran korelasi antarkolom, perluasan ke kueri rentang, serta "
     "verifikasi pada beban kerja produksi dengan distribusi yang benar-benar "
     "teramati."),
]

# ---------------------------------------------------------------------------
# Tabel
# ---------------------------------------------------------------------------

TABEL = {
    "model_penyerang": {
        "judul": "MODEL PENYERANG",
        "header": ["Model", "Posisi", "Kemampuan"],
        "baris": [
            ["M1", "Pemegang salinan non-produksi",
             "Membaca seluruh kolom pada salinan yang telah dimask"],
            ["M2", "Pengembang atau DBA",
             "SELECT atas tabel produksi; tidak memegang kunci aplikasi"],
            ["M3", "Pemegang cadangan basis data",
             "Membaca isi tabel setelah lapisan enkripsi penyimpanan dilewati"],
        ],
        "lebar": [0.42, 1.05, 1.68],
    },
    "sifat_skema": {
        "judul": "PEMENUHAN SIFAT OLEH SETIAP SKEMA",
        "header": ["Kode", "Skema", "S1", "R1", "R2"],
        "baris": [
            ["B0", "Plaintext (kontrol)", "tidak", "ya", "ya"],
            ["B1", "Masking konsisten", "tidak", "ya", "ya"],
            ["B2", "Enkripsi deterministik AES-SIV", "tidak", "ya", "ya"],
            ["B3", "AES-GCM acak + blind index HMAC", "tidak", "ya", "ya"],
            ["V1", "Homofonik acak (ablasi)", "ya", "ya", "tidak"],
            ["P", "SAMAR", "ya", "ya", "ya"],
        ],
        "lebar": [0.40, 1.42, 0.40, 0.38, 0.45],
        "catatan": "S1 ketahanan analisis frekuensi; R1 kueri kesetaraan; "
                   "R2 konsistensi antartabel.",
    },
    "hasil_a1a2": {
        "judul": "RECOVERY RATE SERANGAN A1 DAN A2 (%, RERATA ± SB, 20 PERCOBAAN)",
        "header": ["Kolom", "B0", "B1", "B2", "B3", "V1", "P", "Lantai"],
        "baris": [
            ["A1 Analisis frekuensi", "", "", "", "", "", "", ""],
            ["jenis_kelamin", "100,0", "100,0", "100,0", "100,0", "1,4", "1,5", "63,0"],
            ["golongan", "96,6", "94,6", "96,6", "96,6", "1,2", "1,0", "30,0"],
            ["agama", "100,0", "100,0", "100,0", "100,0", "0,7", "0,4", "83,9"],
            ["status_kawin", "100,0", "100,0", "100,0", "100,0", "1,2", "1,3", "70,0"],
            ["unit_kerja", "79,3", "43,6", "79,3", "79,3", "0,8", "0,8", "16,7"],
            ["A2 Penugasan optimal", "", "", "", "", "", "", ""],
            ["jenis_kelamin", "100,0", "100,0", "100,0", "100,0", "1,5", "1,4", "63,0"],
            ["golongan", "96,6", "93,8", "96,6", "96,6", "1,3", "1,5", "30,0"],
            ["agama", "100,0", "100,0", "100,0", "100,0", "1,2", "1,9", "83,9"],
            ["status_kawin", "100,0", "100,0", "100,0", "100,0", "1,6", "1,3", "70,0"],
            ["unit_kerja", "76,8", "47,7", "76,8", "76,8", "1,9", "1,6", "16,7"],
        ],
        "lebar": [1.35, 0.60, 0.60, 0.60, 0.60, 0.52, 0.52, 0.62],
        "dua_kolom": True,
        "catatan": "Lantai = tebak-terbanyak, yaitu hasil penyerang yang "
                   "mengabaikan token. Nilai di bawah lantai berarti token "
                   "tidak memberi informasi. Simpangan baku terbesar 15,5 poin "
                   "pada unit_kerja; lihat naskah.",
    },
    "hasil_a4": {
        "judul": "RECOVERY RATE SERANGAN A4 LINTAS TABEL (%)",
        "header": ["Kolom", "B0", "B1", "B2", "B3", "V1", "P", "Lantai"],
        "baris": [
            ["golongan", "96,6", "93,8", "96,6", "96,6", "1,1", "1,5", "30,0"],
            ["unit_kerja", "76,8", "47,7", "76,8", "76,8", "1,5", "1,6", "16,7"],
        ],
        "lebar": [0.66, 0.35, 0.35, 0.35, 0.35, 0.30, 0.30, 0.52],
        "catatan": "Angka V1 tidak bermakna operasional karena V1 tidak "
                   "menyediakan konsistensi antartabel.",
    },
    "hasil_fungsional": {
        "judul": "KONSISTENSI ANTARTABEL (R2) DAN KERATAAN HISTOGRAM "
                 "(N = 100.000, t = 250)",
        "header": ["Kode", "Konsistensi (%)", "Token terbanyak (%)", "Jumlah token"],
        "baris": [
            ["B0", "100,0", "29,94", "8"],
            ["B1", "100,0", "29,94", "7"],
            ["B2", "100,0", "29,94", "8"],
            ["B3", "100,0", "29,94", "8"],
            ["V1", "2,1", "0,29", "401"],
            ["P", "100,0", "0,29", "401"],
        ],
        "lebar": [0.40, 0.85, 1.00, 0.70],
        "catatan": "B1 menghasilkan tujuh token untuk delapan nilai akibat "
                   "tabrakan substitusi.",
    },
    "hasil_oracle": {
        "judul": "KINERJA PADA ORACLE 12c, 100.000 BARIS",
        "header": ["Kode", "k̄", "INSERT (baris/s)", "Indeks (MB)",
                   "Buffer gets/eks"],
        "baris": [
            ["B0", "1,00", "95.023", "3,00", "50,1"],
            ["B1", "1,00", "106.383", "3,00", "65,2"],
            ["B2", "1,00", "57.438", "7,00", "153,2"],
            ["B3", "1,00", "108.559", "3,00", "54,6"],
            ["V1", "78,59", "31.633", "5,00", "274,3"],
            ["P", "78,59", "72.170", "5,00", "273,4"],
        ],
        "lebar": [0.38, 0.45, 0.85, 0.65, 0.82],
    },
}

# ---------------------------------------------------------------------------
# Gambar
# ---------------------------------------------------------------------------

GAMBAR = {
    "sistem": {
        "berkas": "gbr_sistem.png",
        "caption": "Gambar 1. Model sistem dan ancaman. Aplikasi memegang "
                   "kunci dan menjalankan transformasi SAMAR sebelum data "
                   "ditulis, sehingga mesin basis data tidak pernah memegang "
                   "kunci. Penyerang snapshot (M1-M3) hanya membaca kolom "
                   "tersamar pada basis data atau salinannya, tanpa kunci.",
        "lebar_in": 6.6, "dua_kolom": True,
    },
    "konstruksi": {
        "berkas": "gbr_konstruksi.png",
        "caption": "Gambar 2. Alur pembentukan token SAMAR. Kuota homofon k(v) "
                   "ditetapkan dari frekuensi f(v) dan target t, sedangkan "
                   "pemilih j diturunkan secara deterministik dari pengenal "
                   "entitas e memakai HMAC berkunci. Karena j hanya bergantung "
                   "pada e dan v, entitas yang sama memperoleh token yang sama "
                   "di semua tabel, sehingga konsistensi antartabel terjaga.",
        "lebar_in": 6.6, "dua_kolom": True,
    },
    "gbr1": {
        "berkas": "gbr1_sebaran_frekuensi.png",
        "caption": "Gambar 3. Sebaran frekuensi token pada kolom golongan, "
                   "skala ganda logaritmik. Skema deterministik membawa utuh "
                   "histogram plaintext dengan token terbanyak 29,9%, "
                   "sedangkan SAMAR meratakannya ke 0,29%.",
        "lebar_in": 3.25, "dua_kolom": False,
    },
    "gbr2": {
        "berkas": "gbr2_biaya_vs_k.png",
        "caption": "Gambar 4. Biaya eksekusi pada Oracle 12c terhadap faktor "
                   "ekspansi kueri. Hubungannya linear dengan kemiringan 1,96 "
                   "buffer gets per homofon, sehingga ekspansi 196 kali hanya "
                   "berbiaya 4,16 kali.",
        "lebar_in": 3.25, "dua_kolom": False,
    },
    "gbr3": {
        "berkas": "gbr3_recovery.png",
        "caption": "Gambar 5. Recovery rate kolom golongan terhadap empat "
                   "serangan. SAMAR meruntuhkan A1, A2, dan A4 ke sekitar 1%, "
                   "tetapi tidak menahan A3 yang memanfaatkan korelasi kolom "
                   "gaji yang dibiarkan terbuka.",
        "lebar_in": 6.4, "dua_kolom": True,
    },
}

# ---------------------------------------------------------------------------
# Referensi
# ---------------------------------------------------------------------------

REFERENSI = [
    "Republik Indonesia, Undang-Undang Nomor 27 Tahun 2022 tentang "
    "Pelindungan Data Pribadi. Jakarta, Indonesia, 2022.",

    "Oracle Corporation, “Introduction to Transparent Data Encryption,” "
    "dalam Oracle Database Advanced Security Guide. [Daring]. Tersedia: "
    "https://docs.oracle.com/en/database/oracle/oracle-database/19/asoag/"
    "introduction-to-transparent-data-encryption.html. Diakses: 24 Oktober 2026.",

    "M. Bellare, A. Boldyreva, dan A. O’Neill, “Deterministic and "
    "efficiently searchable encryption,” dalam Advances in Cryptology – "
    "CRYPTO 2007, LNCS vol. 4622. Berlin, Jerman: Springer, 2007, pp. 535–552.",

    "H. Krawczyk, M. Bellare, dan R. Canetti, “HMAC: Keyed-hashing for "
    "message authentication,” RFC 2104, IETF, Feb. 1997.",

    "Oracle Corporation, “Data Masking Format Library and Masking "
    "Definitions,” dalam Oracle Data Masking and Subsetting Guide. [Daring]. "
    "Tersedia: https://docs.oracle.com/en/database/oracle/oracle-database/19/"
    "dmksb/. Diakses: 24 Oktober 2026.",

    "M. Naveed, S. Kamara, dan C. V. Wright, “Inference attacks on "
    "property-preserving encrypted databases,” dalam Proc. 22nd ACM SIGSAC "
    "Conf. Computer and Communications Security (CCS), Denver, CO, USA, 2015, "
    "pp. 644–655, doi: 10.1145/2810103.2813651.",

    "M.-S. Lacharité dan K. G. Paterson, “Frequency-smoothing "
    "encryption: preventing snapshot attacks on deterministically encrypted "
    "data,” IACR Trans. Symmetric Cryptol., vol. 2018, no. 1, pp. 277–313, "
    "2018, doi: 10.13154/tosc.v2018.i1.277-313.",

    "P. Rogaway dan T. Shrimpton, “A provable-security treatment of the "
    "key-wrap problem,” dalam Advances in Cryptology – EUROCRYPT 2006, "
    "LNCS vol. 4004. Berlin, Jerman: Springer, 2006, pp. 373–390.",

    "D. Harkins, “Synthetic initialization vector (SIV) authenticated "
    "encryption using the Advanced Encryption Standard (AES),” RFC 5297, "
    "IETF, Okt. 2008.",

    "R. A. Popa, C. M. S. Redfield, N. Zeldovich, dan H. Balakrishnan, "
    "“CryptDB: Protecting confidentiality with encrypted query "
    "processing,” dalam Proc. 23rd ACM Symp. Operating Systems Principles "
    "(SOSP), Cascais, Portugal, 2011, pp. 85–100, "
    "doi: 10.1145/2043556.2043566.",

    "P. Grubbs, K. Sekniqi, V. Bindschaedler, M. Naveed, dan T. Ristenpart, "
    "“Leakage-abuse attacks against order-revealing encryption,” dalam "
    "Proc. IEEE Symp. Security and Privacy (S&P), San Jose, CA, USA, 2017, "
    "pp. 655–672, doi: 10.1109/SP.2017.44.",

    "V. Bindschaedler, P. Grubbs, D. Cash, T. Ristenpart, dan M. Naveed, "
    "“The tao of inference in privacy-protected databases,” Proc. VLDB "
    "Endowment, vol. 11, no. 11, pp. 1715–1728, 2018, "
    "doi: 10.14778/3236187.3236217.",

    "G. Kellaris, G. Kollios, K. Nissim, dan A. O’Neill, “Generic "
    "attacks on secure outsourced databases,” dalam Proc. 23rd ACM SIGSAC "
    "Conf. Computer and Communications Security (CCS), Vienna, Austria, 2016, "
    "pp. 1329–1340, doi: 10.1145/2976749.2978386.",

    "P. Grubbs, A. Khandelwal, M.-S. Lacharité, L. Brown, L. Li, "
    "R. Agarwal, dan T. Ristenpart, “Pancake: Frequency smoothing for "
    "encrypted data stores,” dalam Proc. 29th USENIX Security Symposium, "
    "2020, pp. 2451–2468.",

    "European Union Agency for Cybersecurity (ENISA), Pseudonymisation "
    "Techniques and Best Practices. Heraklion, Yunani: ENISA, 2019. [Daring]. "
    "Tersedia: https://www.enisa.europa.eu/publications/"
    "pseudonymisation-techniques-and-best-practices. Diakses: 24 Oktober 2026.",

    "S. Garfinkel, J. Near, A. Dajani, P. Singer, dan B. Guttman, "
    "“De-identifying government datasets: Techniques and governance,” "
    "NIST Special Publication 800-188, National Institute of Standards and "
    "Technology, Gaithersburg, MD, USA, Sep. 2023, doi: 10.6028/NIST.SP.800-188.",

    "Python Cryptographic Authority, “cryptography documentation.” "
    "[Daring]. Tersedia: https://cryptography.io. Diakses: 24 Oktober 2026.",

    "Oracle Corporation, “python-oracledb documentation.” [Daring]. "
    "Tersedia: https://python-oracledb.readthedocs.io. "
    "Diakses: 24 Oktober 2026.",

    "H. W. Kuhn, “The Hungarian method for the assignment problem,” "
    "Naval Research Logistics Quarterly, vol. 2, no. 1–2, pp. 83–97, 1955, "
    "doi: 10.1002/nav.3800020109.",

    "L. Sweeney, “k-anonymity: A model for protecting privacy,” Int. J. "
    "Uncertainty, Fuzziness and Knowledge-Based Systems, vol. 10, no. 5, "
    "pp. 557–570, 2002, doi: 10.1142/S0218488502001648.",

    "R. Munir, Kriptografi, edisi ke-2. Bandung, Indonesia: Penerbit "
    "Informatika, 2019.",
]

PERNYATAAN = (
    "Dengan ini saya menyatakan bahwa makalah yang saya tulis ini adalah "
    "tulisan saya sendiri, bukan saduran, atau terjemahan dari makalah orang "
    "lain, dan bukan plagiasi."
)
TANGGAL = "Bandung, 24 Oktober 2026"
TTD = "Muchammad Iqbal 23525011"
