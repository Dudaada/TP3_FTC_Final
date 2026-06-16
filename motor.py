import time
from collections import deque

# Tempo limite em segundos para prevenir loops infinitos (ex: pilha crescendo infinitamente em lambdas)
TEMPO_LIMITE_SEGUNDOS = 2.0 

class TimeoutException(Exception):
    pass

class MotorAFD:
    # Motor para processar Autômatos Finitos Determinísticos clássicos (sem ambiguidade de caminhos)
    def criar_mapa_transicoes(self, afd):
        mapa = {} # Dicionário de dicionários representando δ(estado, símbolo) = destino
        for transicao in afd.transicoes:
            origem = transicao["origem"]
            simbolo = transicao["simbolo"]
            destino = transicao["destino"]
            if origem not in mapa:
                mapa[origem] = {} # Inicia dicionário interno se for o primeiro símbolo desse estado de origem
            mapa[origem][simbolo] = destino # Em AFD sempre teremos 1 único destino por símbolo
        return mapa

    def processar_palavra(self, afd, mapa_transicoes, palavra):
        # Para AFD, iniciamos a leitura na configuração (q0) e vamos consumindo um a um
        estado_atual = getattr(afd, 'estado_inicial', afd.estados_iniciais[0] if hasattr(afd, 'estados_iniciais') and afd.estados_iniciais else "")
        start_time = time.time()
        
        for simbolo in palavra: # Laço consumindo cada símbolo
            if time.time() - start_time > TEMPO_LIMITE_SEGUNDOS:
                return False # Estoura o tempo limite se por algum motivo obscuro travar
            
            if estado_atual not in mapa_transicoes:
                return False # Se não tem transição mapeada a partir daqui, morreu e rejeita
            if simbolo not in mapa_transicoes[estado_atual]:
                return False # Se não transita para o símbolo lido, morreu e rejeita
            estado_atual = mapa_transicoes[estado_atual][simbolo] # Pula pro novo estado
            
        # A palavra acabou. Se paramos em um estado de aceitação, OK (True), senão X (False)
        return estado_atual in afd.estados_finais

class MotorAFND:
    # Motor para processar Não-Determinismo usando "Construção de Subconjunto" on-the-fly, 
    # mantendo tracking sobre múltiplos estados simultâneos
    def criar_mapa_transicoes(self, afd):
        mapa = {}
        for transicao in afd.transicoes:
            origem = transicao["origem"]
            simbolo = transicao["simbolo"]
            destino = transicao["destino"]
            if origem not in mapa:
                mapa[origem] = {}
            if simbolo not in mapa[origem]:
                mapa[origem][simbolo] = [] # Agora é uma lista, pois δ(q, a) = {q1, q2...}
            mapa[origem][simbolo].append(destino) # Adiciona todos os possíveis caminhos
        return mapa

    def fecho_epsilon(self, mapa_transicoes, estados, start_time):
        # Realiza o ε-closure (fecho lambda): quais estados alcançamos de graça, sem consumir fita
        fecho = set(estados) # Conjunto acumulando todos os estados alcançados
        fila = deque(estados) # Fila BFS de estados para explorar as ramificações epsilon
        while fila:
            if time.time() - start_time > TEMPO_LIMITE_SEGUNDOS:
                raise TimeoutException()
                
            estado = fila.popleft() # Tira o da frente da fila
            if estado in mapa_transicoes and '\\' in mapa_transicoes[estado]:
                # Se existe transição epsilon '\'
                for destino in mapa_transicoes[estado]['\\']:
                    if destino not in fecho: # Previne loops infinitos
                        fecho.add(destino) # Adiciona o destino alcançado de graça
                        fila.append(destino) # Coloca na fila pra ver se dali também sai mais epsilon
        return fecho

    def processar_palavra(self, afd, mapa_transicoes, palavra):
        start_time = time.time()
        try:
            # A simulação começa explorando todos os inícios + seus fechos epsilon
            estados_atuais = self.fecho_epsilon(mapa_transicoes, afd.estados_iniciais, start_time)
            
            for simbolo in palavra: # Laço de processamento da palavra, consumo de 1 char
                if time.time() - start_time > TEMPO_LIMITE_SEGUNDOS:
                    return False
                    
                proximos_estados = set() # Estados em que cairemos no próximo passo
                for estado in estados_atuais: # Para cada branch atual do nosso "universo paralelo"
                    if estado in mapa_transicoes and simbolo in mapa_transicoes[estado]:
                        # Junta todos os resultados possíveis
                        proximos_estados.update(mapa_transicoes[estado][simbolo])
                
                # Após mover consumindo o símbolo, sempre faz o fecho epsilon para ver as ramificações grátis a seguir
                estados_atuais = self.fecho_epsilon(mapa_transicoes, proximos_estados, start_time)
                
                if not estados_atuais:
                    return False # Se todos os ramos de possibilidades morreram, rejeita de imediato
                    
            # Fim da palavra: Se existir pelo menos um "universo" cujo estado atual é de aceitação, aceita
            return any(estado in afd.estados_finais for estado in estados_atuais)
        except TimeoutException:
            # Se estourar o limite de tempo em qualquer lugar (ex: um loop matemático degenerado), rejeita
            return False

class MotorAP:
    # Motor para Autômato de Pilha (Pushdown Automaton - PDA). Rastreia Descrições Instantâneas (estado, conteúdo da pilha).
    def criar_mapa_transicoes(self, afd):
        mapa = {}
        for transicao in afd.transicoes:
            origem = transicao["origem"]
            simbolo = transicao["simbolo"]
            pop = transicao["pop"]
            push = transicao["push"]
            destino = transicao["destino"]
            
            if origem not in mapa:
                mapa[origem] = {}
            if simbolo not in mapa[origem]:
                mapa[origem][simbolo] = []
                
            # No AP mapeamos os múltiplos retornos possíveis de (destino, pop, push)
            mapa[origem][simbolo].append({
                "destino": destino,
                "pop": pop,
                "push": push
            })
        return mapa

    def fecho_epsilon(self, mapa_transicoes, configs_iniciais, start_time):
        # fecho lambda sobre as Descrições Instantâneas: (estado, tuple(pilha_como_lista))
        fecho = set(configs_iniciais) # Set para prevenir loop e para acesso rápido
        fila = deque(configs_iniciais) # Fila BFS de ramificações da máquina
        
        while fila:
            if time.time() - start_time > TEMPO_LIMITE_SEGUNDOS:
                raise TimeoutException()
                
            estado, pilha = fila.popleft() # Extrai a Descrição Instantânea
            if estado in mapa_transicoes and '\\' in mapa_transicoes[estado]:
                for trans in mapa_transicoes[estado]['\\']: # Passa pelas transições lambdas ('\')
                    destino = trans["destino"]
                    pop = trans["pop"]
                    push = trans["push"]
                    
                    pode_aplicar = False # Variável de controle (Flag) de viabilidade
                    nova_pilha = list(pilha) # Copia a pilha para o novo "ramo do universo"
                    
                    if pop == '\\':
                        # Se pop é lambda ('\'), não tira nada e ignora verificação do topo
                        pode_aplicar = True
                    elif nova_pilha and nova_pilha[-1] == pop:
                        # Se tiver o símbolo requirido no topo, consumimos (pop) e a transição é válida
                        pode_aplicar = True
                        nova_pilha.pop()
                        
                    if pode_aplicar:
                        if push != '\\':
                            # Se tem que colocar coisas na pilha:
                            # A convenção canônica (Sipser) de PDA, na string ab, 'a' entra primeiro como novo topo
                            # então colocamos as letras reversamente na pilha pro topo ser o começo da string push.
                            for char in reversed(push):
                                nova_pilha.append(char)
                                
                        nova_config = (destino, tuple(nova_pilha)) # Tupla para poder ser 'hashable' no set
                        if nova_config not in fecho:
                            fecho.add(nova_config) # Salva
                            fila.append(nova_config) # Adiciona pra ver se há encadeamentos
                            
        return fecho

    def processar_palavra(self, afd, mapa_transicoes, palavra):
        start_time = time.time()
        try:
            # O estado atual do PDA é um conjunto de configurações: (estado, (pilha_vazia_neste_caso))
            configs_atuais = {(estado, ()) for estado in afd.estados_iniciais}
            configs_atuais = self.fecho_epsilon(mapa_transicoes, configs_atuais, start_time) # Aplica lambdas iniciais
            
            for simbolo in palavra:
                if time.time() - start_time > TEMPO_LIMITE_SEGUNDOS:
                    return False
                    
                proximas_configs = set()
                for estado, pilha in configs_atuais: # Em cada universo válido
                    if estado in mapa_transicoes and simbolo in mapa_transicoes[estado]:
                        for trans in mapa_transicoes[estado][simbolo]:
                            destino = trans["destino"]
                            pop = trans["pop"]
                            push = trans["push"]
                            
                            pode_aplicar = False
                            nova_pilha = list(pilha) # Copia o buffer da pilha
                            
                            if pop == '\\':
                                pode_aplicar = True
                            elif nova_pilha and nova_pilha[-1] == pop:
                                pode_aplicar = True
                                nova_pilha.pop()
                                
                            if pode_aplicar:
                                if push != '\\':
                                    for char in reversed(push): # Empilha reversamente (sendo topo = final da lista)
                                        nova_pilha.append(char)
                                proximas_configs.add((destino, tuple(nova_pilha))) # Adiciona essa rota à vida
                                
                configs_atuais = self.fecho_epsilon(mapa_transicoes, proximas_configs, start_time) # Lambdas apóes consumir char
                
                if not configs_atuais:
                    return False # Se esgotaram os ramos, morre aqui mesmo e rejeita
                    
            # ACEITAÇÃO: De acordo com o critério explícito pra esse trabalho de Autômato de Pilha (AP) e a formalização matemática de N(M), 
            # a palavra é aceita APENAS SE a palavra for lida integralmente (o for loop acaba) E a pilha se encontrar perfeitamente vazia.
            # Desprezamos aqui a checagem com afd.estados_finais que é característica da formulação L(M) de aceitação por Estado Final.
            return any(len(pilha) == 0 for estado, pilha in configs_atuais)
        except TimeoutException:
            # Captura a falha matemática do AP (crescimento infinito de pilha em loops vazios)
            # Rejeita a palavra silenciosamente, conforme a regra da especificação.
            return False


# Funções "Fábrica"/Despachantes (Strategy Pattern)
def get_motor(afd):
    # Verifica a instância em runtime e pega a classe do motor de lógica ideal
    from leitor import AP, AFND
    if isinstance(afd, AP):
        return MotorAP()
    elif isinstance(afd, AFND):
        return MotorAFND()
    else:
        return MotorAFD()

def criar_mapa_transicoes(afd):
    # Delega pro método do motor correspondente (Polimorfismo)
    motor = get_motor(afd)
    return motor.criar_mapa_transicoes(afd)

def processar_palavra(afd, mapa_transicoes, palavra):
    # Delega o processamento pro motor correspondente (Polimorfismo)
    motor = get_motor(afd)
    return motor.processar_palavra(afd, mapa_transicoes, palavra)
