"""
datagen.py - Pembangkit data sintetis untuk eksperimen.

Seluruh data bersifat sintetis. Distribusi dibuat menyerupai karakteristik
data kepegawaian dan penggajian (kolom berkardinalitas rendah yang condong),
tetapi tidak ada satu pun nilai yang berasal dari data riil.

Dua tabel dibangkitkan agar skenario lintas tabel dapat diuji:
  - pegawai     : satu baris per entitas (NIK unik)
  - transaksi   : banyak baris per entitas (mis. gaji bulanan)
Keduanya berbagi kolom atribut yang sama (golongan, unit, dsb.) sehingga
konsistensi lintas tabel dan JOIN dapat dievaluasi.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


# ---------------------------------------------------------------------------
# Spesifikasi domain kolom: nilai + bobot populasi (tidak harus ternormalisasi)
# ---------------------------------------------------------------------------

DOMAIN = {
    "jenis_kelamin": (["L", "P"], [63, 37]),
    "golongan": (
        ["GOL-1A", "GOL-1B", "GOL-2A", "GOL-2B",
         "GOL-3A", "GOL-3B", "GOL-4A", "GOL-4B"],
        [30, 24, 16, 11, 8, 5, 4, 2],
    ),
    "agama": (
        ["ISLAM", "KRISTEN", "KATOLIK", "HINDU", "BUDDHA", "KONGHUCU"],
        [84, 7, 4, 3, 1.5, 0.5],
    ),
    "status_kawin": (["KAWIN", "BELUM", "CERAI"], [70, 25, 5]),
    "unit_kerja": (
        [f"UNIT-{i:02d}" for i in range(1, 21)],
        # 20 unit, condong: beberapa unit besar, banyak unit kecil
        [40, 32, 28, 22, 18, 15, 13, 11, 10, 9,
         8, 7, 6, 5, 4, 3, 3, 2, 2, 1],
    ),
}

# golongan -> parameter rentang gaji pokok (ribuan rupiah), untuk menguji
# serangan korelasi antarkolom: gaji sangat berkorelasi dengan golongan
GAJI_PER_GOLONGAN = {
    "GOL-1A": 4000, "GOL-1B": 4800, "GOL-2A": 5800, "GOL-2B": 7000,
    "GOL-3A": 8600, "GOL-3B": 10500, "GOL-4A": 13000, "GOL-4B": 16500,
}


@dataclass
class Dataset:
    pegawai: dict = field(default_factory=dict)   # kolom -> np.ndarray
    transaksi: dict = field(default_factory=dict)
    n_pegawai: int = 0
    n_transaksi: int = 0
    # indeks entitas untuk tiap baris transaksi (baris i milik pegawai ke-idx[i])
    idx_entitas: object = None

    def kolom_target(self):
        """Kolom berkardinalitas rendah yang menjadi sasaran serangan."""
        return ["jenis_kelamin", "golongan", "agama", "status_kawin",
                "unit_kerja"]


def _tarik(rng, nama, n):
    nilai, bobot = DOMAIN[nama]
    p = np.asarray(bobot, dtype=float)
    p /= p.sum()
    return rng.choice(nilai, size=n, p=p)


def bangkitkan(n_pegawai=50_000, bulan=12, seed=20261024) -> Dataset:
    """Bangkitkan dataset sintetis.

    n_pegawai : jumlah entitas
    bulan     : jumlah baris transaksi per entitas (mis. 12 bulan gaji)
    """
    rng = np.random.default_rng(seed)

    nik = np.array([f"NIK{i:07d}" for i in range(n_pegawai)])
    peg = {"nik": nik}
    for kol in DOMAIN:
        peg[kol] = _tarik(rng, kol, n_pegawai)

    # gaji pokok berkorelasi dengan golongan (+ derau +-7%)
    dasar = np.array([GAJI_PER_GOLONGAN[g] for g in peg["golongan"]], dtype=float)
    peg["gaji_pokok"] = np.round(dasar * (1 + rng.normal(0, 0.07, n_pegawai)), 0)

    # --- tabel transaksi: ulang tiap pegawai `bulan` kali ------------------
    idx = np.repeat(np.arange(n_pegawai), bulan)
    trx = {
        "nik": nik[idx],
        "golongan": peg["golongan"][idx],
        "unit_kerja": peg["unit_kerja"][idx],
    }
    periode = np.tile(np.arange(1, bulan + 1), n_pegawai)
    trx["periode"] = np.array([f"2025{m:02d}" for m in periode])
    # nominal bulanan = gaji pokok + tunjangan acak kecil
    trx["nominal"] = np.round(
        peg["gaji_pokok"][idx] * (1 + rng.normal(0, 0.03, len(idx))), 0)

    return Dataset(pegawai=peg, transaksi=trx,
                   n_pegawai=n_pegawai, n_transaksi=len(idx),
                   idx_entitas=idx)


def distribusi_bantu(nama, derau=0.10, seed=777):
    """Distribusi bantu (auxiliary) yang 'diketahui' penyerang.

    Mengembalikan dict nilai -> probabilitas. Dibuat sebagai distribusi
    populasi yang diguncang derau relatif, mencerminkan asumsi Naveed et al.:
    penyerang memegang distribusi publik yang berkorelasi baik tetapi tidak
    identik dengan distribusi basis data korban.
    """
    rng = np.random.default_rng(seed + hash(nama) % 10_000)
    nilai, bobot = DOMAIN[nama]
    p = np.asarray(bobot, dtype=float)
    p = p * (1 + rng.normal(0, derau, len(p)))
    p = np.clip(p, 1e-9, None)
    p /= p.sum()
    return dict(zip(nilai, p))


if __name__ == "__main__":
    ds = bangkitkan(n_pegawai=10_000, bulan=12)
    print(f"pegawai : {ds.n_pegawai:,} baris x {len(ds.pegawai)} kolom")
    print(f"transaksi: {ds.n_transaksi:,} baris x {len(ds.transaksi)} kolom")
    print("\nKolom target serangan:", ds.kolom_target())
    from collections import Counter
    for kol in ds.kolom_target():
        c = Counter(ds.pegawai[kol])
        top = c.most_common(1)[0]
        print(f"  {kol:16s} kardinalitas={len(c):3d}  "
              f"terbanyak={top[0]} ({100*top[1]/ds.n_pegawai:.1f}%)")
