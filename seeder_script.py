import random
from faker import Faker
from datetime import datetime, timedelta

# Inisialisasi Faker untuk data Indonesia
fake = Faker('id_ID')

# Jumlah data yang diinginkan (minimal 40, bisa disesuaikan)
NUM_ALAMAT = 50
NUM_PENGGUNA_PENJUAL = 40
NUM_PENGGUNA_PEMBELI = 45 # Buat lebih banyak pembeli
NUM_PRODUK_MIN_PER_PENJUAL = 1
NUM_PRODUK_MAX_PER_PENJUAL = 3
NUM_SKU_PER_PRODUK_MIN = 1
NUM_SKU_PER_PRODUK_MAX = 4
NUM_GAMBAR_TOTAL = 150
NUM_GAMBAR_PER_PRODUK_MIN = 1
NUM_GAMBAR_PER_PRODUK_MAX = 3
NUM_TAG_TOTAL = 60
NUM_TAG_PER_PRODUK_MIN = 1
NUM_TAG_PER_PRODUK_MAX = 4
NUM_BARANG_KERANJANG_PER_KERANJANG_MIN = 0 # Keranjang bisa kosong
NUM_BARANG_KERANJANG_PER_KERANJANG_MAX = 5
NUM_PESANAN_PER_PEMBELI_MIN = 0
NUM_PESANAN_PER_PEMBELI_MAX = 3
NUM_BARANG_PESANAN_PER_PESANAN_MIN = 1
NUM_BARANG_PESANAN_PER_PESANAN_MAX = 4
NUM_WISHLIST_PER_PEMBELI_MIN = 0
NUM_WISHLIST_PER_PEMBELI_MAX = 10
NUM_ULASAN_MAX_PER_PRODUK = 5 # Maksimal ulasan per produk dari pembeli berbeda
NUM_TEMAN_FOLLOWS_MIN = 0
NUM_TEMAN_FOLLOWS_MAX = 10 # Setiap pengguna mengikuti N pengguna lain

# Lists untuk menyimpan ID yang sudah digenerate untuk referensi FK
alamat_ids = []
pengguna_ids_all = []
pengguna_ids_penjual_map = {} # map id_pengguna -> id_penjual
pengguna_ids_pembeli_map = {} # map id_pengguna -> id_pembeli
penjual_ids = []
pembeli_ids = []
produk_ids = []
all_skus = [] # List of tuples (sku, harga, stok)
sku_pks = [] # List of primary keys (sku value)
atribut_varian_pks = ['WARNA', 'UKURAN', 'MATERIAL', 'RAM', 'STORAGE_INTERNAL']
gambar_ids = []
tag_ids = []
keranjang_ids_map = {} # map id_pembeli -> id_keranjang
pesanan_ids = []

sql_statements = []

def add_statement(sql):
    sql_statements.append(sql)

add_statement("CREATE DATABASE IF NOT EXISTS ecommerce;")
add_statement("USE ecommerce;")
add_statement("""
CREATE TABLE IF NOT EXISTS Alamat (
    id_alamat INT PRIMARY KEY,
    provinsi VARCHAR(255),
    kota VARCHAR(255),
    jalan VARCHAR(255)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Pengguna (
    id_pengguna INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    nama_lengkap VARCHAR(255),
    tgl_lahir DATE,
    no_telp VARCHAR(20),
    foto_profil VARCHAR(255),
    is_penjual BOOLEAN
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Penjual (
    id_penjual INT PRIMARY KEY,
    id_pengguna INT,
    foto_diri VARCHAR(255),
    nama VARCHAR(100),
    is_verified BOOLEAN,
    FOREIGN KEY (id_pengguna) REFERENCES Pengguna(id_pengguna)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Pembeli (
    id_pembeli INT PRIMARY KEY,
    id_pengguna INT,
    FOREIGN KEY (id_pengguna) REFERENCES Pengguna(id_pengguna)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS AlamatPembeli (
    id_pembeli INT,
    id_alamat INT,
    id_pesanan INT,
    is_default BOOLEAN,
    PRIMARY KEY (id_pembeli, id_alamat),
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli),
    FOREIGN KEY (id_alamat) REFERENCES Alamat(id_alamat)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Keranjang (
    id_keranjang INT PRIMARY KEY,
    id_pembeli INT,
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Produk (
    id_produk INT PRIMARY KEY,
    id_penjual INT,
    nama VARCHAR(255),
    deskripsi TEXT,
    FOREIGN KEY (id_penjual) REFERENCES Penjual(id_penjual)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS VarianProduk (
    sku VARCHAR(50) PRIMARY KEY,
    harga DECIMAL(10, 2),
    stok INT
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS AtributVarian (
    atribut_varian VARCHAR(50) PRIMARY KEY,
    nama VARCHAR(100)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS ProdukVarianAtribut (
    id_produk INT,
    atribut_varian VARCHAR(50),
    sku VARCHAR(50),
    nilai VARCHAR(100),
    PRIMARY KEY (id_produk, atribut_varian, sku),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (atribut_varian) REFERENCES AtributVarian(atribut_varian),
    FOREIGN KEY (sku) REFERENCES VarianProduk(sku)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Gambar (
    id_gambar INT PRIMARY KEY,
    gambar VARCHAR(255)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS GambarProduk (
    id_produk INT,
    id_gambar INT,
    PRIMARY KEY (id_produk, id_gambar),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (id_gambar) REFERENCES Gambar(id_gambar)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Tag (
    id_tag INT PRIMARY KEY,
    nama VARCHAR(50)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS TagProduk (
    id_produk INT,
    id_tag INT,
    PRIMARY KEY (id_produk, id_tag),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (id_tag) REFERENCES Tag(id_tag)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS BarangKeranjang (
    id_keranjang INT,
    sku VARCHAR(50),
    kuantitas INT,
    PRIMARY KEY (id_keranjang, sku),
    FOREIGN KEY (id_keranjang) REFERENCES Keranjang(id_keranjang),
    FOREIGN KEY (sku) REFERENCES VarianProduk(sku)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Pesanan (
    id_pesanan INT PRIMARY KEY,
    id_pembeli INT,
    metode_pembayaran VARCHAR(50),
    metode_pengiriman VARCHAR(50),
    catatan TEXT,
    status_pesanan VARCHAR(50),
    waktu_pemesanan TIMESTAMP,
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS BarangPesanan (
    id_pesanan INT,
    sku VARCHAR(50),
    kuantitas INT,
    PRIMARY KEY (id_pesanan, sku),
    FOREIGN KEY (id_pesanan) REFERENCES Pesanan(id_pesanan),
    FOREIGN KEY (sku) REFERENCES VarianProduk(sku)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Wishlist (
    id_pembeli INT,
    id_produk INT,
    PRIMARY KEY (id_pembeli, id_produk),
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Ulasan (
    id_produk INT,
    id_pembeli INT,
    komentar TEXT,
    penilaian INT,
    PRIMARY KEY (id_produk, id_pembeli),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Teman (
    id_diikuti INT,
    id_mengikuti INT,
    PRIMARY KEY (id_diikuti, id_mengikuti),
    FOREIGN KEY (id_diikuti) REFERENCES Pengguna(id_pengguna),
    FOREIGN KEY (id_mengikuti) REFERENCES Pengguna(id_pengguna)
);""")
add_statement("\n-- SEEDER DATA\n")


# 1. Alamat
add_statement("-- Alamat")
for i in range(1, NUM_ALAMAT + 1):
    alamat_ids.append(i)
    provinsi = fake.administrative_unit()
    kota = fake.city_name()
    jalan = fake.street_address()
    add_statement(f"INSERT INTO Alamat (id_alamat, provinsi, kota, jalan) VALUES ({i}, '{provinsi.replace('\'', '')}', '{kota.replace('\'', '')}', '{jalan.replace('\'', '')}');")

# 2. Pengguna
add_statement("\n-- Pengguna")
pengguna_id_counter = 1
generated_emails = set()

# Penjual
for i in range(1, NUM_PENGGUNA_PENJUAL + 1):
    email = fake.unique.email()
    while email in generated_emails: # Pastikan unik jika faker.unique kadang miss
        email = fake.email() # Coba lagi jika tidak unik
    generated_emails.add(email)

    password = fake.password(length=12)
    nama_lengkap = fake.name()
    tgl_lahir = fake.date_of_birth(minimum_age=20, maximum_age=60).strftime('%Y-%m-%d')
    no_telp = fake.phone_number()
    foto_profil = f"profil/user{pengguna_id_counter}.jpg"
    is_penjual = "TRUE"
    pengguna_ids_all.append(pengguna_id_counter)
    pengguna_ids_penjual_map[pengguna_id_counter] = None # Akan diisi id_penjual nanti

    add_statement(f"INSERT INTO Pengguna (id_pengguna, email, password, nama_lengkap, tgl_lahir, no_telp, foto_profil, is_penjual) VALUES ({pengguna_id_counter}, '{email}', '{password}', '{nama_lengkap.replace('\'', '')}', '{tgl_lahir}', '{no_telp}', '{foto_profil}', {is_penjual});")
    pengguna_id_counter += 1

# Pembeli
for i in range(1, NUM_PENGGUNA_PEMBELI + 1):
    email = fake.unique.email()
    while email in generated_emails: # Pastikan unik
        email = fake.email()
    generated_emails.add(email)
    password = fake.password(length=12)
    nama_lengkap = fake.name()
    tgl_lahir = fake.date_of_birth(minimum_age=15, maximum_age=70).strftime('%Y-%m-%d')
    no_telp = fake.phone_number()
    foto_profil = f"profil/user{pengguna_id_counter}.jpg"
    is_penjual = "FALSE"
    pengguna_ids_all.append(pengguna_id_counter)
    pengguna_ids_pembeli_map[pengguna_id_counter] = None # Akan diisi id_pembeli nanti

    add_statement(f"INSERT INTO Pengguna (id_pengguna, email, password, nama_lengkap, tgl_lahir, no_telp, foto_profil, is_penjual) VALUES ({pengguna_id_counter}, '{email}', '{password}', '{nama_lengkap.replace('\'', '')}', '{tgl_lahir}', '{no_telp}', '{foto_profil}', {is_penjual});")
    pengguna_id_counter += 1

# 3. Penjual
add_statement("\n-- Penjual")
penjual_id_counter = 1
for p_id_pengguna in pengguna_ids_penjual_map.keys():
    foto_diri = f"fotodiri/penjual{penjual_id_counter}.jpg"
    nama_toko = fake.company().replace('\'', '') + " Store"
    is_verified = random.choice(["TRUE", "FALSE"])
    penjual_ids.append(penjual_id_counter)
    pengguna_ids_penjual_map[p_id_pengguna] = penjual_id_counter # Update map

    add_statement(f"INSERT INTO Penjual (id_penjual, id_pengguna, foto_diri, nama, is_verified) VALUES ({penjual_id_counter}, {p_id_pengguna}, '{foto_diri}', '{nama_toko}', {is_verified});")
    penjual_id_counter +=1

# 4. Pembeli
add_statement("\n-- Pembeli")
pembeli_id_counter = 1
for p_id_pengguna in pengguna_ids_pembeli_map.keys():
    pembeli_ids.append(pembeli_id_counter)
    pengguna_ids_pembeli_map[p_id_pengguna] = pembeli_id_counter # Update map

    add_statement(f"INSERT INTO Pembeli (id_pembeli, id_pengguna) VALUES ({pembeli_id_counter}, {p_id_pengguna});")
    pembeli_id_counter += 1

# 5. AlamatPembeli
add_statement("\n-- AlamatPembeli")
for pb_id in pembeli_ids:
    num_addresses_for_buyer = random.randint(1, min(3, len(alamat_ids))) # Maks 3 alamat per pembeli
    chosen_alamat_ids = random.sample(alamat_ids, num_addresses_for_buyer)
    default_set = False
    for idx, al_id in enumerate(chosen_alamat_ids):
        is_default = "FALSE"
        if not default_set or (idx == len(chosen_alamat_ids) -1 and not default_set) : # Pastikan ada satu default
            is_default = "TRUE"
            default_set = True
        add_statement(f"INSERT INTO AlamatPembeli (id_pembeli, id_alamat, id_pesanan, is_default) VALUES ({pb_id}, {al_id}, NULL, {is_default});")

# 6. Keranjang
add_statement("\n-- Keranjang")
keranjang_id_counter = 1
for pb_id in pembeli_ids:
    keranjang_ids_map[pb_id] = keranjang_id_counter
    add_statement(f"INSERT INTO Keranjang (id_keranjang, id_pembeli) VALUES ({keranjang_id_counter}, {pb_id});")
    keranjang_id_counter += 1

# 7. AtributVarian
add_statement("\n-- AtributVarian")
atribut_nama_map = {
    'WARNA': 'Warna', 'UKURAN': 'Ukuran', 'MATERIAL': 'Material',
    'RAM': 'RAM', 'STORAGE_INTERNAL': 'Penyimpanan Internal'
}
for atr_pk in atribut_varian_pks:
    nama_atr = atribut_nama_map[atr_pk]
    add_statement(f"INSERT INTO AtributVarian (atribut_varian, nama) VALUES ('{atr_pk}', '{nama_atr}');")

# 8. VarianProduk, Produk, ProdukVarianAtribut
# Karena saling terkait, generate bersamaan
add_statement("\n-- Produk, VarianProduk, ProdukVarianAtribut")
produk_id_counter = 1
sku_global_counter = 1
sku_values_generated_this_run = set()

for pj_id in penjual_ids:
    num_produk_for_penjual = random.randint(NUM_PRODUK_MIN_PER_PENJUAL, NUM_PRODUK_MAX_PER_PENJUAL)
    for _ in range(num_produk_for_penjual):
        nama_produk = fake.catch_phrase().replace('\'', '') + " " + random.choice(["Berkualitas", "Terbaru", "Original", "Spesial"])
        deskripsi_produk = fake.paragraph(nb_sentences=3).replace('\'', '')
        add_statement(f"INSERT INTO Produk (id_produk, id_penjual, nama, deskripsi) VALUES ({produk_id_counter}, {pj_id}, '{nama_produk}', '{deskripsi_produk}');")
        produk_ids.append(produk_id_counter)

        num_skus_for_produk = random.randint(NUM_SKU_PER_PRODUK_MIN, NUM_SKU_PER_PRODUK_MAX)
        for _ in range(num_skus_for_produk):
            sku_val = f"SKU{str(sku_global_counter).zfill(5)}"
            while sku_val in sku_values_generated_this_run: # Pastikan SKU unik dalam sekali run
                sku_global_counter += 1
                sku_val = f"SKU{str(sku_global_counter).zfill(5)}"
            sku_values_generated_this_run.add(sku_val)

            harga_varian = round(random.uniform(10000, 2000000), 2)
            stok_varian = random.randint(0, 200)
            all_skus.append({'sku': sku_val, 'harga': harga_varian, 'stok': stok_varian, 'id_produk': produk_id_counter}) # Simpan untuk referensi
            sku_pks.append(sku_val)
            add_statement(f"INSERT INTO VarianProduk (sku, harga, stok) VALUES ('{sku_val}', {harga_varian}, {stok_varian});")

            # ProdukVarianAtribut
            # Ambil 1-2 atribut untuk SKU ini
            num_attrs_for_sku = random.randint(1, min(2, len(atribut_varian_pks)))
            chosen_attrs = random.sample(atribut_varian_pks, num_attrs_for_sku)
            for attr_pk_val in chosen_attrs:
                nilai_attr = "N/A"
                if attr_pk_val == 'WARNA':
                    nilai_attr = fake.color_name()
                elif attr_pk_val == 'UKURAN':
                    nilai_attr = random.choice(['S', 'M', 'L', 'XL', 'XXL', 'All Size'])
                elif attr_pk_val == 'MATERIAL':
                    nilai_attr = random.choice(['Katun', 'Polyester', 'Kulit Sintetis', 'Plastik ABS', 'Logam'])
                elif attr_pk_val == 'RAM':
                    nilai_attr = random.choice(['4GB', '8GB', '16GB', '32GB'])
                elif attr_pk_val == 'STORAGE_INTERNAL':
                    nilai_attr = random.choice(['64GB', '128GB', '256GB', '512GB', '1TB'])
                add_statement(f"INSERT INTO ProdukVarianAtribut (id_produk, atribut_varian, sku, nilai) VALUES ({produk_id_counter}, '{attr_pk_val}', '{sku_val}', '{nilai_attr.replace('\'', '')}');")
            sku_global_counter += 1
        produk_id_counter += 1

# 9. Gambar
add_statement("\n-- Gambar")
for i in range(1, NUM_GAMBAR_TOTAL + 1):
    gambar_ids.append(i)
    add_statement(f"INSERT INTO Gambar (id_gambar, gambar) VALUES ({i}, 'img/item/placeholder_{i}.jpg');")

# 10. GambarProduk
add_statement("\n-- GambarProduk")
if produk_ids and gambar_ids: # Pastikan ada produk dan gambar
    for pr_id in produk_ids:
        num_gambar_for_produk = random.randint(NUM_GAMBAR_PER_PRODUK_MIN, min(NUM_GAMBAR_PER_PRODUK_MAX, len(gambar_ids)))
        chosen_gbr_ids = random.sample(gambar_ids, num_gambar_for_produk)
        for gbr_id in chosen_gbr_ids:
            add_statement(f"INSERT INTO GambarProduk (id_produk, id_gambar) VALUES ({pr_id}, {gbr_id});")

# 11. Tag
add_statement("\n-- Tag")
common_tags = ["Elektronik", "Fashion Pria", "Fashion Wanita", "Rumah Tangga", "Kesehatan", "Kecantikan", "Mainan", "Buku", "Olahraga", "Otomotif", "Voucher", "Hobi"]
for i in range(1, NUM_TAG_TOTAL + 1):
    tag_ids.append(i)
    if i <= len(common_tags):
        nama_tag = common_tags[i-1]
    else:
        nama_tag = fake.word().capitalize() + str(i) # Pastikan unik
    add_statement(f"INSERT INTO Tag (id_tag, nama) VALUES ({i}, '{nama_tag.replace('\'', '')}');")

# 12. TagProduk
add_statement("\n-- TagProduk")
if produk_ids and tag_ids: # Pastikan ada produk dan tag
    for pr_id in produk_ids:
        num_tag_for_produk = random.randint(NUM_TAG_PER_PRODUK_MIN, min(NUM_TAG_PER_PRODUK_MAX, len(tag_ids)))
        chosen_tg_ids = random.sample(tag_ids, num_tag_for_produk)
        for tg_id in chosen_tg_ids:
            add_statement(f"INSERT INTO TagProduk (id_produk, id_tag) VALUES ({pr_id}, {tg_id});")


# 13. BarangKeranjang
add_statement("\n-- BarangKeranjang")
if sku_pks: # Pastikan ada SKU
    for pb_id, kr_id in keranjang_ids_map.items():
        num_barang_in_keranjang = random.randint(NUM_BARANG_KERANJANG_PER_KERANJANG_MIN, min(NUM_BARANG_KERANJANG_PER_KERANJANG_MAX, len(sku_pks)))
        if num_barang_in_keranjang > 0:
            chosen_skus_for_cart = random.sample(sku_pks, num_barang_in_keranjang)
            for cart_sku in chosen_skus_for_cart:
                kuantitas = random.randint(1, 3)
                # Cek stok, idealnya. Untuk seeder, kita skip agar lebih mudah.
                add_statement(f"INSERT INTO BarangKeranjang (id_keranjang, sku, kuantitas) VALUES ({kr_id}, '{cart_sku}', {kuantitas});")

# 14. Pesanan
add_statement("\n-- Pesanan")
pesanan_id_counter = 1
metode_pembayaran_opsi = ['Transfer Bank BCA', 'Transfer Bank Mandiri', 'GoPay', 'OVO', 'Dana', 'COD', 'Kartu Kredit Visa', 'Alfamart']
metode_pengiriman_opsi = ['JNE REG', 'JNE YES', 'Sicepat BEST', 'Sicepat HALU', 'J&T Express', 'Anteraja Regular', 'Gojek Instant', 'Grab SameDay']
status_pesanan_opsi = ['Pending', 'Diproses', 'Dikirim', 'Selesai', 'Dibatalkan', 'Menunggu Pembayaran']

for pb_id in pembeli_ids:
    num_pesanan_for_pembeli = random.randint(NUM_PESANAN_PER_PEMBELI_MIN, NUM_PESANAN_PER_PEMBELI_MAX)
    for _ in range(num_pesanan_for_pembeli):
        metode_pembayaran = random.choice(metode_pembayaran_opsi)
        metode_pengiriman = random.choice(metode_pengiriman_opsi)
        catatan = fake.sentence(nb_words=10) if random.random() > 0.7 else "NULL"
        if catatan != "NULL": catatan = f"'{catatan.replace('\'', '')}'"
        status_pesanan = random.choice(status_pesanan_opsi)
        waktu_pemesanan = (datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0,23), minutes=random.randint(0,59)))
        waktu_pemesanan_str = waktu_pemesanan.strftime('%Y-%m-%d %H:%M:%S')

        pesanan_ids.append(pesanan_id_counter)
        add_statement(f"INSERT INTO Pesanan (id_pesanan, id_pembeli, metode_pembayaran, metode_pengiriman, catatan, status_pesanan, waktu_pemesanan) VALUES ({pesanan_id_counter}, {pb_id}, '{metode_pembayaran}', '{metode_pengiriman}', {catatan}, '{status_pesanan}', '{waktu_pemesanan_str}');")
        pesanan_id_counter += 1


# 15. BarangPesanan
add_statement("\n-- BarangPesanan")
if pesanan_ids and sku_pks: # Pastikan ada pesanan dan SKU
    for ps_id in pesanan_ids:
        num_barang_in_pesanan = random.randint(NUM_BARANG_PESANAN_PER_PESANAN_MIN, min(NUM_BARANG_PESANAN_PER_PESANAN_MAX, len(sku_pks)))
        chosen_skus_for_order = random.sample(sku_pks, num_barang_in_pesanan)
        for order_sku in chosen_skus_for_order:
            kuantitas = random.randint(1, 2)
            # Idealnya, cek stok dan SKU yang dijual oleh penjual terkait produk, tapi disederhanakan.
            add_statement(f"INSERT INTO BarangPesanan (id_pesanan, sku, kuantitas) VALUES ({ps_id}, '{order_sku}', {kuantitas});")

# 16. Wishlist
add_statement("\n-- Wishlist")
if pembeli_ids and produk_ids:
    for pb_id in pembeli_ids:
        num_wishlist_items = random.randint(NUM_WISHLIST_PER_PEMBELI_MIN, min(NUM_WISHLIST_PER_PEMBELI_MAX, len(produk_ids)))
        if num_wishlist_items > 0:
            chosen_prods_for_wishlist = random.sample(produk_ids, num_wishlist_items)
            for wl_prod_id in chosen_prods_for_wishlist:
                # Hindari duplikasi PK
                add_statement(f"INSERT IGNORE INTO Wishlist (id_pembeli, id_produk) VALUES ({pb_id}, {wl_prod_id});")


# 17. Ulasan
add_statement("\n-- Ulasan")
# Logika sederhana: Pembeli mengulas produk yang mungkin pernah ada di pesanannya (disimplifikasi)
# Untuk memastikan PK (id_produk, id_pembeli) unik
ulasan_pairs = set()
if produk_ids and pembeli_ids and pesanan_ids: # Pastikan ada data yang cukup
    # Ambil pembeli yang pernah memesan
    pembeli_yg_order = list(set([pb_id for ps_id in pesanan_ids for _ps_detail in sql_statements if f"Pesanan ({ps_id}" in _ps_detail for pb_id in pembeli_ids if f", {pb_id}," in _ps_detail]))

    for pr_id in produk_ids:
        # Ambil beberapa pembeli acak yang pernah order untuk mengulas produk ini
        num_ulasan_for_produk = random.randint(0, min(NUM_ULASAN_MAX_PER_PRODUK, len(pembeli_yg_order)))
        if num_ulasan_for_produk > 0 and pembeli_yg_order:
            ulasan_reviewers = random.sample(pembeli_yg_order, min(num_ulasan_for_produk, len(pembeli_yg_order)))
            for reviewer_pb_id in ulasan_reviewers:
                if (pr_id, reviewer_pb_id) not in ulasan_pairs:
                    komentar = fake.paragraph(nb_sentences=2).replace('\'', '')
                    penilaian = random.randint(1, 5)
                    add_statement(f"INSERT INTO Ulasan (id_produk, id_pembeli, komentar, penilaian) VALUES ({pr_id}, {reviewer_pb_id}, '{komentar}', {penilaian});")
                    ulasan_pairs.add((pr_id, reviewer_pb_id))


# 18. Teman
add_statement("\n-- Teman")
teman_pairs = set()
if pengguna_ids_all:
    for follower_id_pengguna in pengguna_ids_all:
        num_following = random.randint(NUM_TEMAN_FOLLOWS_MIN, min(NUM_TEMAN_FOLLOWS_MAX, len(pengguna_ids_all) -1 ))
        if num_following > 0:
            possible_followed_ids = [pid for pid in pengguna_ids_all if pid != follower_id_pengguna]
            if possible_followed_ids: # Pastikan ada kandidat untuk diikuti
                followed_ids_pengguna = random.sample(possible_followed_ids, min(num_following, len(possible_followed_ids)))
                for followed_id_pengguna in followed_ids_pengguna:
                    if (followed_id_pengguna, follower_id_pengguna) not in teman_pairs:
                        add_statement(f"INSERT INTO Teman (id_diikuti, id_mengikuti) VALUES ({followed_id_pengguna}, {follower_id_pengguna});")
                        teman_pairs.add((followed_id_pengguna, follower_id_pengguna))


# Tulis ke file SQL
output_filename = "ecommerce_seeder.sql"
with open(output_filename, "w", encoding="utf-8") as f:
    for stmt in sql_statements:
        f.write(stmt + "\n")

print(f"Seeder SQL telah digenerate ke file: {output_filename}")