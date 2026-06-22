from flask import Flask, render_template, request, jsonify
import tempfile
import os

from leitor import ler_configuracao_afd, MT
from motor import criar_mapa_transicoes, processar_palavra

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files', methods=['GET'])
def get_files():
    # Escaneia a raiz do projeto procurando arquivos de casos de teste para alimentar o seletor do Frontend
    arquivos = [f for f in os.listdir('.') if f.endswith('.txt') and f != 'requirements.txt']
    return jsonify({'files': arquivos})

@app.route('/api/file/<filename>', methods=['GET'])
def get_file_content(filename):
    if not filename.endswith('.txt') or '..' in filename:
        return jsonify({'erro': 'Arquivo inválido'}), 400
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Quebra o arquivo em duas metades: as regras da máquina (cima) e as palavras a serem validadas (baixo)
        partes = conteudo.split('---')
        automato = partes[0].strip() if len(partes) > 0 else ''
        testes = partes[1].strip() if len(partes) > 1 else ''
        
        return jsonify({'automato': automato, 'testes': testes})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/simular', methods=['POST'])
def simular():
    data = request.json
    automato_config = data.get('automato', '')
    testes_config = data.get('testes', '')
    
    # Remonta o arquivo texto em formato string para manter compatibilidade com a sintaxe original
    conteudo_completo = f"{automato_config.strip()}\n---\n{testes_config.strip()}"
    
    resultados = []
    
    # Precisamos salvar o conteúdo fisicamente num tempfile, pois o 'ler_configuracao_afd' 
    # foi desenhado no projeto base para operar com paths de arquivos no disco.
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp:
        tmp.write(conteudo_completo)
        caminho_tmp = tmp.name
        
    try:
        afd, palavras_teste = ler_configuracao_afd(caminho_tmp)
        
        if afd is None:
            return jsonify({'erro': 'Arquivo de configuração vazio ou inválido.'}), 400
            
        # Transforma as transições lidas em um dicionário de busca em O(1) usando as funções do motor.py
        mapa_transicoes = criar_mapa_transicoes(afd)
        
        # Passa cada palavra para simulação, da mesma forma que o main.py original atua no CLI
        for palavra in palavras_teste:
            try:
                resultado = processar_palavra(afd, mapa_transicoes, palavra)
                is_mt = isinstance(afd, MT)
                
                if is_mt:
                    aceita, conteudo_fita = resultado
                    resultados.append({
                        'palavra': palavra if palavra != "" else "[Palavra Vazia]",
                        'aceita': aceita,
                        'fita': conteudo_fita,
                        'tipo': 'MT/ALL'
                    })
                else:
                    resultados.append({
                        'palavra': palavra if palavra != "" else "[Palavra Vazia]",
                        'aceita': bool(resultado),
                        'fita': None,
                        'tipo': 'AFD/AFND/AP'
                    })
            except Exception as e:
                resultados.append({
                    'palavra': palavra if palavra != "" else "[Palavra Vazia]",
                    'aceita': False,
                    'fita': None,
                    'erro': str(e),
                    'tipo': 'Erro'
                })
                
    except Exception as e:
        return jsonify({'erro': f'Erro fatal ao simular: {str(e)}'}), 500
    finally:
        os.remove(caminho_tmp)
        
    return jsonify({'resultados': resultados})

if __name__ == '__main__':
    app.run(debug=True)
