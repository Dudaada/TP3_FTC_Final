class AFD:
    def __init__(self):
        self.estados = [] # Conjunto de estados (Q)
        self.estado_inicial = "" # Estado inicial 
        self.estados_finais = [] # Conjunto de estados de aceitação (F)
        self.transicoes = []  # Função de transição armazenada como uma lista de dicionários

class AFND(AFD):
    # Classe que representa um Autômato Finito Não Determinístico, estendendo o AFD
    def __init__(self):
        super().__init__() # Inicializa os atributos da classe base
        self.estados_iniciais = [] # Caso de multiplos estados iniciais, mantemos uma lista separada
        self.alfabeto_entrada = [] # Alfabeto de entrada, que pode ser customizado via tag S:

class AP(AFND):
    # Classe que representa um Autômato de Pilha, estendendo o AFND
    def __init__(self):
        super().__init__() # Inicializa os atributos da classe base
        self.alfabeto_pilha = [] # Alfabeto da pilha, lido via tag G:

def ler_configuracao_afd(caminho_arquivo):
    # Função para ler o arquivo texto e construir o autômato apropriado
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines() # Lê todas as linhas do arquivo texto

    iterador_linhas = iter(linhas) # Cria um iterador para avançar pelas linhas sequencialmente
    
    # Variáveis temporárias para armazenar os componentes da quíntupla/sêxtupla antes de instanciar a classe
    estados = []
    estados_iniciais = []
    estados_finais = []
    alfabeto_entrada = None
    alfabeto_pilha = None
    transicoes_raw = [] # Armazenará as strings cruas das transições para processamento posterior

    try:
        linha = next(iterador_linhas).strip() # Pega a primeira linha removendo espaços em branco
    except StopIteration:
        return None, [] # Se o arquivo estiver vazio, retorna None
        
    while linha != "---": # O delimitador '---' separa a definição da máquina dos casos de teste
        if not linha:
            # Se a linha for vazia (apenas quebra de linha), pula para a próxima
            linha = next(iterador_linhas).strip()
            continue

        if linha.startswith("Q:"):
            # Lendo a definição dos estados (Q) separados por espaço
            estados = linha[2:].strip().split()
        elif linha.startswith("S:"):
            # Lendo o alfabeto de entrada (Σ). Exemplo: S: abc
            str_alfabeto = linha[2:]
            if str_alfabeto.startswith(" "):
                str_alfabeto = str_alfabeto[1:] # Tira o primeiro espaço que apenas separa os dois pontos dos caracteres
            alfabeto_entrada = list(str_alfabeto) # Cada caractere restante se torna um símbolo do alfabeto
        elif linha.startswith("G:"):
            # Lendo o alfabeto da pilha (Γ) para Autômatos de Pilha. Exemplo: G: XY
            str_pilha = linha[2:]
            if str_pilha.startswith(" "):
                str_pilha = str_pilha[1:] # Tira o primeiro espaço após os dois pontos
            alfabeto_pilha = list(str_pilha) # Transforma a string em uma lista de caracteres
        elif linha.startswith("I:"):
            # Lendo o estado inicial (ou múltiplos estados iniciais para AFND)
            estados_iniciais = linha[2:].strip().split()
        elif linha.startswith("F:"):
            # Lendo os estados de aceitação (F)
            estados_finais = linha[2:].strip().split()
        elif "->" in linha:
            # Se tiver '->' é uma regra da função de transição, salva cru para parsear depois
            transicoes_raw.append(linha)
            
        try:
            linha = next(iterador_linhas).strip() # Avança para a próxima linha do laço
        except StopIteration:
            break # Fim do arquivo encontrado precocemente

    if alfabeto_entrada is None:
        # Padrão da especificação caso não exista a chave S: (o alfabeto default é apenas 0 e 1)
        alfabeto_entrada = ['0', '1']

    # Lógica para descobrir qual classe instanciar baseada na leitura
    is_ap = alfabeto_pilha is not None # Se tem G:, é um Autômato de Pilha
    # Se tem mais de 1 estado inicial ou se alguma transição possui a contrabarra (lambda/epsilon), é AFND
    is_afnd = len(estados_iniciais) > 1 or any('\\' in tr for tr in transicoes_raw)
    
    if is_ap:
        afd = AP() # Instancia o Autômato de Pilha
        afd.alfabeto_pilha = alfabeto_pilha # Configura o alfabeto da pilha
        afd.estados_iniciais = estados_iniciais # Configura estados iniciais
        afd.alfabeto_entrada = alfabeto_entrada # Configura alfabeto de entrada
    elif is_afnd:
        afd = AFND() # Instancia Autômato Finito Não Determinístico
        afd.estados_iniciais = estados_iniciais # Configura estados iniciais
        afd.alfabeto_entrada = alfabeto_entrada # Configura alfabeto de entrada
    else:
        afd = AFD() # Instancia o AFD clássico
        # AFD clássico tem apenas um estado inicial por definição (Sipser)
        afd.estado_inicial = estados_iniciais[0] if estados_iniciais else ""
        afd.estados_iniciais = estados_iniciais # Mantém a lista também para compatibilidade
        afd.alfabeto_entrada = alfabeto_entrada # Configura alfabeto de entrada

    afd.estados = estados # Associa o conjunto Q lido
    afd.estados_finais = estados_finais # Associa o conjunto F lido

    # Processamento refinado da função de transição (δ)
    for linha_limpa in transicoes_raw:
        partes = linha_limpa.split("->") # Separa a origem do resto da transição
        origem = partes[0].strip() # Isola o estado de origem
        
        resto = partes[1].strip().split() # Pega o estado de destino e os símbolos transitados
        if len(resto) >= 2:
            destino = resto[0] # O primeiro token da segunda metade é sempre o estado de destino
            elementos_restantes = resto[1:] # O que sobra são as definições do que engatilha a transição
            
            if isinstance(afd, AP):
                # Formato da transição do AP: a,b/z (consome a, pop b, push z)
                for elem in elementos_restantes:
                    if ',' in elem and '/' in elem:
                        partes_elem = elem.split(',') # Separa o símbolo de entrada das ações da pilha
                        simbolo_entrada = partes_elem[0] # 'a'
                        resto_elem = partes_elem[1].split('/') # Separa a ação de pop da ação de push
                        simbolo_pop = resto_elem[0] # 'b' (o que tirar do topo)
                        simbolo_push = resto_elem[1] # 'z' (o que colocar no topo)
                        
                        afd.transicoes.append({
                            "origem": origem, # De onde sai
                            "destino": destino, # Pra onde vai
                            "simbolo": simbolo_entrada, # Símbolo consumido da fita
                            "pop": simbolo_pop, # Retirado do topo
                            "push": simbolo_push # Empurrado na pilha
                        })
            else:
                # AF e AFND: Símbolos são apenas caracteres
                for simbolo in elementos_restantes:
                    if simbolo == '|': continue # A barra pipe é opcional na sintaxe para fins estéticos, ignoramos ela
                    afd.transicoes.append({
                        "origem": origem, # De onde sai
                        "simbolo": simbolo, # Símbolo consumido
                        "destino": destino # Pra onde vai
                    })

    # Coleta todas as palavras teste que existem abaixo da linha delimitadora "---"
    linhas_de_teste = [linha.replace("\n", "") for list_linha in iterador_linhas if (linha := list_linha)]
    
    return afd, linhas_de_teste # Retorna o autômato criado em memória e a lista de palavras para testar