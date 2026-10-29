"""
attacks.py - Empat serangan inferensi terhadap kolom tersamar.

Model penyerang (snapshot / persisten semi-jujur): penyerang memperoleh
salinan statis kolom token pada satu tabel atau lebih, plus distribusi bantu
publik per kolom. Penyerang tidak memiliki kunci.

Metrik utama: recovery rate = proporsi baris yang nilai aslinya berhasil
ditebak dengan benar. Sebagai pembanding disertakan baseline_tebak_terbanyak,
yaitu menebak nilai paling umum (menurut distribusi bantu) untuk semua baris.

Serangan:
  A1  frequency_analysis       - pencocokan peringkat frekuensi
  A2  optimal_assignment       - penugasan optimal (Hungarian) pada histogram
  A3  cross_column             - korelasi antarkolom (gaji -> golongan)
  A4  cross_table              - agregasi frekuensi lintas tabel (kontribusi)
"""

from __future__ import annotations

from collections import Counter

import numpy as np
from scipy.optimize import linear_sum_assignment


def _recovery(pred_map, tokens, truth):
    """pred_map: token -> nilai tebakan. Hitung proporsi benar."""
    benar = sum(1 for t, y in zip(tokens, truth) if pred_map.get(t) == y)
    return benar / len(tokens)


def baseline_tebak_terbanyak(aux_dist, tokens, truth):
    """Tebak nilai paling umum untuk semua baris. Lantai pembanding."""
    nilai_top = max(aux_dist, key=aux_dist.get)
    return sum(1 for y in truth if y == nilai_top) / len(truth)


# ---------------------------------------------------------------------------
# A1 - Analisis frekuensi: cocokkan peringkat
# ---------------------------------------------------------------------------

def frequency_analysis(aux_dist, tokens, truth):
    tok_freq = Counter(tokens)
    # token diurut dari paling sering; nilai bantu diurut dari paling mungkin
    tok_rank = [t for t, _ in tok_freq.most_common()]
    val_rank = sorted(aux_dist, key=aux_dist.get, reverse=True)
    pred = {t: v for t, v in zip(tok_rank, val_rank)}
    return _recovery(pred, tokens, truth)


# ---------------------------------------------------------------------------
# A2 - Penugasan optimal (varian l_p Naveed et al.)
# ---------------------------------------------------------------------------

def optimal_assignment(aux_dist, tokens, truth):
    """Cocokkan histogram token ke histogram bantu dengan meminimalkan total
    selisih frekuensi absolut (penugasan optimal via Hungarian).

    Hanya token yang cukup sering (>= ambang) yang ditugaskan; sisanya
    dibiarkan tak tertebak. Ini memberi penyerang keuntungan maksimal pada
    skema deterministik dan, sebaliknya, gagal rapi pada skema homofonik
    karena tidak ada token yang menonjol.
    """
    n = len(tokens)
    tok_freq = Counter(tokens)
    # ambil token teratas sebanyak kardinalitas domain bantu
    m = len(aux_dist)
    tok_top = [t for t, _ in tok_freq.most_common(m)]
    vals = list(aux_dist)

    f_tok = np.array([tok_freq[t] / n for t in tok_top])
    f_val = np.array([aux_dist[v] for v in vals])

    # matriks biaya |f_tok_i - f_val_j|
    biaya = np.abs(f_tok[:, None] - f_val[None, :])
    r, c = linear_sum_assignment(biaya)
    pred = {tok_top[i]: vals[j] for i, j in zip(r, c)}
    return _recovery(pred, tokens, truth)


# ---------------------------------------------------------------------------
# A3 - Korelasi antarkolom: pulihkan golongan lewat gaji pokok
# ---------------------------------------------------------------------------

def cross_column(aux_joint, tokens_gol, gaji, truth_gol):
    """Penyerang tahu hubungan publik antara rentang gaji dan golongan
    (aux_joint: nilai_golongan -> perkiraan gaji rata-rata). Untuk tiap token
    golongan, tetapkan gaji rata-rata baris bertoken itu, lalu petakan ke
    golongan dengan gaji acuan terdekat.

    Ini menembus skema deterministik meski golongan tersamar, karena gaji
    (sering dibiarkan apa adanya untuk kebutuhan analitik) membocorkannya.
    """
    gaji = np.asarray(gaji, dtype=float)
    tokens_gol = np.asarray(tokens_gol)
    rata_per_token = {}
    for t in set(tokens_gol):
        mask = tokens_gol == t
        rata_per_token[t] = gaji[mask].mean()

    vals = list(aux_joint)
    acuan = np.array([aux_joint[v] for v in vals])
    pred = {}
    for t, g in rata_per_token.items():
        pred[t] = vals[int(np.argmin(np.abs(acuan - g)))]
    return _recovery(pred, tokens_gol, truth_gol)


# ---------------------------------------------------------------------------
# A4 - Serangan lintas tabel (kontribusi)
# ---------------------------------------------------------------------------

def cross_table(aux_dist, tokens_a, truth_a, tokens_b):
    """Penyerang menggabungkan frekuensi token dari dua tabel yang berbagi
    atribut sama (mis. golongan di tabel pegawai dan di tabel transaksi).
    Tabel transaksi jauh lebih besar sehingga mempertajam estimasi frekuensi.

    Histogram gabungan dipakai untuk membangun peta token -> nilai (via
    penugasan optimal), lalu diterapkan pada tabel pegawai untuk mengukur
    pemulihan di tingkat entitas.

    Terhadap skema deterministik (B1/B2/B3) data tambahan memperkuat serangan.
    Terhadap SAMAR, frekuensi token tetap rata walau diagregasi lintas tabel,
    karena homofon ditentukan per entitas; serangan tidak memperoleh apa pun.
    """
    n_a = len(tokens_a)
    gab = Counter(tokens_a) + Counter(tokens_b)
    m = len(aux_dist)
    tok_top = [t for t, _ in gab.most_common(m)]
    vals = list(aux_dist)

    tot = sum(gab.values())
    f_tok = np.array([gab[t] / tot for t in tok_top])
    f_val = np.array([aux_dist[v] for v in vals])
    biaya = np.abs(f_tok[:, None] - f_val[None, :])
    r, c = linear_sum_assignment(biaya)
    pred = {tok_top[i]: vals[j] for i, j in zip(r, c)}

    # terapkan ke tabel pegawai (entitas)
    benar = sum(1 for t, y in zip(tokens_a, truth_a) if pred.get(t) == y)
    return benar / n_a
