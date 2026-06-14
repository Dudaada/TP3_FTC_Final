class AFD:
    def __init__(self):
        self.estados = []
        self.estado_inicial = ""
        self.estados_finais = []
        self.transicoes = []  # Lista de dicionários/tuplas contendo (origem, simbolo, destino)

def ler_configuracao_afd(caminho_arquivo) -> tuple[AFD, list]:
    afd = AFD()
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()

    # Iterador para percorrer as linhas do arquivo
    iterador_linhas = iter(linhas)
    
    # 1. LER ESTADOS (Q:)
    linha_q = next(iterador_linhas).strip()
    if linha_q.startswith("Q:"):
        # Pula "Q:" e quebra o restante pelos espaços
        afd.estados = linha_q[2:].strip().split()

    # 2. LER ESTADO INICIAL (I:)
    linha_i = next(iterador_linhas).strip()
    if linha_i.startswith("I:"):
        afd.estado_inicial = linha_i[2:].strip()

    # 3. LER ESTADOS FINAIS (F:)
    linha_f = next(iterador_linhas).strip()
    if linha_f.startswith("F:"):
        afd.estados_finais = linha_f[2:].strip().split()

    # 4. LER FUNÇÃO DE TRANSIÇÃO (Até achar "---")
    for linha in iterador_linhas:
        linha_limpa = linha.strip()
        
        if linha_limpa == "---":
            break
            
        if not linha_limpa:
            continue

        if "->" in linha_limpa:
            partes = linha_limpa.split("->")
            origem = partes[0].strip()
            
            resto = partes[1].strip().split()
            if len(resto) >= 2:
                destino = resto[0]
                
                # Pega o restante dos elementos pulando o destino
                elementos_restantes = resto[1:] 
                
                # Filtra para salvar APENAS os símbolos '0' e '1', ignorando a barra '|'
                simbolos = [s for s in elementos_restantes if s in ('0', '1')]
                
                for simbolo in simbolos:
                    afd.transicoes.append({
                        "origem": origem,
                        "simbolo": simbolo,
                        "destino": destino
                    })

    linhas_de_teste = [linha.replace("\n", "") for list_linha in iterador_linhas if (linha := list_linha)]
    
    return afd, linhas_de_teste