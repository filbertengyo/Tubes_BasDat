import random
from faker import Faker
from datetime import datetime, timedelta

# Inisialisasi Faker untuk data Indonesia
fake = Faker('id_ID')

# Target jumlah data minimal per tabel yang bervariasi
TARGET_MIN_RECORDS = 100

# Konfigurasi Jumlah Data Awal (ini akan menjadi basis)
NUM_ALAMAT_INITIAL = max(TARGET_MIN_RECORDS, 50)
NUM_PENGGUNA_PENJUAL_INITIAL = max(TARGET_MIN_RECORDS // 2, 50)
NUM_PENGGUNA_PEMBELI_INITIAL = max(TARGET_MIN_RECORDS // 2, 60)
NUM_GAMBAR_TOTAL_INITIAL = max(TARGET_MIN_RECORDS * 2, 150)
NUM_TAG_TOTAL_INITIAL = max(TARGET_MIN_RECORDS + 20, 60)

atribut_varian_pks = ['WARNA', 'UKURAN', 'MATERIAL', 'RAM', 'STORAGE_INTERNAL', 'JENIS_KAIN', 'RESOLUSI_LAYAR']
atribut_nama_map = {
    'WARNA': 'Warna', 'UKURAN': 'Ukuran', 'MATERIAL': 'Material',
    'RAM': 'RAM', 'STORAGE_INTERNAL': 'Penyimpanan Internal',
    'JENIS_KAIN': 'Jenis Kain', 'RESOLUSI_LAYAR': 'Resolusi Layar'
}

# Lists untuk menyimpan ID yang sudah digenerate untuk referensi FK
alamat_ids = []
pengguna_ids_all = []
pengguna_penjual_details = {}
pengguna_pembeli_details = {}
penjual_ids = []
pembeli_ids = []

# New structure for AlamatPembeli
alamat_pembeli_records = [] # List of dicts {'id_alamat_pembeli': pk, 'id_pembeli': fk, 'id_alamat': fk}

produk_details = []
all_skus_generated = []
sku_pks_only = []
gambar_ids = []
tag_ids = []
pesanan_details = []

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
    ktp VARCHAR(255),
    foto_diri VARCHAR(255),
    is_verified BOOLEAN,
    FOREIGN KEY (id_pengguna) REFERENCES Pengguna(id_pengguna)
);""")
add_statement("""
CREATE TABLE IF NOT EXISTS Pembeli (
    id_pembeli INT PRIMARY KEY,
    id_pengguna INT,
    FOREIGN KEY (id_pengguna) REFERENCES Pengguna(id_pengguna)
);""")

# Modified AlamatPembeli structure
add_statement("""
CREATE TABLE IF NOT EXISTS AlamatPembeli (
    id_alamat_pembeli INT PRIMARY KEY, -- New surrogate PK
    id_pembeli INT,
    id_alamat INT,
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli),
    FOREIGN KEY (id_alamat) REFERENCES Alamat(id_alamat)
);""")

# New AlamatDefault table
add_statement("""
CREATE TABLE IF NOT EXISTS AlamatDefault (
    id_alamat_pembeli INT PRIMARY KEY, -- FK to AlamatPembeli.id_alamat_pembeli
    is_default BOOLEAN DEFAULT TRUE, -- As per image, though TRUE is implied by presence
    FOREIGN KEY (id_alamat_pembeli) REFERENCES AlamatPembeli(id_alamat_pembeli)
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

# Modified VarianProduk structure
add_statement("""
CREATE TABLE IF NOT EXISTS VarianProduk (
    sku VARCHAR(50) PRIMARY KEY,
    id_produk INT, -- Added FK to Produk
    harga DECIMAL(10, 2),
    stok INT,
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
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

# Modified Pesanan structure
add_statement("""
CREATE TABLE IF NOT EXISTS Pesanan (
    id_pesanan INT PRIMARY KEY,
    id_pembeli INT,
    id_alamat_pembeli INT, -- Added FK to AlamatPembeli
    metode_pembayaran VARCHAR(50),
    metode_pengiriman VARCHAR(50),
    catatan TEXT,
    status_pesanan VARCHAR(50),
    waktu_pemesanan TIMESTAMP,
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli),
    FOREIGN KEY (id_alamat_pembeli) REFERENCES AlamatPembeli(id_alamat_pembeli)
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
for i in range(1, NUM_ALAMAT_INITIAL + 1):
    alamat_ids.append(i)
    provinsi = fake.administrative_unit()
    kota = fake.city_name()
    jalan = fake.street_address()
    add_statement(f"INSERT IGNORE INTO Alamat (id_alamat, provinsi, kota, jalan) VALUES ({i}, '{provinsi.replace('\'', '\'\'')}', '{kota.replace('\'', '\'\'')}', '{jalan.replace('\'', '\'\'')}');")

# 2. Pengguna
add_statement("\n-- Pengguna")
pengguna_id_counter = 1
generated_emails = set()
for i in range(1, NUM_PENGGUNA_PENJUAL_INITIAL + 1):
    email = fake.unique.email()
    while email in generated_emails: email = fake.email() # Ensure uniqueness if fake.unique fails
    generated_emails.add(email)
    password = fake.password(length=12)
    nama_lengkap = fake.name()
    tgl_lahir = fake.date_of_birth(minimum_age=20, maximum_age=60).strftime('%Y-%m-%d')
    no_telp = fake.phone_number()
    foto_profil = f"profil/user{pengguna_id_counter}.jpg"
    pengguna_ids_all.append(pengguna_id_counter)
    pengguna_penjual_details[pengguna_id_counter] = {}
    add_statement(f"INSERT IGNORE INTO Pengguna (id_pengguna, email, password, nama_lengkap, tgl_lahir, no_telp, foto_profil, is_penjual) VALUES ({pengguna_id_counter}, '{email}', '{password.replace('\'', '\'\'')}', '{nama_lengkap.replace('\'', '\'\'')}', '{tgl_lahir}', '{no_telp}', '{foto_profil}', TRUE);")
    pengguna_id_counter += 1
for i in range(1, NUM_PENGGUNA_PEMBELI_INITIAL + 1):
    email = fake.unique.email()
    while email in generated_emails: email = fake.email() # Ensure uniqueness
    generated_emails.add(email)
    password = fake.password(length=12)
    nama_lengkap = fake.name()
    tgl_lahir = fake.date_of_birth(minimum_age=15, maximum_age=70).strftime('%Y-%m-%d')
    no_telp = fake.phone_number()
    foto_profil = f"profil/user{pengguna_id_counter}.jpg"
    pengguna_ids_all.append(pengguna_id_counter)
    pengguna_pembeli_details[pengguna_id_counter] = {}
    add_statement(f"INSERT IGNORE INTO Pengguna (id_pengguna, email, password, nama_lengkap, tgl_lahir, no_telp, foto_profil, is_penjual) VALUES ({pengguna_id_counter}, '{email}', '{password.replace('\'', '\'\'')}', '{nama_lengkap.replace('\'', '\'\'')}', '{tgl_lahir}', '{no_telp}', '{foto_profil}', FALSE);")
    pengguna_id_counter += 1

# 3. Penjual
add_statement("\n-- Penjual")
penjual_id_counter = 1
for p_id_pengguna in pengguna_penjual_details.keys():
    ktp_val = fake.numerify(text='3###############') # 16 digit NIK
    foto_diri = f"fotodiri/penjual{penjual_id_counter}.jpg"
    is_verified = random.choice(["TRUE", "FALSE"])
    penjual_ids.append(penjual_id_counter)
    pengguna_penjual_details[p_id_pengguna]['id_penjual'] = penjual_id_counter
    add_statement(f"INSERT IGNORE INTO Penjual (id_penjual, id_pengguna, ktp, foto_diri, is_verified) VALUES ({{penjual_id_counter}}, {{p_id_pengguna}}, '{{ktp_val}}', '{{foto_diri}}', {{is_verified}});")
    penjual_id_counter +=1

# 4. Pembeli
add_statement("\n-- Pembeli")
pembeli_id_counter = 1
for p_id_pengguna in pengguna_pembeli_details.keys():
    pembeli_ids.append(pembeli_id_counter)
    pengguna_pembeli_details[p_id_pengguna]['id_pembeli'] = pembeli_id_counter
    add_statement(f"INSERT IGNORE INTO Pembeli (id_pembeli, id_pengguna) VALUES ({pembeli_id_counter}, {p_id_pengguna});")
    pembeli_id_counter += 1

# 5. AlamatPembeli (Modified)
add_statement("\n-- AlamatPembeli")
id_alamat_pembeli_counter = 1
alamat_pembeli_per_buyer = {} # To track addresses for AlamatDefault

for pb_id in pembeli_ids:
    num_addresses_for_buyer = random.randint(1, min(3, len(alamat_ids)))
    if not alamat_ids: continue # Skip if no addresses to assign
    chosen_alamat_ids = random.sample(alamat_ids, num_addresses_for_buyer)
    
    if pb_id not in alamat_pembeli_per_buyer:
        alamat_pembeli_per_buyer[pb_id] = []

    for al_id in chosen_alamat_ids:
        alamat_pembeli_records.append({
            'id_alamat_pembeli': id_alamat_pembeli_counter,
            'id_pembeli': pb_id,
            'id_alamat': al_id
        })
        alamat_pembeli_per_buyer[pb_id].append(id_alamat_pembeli_counter)
        add_statement(f"INSERT IGNORE INTO AlamatPembeli (id_alamat_pembeli, id_pembeli, id_alamat) VALUES ({id_alamat_pembeli_counter}, {pb_id}, {al_id});")
        id_alamat_pembeli_counter += 1

# Ensure TARGET_MIN_RECORDS for AlamatPembeli if needed (simple addition)
while len(alamat_pembeli_records) < TARGET_MIN_RECORDS and pembeli_ids and alamat_ids:
    pb_id = random.choice(pembeli_ids)
    al_id = random.choice(alamat_ids)
    # Check for duplicate (pb_id, al_id) pair before inserting if strictly necessary,
    # but with surrogate PK, it's less of an issue unless business logic dictates uniqueness.
    # For this seeder, we'll just add, relying on surrogate PK for table uniqueness.
    alamat_pembeli_records.append({
        'id_alamat_pembeli': id_alamat_pembeli_counter,
        'id_pembeli': pb_id,
        'id_alamat': al_id
    })
    if pb_id not in alamat_pembeli_per_buyer:
        alamat_pembeli_per_buyer[pb_id] = []
    alamat_pembeli_per_buyer[pb_id].append(id_alamat_pembeli_counter)
    add_statement(f"INSERT IGNORE INTO AlamatPembeli (id_alamat_pembeli, id_pembeli, id_alamat) VALUES ({id_alamat_pembeli_counter}, {pb_id}, {al_id});")
    id_alamat_pembeli_counter += 1

# 6. AlamatDefault (New)
add_statement("\n-- AlamatDefault")
alamat_default_count = 0
for pb_id in pembeli_ids:
    if pb_id in alamat_pembeli_per_buyer and alamat_pembeli_per_buyer[pb_id]:
        # Pick one id_alamat_pembeli for this buyer to be the default
        default_ap_id = random.choice(alamat_pembeli_per_buyer[pb_id])
        add_statement(f"INSERT IGNORE INTO AlamatDefault (id_alamat_pembeli, is_default) VALUES ({default_ap_id}, TRUE);")
        alamat_default_count += 1
# Ensure TARGET_MIN_RECORDS (though less critical for this table if all buyers have one)
# This loop might create >1 default if not careful, but schema doesn't prevent.
# For simplicity, we'll assume the above loop is sufficient for reasonable data.

# 7. Keranjang
add_statement("\n-- Keranjang")
keranjang_id_counter = 1
for p_id_pengguna, details in pengguna_pembeli_details.items():
    pb_id = details['id_pembeli']
    pengguna_pembeli_details[p_id_pengguna]['keranjang_id'] = keranjang_id_counter
    add_statement(f"INSERT IGNORE INTO Keranjang (id_keranjang, id_pembeli) VALUES ({keranjang_id_counter}, {pb_id});")
    keranjang_id_counter += 1

# 8. AtributVarian
add_statement("\n-- AtributVarian")
for atr_pk in atribut_varian_pks:
    nama_atr = atribut_nama_map.get(atr_pk, atr_pk.replace('_', ' ').title())
    add_statement(f"INSERT IGNORE INTO AtributVarian (atribut_varian, nama) VALUES ('{atr_pk}', '{nama_atr}');")

# 9. Produk, VarianProduk, ProdukVarianAtribut
add_statement("\n-- Produk, VarianProduk, ProdukVarianAtribut")
produk_id_counter = 1
sku_global_counter = 1
sku_values_generated_this_run = set()
produk_varian_atribut_count = 0

num_produk_to_generate = 0
if penjual_ids:
    avg_produk_per_penjual = max(1, TARGET_MIN_RECORDS // len(penjual_ids)) if len(penjual_ids) > 0 else TARGET_MIN_RECORDS
    num_produk_to_generate = len(penjual_ids) * avg_produk_per_penjual
    if num_produk_to_generate < TARGET_MIN_RECORDS:
         num_produk_to_generate = TARGET_MIN_RECORDS

for i in range(num_produk_to_generate):
    if not penjual_ids: break
    pj_id = random.choice(penjual_ids)
    nama_produk = fake.bs().replace('\'', '\'\'').title() + " " + random.choice(["Premium", "Edisi Terbatas", "Serbaguna", "Modern"])
    deskripsi_produk = fake.paragraph(nb_sentences=random.randint(2,4)).replace('\'', '\'\'')
    add_statement(f"INSERT IGNORE INTO Produk (id_produk, id_penjual, nama, deskripsi) VALUES ({produk_id_counter}, {pj_id}, '{nama_produk}', '{deskripsi_produk}');")
    
    current_produk_skus = []
    num_skus_for_produk = random.randint(1, 3)
    for _ in range(num_skus_for_produk):
        sku_val = f"SKU{str(sku_global_counter).zfill(6)}"
        while sku_val in sku_values_generated_this_run:
            sku_global_counter += 1
            sku_val = f"SKU{str(sku_global_counter).zfill(6)}"
        sku_values_generated_this_run.add(sku_val)

        harga_varian = round(random.uniform(10000, 3000000), 2)
        stok_varian = random.randint(0, 150)
        
        # Add to all_skus_generated with id_produk
        all_skus_generated.append({'sku': sku_val, 'id_produk': produk_id_counter, 'harga': harga_varian, 'stok': stok_varian})
        sku_pks_only.append(sku_val)
        current_produk_skus.append(sku_val)
        
        # Insert into VarianProduk with id_produk
        add_statement(f"INSERT IGNORE INTO VarianProduk (sku, id_produk, harga, stok) VALUES ('{sku_val}', {produk_id_counter}, {harga_varian}, {stok_varian});")

        num_attrs_for_sku = random.randint(1, min(3, len(atribut_varian_pks)))
        chosen_attrs = random.sample(atribut_varian_pks, num_attrs_for_sku)
        for attr_pk_val in chosen_attrs:
            nilai_attr = "N/A"
            if attr_pk_val == 'WARNA': nilai_attr = fake.color_name()
            elif attr_pk_val == 'UKURAN': nilai_attr = random.choice(['S', 'M', 'L', 'XL', 'XXL', 'All Size', '38', '39', '40', '41', '42'])
            elif attr_pk_val == 'MATERIAL': nilai_attr = random.choice(['Katun Combed 30s', 'Polyester Blend', 'Kulit Sintetis PU', 'Plastik ABS Food Grade', 'Stainless Steel 304', 'Kanvas Tebal'])
            elif attr_pk_val == 'RAM': nilai_attr = random.choice(['4GB', '8GB', '12GB', '16GB', '32GB'])
            elif attr_pk_val == 'STORAGE_INTERNAL': nilai_attr = random.choice(['64GB', '128GB', '256GB', '512GB', '1TB'])
            elif attr_pk_val == 'JENIS_KAIN': nilai_attr = random.choice(['Denim', 'Flanel', 'Satin', 'Rayon'])
            elif attr_pk_val == 'RESOLUSI_LAYAR': nilai_attr = random.choice(['HD', 'FHD', 'QHD', '4K'])
            add_statement(f"INSERT IGNORE INTO ProdukVarianAtribut (id_produk, atribut_varian, sku, nilai) VALUES ({produk_id_counter}, '{attr_pk_val}', '{sku_val}', '{nilai_attr.replace('\'', '\'\'')}');")
            produk_varian_atribut_count += 1
        sku_global_counter += 1
    produk_details.append({'id_produk': produk_id_counter, 'id_penjual': pj_id, 'skus': current_produk_skus})
    produk_id_counter += 1

while produk_varian_atribut_count < TARGET_MIN_RECORDS and produk_details and atribut_varian_pks:
    prod_detail = random.choice(produk_details)
    if not prod_detail['skus']: continue
    sku_val = random.choice(prod_detail['skus'])
    attr_pk_val = random.choice(atribut_varian_pks)
    nilai_attr = fake.word().title()
    add_statement(f"INSERT IGNORE INTO ProdukVarianAtribut (id_produk, atribut_varian, sku, nilai) VALUES ({prod_detail['id_produk']}, '{attr_pk_val}', '{sku_val}', '{nilai_attr.replace('\'', '\'\'')}');")
    produk_varian_atribut_count += 1

# 10. Gambar
add_statement("\n-- Gambar")
for i in range(1, NUM_GAMBAR_TOTAL_INITIAL + 1):
    gambar_ids.append(i)
    add_statement(f"INSERT IGNORE INTO Gambar (id_gambar, gambar) VALUES ({i}, 'img/item/placeholder_{i}.jpg');")

# 11. GambarProduk
add_statement("\n-- GambarProduk")
gambar_produk_count = 0
if produk_details and gambar_ids:
    for pr_detail in produk_details:
        pr_id = pr_detail['id_produk']
        num_gambar_for_produk = random.randint(1, min(3, len(gambar_ids)))
        if not gambar_ids : continue
        chosen_gbr_ids = random.sample(gambar_ids, num_gambar_for_produk)
        for gbr_id in chosen_gbr_ids:
            add_statement(f"INSERT IGNORE INTO GambarProduk (id_produk, id_gambar) VALUES ({pr_id}, {gbr_id});")
            gambar_produk_count += 1
while gambar_produk_count < TARGET_MIN_RECORDS and produk_details and gambar_ids:
    pr_detail = random.choice(produk_details)
    gbr_id = random.choice(gambar_ids)
    add_statement(f"INSERT IGNORE INTO GambarProduk (id_produk, id_gambar) VALUES ({pr_detail['id_produk']}, {gbr_id});")
    gambar_produk_count += 1

# 12. Tag
add_statement("\n-- Tag")
common_tags = ["Elektronik", "Fashion Pria", "Fashion Wanita", "Rumah Tangga", "Kesehatan", "Kecantikan", "Mainan Anak", "Buku & Alat Tulis", "Olahraga & Outdoor", "Otomotif Parts", "Voucher Digital", "Hobi & Koleksi", "Makanan & Minuman", "Perlengkapan Bayi", "Komputer & Aksesoris", "Handphone & Tablet"]
for i in range(1, NUM_TAG_TOTAL_INITIAL + 1):
    tag_ids.append(i)
    if i <= len(common_tags):
        nama_tag = common_tags[i-1]
    else:
        nama_tag = fake.catch_phrase().replace('\'', '\'\'').title() + " " + str(i)
    add_statement(f"INSERT IGNORE INTO Tag (id_tag, nama) VALUES ({i}, '{nama_tag.replace('\'', '\'\'')}');")

# 13. TagProduk
add_statement("\n-- TagProduk")
tag_produk_count = 0
if produk_details and tag_ids:
    for pr_detail in produk_details:
        pr_id = pr_detail['id_produk']
        num_tag_for_produk = random.randint(1, min(4, len(tag_ids)))
        if not tag_ids: continue
        chosen_tg_ids = random.sample(tag_ids, num_tag_for_produk)
        for tg_id in chosen_tg_ids:
            add_statement(f"INSERT IGNORE INTO TagProduk (id_produk, id_tag) VALUES ({pr_id}, {tg_id});")
            tag_produk_count +=1
while tag_produk_count < TARGET_MIN_RECORDS and produk_details and tag_ids:
    pr_detail = random.choice(produk_details)
    tg_id = random.choice(tag_ids)
    add_statement(f"INSERT IGNORE INTO TagProduk (id_produk, id_tag) VALUES ({pr_detail['id_produk']}, {tg_id});")
    tag_produk_count += 1

# 14. BarangKeranjang
add_statement("\n-- BarangKeranjang")
barang_keranjang_count = 0
if sku_pks_only:
    for p_id_pengguna, details in pengguna_pembeli_details.items():
        if 'keranjang_id' in details:
            kr_id = details['keranjang_id']
            num_barang_in_keranjang = random.randint(0, min(5, len(sku_pks_only)))
            if num_barang_in_keranjang > 0 and sku_pks_only:
                chosen_skus_for_cart = random.sample(sku_pks_only, num_barang_in_keranjang)
                for cart_sku in chosen_skus_for_cart:
                    kuantitas = random.randint(1, 3)
                    add_statement(f"INSERT IGNORE INTO BarangKeranjang (id_keranjang, sku, kuantitas) VALUES ({kr_id}, '{cart_sku}', {kuantitas});")
                    barang_keranjang_count += 1
all_keranjang_ids = [d['keranjang_id'] for d in pengguna_pembeli_details.values() if 'keranjang_id' in d]
while barang_keranjang_count < TARGET_MIN_RECORDS and all_keranjang_ids and sku_pks_only:
    kr_id = random.choice(all_keranjang_ids)
    cart_sku = random.choice(sku_pks_only)
    kuantitas = random.randint(1,2)
    add_statement(f"INSERT IGNORE INTO BarangKeranjang (id_keranjang, sku, kuantitas) VALUES ({kr_id}, '{cart_sku}', {kuantitas});")
    barang_keranjang_count += 1

# 15. Pesanan (Modified)
add_statement("\n-- Pesanan")
pesanan_id_counter = 1
metode_pembayaran_opsi = ['Transfer Bank BCA', 'Transfer Bank Mandiri', 'Virtual Account BNI', 'GoPay', 'OVO', 'Dana', 'ShopeePay', 'COD', 'Kartu Kredit Visa', 'Kartu Kredit Mastercard', 'Indomaret', 'Alfamart']
metode_pengiriman_opsi = ['JNE REG', 'JNE YES', 'JNE Trucking', 'Sicepat BEST', 'Sicepat HALU', 'Sicepat Gokil', 'J&T Express', 'Anteraja Regular', 'Ninja Xpress', 'Gojek Instant', 'Grab SameDay', 'POS Indonesia']
status_pesanan_opsi = ['Pending', 'Diproses', 'Dikirim', 'Selesai', 'Dibatalkan', 'Menunggu Pembayaran', 'Pengembalian Dana']
num_pesanan_generated = 0

if pembeli_ids:
    avg_pesanan_per_pembeli = max(1, TARGET_MIN_RECORDS // len(pembeli_ids)) if len(pembeli_ids) > 0 else 1
    target_total_pesanan = max(TARGET_MIN_RECORDS, len(pembeli_ids) * avg_pesanan_per_pembeli)
    
    for _ in range(target_total_pesanan):
        if not pembeli_ids: break
        pb_id = random.choice(pembeli_ids)
        
        # Select an id_alamat_pembeli for this buyer
        valid_alamat_pembeli_ids_for_buyer = [ap['id_alamat_pembeli'] for ap in alamat_pembeli_records if ap['id_pembeli'] == pb_id]
        if not valid_alamat_pembeli_ids_for_buyer:
            # Fallback: if buyer has no address, try to assign a random one or skip
            # For simplicity, if no specific address, try to pick any from AlamatPembeli
            # This situation should be rare if AlamatPembeli is populated correctly for all buyers
            if not alamat_pembeli_records: continue # Cannot create order without any address
            selected_ap_id = random.choice([ap['id_alamat_pembeli'] for ap in alamat_pembeli_records])
        else:
            selected_ap_id = random.choice(valid_alamat_pembeli_ids_for_buyer)

        metode_pembayaran = random.choice(metode_pembayaran_opsi)
        metode_pengiriman = random.choice(metode_pengiriman_opsi)
        catatan = fake.sentence(nb_words=random.randint(5,15)) if random.random() > 0.6 else "NULL"
        if catatan != "NULL": catatan = f"'{catatan.replace('\'', '\'\'')}'"
        status_pesanan = random.choice(status_pesanan_opsi)
        waktu_pemesanan = (datetime.now() - timedelta(days=random.randint(0, 180), hours=random.randint(0,23), minutes=random.randint(0,59)))
        waktu_pemesanan_str = waktu_pemesanan.strftime('%Y-%m-%d %H:%M:%S')

        pesanan_details.append({'id_pesanan': pesanan_id_counter, 'id_pembeli': pb_id, 'items': []})
        add_statement(f"INSERT IGNORE INTO Pesanan (id_pesanan, id_pembeli, id_alamat_pembeli, metode_pembayaran, metode_pengiriman, catatan, status_pesanan, waktu_pemesanan) VALUES ({pesanan_id_counter}, {pb_id}, {selected_ap_id}, '{metode_pembayaran}', '{metode_pengiriman}', {catatan}, '{status_pesanan}', '{waktu_pemesanan_str}');")
        pesanan_id_counter += 1
        num_pesanan_generated +=1
        if num_pesanan_generated >= TARGET_MIN_RECORDS and random.random() < 0.3 :
            if len(pesanan_details) > TARGET_MIN_RECORDS * 1.2 : break


# 16. BarangPesanan
add_statement("\n-- BarangPesanan")
barang_pesanan_count = 0
if pesanan_details and sku_pks_only:
    for ps_detail in pesanan_details:
        ps_id = ps_detail['id_pesanan']
        num_barang_in_pesanan = random.randint(1, min(4, len(sku_pks_only)))
        if not sku_pks_only: continue
        chosen_skus_for_order = random.sample(sku_pks_only, num_barang_in_pesanan)
        for order_sku in chosen_skus_for_order:
            kuantitas = random.randint(1, 2)
            ps_detail['items'].append({'sku': order_sku, 'kuantitas': kuantitas})
            add_statement(f"INSERT IGNORE INTO BarangPesanan (id_pesanan, sku, kuantitas) VALUES ({ps_id}, '{order_sku}', {kuantitas});")
            barang_pesanan_count += 1
while barang_pesanan_count < TARGET_MIN_RECORDS and pesanan_details and sku_pks_only:
    ps_detail = random.choice(pesanan_details)
    order_sku = random.choice(sku_pks_only)
    kuantitas = random.randint(1,2)
    add_statement(f"INSERT IGNORE INTO BarangPesanan (id_pesanan, sku, kuantitas) VALUES ({ps_detail['id_pesanan']}, '{order_sku}', {kuantitas});")
    barang_pesanan_count += 1

# 17. Wishlist
add_statement("\n-- Wishlist")
wishlist_count = 0
if pembeli_ids and produk_details:
    all_produk_ids_only = [p['id_produk'] for p in produk_details]
    if all_produk_ids_only: # ensure list is not empty
        for pb_id in pembeli_ids:
            num_wishlist_items = random.randint(0, min(10, len(all_produk_ids_only)))
            if num_wishlist_items > 0:
                chosen_prods_for_wishlist = random.sample(all_produk_ids_only, num_wishlist_items)
                for wl_prod_id in chosen_prods_for_wishlist:
                    add_statement(f"INSERT IGNORE INTO Wishlist (id_pembeli, id_produk) VALUES ({pb_id}, {wl_prod_id});")
                    wishlist_count += 1
# Tambah jika kurang
while wishlist_count < TARGET_MIN_RECORDS and pembeli_ids and produk_details:
    all_produk_ids_only = [p['id_produk'] for p in produk_details if p['id_produk']] # re-check
    if not all_produk_ids_only: break
    pb_id = random.choice(pembeli_ids)
    wl_prod_id = random.choice(all_produk_ids_only)
    add_statement(f"INSERT IGNORE INTO Wishlist (id_pembeli, id_produk) VALUES ({pb_id}, {wl_prod_id});")
    wishlist_count += 1

# 18. Ulasan
add_statement("\n-- Ulasan")
ulasan_count = 0
ulasan_pairs = set() 
produk_dibeli_map = {} 
if pesanan_details and all_skus_generated:
    sku_to_produk_map = {s['sku']: s['id_produk'] for s in all_skus_generated}
    for ps_detail in pesanan_details:
        pb_id = ps_detail['id_pembeli']
        if pb_id not in produk_dibeli_map:
            produk_dibeli_map[pb_id] = set()
        for item in ps_detail['items']:
            if item['sku'] in sku_to_produk_map:
                produk_dibeli_map[pb_id].add(sku_to_produk_map[item['sku']])

if produk_dibeli_map:
    for pb_id, purchased_prod_ids in produk_dibeli_map.items():
        if not purchased_prod_ids: continue
        num_ulasan_dari_pembeli_ini = random.randint(0, min(5, len(purchased_prod_ids)))
        if num_ulasan_dari_pembeli_ini > 0:
            prods_to_review = random.sample(list(purchased_prod_ids), num_ulasan_dari_pembeli_ini)
            for pr_id_review in prods_to_review:
                if (pr_id_review, pb_id) not in ulasan_pairs:
                    komentar = fake.paragraph(nb_sentences=random.randint(1,3)).replace('\'', '\'\'')
                    penilaian = random.randint(1, 5)
                    add_statement(f"INSERT IGNORE INTO Ulasan (id_produk, id_pembeli, komentar, penilaian) VALUES ({pr_id_review}, {pb_id}, '{komentar}', {penilaian});")
                    ulasan_pairs.add((pr_id_review, pb_id))
                    ulasan_count += 1
all_produk_ids_only = [p['id_produk'] for p in produk_details if p['id_produk']]
while ulasan_count < TARGET_MIN_RECORDS and all_produk_ids_only and pembeli_ids:
    if not all_produk_ids_only : break # double check
    pr_id = random.choice(all_produk_ids_only)
    pb_id = random.choice(pembeli_ids)
    if (pr_id, pb_id) not in ulasan_pairs:
        komentar = fake.text(max_nb_chars=150).replace('\'', '\'\'')
        penilaian = random.randint(3,5)
        add_statement(f"INSERT IGNORE INTO Ulasan (id_produk, id_pembeli, komentar, penilaian) VALUES ({pr_id}, {pb_id}, '{komentar}', {penilaian});")
        ulasan_pairs.add((pr_id, pb_id))
        ulasan_count += 1

# 19. Teman
add_statement("\n-- Teman")
teman_count = 0
teman_pairs_set = set()
if pengguna_ids_all:
    for follower_id_pengguna in pengguna_ids_all:
        num_following = random.randint(0, min(7, len(pengguna_ids_all) -1 ))
        if num_following > 0:
            possible_followed_ids = [pid for pid in pengguna_ids_all if pid != follower_id_pengguna]
            if possible_followed_ids:
                followed_ids_pengguna = random.sample(possible_followed_ids, min(num_following, len(possible_followed_ids)))
                for followed_id_pengguna in followed_ids_pengguna:
                    if (followed_id_pengguna, follower_id_pengguna) not in teman_pairs_set:
                        add_statement(f"INSERT IGNORE INTO Teman (id_diikuti, id_mengikuti) VALUES ({followed_id_pengguna}, {follower_id_pengguna});")
                        teman_pairs_set.add((followed_id_pengguna, follower_id_pengguna))
                        teman_count += 1
while teman_count < TARGET_MIN_RECORDS and len(pengguna_ids_all) > 1:
    follower = random.choice(pengguna_ids_all)
    followed_candidates = [pid for pid in pengguna_ids_all if pid != follower]
    if not followed_candidates: break
    followed = random.choice(followed_candidates)
    if (followed, follower) not in teman_pairs_set:
        add_statement(f"INSERT IGNORE INTO Teman (id_diikuti, id_mengikuti) VALUES ({followed}, {follower});")
        teman_pairs_set.add((followed, follower))
        teman_count += 1

# Tulis ke file SQL
output_filename = "E-com.sql"
with open(output_filename, "w", encoding="utf-8") as f:
    for stmt in sql_statements:
        f.write(stmt + "\n")

print(f"Generated SQL statements written to {output_filename}")