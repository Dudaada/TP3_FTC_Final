import sys
from leitor import ler_configuracao_afd
from motor import criar_mapa_transicoes, processar_palavra

def main():
    # Pega o primeiro parâmetro de chamada do terminal (se existir), ou roda 'entrada.txt' por padrão
    caminho_arquivo = sys.argv[1] if len(sys.argv) > 1 else 'entrada.txt'
    
    # 1. Faz o parse do arquivo TXT e instancia o objeto filho correto (AFD, AFND ou AP)
    # A variável 'palavras_teste' coleta as linhas pós-'---'
    afd, palavras_teste = ler_configuracao_afd(caminho_arquivo)
    
    if afd is None:
        print("Erro: Arquivo de entrada vazio ou inválido.")
        return

    # 2. Transforma as transições lidas em um dicionário de busca em O(1) (Hashmap)
    # Aqui, dependendo se o 'afd' é AP ou AFND, o mapa de transição virá construído da forma certa para sua engine
    mapa_transicoes = criar_mapa_transicoes(afd)
    
    # 3. For loop que passa linha a linha nas palavras abaixo da divisória "---"
    for palavra in palavras_teste:
        # Entrega o autômato, o mapa feito em memória e a palavra para o despachante do motor,
        # que por sua vez manda a Engine de execução própria simular os estados.
        aceita = processar_palavra(afd, mapa_transicoes, palavra)
        
        # De acordo com a especificação formal, escreve OK se foi verdadeiro (Aceita)
        if aceita:
            print("OK")
        # E escreve X se foi falso (Rejeitada)
        else:
            print("X")

if __name__ == "__main__":
    # Ponto de entrada canônico do Python
    main()
