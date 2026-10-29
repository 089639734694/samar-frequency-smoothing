"""
oracle_bench.py - Pengukuran kinerja keenam skema pada Oracle sungguhan.

Dijalankan OLEH PENGGUNA pada instance dev. Skrip:
  1. membuat tabel sintetis berawalan SAMAR_ di schema pada config/oracle.ini,
  2. mengisinya dengan data sintetis bertoken (dibangkitkan di Python),
  3. membangun indeks pada kolom token golongan,
  4. mengukur: throughput INSERT, ukuran indeks & tabel, dan latensi kueri
     kesetaraan (termasuk IN-list sebanyak faktor ekspansi untuk V1 & SAMAR),
  5. menulis hasil ke results/oracle_results.csv.

TIDAK menyentuh tabel ERP apa pun. Gunakan schema uji terpisah.

Cara pakai (pakai Python Anaconda 64-bit yang paketnya lengkap):
    python src/oracle_bench.py            # jalankan benchmark
    python src/oracle_bench.py --cleanup  # hapus semua tabel SAMAR_*

Catatan: butuh paket  oracledb  dan  cryptography  (keduanya sudah terpasang
di Anaconda pada laptop ini). Kredensial dibaca dari config/oracle.ini.
"""

from __future__ import annotations

import argparse
import configparser
import os
import statistics
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

import datagen  # noqa: E402
from schemes import (B0Plaintext, B1MaskingKonsisten, B2AesSiv,  # noqa: E402
                     B3BlindIndex, PSamar, V1HomofonikAcak)

try:
    import oracledb
except ImportError:
    oracledb = None

PREFIX = "SAMAR_"
TARGET = 250
N_PEGAWAI = 50_000
BULAN = 12
N_KUERI = 200          # jumlah kueri kesetaraan per skema untuk rerata latensi
ROOT = os.path.dirname(os.path.dirname(__file__))


def koneksi():
    if oracledb is None:
        sys.exit("Paket 'oracledb' belum terpasang. Jalankan: pip install oracledb")
    cfg = configparser.ConfigParser()
    path = os.path.join(ROOT, "config", "oracle.ini")
    if not os.path.exists(path):
        sys.exit(f"Tidak ada {path}. Salin oracle.ini.contoh lalu isi kredensial.")
    cfg.read(path)
    o = cfg["oracle"]
    return oracledb.connect(user=o["user"], password=o["password"], dsn=o["dsn"])


def buat_skema(Skema):
    return (Skema(target=TARGET)
            if Skema in (V1HomofonikAcak, PSamar) else Skema())


def drop_tabel(cur, nama):
    try:
        cur.execute(f"DROP TABLE {nama} PURGE")
    except oracledb.DatabaseError:
        pass


def ukuran_segmen(cur, nama):
    """Ukuran segmen (MB) untuk tabel/indeks bernama (uppercase)."""
    cur.execute(
        "SELECT NVL(SUM(bytes),0)/1048576 FROM user_segments "
        "WHERE segment_name = :1", [nama.upper()])
    return cur.fetchone()[0]


def cleanup(conn):
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM user_tables "
                "WHERE table_name LIKE :1", [PREFIX + "%"])
    tabel = [r[0] for r in cur.fetchall()]
    for t in tabel:
        drop_tabel(cur, t)
        print("  drop", t)
    conn.commit()
    print(f"Selesai. {len(tabel)} tabel dihapus.")


def benchmark(conn):
    ds = datagen.bangkitkan(n_pegawai=N_PEGAWAI, bulan=BULAN)
    nik = ds.pegawai["nik"]
    gol = ds.pegawai["golongan"]
    cur = conn.cursor()
    rng = np.random.default_rng(13)

    baris_csv = [("kode", "skema", "k_ekspansi", "insert_rps",
                  "tabel_mb", "indeks_mb", "latensi_ms_median",
                  "latensi_ms_p95")]

    for Skema in [B0Plaintext, B1MaskingKonsisten, B2AesSiv,
                  B3BlindIndex, V1HomofonikAcak, PSamar]:
        s = buat_skema(Skema)
        s.fit(gol)
        kode = s.kode
        tbl = f"{PREFIX}PEG_{kode}"
        idx = f"{PREFIX}IDX_{kode}"

        # token golongan untuk setiap pegawai
        tok = [s.transform(g, e) for g, e in zip(gol, nik)]

        drop_tabel(cur, tbl)
        cur.execute(f"CREATE TABLE {tbl} "
                    f"(nik VARCHAR2(16), gol_token VARCHAR2(128))")

        # --- INSERT throughput ---
        rows = list(zip(nik.tolist(), tok))
        t0 = time.perf_counter()
        cur.executemany(
            f"INSERT INTO {tbl} (nik, gol_token) VALUES (:1, :2)", rows)
        conn.commit()
        dt = time.perf_counter() - t0
        insert_rps = len(rows) / dt

        cur.execute(f"CREATE INDEX {idx} ON {tbl}(gol_token)")
        cur.execute(f"BEGIN DBMS_STATS.GATHER_TABLE_STATS(USER, '{tbl}'); END;")
        conn.commit()

        tabel_mb = ukuran_segmen(cur, tbl)
        indeks_mb = ukuran_segmen(cur, idx)
        k_eksp = getattr(s, "faktor_ekspansi_terbobot", 1.0)

        # --- latensi kueri kesetaraan ---
        # ambil N_KUERI nilai golongan acak (dibobot frekuensi) lalu kuerikan
        sampel = rng.choice(gol, size=N_KUERI)
        waktu = []
        for v in sampel:
            qt = s.query_tokens(v)       # 1 token (deterministik) / k token (homofonik)
            ph = ", ".join(f":{i+1}" for i in range(len(qt)))
            sql = f"SELECT COUNT(*) FROM {tbl} WHERE gol_token IN ({ph})"
            t0 = time.perf_counter()
            cur.execute(sql, qt)
            cur.fetchone()
            waktu.append((time.perf_counter() - t0) * 1000)

        med = statistics.median(waktu)
        p95 = sorted(waktu)[int(0.95 * len(waktu)) - 1]

        print(f"{kode:3s} {s.nama:34s} k={k_eksp:6.1f}  "
              f"ins={insert_rps:8.0f} rps  idx={indeks_mb:5.2f}MB  "
              f"lat_med={med:6.3f}ms  p95={p95:6.3f}ms")
        baris_csv.append((kode, s.nama, f"{k_eksp:.2f}", f"{insert_rps:.0f}",
                          f"{tabel_mb:.3f}", f"{indeks_mb:.3f}",
                          f"{med:.4f}", f"{p95:.4f}"))

    # tulis CSV
    out = os.path.join(ROOT, "results", "oracle_results.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in baris_csv:
            f.write(",".join(map(str, r)) + "\n")
    print(f"\nHasil ditulis ke {out}")
    print("Jalankan 'python src/oracle_bench.py --cleanup' untuk menghapus tabel uji.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cleanup", action="store_true",
                    help="hapus semua tabel SAMAR_* lalu keluar")
    args = ap.parse_args()
    conn = koneksi()
    print("Terhubung ke Oracle:",
          conn.version if hasattr(conn, "version") else "ok")
    try:
        if args.cleanup:
            cleanup(conn)
        else:
            benchmark(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
