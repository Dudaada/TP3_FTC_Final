def criar_mapa_transicoes(afd):
    mapa = {}
    for transicao in afd.transicoes:
        origem = transicao["origem"]
        simbolo = transicao["simbolo"]
        destino = transicao["destino"]
        if origem not in mapa:
            mapa[origem] = {}
        mapa[origem][simbolo] = destino
    return mapa

def processar_palavra(afd, mapa_transicoes, palavra):
    estado_atual = afd.estado_inicial
    for simbolo in palavra:
        if estado_atual not in mapa_transicoes:
            return False
        if simbolo not in mapa_transicoes[estado_atual]:
            return False
        estado_atual = mapa_transicoes[estado_atual][simbolo]
    return estado_atual in afd.estados_finais
