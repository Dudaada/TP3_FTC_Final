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

class MT(AFND):
    # Classe que representa uma Máquina de Turing / Autômato Linearmente Limitado (ALL), estendendo o AFND
    # Herda de AFND pois a MT também pode, em tese, ter múltiplos estados iniciais e transições lambda,
    # além de reaproveitar o atributo 'alfabeto_entrada' já existente na classe base.
    def __init__(self):
        super().__init__() # Inicializa os atributos da classe base
        self.alfabeto_fita = [] # Símbolos exclusivos do alfabeto da fita (Γ \ Σ), lidos via tag G:

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
    alfabeto_fita = None
    transicoes_raw = [] # Armazenará as strings cruas das transições para processamento posterior
    tipo_forcado = None # Extra 5: caso a entrada comece com @AF, @AP ou @ALL/@MT, guarda aqui o tipo escolhido

    try:
        linha = next(iterador_linhas).strip() # Pega a primeira linha removendo espaços em branco
    except StopIteration:
        return None, [] # Se o arquivo estiver vazio, retorna None

    if linha.startswith("@"):
        # Extra 5 (Múltiplos tipos): a primeira linha do arquivo pode indicar explicitamente
        # qual tipo de autômato será descrito, dispensando a heurística de detecção automática.
        tipo_forcado = linha[1:].strip().upper() # Remove o '@' e normaliza (ex.: 'AF', 'AP', 'ALL', 'MT')
        try:
            linha = next(iterador_linhas).strip() # Avança para a linha seguinte (início da definição de fato)
        except StopIteration:
            return None, [] # Arquivo só com a tag @TIPO e nada mais é inválido
        
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
            # Lendo o alfabeto extra (Γ), usado tanto pelo AP (alfabeto da pilha) quanto pela MT/ALL (alfabeto da fita).
            # A decisão de para qual dos dois esse conteúdo se destina é feita mais adiante, com base no tipo da máquina.
            str_g = linha[2:]
            if str_g.startswith(" "):
                str_g = str_g[1:] # Tira o primeiro espaço após os dois pontos
            alfabeto_pilha = list(str_g) # Mantém o nome original 'alfabeto_pilha' para não alterar o AP já pronto
            alfabeto_fita = list(str_g) # Mesma leitura, guardada também sob o nome usado pela MT/ALL
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

    # Extra 4 (MT/ALL): uma transição de MT é escrita como 'a/bd' (lê a, escreve b, anda d), sem vírgula e sem
    # o '|' antes da lista — diferente do AF/AFND ('-> destino | s1 s2') e do AP ('-> destino | a,b/z').
    # Detectamos isso varrendo o lado direito de cada transição crua em busca de um elemento no formato 'x/yz'
    # que não contenha vírgula (a vírgula é exclusiva da sintaxe do AP).
    def _parece_transicao_mt(linha_crua):
        resto = linha_crua.split("->")[1].strip().split()[1:] # Ignora o destino, sobra só os símbolos/regras
        for elem in resto:
            if elem == '|':
                continue
            if '/' in elem and ',' not in elem:
                return True
        return False
    tem_transicao_mt = any(_parece_transicao_mt(tr) for tr in transicoes_raw)

    # Lógica para descobrir qual classe instanciar.
    # Extra 5: se a entrada trouxe a tag @TIPO explícita, ela tem prioridade absoluta sobre qualquer heurística.
    if tipo_forcado is not None:
        is_mt = tipo_forcado in ("MT", "ALL")
        is_ap = tipo_forcado == "AP"
        is_afnd = tipo_forcado == "AF" and (len(estados_iniciais) > 1 or any('\\' in tr for tr in transicoes_raw))
        # Para '@AF', ainda decidimos entre AFD/AFND normalmente, pois o enunciado trata AFD e AFND como o mesmo tipo 'AF'
    else:
        # Sem @TIPO: mantém a heurística original para AF/AFND/AP, e detecta MT/ALL pelo formato das transições
        # (a/bd), independentemente de existir ou não a tag G:, já que ela é opcional na MT (a especificação
        # permite considerar apenas 0 e 1 como alfabeto de entrada, sem símbolos extras de fita).
        is_mt = tem_transicao_mt
        is_ap = alfabeto_pilha is not None and not is_mt # Tem G: e não usa formato a/bd -> é AP
        is_afnd = len(estados_iniciais) > 1 or any('\\' in tr for tr in transicoes_raw)

    if is_mt:
        afd = MT() # Instancia a Máquina de Turing / Autômato Linearmente Limitado
        afd.alfabeto_fita = alfabeto_fita if alfabeto_fita is not None else [] # Configura o alfabeto extra da fita
        afd.estados_iniciais = estados_iniciais # Configura estados iniciais
        afd.alfabeto_entrada = alfabeto_entrada # Configura alfabeto de entrada
    elif is_ap:
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
            
            if isinstance(afd, MT):
                # Formato da transição da MT/ALL: a/bd (lê a, escreve b, anda d -> E ou D)
                for elem in elementos_restantes:
                    if '/' in elem and ',' not in elem:
                        simbolo_lido, resto_elem = elem.split('/') # 'a' separado de 'bd'
                        simbolo_escrito = resto_elem[:-1] # Tudo menos o último char é o símbolo a escrever ('b')
                        direcao = resto_elem[-1] # Último caractere é a direção do movimento ('E' ou 'D')
                        
                        afd.transicoes.append({
                            "origem": origem, # De onde sai
                            "destino": destino, # Pra onde vai
                            "simbolo": simbolo_lido, # Símbolo lido da fita
                            "escreve": simbolo_escrito, # Símbolo gravado no lugar do lido
                            "direcao": direcao # 'E' (esquerda) ou 'D' (direita)
                        })
            elif isinstance(afd, AP):
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