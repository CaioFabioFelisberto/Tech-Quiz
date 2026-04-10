from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time


load_dotenv()

def get_db():
    try:
        client = MongoClient(os.getenv("CLIENT"))
        db = client[os.getenv("DB_NAME")]
        collection = db[os.getenv("COLLECTION_NAME")]
        return collection
    except Exception as e:
        return None

collection = get_db()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

@app.route("/<int:questao_id>", methods=["GET", "POST"])
def index(questao_id):
    
    questao_atual = collection.find_one({"id": questao_id})

    if questao_atual is None:
        return render_template("resultado.html", resultado="Erro ao conectar ao banco de dados.")

    if 'erros' not in session:
        session['erros'] = 0

    if 'perguntas_erradas' not  in session:
        session['perguntas_erradas'] = []
    
    if 'tempo_inicio' not in session:
        session['tempo_inicio'] = time.time()

    if request.method == "GET":
        return render_template("index.html", questao=questao_atual)
    
    if request.method == "POST":
        resposta_usuario = request.form.get("resposta")
        
        if resposta_usuario == questao_atual["correta"]:
            proxima_questao = questao_id + 1
            total_perguntas = collection.count_documents({})

            if proxima_questao > total_perguntas:
                erros_finais = session['erros']
                perguntas_erradas_finais = session['perguntas_erradas']
                inicio = session['tempo_inicio']

                fim = time.time()
                tempo_gasto = round(fim - inicio, 2)

                session.clear()

                if erros_finais == 0:
                    return render_template("resultado.html", resultado="🎉 Parabéns! Você completou o quiz, sem nenhum erro!", erros=None,tempo_gasto=tempo_gasto, perguntas_erradas=None)
                else:
                    return render_template("resultado.html", resultado="Quiz finalizado!", erros=erros_finais, tempo_gasto=tempo_gasto, perguntas_erradas=perguntas_erradas_finais)
            return redirect(url_for('index', questao_id=proxima_questao))
        else:
            texto_da_questao = questao_atual["pergunta"]
            if texto_da_questao not in session['perguntas_erradas']:
                session['perguntas_erradas'].append(texto_da_questao)
                session.modified = True 
            session['erros'] += 1
            return render_template("index.html", questao=questao_atual, erro="Resposta incorreta. Tente novamente!")

if __name__ == "__main__":
    app.run(debug=True) 
    