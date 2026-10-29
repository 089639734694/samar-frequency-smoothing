"""
schemes.py - Enam skema transformasi kolom sensitif yang dibandingkan.

Seluruh skema mengekspos antarmuka yang sama:

    s = Skema(...)
    s.fit(nilai_kolom)                     # mempelajari domain / kuota homofon
    token = s.transform(nilai, entity_id)
    daftar = s.query_tokens(nilai)         # token yang dicari saat WHERE col = nilai

Catatan desain: argumen entity_id hanya dipakai oleh SAMAR. Skema lain
mengabaikannya, sehingga seluruh skema dapat dipanggil lewat kode yang sama.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import struct
from collections import Counter

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, AESSIV


# ---------------------------------------------------------------------------
# Utilitas
# ---------------------------------------------------------------------------

def _hmac256(key: bytes, *parts: bytes) -> bytes:
    h = hmac.new(key, digestmod=hashlib.sha256)
    for p in parts:
        # panjang ikut dicacah agar penggabungan tidak ambigu
        h.update(struct.pack(">I", len(p)))
        h.update(p)
    return h.digest()


def _b(v) -> bytes:
    return str(v).encode("utf-8")


class Skema:
    """Antarmuka dasar. Nilai kembalian transform() selalu str agar dapat
    disimpan pada kolom VARCHAR2 Oracle tanpa konversi tambahan."""

    kode = "?"
    nama = "?"
    # sifat fungsional yang diklaim, dipakai untuk tabel ringkasan makalah
    mendukung_kesetaraan = True
    menjaga_konsistensi_lintas_tabel = True
    meratakan_frekuensi = False
    # True bila token hanya bergantung pada nilai (bukan entitas/acak),
    # sehingga tokenisasi dapat di-cache per nilai distinct. Dipakai runner.
    deterministik_nilai = True

    def fit(self, nilai):
        return self

    def transform(self, nilai, entity_id=None) -> str:
        raise NotImplementedError

    def query_tokens(self, nilai) -> list:
        return [self.transform(nilai)]

    @property
    def faktor_ekspansi_rerata(self) -> float:
        return 1.0


# ---------------------------------------------------------------------------
# B0 - Plaintext (kontrol)
# ---------------------------------------------------------------------------

class B0Plaintext(Skema):
    kode, nama = "B0", "Plaintext (kontrol)"

    def transform(self, nilai, entity_id=None) -> str:
        return str(nilai)


# ---------------------------------------------------------------------------
# B1 - Masking konsisten berbasis hash
# ---------------------------------------------------------------------------

class B1MaskingKonsisten(Skema):
    """Substitusi deterministik ke kolam nilai palsu, meniru mode
    deterministic/consistent masking pada perkakas masking komersial.

    Perhatikan bahwa seed di sini bukan kunci kriptografis: pada praktiknya
    nilai tersebut tersimpan bersama definisi masking dan ikut terbawa ke
    lingkungan non-produksi. Kelemahan itu sengaja dimodelkan.
    """

    kode, nama = "B1", "Masking konsisten (hash)"

    def __init__(self, seed: bytes = b"masking-seed-v1", prefiks: str = "MSK"):
        self.seed = seed
        self.prefiks = prefiks
        self._kolam: list = []

    def fit(self, nilai):
        domain = sorted(set(map(str, nilai)))
        # kolam nilai palsu dibuat tiga kali ukuran domain, sesuai anjuran
        # vendor agar tabrakan substitusi jarang terjadi
        self._kolam = [f"{self.prefiks}-{i:06d}"
                       for i in range(max(8, 3 * len(domain)))]
        return self

    def transform(self, nilai, entity_id=None) -> str:
        if not self._kolam:
            raise RuntimeError("fit() harus dipanggil lebih dulu")
        d = hashlib.sha256(self.seed + _b(nilai)).digest()
        return self._kolam[int.from_bytes(d[:8], "big") % len(self._kolam)]


# ---------------------------------------------------------------------------
# B2 - Enkripsi deterministik AES-SIV (RFC 5297)
# ---------------------------------------------------------------------------

class B2AesSiv(Skema):
    """AES-SIV tanpa komponen nonce: plaintext sama selalu menghasilkan
    ciphertext sama, sehingga kesetaraan dan JOIN tetap bekerja."""

    kode, nama = "B2", "Enkripsi deterministik AES-SIV"

    def __init__(self, key: bytes = None):
        self.key = key or AESSIV.generate_key(256)
        self._siv = AESSIV(self.key)

    def transform(self, nilai, entity_id=None) -> str:
        return self._siv.encrypt(_b(nilai), None).hex()

    def decrypt(self, token: str) -> str:
        return self._siv.decrypt(bytes.fromhex(token), None).decode("utf-8")


# ---------------------------------------------------------------------------
# B3 - AES-GCM acak + blind index HMAC terpotong
# ---------------------------------------------------------------------------

class B3BlindIndex(Skema):
    """Pola yang paling sering dianjurkan di tingkat aplikasi: nilai disimpan
    terenkripsi acak (AES-GCM) sehingga kolom data tidak membocorkan apa pun,
    lalu ditambahkan blind index HMAC agar kolom tetap dapat dicari.

    Blind index dipotong menjadi bit_indeks bit. Pemotongan menimbulkan
    tabrakan antarnilai berbeda, yang berfungsi sebagai derau sekaligus
    menimbulkan false positive yang harus disaring ulang oleh aplikasi.
    """

    kode, nama = "B3", "AES-GCM acak + blind index HMAC"

    def __init__(self, key_idx: bytes = None, key_enc: bytes = None,
                 bit_indeks: int = 32):
        self.key_idx = key_idx or os.urandom(32)
        self.key_enc = key_enc or AESGCM.generate_key(256)
        self.bit_indeks = bit_indeks
        self._gcm = AESGCM(self.key_enc)

    def _indeks(self, nilai) -> str:
        d = _hmac256(self.key_idx, _b(nilai))
        n_byte = (self.bit_indeks + 7) // 8
        v = int.from_bytes(d[:n_byte], "big") >> (8 * n_byte - self.bit_indeks)
        return format(v, "x")

    def transform(self, nilai, entity_id=None) -> str:
        return self._indeks(nilai)

    def ciphertext(self, nilai) -> str:
        nonce = os.urandom(12)
        return (nonce + self._gcm.encrypt(nonce, _b(nilai), None)).hex()


# ---------------------------------------------------------------------------
# Dasar penghalusan frekuensi homofonik
# ---------------------------------------------------------------------------

class _DasarHomofonik(Skema):
    """Berbagi logika kuota homofon antara V1 dan SAMAR.

    Setiap nilai v memperoleh k_v homofon, dengan k_v sebanding dengan
    frekuensinya sehingga setiap homofon diharapkan muncul kira-kira sebanyak
    target baris. Nilai yang jarang memperoleh k_v = 1 dan karena itu tidak
    menanggung biaya ekspansi kueri sama sekali.
    """

    def __init__(self, key: bytes = None, target: int = 1, k_maks: int = 4096):
        self.key = key or os.urandom(32)
        self.target = target
        self.k_maks = k_maks
        self.k: dict = {}
        self.freq: dict = {}
        self._n = 0
        # memoisasi token: jumlah pasangan (nilai, j) yang mungkin hanya
        # sebanyak sum(k_v), biasanya beberapa ratus, sehingga HMAC tidak
        # perlu dihitung ulang untuk setiap baris.
        self._memo: dict = {}

    def fit(self, nilai):
        c = Counter(map(str, nilai))
        self._n = sum(c.values())
        self.freq = dict(c)
        self.k = {v: max(1, min(self.k_maks, round(f / self.target)))
                  for v, f in c.items()}
        return self

    def _token(self, nilai, j: int) -> str:
        kunci = (nilai, j)
        t = self._memo.get(kunci)
        if t is None:
            t = _hmac256(self.key, _b(nilai), struct.pack(">I", j))[:16].hex()
            self._memo[kunci] = t
        return t

    def query_tokens(self, nilai) -> list:
        k = self.k.get(str(nilai), 1)
        return [self._token(nilai, j) for j in range(k)]

    @property
    def faktor_ekspansi_rerata(self) -> float:
        """Rerata jumlah token per kueri jika setiap nilai distinct
        dikueri dengan peluang sama."""
        if not self.k:
            return 1.0
        return sum(self.k.values()) / len(self.k)

    @property
    def faktor_ekspansi_terbobot(self) -> float:
        """Rerata jumlah token per kueri jika peluang mengueri sebuah nilai
        sebanding dengan frekuensinya di dalam tabel. Lebih mewakili beban
        kerja nyata, karena nilai yang umum juga lebih sering dicari.

        Dihitung dari frekuensi sebenarnya, bukan dari aproksimasi
        f_v = k_v * target, yang tidak berlaku saat k_v terkena batas bawah 1
        atau batas atas k_maks."""
        if not self.k or self._n == 0:
            return 1.0
        return sum(self.freq[v] * self.k[v] for v in self.k) / self._n


# ---------------------------------------------------------------------------
# V1 - Penghalusan frekuensi homofonik acak (ablasi)
# ---------------------------------------------------------------------------

class V1HomofonikAcak(_DasarHomofonik):
    """Varian ablasi yang mengikuti frequency-smoothing encryption: homofon
    dipilih acak seragam untuk setiap baris. Frekuensi menjadi rata, tetapi
    atribut milik entitas yang sama menjadi berbeda di tiap tabel, sehingga
    konsistensi lintas tabel rusak."""

    kode, nama = "V1", "Homofonik acak (ablasi)"
    menjaga_konsistensi_lintas_tabel = False
    meratakan_frekuensi = True
    deterministik_nilai = False

    # Kolam acak ber-buffer: menghindari satu syscall os.urandom per baris.
    # Sumber entropinya tetap os.urandom, hanya diambil per blok, sehingga
    # perilaku statistiknya identik.
    _BLOK = 1 << 16

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._buf = b""
        self._pos = 0

    def _acak32(self) -> int:
        if self._pos + 4 > len(self._buf):
            self._buf = os.urandom(self._BLOK)
            self._pos = 0
        v = int.from_bytes(self._buf[self._pos:self._pos + 4], "big")
        self._pos += 4
        return v

    def transform(self, nilai, entity_id=None) -> str:
        k = self.k.get(str(nilai), 1)
        return self._token(nilai, self._acak32() % k)


# ---------------------------------------------------------------------------
# P - SAMAR
# ---------------------------------------------------------------------------

class PSamar(_DasarHomofonik):
    """Homofon tidak dipilih acak, melainkan diturunkan secara deterministik
    dari pengenal entitas baris melalui HMAC berkunci:

        j = HMAC(key_sel, entity_id || nilai) mod k_v

    Akibatnya satu entitas selalu memperoleh homofon yang sama untuk nilai
    yang sama, di tabel mana pun, sehingga konsistensi lintas tabel terjaga.
    Sementara itu entitas berbeda yang bernilai sama tersebar ke homofon
    berbeda, sehingga histogram token tetap rata.

    Pemilih j tidak dapat dihitung penyerang karena bergantung pada kunci,
    walaupun entity_id sendiri terlihat di tabel.
    """

    kode, nama = "P", "SAMAR"
    meratakan_frekuensi = True
    deterministik_nilai = False

    def __init__(self, key: bytes = None, key_sel: bytes = None,
                 target: int = 1, k_maks: int = 4096):
        super().__init__(key=key, target=target, k_maks=k_maks)
        self.key_sel = key_sel or os.urandom(32)

    def transform(self, nilai, entity_id=None) -> str:
        if entity_id is None:
            raise ValueError("SAMAR memerlukan entity_id")
        k = self.k.get(str(nilai), 1)
        j = int.from_bytes(
            _hmac256(self.key_sel, _b(entity_id), _b(nilai))[:8], "big") % k
        return self._token(nilai, j)


SEMUA_SKEMA = [B0Plaintext, B1MaskingKonsisten, B2AesSiv,
               B3BlindIndex, V1HomofonikAcak, PSamar]
