from flask import Flask, request, redirect, render_template, send_from_directory, flash
from werkzeug.security import generate_password_hash
import sqlite3
import os

app = Flask(__name__, template_folder='.')
app.secret_key = 'biblioteca-secreta'
DB_NAME = 'banco.db'

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = conectar()
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    livros = conn.execute('SELECT * FROM livros').fetchall()
    conn.close()
    return render_template('cadastro.html', usuarios=usuarios, livros=livros)

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    try:
        dados = (
            request.form['nome'],
            request.form['email'],
            request.form.get('telefone', ''),
            request.form['cpf'],
            generate_password_hash(request.form['senha'])
        )
        conn = conectar()
        conn.execute('''
            INSERT INTO usuarios (nome, email, telefone, cpf, senha)
            VALUES (?, ?, ?, ?, ?)
        ''', dados)
        conn.commit()
        conn.close()
        flash('✅ Usuário cadastrado com sucesso!')
    except sqlite3.IntegrityError:
        flash('⚠️ Erro: CPF já cadastrado.')
    return redirect('/')

@app.route('/cadastrar_livro', methods=['POST'])
def cadastrar_livro():
    dados = (
        request.form['titulo'],
        request.form['autor'],
        request.form.get('isbn', ''),
        int(request.form['quantidade']),
        int(request.form['quantidade'])  # disponíveis = quantidade inicial
    )
    conn = conectar()
    conn.execute('''
        INSERT INTO livros (titulo, autor, isbn, quantidade, disponiveis)
        VALUES (?, ?, ?, ?, ?)
    ''', dados)
    conn.commit()
    conn.close()
    flash('📚 Livro cadastrado com sucesso!')
    return redirect('/')

@app.route('/emprestar', methods=['POST'])
def emprestar():
    usuario_id = request.form['usuario_id']
    livro_id = request.form['livro_id']
    data_prevista = request.form['data_prevista']

    conn = conectar()
    livro = conn.execute('SELECT disponiveis FROM livros WHERE id = ?', (livro_id,)).fetchone()
    if livro and livro['disponiveis'] > 0:
        conn.execute('''
            INSERT INTO emprestimos (usuario_id, livro_id, data_prevista)
            VALUES (?, ?, ?)
        ''', (usuario_id, livro_id, data_prevista))
        conn.execute('''
            UPDATE livros SET disponiveis = disponiveis - 1 WHERE id = ?
        ''', (livro_id,))
        conn.commit()
        flash('📖 Empréstimo registrado com sucesso!')
    else:
        flash('❌ Livro indisponível para empréstimo.')
    conn.close()
    return redirect('/')

@app.route('/devolver', methods=['POST'])
def devolver():
    livro_id = request.form['livro_id']
    conn = conectar()
    conn.execute('''
        UPDATE livros SET disponiveis = disponiveis + 1 WHERE id = ?
    ''', (livro_id,))
    conn.commit()
    conn.close()
    flash('✅ Livro devolvido com sucesso!')
    return redirect('/')

@app.route('/initdb')
def initdb():
    conn = conectar()
    conn.executescript(open('schema.sql', encoding='utf-8').read())
    conn.commit()
    conn.close()
    return '📦 Banco de dados criado com sucesso!'

@app.route('/pagina/<path:filename>')
def pagina_static(filename):
    return send_from_directory('pagina', filename)

@app.route('/img/<path:filename>')
def img_static(filename):
    return send_from_directory('img', filename)

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        with app.app_context():
            initdb()
    app.run(debug=True)