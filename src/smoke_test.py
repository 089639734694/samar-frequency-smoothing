"""Uji cepat klaim inti: SAMAR meratakan frekuensi SEKALIGUS menjaga
konsistensi lintas tabel, sedangkan homofonik acak hanya meratakan frekuensi.
"""

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("\\", 1)[0])

from schemes import (B0Plaintext, B1MaskingKonsisten, B2AesSiv,  # noqa: E402
                     B3BlindIndex, PSamar, V1HomofonikAcak)

rng = np.random.default_rng(20261024)

# --- data sintetis kecil: 20.000 pegawai, kolom golongan yang sangat condong
N = 20_000
GOL = ["GOL-1A", "GOL-1B", "GOL-2A", "GOL-2B", "GOL-3A",
       "GOL-3B", "GOL-4A", "GOL-4B"]
bobot = np.array([30, 24, 16, 11, 8, 5, 4, 2], dtype=float)
bobot /= bobot.sum()

entity = [f"NIK{i:07d}" for i in range(N)]
gol = rng.choice(GOL, size=N, p=bobot)

print(f"Distribusi plaintext (N={N:,}):")
for v, f in Counter(gol).most_common():
    print(f"   {v}  {f:6,}  {100*f/N:5.2f}%")

skema = [
    B0Plaintext(),
    B1MaskingKonsisten(),
    B2AesSiv(),
    B3BlindIndex(bit_indeks=32),
    V1HomofonikAcak(target=250),
    PSamar(target=250),
]

print("\n" + "=" * 78)
print(f"{'Kode':5s} {'Skema':34s} {'#token':>7s} {'maks%':>7s} {'Konsisten':>10s} {'k_rata':>7s}")
print("=" * 78)

for s in skema:
    s.fit(gol)

    # tabel A dan tabel B memuat atribut pegawai yang sama
    tok_a = [s.transform(g, e) for g, e in zip(gol, entity)]
    tok_b = [s.transform(g, e) for g, e in zip(gol, entity)]

    cnt = Counter(tok_a)
    maks = 100 * max(cnt.values()) / N
    # konsistensi lintas tabel: berapa persen entitas yang tokennya cocok
    cocok = 100 * sum(a == b for a, b in zip(tok_a, tok_b)) / N
    kbar = getattr(s, "faktor_ekspansi_terbobot", 1.0)

    print(f"{s.kode:5s} {s.nama:34s} {len(cnt):7,} {maks:6.2f}% "
          f"{cocok:9.1f}% {kbar:7.1f}")

print("=" * 78)
print("""
Pembacaan:
  maks%      frekuensi token terbanyak. Mendekati 30% artinya histogram
             plaintext terbawa utuh, yaitu persis yang dieksploitasi
             analisis frekuensi. Makin kecil makin baik.
  Konsisten  persentase pegawai yang memperoleh token sama di dua tabel.
             Harus 100% agar salinan non-produksi masih dapat di-JOIN.
  k_rata     rerata jumlah token per kueri kesetaraan (biaya ekspansi).
""")

# --- verifikasi kebenaran kueri kesetaraan untuk SAMAR
s = skema[-1]
tok = [s.transform(g, e) for g, e in zip(gol, entity)]
for v in GOL:
    diminta = set(s.query_tokens(v))
    benar = {i for i, g in enumerate(gol) if g == v}
    didapat = {i for i, t in enumerate(tok) if t in diminta}
    assert benar == didapat, f"kueri kesetaraan SAMAR salah untuk {v}"
print("Kueri kesetaraan SAMAR: tepat untuk seluruh nilai domain (tanpa "
      "false positive maupun false negative).")
