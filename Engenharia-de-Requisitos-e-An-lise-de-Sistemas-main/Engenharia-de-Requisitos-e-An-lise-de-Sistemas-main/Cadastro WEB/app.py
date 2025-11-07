from flask import Flask, request, redirect, render_template, send_from_directory
import sqlite3

app = Flask(__name__, template_folder='.')
DB_NAME = 'banco.db'

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = conectar()
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template('cadastro.html', usuarios=usuarios)

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = (
        request.form['nome'],
        request.form['email'],
        request.form['endereco'],
        request.form['bairro'],
        request.form['cidade'],
        request.form['cpf'],
        request.form['senha']
    )
    conn = conectar()
    conn.execute('''
        INSERT INTO usuarios (nome, email, endereco, bairro, cidade, cpf, senha)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', dados)
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/initdb')
def initdb():
    conn = conectar()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            endereco TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
    return 'Banco de dados criado com sucesso!'

@app.route('/pagina/<path:filename>')
def pagina_static(filename):
    return send_from_directory('pagina', filename)

if __name__ == '__main__':
    app.run(debug=True)