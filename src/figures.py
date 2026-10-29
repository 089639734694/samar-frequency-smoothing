"""
figures.py - Gambar untuk makalah (IEEE dua kolom, lebar kolom ~8,4 cm).

Prinsip: mark tipis, grid hairline solid (bukan putus-putus), sumbu recessive,
legenda untuk >=2 seri, label langsung hanya pada titik yang penting, dan
pembeda sekunder berupa gaya garis + penanda agar tetap terbaca saat dicetak
hitam-putih.
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import datagen  # noqa: E402
from schemes import B2AesSiv, PSamar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(__file__))
OUT = os.path.join(ROOT, "results", "figs")
os.makedirs(OUT, exist_ok=True)

# --- palet tervalidasi (slot 1 & 2) ---
BIRU, ORANYE = "#2a78d6", "#eb6834"
TEKS, TEKS2, GRID = "#0b0b0b", "#52514e", "#d8d8d4"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 7.5,
    "axes.labelsize": 7.5,
    "axes.titlesize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.edgecolor": TEKS2,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.color": TEKS2,
    "ytick.color": TEKS2,
    "grid.color": GRID,
    "grid.linewidth": 0.4,
    "grid.linestyle": "-",          # hairline SOLID, tidak putus-putus
    "figure.dpi": 400,
    "savefig.dpi": 400,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})

SATU_KOLOM = (3.3, 2.35)


def _kunci(label: str, n: int = 32) -> bytes:
    """Kunci tetap turunan label, agar gambar dapat direproduksi persis.
    Hanya untuk keperluan pembuatan gambar; bukan praktik produksi."""
    return hashlib.sha256(b"SAMAR-figur|" + label.encode()).digest()[:n]


def km(x, desimal=1):
    """Format angka dengan koma desimal sesuai kaidah Bahasa Indonesia."""
    return f"{x:.{desimal}f}".replace(".", ",")


def _rapikan(ax):
    for sisi in ("top", "right"):
        ax.spines[sisi].set_visible(False)
    ax.tick_params(length=2.5)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
# Gambar 1: sebaran frekuensi token - deterministik vs SAMAR
# ---------------------------------------------------------------------------

def gambar_sebaran():
    ds = datagen.bangkitkan(n_pegawai=100_000, bulan=1, seed=20261024)
    gol, nik = ds.pegawai["golongan"], ds.pegawai["nik"]
    n = len(gol)

    det = B2AesSiv(key=_kunci("aessiv")); det.fit(gol)
    sam = PSamar(key=_kunci("samar-token"),
                 key_sel=_kunci("samar-pemilih"), target=250); sam.fit(gol)
    t_det = [det.transform(v) for v in gol]
    t_sam = [sam.transform(v, e) for v, e in zip(gol, nik)]

    f_det = np.array(sorted(Counter(t_det).values(), reverse=True)) / n * 100
    f_sam = np.array(sorted(Counter(t_sam).values(), reverse=True)) / n * 100

    fig, ax = plt.subplots(figsize=SATU_KOLOM)
    ax.plot(np.arange(1, len(f_det) + 1), f_det, color=BIRU, lw=1.2,
            ls="-", marker="o", ms=3.0, mew=0, label="Deterministik (B0–B3)")
    ax.plot(np.arange(1, len(f_sam) + 1), f_sam, color=ORANYE, lw=1.2,
            ls="--", marker="", label="SAMAR ($k$=78,6)")

    ax.set_xscale("log"); ax.set_yscale("log")
    # beri ruang di bawah agar garis SAMAR tidak menempel sumbu
    ax.set_ylim(f_sam.min() * 0.45, f_det[0] * 2.6)
    ax.set_xlabel("Peringkat token")
    ax.set_ylabel("Pangsa baris (%)")
    ax.grid(True, which="major", axis="both")
    _rapikan(ax)

    # label langsung hanya pada dua titik yang menjadi inti argumen
    ax.annotate(f"{km(f_det[0])}%", xy=(1, f_det[0]), xytext=(1.25, f_det[0] * 1.18),
                color=BIRU, fontsize=7)
    ax.annotate(f"{km(f_sam[0], 2)}%", xy=(1, f_sam[0]), xytext=(1.25, f_sam[0] * 1.30),
                color=ORANYE, fontsize=7)

    ax.legend(frameon=False, loc="upper right", handlelength=1.8,
              borderaxespad=0.2)
    p = os.path.join(OUT, "gbr1_sebaran_frekuensi.png")
    fig.savefig(p); plt.close(fig)
    print("->", p, f"(maks det {f_det[0]:.2f}% vs SAMAR {f_sam[0]:.2f}%)")


# ---------------------------------------------------------------------------
# Gambar 2: biaya eksekusi Oracle terhadap faktor ekspansi k
# ---------------------------------------------------------------------------

def gambar_biaya():
    path = os.path.join(ROOT, "results", "oracle_bagianB.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    k = np.array([float(r["k_ekspansi"]) for r in rows])
    bg = np.array([float(r["buffer_gets_per_eks"]) for r in rows])
    urut = np.argsort(k); k, bg = k[urut], bg[urut]

    A = np.vstack([k, np.ones_like(k)]).T
    m, c = np.linalg.lstsq(A, bg, rcond=None)[0]

    fig, ax = plt.subplots(figsize=SATU_KOLOM)
    kk = np.linspace(0, k.max() * 1.05, 100)
    ax.plot(kk, m * kk + c, color=ORANYE, lw=1.0, ls="--",
            label=f"Regresi: {c:.0f} + {km(m, 2)}$k$")
    ax.plot(k, bg, color=BIRU, lw=0, marker="o", ms=4.0, mew=0,
            label="Terukur di Oracle")

    ax.set_xlabel("Faktor ekspansi kueri $k$")
    ax.set_ylabel("Buffer gets per eksekusi")
    ax.grid(True, which="major", axis="y")
    ax.set_xlim(0, k.max() * 1.05)
    ax.set_ylim(0, bg.max() * 1.12)
    _rapikan(ax)

    # label langsung hanya pada dua ujung
    ax.annotate(f"$k$=1\n{bg[0]:.0f}", xy=(k[0], bg[0]), xytext=(k[0] + 6, bg[0] - 60),
                color=TEKS2, fontsize=6.5)
    ax.annotate(f"$k$={k[-1]:.0f}\n{bg[-1]:.0f}", xy=(k[-1], bg[-1]),
                xytext=(k[-1] - 48, bg[-1] + 18), color=TEKS2, fontsize=6.5)

    ax.legend(frameon=False, loc="upper left", handlelength=1.8)
    p = os.path.join(OUT, "gbr2_biaya_vs_k.png")
    fig.savefig(p); plt.close(fig)
    print("->", p, f"(biaya = {c:.1f} + {m:.3f}k; {k.max()/k.min():.0f}x ekspansi "
          f"-> {bg.max()/bg.min():.2f}x biaya)")


if __name__ == "__main__":
    gambar_sebaran()
    gambar_biaya()


# ---------------------------------------------------------------------------
# Gambar 3: ringkasan recovery rate per serangan (lebar dua kolom)
# ---------------------------------------------------------------------------

AQUA = "#1baf7a"
DUA_KOLOM = (6.6, 2.45)   # <= lebar teks A4 (6,69 in)


def gambar_recovery():
    """Ringkasan keamanan: recovery rate tiga skema terhadap empat serangan.

    Label nilai ditampilkan pada setiap batang sebagai relief atas peringatan
    kontras aqua, dan hatch dipakai sebagai pembeda sekunder untuk cetak
    hitam-putih.
    """
    path = os.path.join(ROOT, "results", "attack_results.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))

    # kolom wakil per serangan: golongan untuk semua, agar sebanding
    pilih = {"A1": "golongan", "A2": "golongan", "A3": "golongan",
             "A4": "golongan"}
    label = {"A1": "A1\nAnalisis\nfrekuensi", "A2": "A2\nPenugasan\noptimal",
             "A3": "A3\nKorelasi\nantarkolom", "A4": "A4\nLintas\ntabel"}
    seri = [("B2", "Enkripsi deterministik", BIRU, ""),
            ("B1", "Masking konsisten", ORANYE, "///"),
            ("P", "SAMAR", AQUA, "...")]

    ser_order = ["A1", "A2", "A3", "A4"]
    data = {}
    for r in rows:
        if r["kolom"] == pilih.get(r["serangan"]):
            data[r["serangan"]] = r

    x = np.arange(len(ser_order))
    lebar = 0.26
    fig, ax = plt.subplots(figsize=DUA_KOLOM)

    for i, (kode, nama, warna, hatch) in enumerate(seri):
        y = [float(data[s][kode]) for s in ser_order]
        pos = x + (i - 1) * lebar
        ax.bar(pos, y, lebar * 0.88, color=warna, linewidth=0,
               hatch=hatch, edgecolor="white", label=nama)
        for px, py in zip(pos, y):
            ax.text(px, py + 2.2, km(py), ha="center", va="bottom",
                    fontsize=6.3, color=TEKS2)

    # garis lantai baseline
    base = float(data["A1"]["baseline"])
    ax.axhline(base, color=TEKS2, lw=0.7, zorder=0)
    # diletakkan di sela antarkelompok agar tidak tertutup batang
    ax.text(0.5, base + 2.4, f"{km(base)}%", fontsize=6.3,
            color=TEKS2, ha="center", va="bottom")

    ax.set_xticks(x); ax.set_xticklabels([label[s] for s in ser_order])
    ax.set_ylabel("Recovery rate (%)")
    ax.set_ylim(0, 116)
    ax.grid(True, which="major", axis="y")
    _rapikan(ax)
    ax.legend(frameon=False, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 1.16), handlelength=1.4, columnspacing=1.4)

    p = os.path.join(OUT, "gbr3_recovery.png")
    fig.savefig(p); plt.close(fig)
    print("->", p)
