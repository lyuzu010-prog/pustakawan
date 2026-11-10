import sqlite3

DATABASE = 'peminjaman.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Tabel Pengguna (Pustakawan & Peminjam)
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password
                       TEXT
                       NOT
                       NULL,
                       role
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       role
                       IN
                   (
                       'pustakawan',
                       'peminjam'
                   ))
                       )
                   ''')

    # 2. Tabel Buku
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS books
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       author
                       TEXT
                       NOT
                       NULL,
                       stock
                       INTEGER
                       NOT
                       NULL
                       DEFAULT
                       1
                   )
                   ''')

    # 3. Tabel Transaksi Peminjaman
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS borrowings
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER
                       NOT
                       NULL,
                       book_id
                       INTEGER
                       NOT
                       NULL,
                       status
                       TEXT
                       DEFAULT
                       'dipinjam', -- Status: 'dipinjam' atau 'dikembalikan'
                       borrow_date
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       book_id
                   ) REFERENCES books
                   (
                       id
                   )
                       )
                   ''')

    # Seed Data (Suntik data awal jika tabel kosong)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Akun Pustakawan
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'pustakawan')")
        # Akun Peminjam
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('peter', 'parker123', 'peminjam')")

        # Data Buku Dummy
        cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Advanced Python', 'G. Rossum', 5)")
        cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Web UI/UX 2D', 'S. Lee', 3)")

    conn.commit()
    conn.close()
    print("Database SQLite berhasil diinisialisasi dan siap digunakan.")


if __name__ == '__main__':
    init_db()