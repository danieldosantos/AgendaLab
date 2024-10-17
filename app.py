from flask import Flask, request, render_template, redirect, url_for, flash
import json
import os
from datetime import datetime  # Importa o datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Substitua pela sua chave secreta


# Função para carregar dados do arquivo JSON
def carregar_dados():
    if not os.path.exists('data.json'):
        print("Arquivo data.json não encontrado. Criando um novo arquivo.")
        return []  # Retorna uma lista vazia se o arquivo não existir
    with open('data.json', 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("Erro ao carregar data.json. O arquivo está corrompido.")
            return []  # Retorna uma lista vazia se o arquivo estiver corrompido


# Função para salvar dados no arquivo JSON
def salvar_dados(novo_agendamento):
    # Carregar os agendamentos existentes
    agendamentos = carregar_dados()

    # Adicionar o novo agendamento à lista
    agendamentos.append(novo_agendamento)

    # Salvar a lista atualizada no arquivo
    with open('data.json', 'w') as file:
        json.dump(agendamentos, file, indent=4)
        print("Dados salvos no arquivo data.json:", agendamentos)


@app.route('/')
def home():
    return redirect(url_for('agendar'))  # Redireciona para a página de agendamento


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        # Coletar dados do formulário
        professor = request.form.get('professor')
        laboratorio = request.form['laboratorio']
        curso = request.form['curso']
        disciplina = request.form['disciplina']
        data = request.form['data']
        periodo = request.form['periodo']  # Captura o período selecionado (manhã, tarde, noite)

        # Carregar dados existentes
        agendamentos = carregar_dados()
        print("Agendamentos existentes antes de adicionar:", agendamentos)

        # Verifica se já existe um agendamento para o mesmo laboratório na mesma data e período
        for agendamento in agendamentos:
            if (agendamento['laboratorio'] == laboratorio and
                    agendamento['data'] == data and
                    agendamento['periodo'] == periodo):
                # Formatar a data para DD/MM/AAAA
                data_formatada = datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
                flash(
                    f'O laboratório "{laboratorio}" já está reservado no dia {data_formatada} para o período "{periodo}".')
                return redirect(url_for('agendar'))

        # Adicionar novo agendamento
        novo_agendamento = {
            "professor": professor,
            "laboratorio": laboratorio,
            "curso": curso,
            "disciplina": disciplina,
            "data": data,
            "periodo": periodo  # Inclui o período no novo agendamento
        }
        print("Novo agendamento adicionado:", novo_agendamento)

        # Salvar dados atualizados com o novo agendamento
        salvar_dados(novo_agendamento)

        flash('Agendamento realizado com sucesso!')
        return redirect(url_for('ver_agendamentos'))

    # Lista de laboratórios disponíveis
    laboratorios = ['Laboratório 1', 'Laboratório 2', 'Laboratório 3']
    return render_template('agendar.html', laboratorios=laboratorios)


@app.route('/ver_agendamentos')
def ver_agendamentos():
    # Carregar os agendamentos do arquivo JSON
    agendamentos = carregar_dados()
    print("Agendamentos carregados para visualização:", agendamentos)

    # Formatar as datas para o formato sul-americano
    for agendamento in agendamentos:
        agendamento['data'] = datetime.strptime(agendamento['data'], '%Y-%m-%d').strftime('%d/%m/%Y')

    return render_template('ver_agendamentos.html', agendamentos=agendamentos)


if __name__ == '__main__':
    app.run(debug=True)
