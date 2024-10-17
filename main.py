from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Substitua pela sua chave secreta

def conectar_banco():
    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        laboratorio TEXT,
        curso TEXT,
        disciplina TEXT,
        data TEXT,
        hora_inicio TEXT,
        hora_fim TEXT
    )
    ''')
    conn.commit()
    return conn, cursor

def validar_hora(hora_str):
    try:
        datetime.strptime(hora_str, "%H:%M")
        return True
    except ValueError:
        return False

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('agendar'))
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        professor = request.form.get('professor')
        laboratorio = request.form['laboratorio']
        curso = request.form['curso']
        disciplina = request.form['disciplina']
        data_str = request.form['data']  # data no formato YYYY-MM-DD
        hora_inicio = request.form['hora_inicio']
        hora_fim = request.form['hora_fim']

        # Verificação da data
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").strftime("%Y-%m-%d")  # Confirmando o formato correto
        except ValueError:
            flash('Data inválida. Por favor, insira a data no formato AAAA-MM-DD.')
            return redirect(url_for('agendar'))

        # Validação das horas
        if not validar_hora(hora_inicio) or not validar_hora(hora_fim):
            flash('Horas inválidas. Por favor, insira no formato HH:MM.')
            return redirect(url_for('agendar'))

        conn, cursor = conectar_banco()

        # Verifica se já existe um agendamento para o mesmo laboratório, data e horário
        cursor.execute('''
            SELECT * FROM agendamentos WHERE laboratorio = ? AND data = ? AND 
            ((hora_inicio <= ? AND hora_fim > ?) OR (hora_inicio < ? AND hora_fim >= ?))
        ''', (laboratorio, data, hora_inicio, hora_inicio, hora_fim, hora_fim))

        if cursor.fetchone():
            flash('Conflito de agendamento: já existe um agendamento para esse laboratório nessa data e horário.')
            conn.close()
            return redirect(url_for('agendar'))

        # Insere o novo agendamento
        try:
            cursor.execute('''INSERT INTO agendamentos (professor, laboratorio, curso, disciplina, data, hora_inicio, hora_fim)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (professor, laboratorio, curso, disciplina, data, hora_inicio, hora_fim))
            conn.commit()
            flash('Agendamento realizado com sucesso!')
        except Exception as e:
            flash(f'Erro ao inserir agendamento: {str(e)}')
        finally:
            conn.close()

        return redirect(url_for('ver_agendamentos'))

    laboratorios = ['Laboratório 1', 'Laboratório 2', 'Laboratório 3']
    return render_template('agendar.html', laboratorios=laboratorios)

@app.route('/visualizar')
def visualizar():
    conn, cursor = conectar_banco()
    cursor.execute("SELECT professor, laboratorio, curso, disciplina, data, hora_inicio, hora_fim FROM agendamentos")
    agendamentos = cursor.fetchall()
    conn.close()
    return render_template('visualizar.html', agendamentos=agendamentos)

@app.route('/ver_agendamentos')
def ver_agendamentos():
    conn, cursor = conectar_banco()
    cursor.execute("SELECT professor, laboratorio, curso, disciplina, data, hora_inicio, hora_fim FROM agendamentos")
    agendamentos = cursor.fetchall()
    conn.close()

    # Formatação das datas e horários no padrão sul-americano
    for i in range(len(agendamentos)):
        try:
            data_formatada = datetime.strptime(agendamentos[i][4], "%Y-%m-%d").strftime("%d/%m/%Y")  # 4 é o índice da data
            hora_inicio_formatada = datetime.strptime(agendamentos[i][5], "%H:%M").strftime("%H:%M")  # 5 é o índice da hora de início
            hora_fim_formatada = datetime.strptime(agendamentos[i][6], "%H:%M").strftime("%H:%M")  # 6 é o índice da hora de fim
            agendamentos[i] = (agendamentos[i][0], agendamentos[i][1], agendamentos[i][2], agendamentos[i][3], data_formatada, hora_inicio_formatada, hora_fim_formatada)
        except ValueError:
            agendamentos[i] = (agendamentos[i][0], agendamentos[i][1], agendamentos[i][2], agendamentos[i][3], "Data inválida", "Hora inválida", "Hora inválida")

    return render_template('ver_agendamentos.html', agendamentos=agendamentos)

if __name__ == '__main__':
    app.run(debug=True)
