"""
run_attacks.py - Jalankan keempat serangan atas keenam skema dan cetak
tabel recovery rate (%). Murni Python, tanpa Oracle.
"""

import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("\\", 1)[0])

import attacks  # noqa: E402
import datagen  # noqa: E402
from schemes import (B0Plaintext, B1MaskingKonsisten, B2AesSiv,  # noqa: E402
                     B3BlindIndex, PSamar, V1HomofonikAcak)

TARGET = 250   # target baris per homofon untuk V1 & SAMAR


def buat_skema():
    return [B0Plaintext(), B1MaskingKonsisten(), B2AesSiv(),
            B3BlindIndex(bit_indeks=32),
            V1HomofonikAcak(target=TARGET), PSamar(target=TARGET)]


def tokenisasi(s, nilai, entity):
    return np.array([s.transform(v, e) for v, e in zip(nilai, entity)])


def main(n_pegawai=50_000, bulan=12):
    ds = datagen.bangkitkan(n_pegawai=n_pegawai, bulan=bulan)
    nik = ds.pegawai["nik"]
    nik_trx = ds.transaksi["nik"]

    kolom = ds.kolom_target()
    aux = {k: datagen.distribusi_bantu(k) for k in kolom}
    aux_gaji = datagen.GAJI_PER_GOLONGAN

    print(f"Dataset: {ds.n_pegawai:,} pegawai, {ds.n_transaksi:,} transaksi\n")

    hasil = {}  # (serangan, kode) -> list recovery per kolom

    for Skema in [type(s) for s in buat_skema()]:
        s = Skema(target=TARGET) if Skema in (V1HomofonikAcak, PSamar) else Skema()
        kode = s.kode

        for kol in kolom:
            s_k = (Skema(target=TARGET)
                   if Skema in (V1HomofonikAcak, PSamar) else Skema())
            s_k.fit(ds.pegawai[kol])
            tok = tokenisasi(s_k, ds.pegawai[kol], nik)
            truth = ds.pegawai[kol]

            # A1, A2 berlaku untuk semua kolom
            r1 = attacks.frequency_analysis(aux[kol], tok, truth)
            r2 = attacks.optimal_assignment(aux[kol], tok, truth)
            hasil.setdefault(("A1", kode), {})[kol] = r1
            hasil.setdefault(("A2", kode), {})[kol] = r2

            # A4 lintas tabel: butuh token atribut yang sama di transaksi
            if kol in ("golongan", "unit_kerja"):
                tok_b = tokenisasi(s_k, ds.transaksi[kol], nik_trx)
                r4 = attacks.cross_table(aux[kol], tok, truth, tok_b)
                hasil.setdefault(("A4", kode), {})[kol] = r4

        # A3 korelasi antarkolom: khusus golongan via gaji
        s_g = (Skema(target=TARGET)
               if Skema in (V1HomofonikAcak, PSamar) else Skema())
        s_g.fit(ds.pegawai["golongan"])
        tok_g = tokenisasi(s_g, ds.pegawai["golongan"], nik)
        r3 = attacks.cross_column(aux_gaji, tok_g, ds.pegawai["gaji_pokok"],
                                  ds.pegawai["golongan"])
        hasil.setdefault(("A3", kode), {})["golongan"] = r3

    # ---- baseline lantai per kolom ----
    print("Baseline tebak-terbanyak (lantai) per kolom:")
    base = {}
    for kol in kolom:
        b = attacks.baseline_tebak_terbanyak(aux[kol], None, ds.pegawai[kol])
        base[kol] = b
        print(f"  {kol:16s} {100*b:5.1f}%")

    kodes = ["B0", "B1", "B2", "B3", "V1", "P"]

    def cetak_tabel(ser, judul, kols):
        print(f"\n=== {judul} ===")
        print(f"{'Kolom':16s} " + " ".join(f"{k:>7s}" for k in kodes))
        for kol in kols:
            baris = []
            for k in kodes:
                v = hasil.get((ser, k), {}).get(kol)
                baris.append("   -   " if v is None else f"{100*v:6.1f}%")
            print(f"{kol:16s} " + " ".join(baris))

    cetak_tabel("A1", "A1 Analisis frekuensi (recovery %)", kolom)
    cetak_tabel("A2", "A2 Penugasan optimal (recovery %)", kolom)
    cetak_tabel("A3", "A3 Korelasi antarkolom: golongan via gaji", ["golongan"])
    cetak_tabel("A4", "A4 Lintas tabel (kontribusi)", ["golongan", "unit_kerja"])

    return hasil, base


if __name__ == "__main__":
    main()
