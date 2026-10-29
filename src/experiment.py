"""
experiment.py - Eksperimen keamanan definitif: jalankan keempat serangan atas
keenam skema selama T percobaan dengan seed berbeda, lalu laporkan
rerata +- simpangan baku recovery rate (%) ke results/attack_results.csv.

Tokenisasi untuk skema yang bergantung-nilai di-cache per nilai distinct agar
percobaan berulang tetap cepat.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

import attacks  # noqa: E402
import datagen  # noqa: E402
from schemes import (B0Plaintext, B1MaskingKonsisten, B2AesSiv,  # noqa: E402
                     B3BlindIndex, PSamar, V1HomofonikAcak)

ROOT = os.path.dirname(os.path.dirname(__file__))
TARGET = 250
KELAS = [B0Plaintext, B1MaskingKonsisten, B2AesSiv,
         B3BlindIndex, V1HomofonikAcak, PSamar]
KODES = ["B0", "B1", "B2", "B3", "V1", "P"]


def _skema(Kelas):
    return (Kelas(target=TARGET)
            if Kelas in (V1HomofonikAcak, PSamar) else Kelas())


def tokenisasi(s, nilai, entity):
    """Tokenisasi dengan cache per nilai jika token hanya bergantung nilai."""
    nilai = np.asarray(nilai)
    if s.deterministik_nilai:
        peta = {v: s.transform(v) for v in np.unique(nilai)}
        return np.array([peta[v] for v in nilai])
    return np.array([s.transform(v, e) for v, e in zip(nilai, entity)])


def tokenisasi_transaksi(s, tok_pegawai, idx_entitas, nilai_trx, entity_trx):
    """Tokenisasi kolom atribut pada tabel transaksi.

    Jalan pintas yang sah: untuk skema yang tokennya ditentukan oleh (entitas,
    nilai) - yakni B0-B3 dan SAMAR - atribut seorang pegawai bernilai sama di
    seluruh barisnya, sehingga tokennya identik dan cukup diperluas dari token
    tabel pegawai. V1 memilih homofon acak per baris sehingga harus dihitung
    satu per satu.
    """
    if s.kode == "V1":
        return tokenisasi(s, nilai_trx, entity_trx)
    return tok_pegawai[idx_entitas]


def satu_percobaan(seed, n_pegawai, bulan):
    ds = datagen.bangkitkan(n_pegawai=n_pegawai, bulan=bulan, seed=seed)
    nik, nik_trx = ds.pegawai["nik"], ds.transaksi["nik"]
    kolom = ds.kolom_target()
    aux = {k: datagen.distribusi_bantu(k, seed=seed) for k in kolom}

    out = {}  # (serangan, kode, kolom) -> recovery
    for Kelas, kode in zip(KELAS, KODES):
        for kol in kolom:
            s = _skema(Kelas); s.fit(ds.pegawai[kol])
            tok = tokenisasi(s, ds.pegawai[kol], nik)
            truth = ds.pegawai[kol]
            out[("A1", kode, kol)] = attacks.frequency_analysis(aux[kol], tok, truth)
            out[("A2", kode, kol)] = attacks.optimal_assignment(aux[kol], tok, truth)
            if kol in ("golongan", "unit_kerja"):
                tok_b = tokenisasi_transaksi(
                    s, tok, ds.idx_entitas, ds.transaksi[kol], nik_trx)
                out[("A4", kode, kol)] = attacks.cross_table(
                    aux[kol], tok, truth, tok_b)
        # A3: golongan via gaji
        s = _skema(Kelas); s.fit(ds.pegawai["golongan"])
        tok_g = tokenisasi(s, ds.pegawai["golongan"], nik)
        out[("A3", kode, "golongan")] = attacks.cross_column(
            datagen.GAJI_PER_GOLONGAN, tok_g, ds.pegawai["gaji_pokok"],
            ds.pegawai["golongan"])

    # lantai baseline per kolom (independen skema)
    for kol in kolom:
        out[("BASE", "-", kol)] = attacks.baseline_tebak_terbanyak(
            aux[kol], None, ds.pegawai[kol])
    return out, kolom


def main(T=30, n_pegawai=20_000, bulan=12, seed0=1000):
    akum = {}
    kolom = None
    for t in range(T):
        out, kolom = satu_percobaan(seed0 + t, n_pegawai, bulan)
        for k, v in out.items():
            akum.setdefault(k, []).append(v)
        print(f"  percobaan {t+1}/{T} selesai", end="\r")
    print(" " * 40, end="\r")

    def ms(key):
        a = np.array(akum.get(key, [np.nan])) * 100
        return np.nanmean(a), np.nanstd(a)

    # cetak + kumpulkan CSV
    baris = [("serangan", "kolom", *KODES, "baseline")]
    judul = {"A1": "A1 Analisis frekuensi", "A2": "A2 Penugasan optimal",
             "A3": "A3 Korelasi antarkolom (gaji->golongan)",
             "A4": "A4 Lintas tabel (kontribusi)"}
    kolom_per = {"A1": kolom, "A2": kolom, "A3": ["golongan"],
                 "A4": ["golongan", "unit_kerja"]}

    print(f"\nRecovery rate rerata +- SB atas T={T} percobaan "
          f"(N={n_pegawai:,} pegawai):\n")
    for ser in ["A1", "A2", "A3", "A4"]:
        print(f"=== {judul[ser]} ===")
        print(f"{'kolom':16s} " + " ".join(f"{k:>13s}" for k in KODES)
              + f" {'baseline':>9s}")
        for kol in kolom_per[ser]:
            sel = []
            for kode in KODES:
                m, s = ms((ser, kode, kol))
                sel.append(f"{m:5.1f}+-{s:4.1f}")
            bm, _ = ms(("BASE", "-", kol))
            print(f"{kol:16s} " + " ".join(f"{x:>13s}" for x in sel)
                  + f" {bm:8.1f}%")
            baris.append((ser, kol,
                          *[f"{ms((ser,k,kol))[0]:.2f}" for k in KODES],
                          f"{bm:.2f}"))
        print()

    out = os.path.join(ROOT, "results", "attack_results.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in baris:
            f.write(",".join(map(str, r)) + "\n")
    print(f"Hasil ditulis ke {out}")


if __name__ == "__main__":
    main()
