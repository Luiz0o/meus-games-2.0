import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from supabase import create_client, Client
from collections import Counter
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================== ROTAS DA APLICAÇÃO ====================

@app.route('/')
def index():
    try:
        # Busca todos os jogos para calcular as estatísticas da Home
        response = supabase.table("games").select("status_platinado, rating").execute()
        jogos = response.data
        
        total_jogos = len(jogos)
        total_platinados = sum(1 for j in jogos if j.get('status_platinado') == True)
        
        if total_jogos > 0:
            soma_notas = sum(j.get('rating', 0) for j in jogos)
            media_notas = round(soma_notas / total_jogos, 1)
        else:
            media_notas = None

        return render_template(
            'index.html', 
            total_jogos=total_jogos, 
            total_platinados=total_platinados, 
            media_notas=media_notas
        )
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        return render_template('index.html', total_jogos=0, total_platinados=0, media_notas=None)


@app.route('/jogos')
def listagem():
    try:
        # Busca todos os jogos cadastrados na tabela 'games' ordenados pelo título
        response = supabase.table("games").select("*").order("title").execute()
        jogos = response.data  # Captura a lista de registros retornada pelo Supabase
        
        return render_template('listagem.html', jogos=jogos)
    except Exception as e:
        flash(f"Erro ao carregar a biblioteca de jogos: {e}", "danger")
        return render_template('listagem.html', jogos=[])


@app.route('/jogos/novo')
def novo_jogo():
    return render_template('cadastro.html')


@app.route('/jogos/salvar', methods=['POST'])
def salvar_jogo():
    try:
        # 1. Captura os dados de texto do formulário
        title = request.form.get('title')
        platform = request.form.get('platform')
        rating = int(request.form.get('rating', 0))
        notes = request.form.get('notes')

        # 2. Captura e trata os campos de checkbox (retornam 'on' se marcados)
        status_zerado = True if request.form.get('status_zerado') == 'on' else False
        status_platinado = True if request.form.get('status_platinado') == 'on' else False
        status_100 = True if request.form.get('status_100') == 'on' else False

        # 3. Trata o upload da imagem da capa
        cover_file = request.files.get('cover')
        cover_url = None

        if cover_file and cover_file.filename != '':
            filename = secure_filename(cover_file.filename)
            file_data = cover_file.read()
            
            # Faz o upload do arquivo binário direto para o Storage do Supabase
            supabase.storage.from_("game-covers").upload(
                path=filename,
                file=file_data,
                file_options={"content-type": cover_file.content_type}
            )
            
            # Monta a URL pública para acessar a imagem depois
            cover_url = f"{SUPABASE_URL}/storage/v1/object/public/game-covers/{filename}"

        # 4. Cria o dicionário com os dados exatamente como as colunas do banco
        novo_jogo_dados = {
            "title": title,
            "platform": platform,
            "status_zerado": status_zerado,
            "status_platinado": status_platinado,
            "status_100": status_100,
            "rating": rating,
            "notes": notes,
            "cover_url": cover_url
        }

        # 5. Insere os dados na tabela 'games' do Supabase
        supabase.table("games").insert(novo_jogo_dados).execute()

        flash("Jogo adicionado com sucesso!", "success")
        return redirect(url_for('listagem'))

    except Exception as e:
        flash(f"Erro ao salvar o jogo: {e}", "danger")
        return redirect(url_for('novo_jogo'))


@app.route('/estatisticas')
def estatisticas():
    try:
        # Busca todos os campos necessários da tabela 'games'
        response = supabase.table("games").select("platform, status_platinado, status_zerado, status_100, rating, created_at").execute()
        jogos = response.data
        
        total = len(jogos)
        platinados = sum(1 for j in jogos if j.get('status_platinado') is True)
        zerados = sum(1 for j in jogos if j.get('status_zerado') is True)
        status_100 = sum(1 for j in jogos if j.get('status_100') is True)
        
        # Média de Avaliação
        if total > 0:
            soma_notas = sum(j.get('rating', 0) for j in jogos)
            media_notas = round(soma_notas / total, 1)
        else:
            media_notas = 0.0

        # 1. Dados para Gráfico de Distribuição por Plataforma
        contagem_plataformas = Counter(j.get('platform', 'Outros') for j in jogos)
        plataformas_labels = list(contagem_plataformas.keys())
        plataformas_valores = list(contagem_plataformas.values())

        # 2. Dados para Gráfico de Avaliação (Contadores de 1 a 5 estrelas)
        contagem_notas = Counter(j.get('rating', 0) for j in jogos)
        notas_valores = [contagem_notas[i] for i in range(1, 6)]

        # 3. Dados para Gráfico de Evolução por Mês (Formatado como YYYY-MM)
        historico_meses = {}
        for j in jogos:
            data_str = j.get('created_at')
            if data_str:
                try:
                    ano_mes = data_str[:7] # Extrai 'YYYY-MM'
                    historico_meses[ano_mes] = historico_meses.get(ano_mes, 0) + 1
                except Exception:
                    pass
        
        meses_ordenados = sorted(historico_meses.keys())
        meses_valores = [historico_meses[m] for m in meses_ordenados]

        return render_template(
            'estatisticas.html',
            total=total,
            platinados=platinados,
            zerados=zerados,
            status_100=status_100,
            media_notas=media_notas,
            plataformas_labels=plataformas_labels,
            plataformas_valores=plataformas_valores,
            notas_valores=notas_valores,
            meses_labels=meses_ordenados,
            meses_valores=meses_valores
        )
    except Exception as e:
        flash(f"Erro ao carregar o dashboard analítico: {e}", "danger")
        return redirect(url_for('index'))


@app.route('/jogo/<jogo_id>')
def visualizar_jogo(jogo_id):
    try:
        # Busca apenas o jogo correspondente ao ID informado
        response = supabase.table("games").select("*").eq("id", jogo_id).execute()
        
        if not response.data:
            flash("Jogo não encontrado!", "warning")
            return redirect(url_for('listagem'))
            
        jogo = response.data[0]
        
        # Mapeamento opcional de texto baseado na nota para exibir abaixo das estrelas
        textos_avaliacao = {5: "Excelente", 4: "Muito Bom", 3: "Bom", 2: "Regular", 1: "Ruim"}
        nota_texto = textos_avaliacao.get(int(jogo.get('rating', 0)), "Não avaliado")

        return render_template('detalhes.html', jogo=jogo, nota_texto=nota_texto)
        
    except Exception as e:
        flash(f"Erro ao carregar os detalhes do jogo: {e}", "danger")
        return redirect(url_for('listagem'))

    
@app.route('/jogo/editar/<jogo_id>', methods=['GET'])
def editar_jogo(jogo_id):
    try:
        # Busca os dados atuais do jogo no banco
        response = supabase.table("games").select("*").eq("id", jogo_id).execute()
        
        if not response.data:
            flash("Jogo não encontrado para edição!", "warning")
            return redirect(url_for('listagem'))
            
        jogo = response.data[0]
        return render_template('editar.html', jogo=jogo)
        
    except Exception as e:
        flash(f"Erro ao carregar o formulário de edição: {e}", "danger")
        return redirect(url_for('listagem'))


# CORREÇÃO AQUI: Mudança de nome e rota de POST para evitar colisão de funções
@app.route('/jogo/atualizar/<jogo_id>', methods=['POST'])
def atualizar_jogo(jogo_id):
    try:
        # Captura os dados vindos do formulário
        title = request.form.get('title')
        platform = request.form.get('platform')
        rating = int(request.form.get('rating', 0))
        notes = request.form.get('notes')
        
        # Captura os checkboxes (se não marcados, o navegador não envia, então tratamos como False)
        status_zerado = True if request.form.get('status_zerado') else False
        status_platinado = True if request.form.get('status_platinado') else False
        status_100 = True if request.form.get('status_100') else False

        # Monta o dicionário de atualização
        dados_atualizados = {
            "title": title,
            "platform": platform,
            "rating": rating,
            "notes": notes,
            "status_zerado": status_zerado,
            "status_platinado": status_platinado,
            "status_100": status_100
        }

        # Processamento de nova imagem de capa na Edição
        file = request.files.get('cover')
        if file and file.filename != '':
            filename = secure_filename(f"{int(datetime.timestamp(datetime.now()))}_{file.filename}")
            file_data = file.read()
            
            # Upload para o storage
            supabase.storage.from_("game-covers").upload(
                path=filename,
                file=file_data,
                file_options={"content-type": file.content_type}
            )
            # Atualiza a chave no dicionário que vai para o banco
            dados_atualizados["cover_url"] = f"{SUPABASE_URL}/storage/v1/object/public/game-covers/{filename}"

        # Atualiza o registro no Supabase filtrando pelo ID
        supabase.table("games").update(dados_atualizados).eq("id", jogo_id).execute()
        
        flash(f"Jogo '{title}' atualizado com sucesso!", "success")
        return redirect(url_for('visualizar_jogo', jogo_id=jogo_id))
        
    except Exception as e:
        flash(f"Erro ao salvar as alterações do jogo: {e}", "danger")
        return redirect(url_for('editar_jogo', jogo_id=jogo_id))

@app.route('/jogo/excluir/<jogo_id>', methods=['POST'])
def excluir_jogo(jogo_id):
    try:
        # Busca o jogo primeiro para sabermos o título (opcional, para a mensagem de flash)
        game_res = supabase.table("games").select("title, cover_url").eq("id", jogo_id).execute()
        if game_res.data:
            title = game_res.data[0].get('title')
            
            # Opcional: Se quiser apagar a foto do Storage do Supabase para não acumular lixo
            cover_url = game_res.data[0].get('cover_url')
            if cover_url:
                filename = cover_url.split('/')[-1]
                try:
                    supabase.storage.from_("game-covers").remove([filename])
                except Exception:
                    pass # Evita travar a exclusão se o arquivo não existir no storage
            
            # Deleta o registro da tabela
            supabase.table("games").delete().eq("id", jogo_id).execute()
            flash(f"Jogo '{title}' excluído com sucesso!", "success")
        
        return redirect(url_for('listagem'))
    except Exception as e:
        flash(f"Erro ao excluir o jogo: {e}", "danger")
        return redirect(url_for('listagem'))


if __name__ == '__main__':
    # O host="0.0.0.0" permite que seu celular encontre o computador
    app.run(host="0.0.0.0", port=5000, debug=True)