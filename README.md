# TP3_FTC_Final

Simulador de autômatos a partir de um arquivo de configuração em texto. Suporta Autômato Finito Determinístico (AFD), Autômato Finito Não Determinístico (AFND), Autômato de Pilha (AP) e Máquina de Turing / Autômato Linearmente Limitado (MT/ALL).

## Como rodar o Modo Texto (CLI)

```bash
python main.py [caminho_do_arquivo]
```

Se nenhum caminho for passado, usa `entrada.txt` por padrão.

## Como rodar a Interface Gráfica (Web)

O projeto inclui uma interface interativa (tema CyberSec) para apresentação e testes rápidos.

1. Instale o framework Flask (caso ainda não tenha):
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie o servidor local:
   ```bash
   python app.py
   ```
3. Abra o navegador e acesse a URL indicada no terminal (geralmente `http://localhost:5000`).

## Extras implementados

- **Extra 1 — Alfabeto de entrada (`S:`)**: permite customizar o alfabeto de entrada do autômato.
- **Extra 2 — Não determinismo**: múltiplos estados iniciais e transições lambda (`\`).
- **Extra 3 — Autômato de Pilha (AP)**: alfabeto da pilha via `G:`, transições no formato `a,b/z`.
- **Extra 4 — Máquina de Turing / Autômato Linearmente Limitado (MT/ALL)**: alfabeto da fita via `G:` (opcional), transições no formato `a/bd` (lê `a`, escreve `b`, anda `d` ∈ {E, D}). A saída, além de `OK`/`X`, inclui o conteúdo final da fita: `OK <conteúdo` ou `X <conteúdo`.
  - O motor detecta automaticamente, pelo formato das transições, se o autômato usa os limitadores `<`/`>` da fita (caracterizando um ALL com fita fisicamente limitada) ou não (caso em que a fita é tratada como teoricamente infinita à direita, no estilo de uma MT clássica). Arquivos de exemplo: `teste_mt.txt` e `teste_all.txt`.
- **Extra 5 — Múltiplos tipos**: a primeira linha do arquivo pode opcionalmente conter `@AF`, `@AP` ou `@ALL`/`@MT`, escolhendo explicitamente o tipo de autômato descrito. Quando ausente, o tipo continua sendo detectado automaticamente pelas pistas da entrada (comportamento original, mantido por compatibilidade). Arquivo de exemplo: `teste_tipos.txt`.

## Arquivos de teste

- `entrada.txt`, `teste_afnd.txt`, `teste_ap.txt`: exemplos de AFD, AFND e AP (conforme especificação).
- `teste_mt.txt`: exemplo de MT com fita teoricamente infinita (sem limitadores nas transições).
- `teste_all.txt`: exemplo de ALL com limitadores `<`/`>` testados explicitamente nas transições.
- `teste_tipos.txt`: exemplo de uso da tag `@AF` (extra 5).
