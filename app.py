from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db

app = Flask(__name__)
# Secret key diperlukan untuk menggunakan session (sistem login)
app.secret_key = 'kunci_rahasia_galaksi_kosmik'


# Route Utama - Pengecekan sesi login
@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'pustakawan':
            return redirect(url_for('dashboard_pustakawan'))
        else:
            return redirect(url_for('dashboard_peminjam'))
    return redirect(url_for('login'))


# Route Autentikasi (Login & Logout)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                          (username, password)).fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Login gagal! Cek kembali kredensial kosmik Anda.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Route Pustakawan
@app.route('/pustakawan')
def dashboard_pustakawan():
    if 'role' not in session or session['role'] != 'pustakawan':
        return redirect(url_for('login'))

    db = get_db()
    books = db.execute('SELECT * FROM books').fetchall()
    return render_template('pustakawan.html', books=books)


@app.route('/tambah_buku', methods=['POST'])
def tambah_buku():
    if 'role' in session and session['role'] == 'pustakawan':
        title = request.form['title']
        author = request.form['author']
        stock = int(request.form['stock'])

        db = get_db()
        db.execute('INSERT INTO books (title, author, stock) VALUES (?, ?, ?)',
                   (title, author, stock))
        db.commit()
    return redirect(url_for('dashboard_pustakawan'))


# Route Peminjam
@app.route('/peminjam')
def dashboard_peminjam():
    if 'role' not in session or session['role'] != 'peminjam':
        return redirect(url_for('login'))

    db = get_db()
    # Hanya tampilkan buku dengan stok tersedia
    books = db.execute('SELECT * FROM books WHERE stock > 0').fetchall()
    # Tampilkan riwayat peminjaman user saat ini
    riwayat = db.execute('''
                         SELECT books.title, borrowings.status, borrowings.borrow_date
                         FROM borrowings
                                  JOIN books ON borrowings.book_id = books.id
                         WHERE borrowings.user_id = ?
                         ''', (session['user_id'],)).fetchall()

    return render_template('peminjam.html', books=books, riwayat=riwayat)


@app.route('/pinjam/<int:book_id>', methods=['POST'])
def pinjam(book_id):
    if 'role' in session and session['role'] == 'peminjam':
        db = get_db()
        # Catat peminjaman dan kurangi stok buku 1 unit
        db.execute('INSERT INTO borrowings (user_id, book_id) VALUES (?, ?)',
                   (session['user_id'], book_id))
        db.execute('UPDATE books SET stock = stock - 1 WHERE id = ?', (book_id,))
        db.commit()
    return redirect(url_for('dashboard_peminjam'))


if __name__ == '__main__':
    app.run(debug=True)