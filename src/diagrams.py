# -*- coding: utf-8 -*-
"""
diagrams.py - Diagram arsitektur dan alur untuk makalah SAMAR.

Berbeda dari figures.py yang membaca CSV hasil eksperimen, berkas ini
menggambar skema (kotak dan panah) langsung: model sistem dan ancaman, serta
alur pembentukan token SAMAR. Gaya dibuat bersih dan aman dicetak hitam-putih:
kotak bergaris tipis, isi warna lembut, teks serif, panah tipis.
"""
from __future__ import annotations
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "figs")
os.makedirs(OUT, exist_ok=True)

PROC = "#e9f1fb"; PROC_E = "#2a4a74"       # proses (biru muda)
IO = "#ffffff"; IO_E = "#444444"           # masukan/keluaran (putih)
OK = "#e6f3ec"; OK_E = "#1f7a46"           # hasil baik (hijau muda)
KEY = "#fff6e5"; KEY_E = "#b5862f"         # kunci/konteks (kuning muda)
ADV = "#fbe9e6"; ADV_E = "#b5442f"         # penyerang (merah muda)
GRP_E = "#9a9a9a"                          # batas kelompok (abu putus-putus)
TEKS = "#111111"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 7.4,
    "figure.dpi": 400, "savefig.dpi": 400,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})


def kotak(ax, x, y, w, h, teks, fc=PROC, ec=PROC_E, fs=7.4, lw=0.9,
          bold=False, italic=False, tc=TEKS, rounded=True):
    style = "round,pad=0,rounding_size=1.6" if rounded else "square,pad=0"
    box = FancyBboxPatch((x, y), w, h, boxstyle=style,
                         facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, teks, ha="center", va="center",
            fontsize=fs, color=tc, zorder=3,
            fontweight="bold" if bold else "normal",
            fontstyle="italic" if italic else "normal")
    return (x, y, w, h)


def tag(ax, b, teks):
    """Label kecil merah di pojok kanan-atas kotak, mirip penanda M1/M2/M3."""
    x, y, w, h = b
    tw, th = 7.5, 6.5
    tx, ty = x + w - tw / 2 - 1.5, y + h - th / 2 - 1.2
    ax.add_patch(Rectangle((tx - tw / 2, ty - th / 2), tw, th,
                 facecolor=ADV_E, edgecolor="none", zorder=5))
    ax.text(tx, ty, teks, ha="center", va="center", fontsize=6.6,
            color="white", fontweight="bold", zorder=6)


def panah(ax, p1, p2, lw=1.0, color="#333333", style="-|>", ms=9, ls="-"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms,
                        linewidth=lw, color=color, linestyle=ls,
                        shrinkA=0, shrinkB=0, zorder=1)
    ax.add_patch(a)


def kanan(b): x, y, w, h = b; return (x + w, y + h / 2)
def kiri(b): x, y, w, h = b; return (x, y + h / 2)
def atas(b): x, y, w, h = b; return (x + w / 2, y + h)
def bawah(b): x, y, w, h = b; return (x + w / 2, y)


def _siap(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


# ---------------------------------------------------------------------------
# Gambar model sistem dan ancaman
# ---------------------------------------------------------------------------
def gambar_sistem():
    fig, ax = _siap((6.9, 3.2))

    # domain aplikasi (tepercaya)
    ax.add_patch(Rectangle((1.5, 40), 42, 57, fill=False, edgecolor=GRP_E,
                 linewidth=0.9, linestyle=(0, (4, 3))))
    ax.text(3.5, 93, "Sisi aplikasi (tepercaya)", ha="left", va="center",
            fontsize=6.6, color="#555", fontstyle="italic",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    app = kotak(ax, 5, 64, 16, 20, "Aplikasi\n(pemegang\nkunci K, Kₛ)",
                fc=PROC, ec=PROC_E, fs=7.0)
    trans = kotak(ax, 24, 64, 17, 20, "Transformasi\nSAMAR", fc=PROC, ec=PROC_E,
                  bold=True)
    panah(ax, kanan(app), kiri(trans))
    ax.text(22.5, 54, "kunci tidak pernah\nmasuk basis data", ha="center",
            va="center", fontsize=6.0, color="#555", fontstyle="italic")

    # domain basis data (tidak tepercaya)
    ax.add_patch(Rectangle((52, 40), 46.5, 57, fill=False, edgecolor=GRP_E,
                 linewidth=0.9, linestyle=(0, (4, 3))))
    ax.text(54, 93, "Basis data / salinan (tidak tepercaya)", ha="left",
            va="center", fontsize=6.6, color="#555", fontstyle="italic",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    t1 = kotak(ax, 57, 70, 38, 15, "Tabel Pegawai\n(kolom tersamar)",
               fc=IO, ec=IO_E, fs=7.0)
    t2 = kotak(ax, 57, 47, 38, 15, "Tabel Penggajian\n(kolom tersamar)",
               fc=IO, ec=IO_E, fs=7.0)
    # garis berbagi atribut
    panah(ax, (76, 70), (76, 62), style="<->", color=OK_E, lw=1.0)
    ax.text(77.5, 66, "berbagi atribut\n(mis. golongan)", ha="left",
            va="center", fontsize=6.0, color=OK_E, fontstyle="italic")

    # tulis dari transformasi ke basis data
    panah(ax, kanan(trans), kiri(t1), lw=1.2)
    ax.text(49.5, 80, "tulis token", ha="center", va="bottom", fontsize=6.2,
            color="#333")

    # penyerang snapshot
    adv = [
        (3, "Salinan\nnon-produksi", "M1"),
        (36.7, "Pengembang / DBA", "M2"),
        (70.3, "Pemegang\ncadangan", "M3"),
    ]
    boxes = []
    for x, lbl, tg in adv:
        b = kotak(ax, x, 4, 27, 20, lbl, fc=ADV, ec=ADV_E, fs=7.0)
        tag(ax, b, tg)
        boxes.append(b)
    # arah baca: dari basis data ke penyerang
    panah(ax, bawah(t2), atas(boxes[1]), ls=(0, (3, 2)), color=ADV_E)
    panah(ax, (62, 47), atas(boxes[0]), ls=(0, (3, 2)), color=ADV_E)
    panah(ax, (90, 47), atas(boxes[2]), ls=(0, (3, 2)), color=ADV_E)
    ax.text(50, 30, "membaca snapshot kolom tersamar (tanpa kunci)",
            ha="center", va="center", fontsize=6.2, color=ADV_E,
            fontstyle="italic",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

    fig.savefig(os.path.join(OUT, "gbr_sistem.png"))
    plt.close(fig)
    print("  gbr_sistem.png")


# ---------------------------------------------------------------------------
# Gambar alur pembentukan token SAMAR
# ---------------------------------------------------------------------------
def gambar_konstruksi():
    fig, ax = _siap((6.9, 3.1))

    # masukan
    inp = [
        (2, "nilai v"),
        (20, "pengenal\nentitas e"),
        (38, "frekuensi f(v)"),
        (57, "target t"),
    ]
    ib = []
    for x, lbl in inp:
        ib.append(kotak(ax, x, 83, 15, 14, lbl, fc=IO, ec=IO_E, fs=7.0))

    # kuota
    kuota = kotak(ax, 34, 56, 40, 16,
                  "Kuota homofon\nk(v) = maks(1, bulat(f(v)/t))",
                  fc=PROC, ec=PROC_E, fs=7.0)
    # pemilih (deterministik, disorot)
    pilih = kotak(ax, 10, 30, 52, 16,
                  "Pemilih (deterministik)\nj = HMAC(Kₛ, e ‖ v) mod k(v)",
                  fc=KEY, ec=KEY_E, fs=7.2, bold=False)
    # token
    token = kotak(ax, 20, 6, 50, 15,
                  "Token  T(v, j) = trunc₁₆(HMAC(K, v ‖ j))",
                  fc=OK, ec=OK_E, fs=7.2, bold=True)

    # panah masukan -> kuota / pemilih
    panah(ax, bawah(ib[2]), (54, 72))      # f(v) -> kuota
    panah(ax, bawah(ib[3]), (64, 72))      # t -> kuota
    panah(ax, bawah(ib[0]), (20, 46))      # v -> pemilih
    panah(ax, bawah(ib[1]), (30, 46))      # e -> pemilih
    panah(ax, bawah(kuota), (50, 46))      # k(v) -> pemilih
    panah(ax, bawah(pilih), atas(token))   # j -> token
    # v juga masuk token
    panah(ax, (9.5, 90), (9.5, 13.5), ls=(0, (2, 2)), color="#888")
    panah(ax, (9.5, 13.5), kiri(token), ls=(0, (2, 2)), color="#888")

    # catatan sifat
    ax.text(88, 38,
            "keacakan diambil\ndari keragaman\nentitas, bukan RNG",
            ha="center", va="center", fontsize=6.2, color=KEY_E,
            fontstyle="italic",
            bbox=dict(facecolor="#fff6e5", edgecolor=KEY_E, linewidth=0.7,
                      boxstyle="round,pad=0.3"))
    ax.text(88, 12,
            "(e, v) sama → token sama\n→ konsisten antartabel;\n"
            "entitas beda → histogram rata",
            ha="center", va="center", fontsize=6.0, color=OK_E,
            fontstyle="italic",
            bbox=dict(facecolor="#e6f3ec", edgecolor=OK_E, linewidth=0.7,
                      boxstyle="round,pad=0.3"))

    fig.savefig(os.path.join(OUT, "gbr_konstruksi.png"))
    plt.close(fig)
    print("  gbr_konstruksi.png")


if __name__ == "__main__":
    print("Menggambar diagram SAMAR ...")
    gambar_sistem()
    gambar_konstruksi()
    print("Selesai ->", OUT)
