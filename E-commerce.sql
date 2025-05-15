CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

CREATE TABLE Alamat (
    id_alamat INT PRIMARY KEY,
    provinsi VARCHAR(255),
    kota VARCHAR(255),
    jalan VARCHAR(255)
);

CREATE TABLE Pengguna (
    id_pengguna INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    nama_lengkap VARCHAR(255),
    tgl_lahir DATE,
    no_telp VARCHAR(20),
    foto_profil VARCHAR(255),
    is_penjual BOOLEAN,
);

CREATE TABLE Penjual (
    id_penjual INT PRIMARY KEY,
    id_pengguna INT,
    foto_diri VARCHAR(255),
    nama VARCHAR(100),
    is_verified BOOLEAN,
    FOREIGN KEY (id_pengguna) REFERENCES Pengguna(id_pengguna)
);

CREATE TABLE Pembeli (
    id_pembeli INT PRIMARY KEY,
    id_pengguna INT,
    FOREIGN KEY (id_pengguna) REFERENCES Pengguna(id_pengguna)
);

CREATE TABLE AlamatPembeli (
    id_pembeli INT,
    id_alamat INT,
    id_pesanan INT,
    is_default BOOLEAN,
    PRIMARY KEY (id_pembeli, id_alamat),
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli),
    FOREIGN KEY (id_alamat) REFERENCES Alamat(id_alamat)
);

CREATE TABLE Keranjang (
    id_keranjang INT PRIMARY KEY,
    id_pembeli INT,
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli)
);

CREATE TABLE Produk (
    id_produk INT PRIMARY KEY,
    id_penjual INT,
    nama VARCHAR(255),
    deskripsi TEXT,
    FOREIGN KEY (id_penjual) REFERENCES Penjual(id_penjual)
);

CREATE TABLE VarianProduk (
    sku VARCHAR(50) PRIMARY KEY,
    harga DECIMAL(10, 2),
    stok INT
);

CREATE TABLE AtributVarian (
    atribut_varian VARCHAR(50) PRIMARY KEY,
    nama VARCHAR(100)
);

CREATE TABLE ProdukVarianAtribut (
    id_produk INT,
    atribut_varian VARCHAR(50),
    sku VARCHAR(50),
    nilai VARCHAR(100),
    PRIMARY KEY (id_produk, atribut_varian, sku),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (atribut_varian) REFERENCES AtributVarian(atribut_varian),
    FOREIGN KEY (sku) REFERENCES VarianProduk(sku)
);

CREATE TABLE Gambar (
    id_gambar INT PRIMARY KEY,
    gambar VARCHAR(255)
);

CREATE TABLE GambarProduk (
    id_produk INT,
    id_gambar INT,
    PRIMARY KEY (id_produk, id_gambar),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (id_gambar) REFERENCES Gambar(id_gambar)
);

CREATE TABLE Tag (
    id_tag INT PRIMARY KEY,
    nama VARCHAR(50)
);

CREATE TABLE TagProduk (
    id_produk INT,
    id_tag INT,
    PRIMARY KEY (id_produk, id_tag),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (id_tag) REFERENCES Tag(id_tag)
);

CREATE TABLE BarangKeranjang (
    id_keranjang INT,
    sku VARCHAR(50),
    kuantitas INT,
    PRIMARY KEY (id_keranjang, sku),
    FOREIGN KEY (id_keranjang) REFERENCES Keranjang(id_keranjang),
    FOREIGN KEY (sku) REFERENCES VarianProduk(sku)
);

CREATE TABLE Pesanan (
    id_pesanan INT PRIMARY KEY,
    id_pembeli INT,
    metode_pembayaran VARCHAR(50),
    metode_pengiriman VARCHAR(50),
    catatan TEXT,
    status_pesanan VARCHAR(50),
    waktu_pemesanan TIMESTAMP,
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli)
);

CREATE TABLE BarangPesanan (
    id_pesanan INT,
    sku VARCHAR(255),
    kuantitas INT,
    PRIMARY KEY (id_pesanan, sku),
    FOREIGN KEY (id_pesanan) REFERENCES Pesanan(id_pesanan),
    FOREIGN KEY (sku) REFERENCES VarianProduk(sku)
);

CREATE TABLE Wishlist (
    id_pembeli INT,
    id_produk INT,
    PRIMARY KEY (id_pembeli, id_produk),
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
);

CREATE TABLE Ulasan (
    id_produk INT,
    id_pembeli INT,
    komentar TEXT,
    penilaian INT,
    PRIMARY KEY (id_produk, id_pembeli),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk),
    FOREIGN KEY (id_pembeli) REFERENCES Pembeli(id_pembeli)
);

CREATE TABLE Teman (
    id_diikuti INT,
    id_mengikuti INT,
    PRIMARY KEY (id_diikuti, id_mengikuti),
    FOREIGN KEY (id_diikuti) REFERENCES Pengguna(id_pengguna),
    FOREIGN KEY (id_mengikuti) REFERENCES Pengguna(id_pengguna)
);