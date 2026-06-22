// Evento disparado assim que a DOM da página está carregada para instanciar as dependências iniciais
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/files');
        const data = await response.json();
        
        const selector = document.getElementById('fileSelector');
        data.files.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            option.textContent = file;
            selector.appendChild(option);
        });
    } catch (e) {
        console.error('Falha ao obter listagem de arquivos:', e);
    }
});

// Handler dinâmico: Escuta as mudanças no select de templates para auto-preencher os campos textuais com o conteúdo do arquivo
document.getElementById('fileSelector').addEventListener('change', async (e) => {
    const filename = e.target.value;
    if (!filename) return;
    
    try {
        const response = await fetch(`/api/file/${filename}`);
        const data = await response.json();
        
        if (!data.erro) {
            document.getElementById('automatoInput').value = data.automato;
            document.getElementById('testesInput').value = data.testes;
        }
    } catch (e) {
        console.error('Falha ao ler arquivo de configuracao:', e);
    }
});

document.getElementById('runBtn').addEventListener('click', async () => {
    const automatoText = document.getElementById('automatoInput').value;
    const testesText = document.getElementById('testesInput').value;
    
    const resultsPanel = document.getElementById('resultsPanel');
    const resultsContent = document.getElementById('resultsContent');
    const terminalScreen = document.getElementById('terminalScreen');
    const terminalOutput = document.getElementById('terminalOutput');
    
    // Reseta as instâncias visuais e engatilha o auto-scroll para guiar o olhar do usuário
    resultsPanel.style.display = 'block';
    resultsContent.style.display = 'none';
    resultsContent.innerHTML = '';
    
    terminalScreen.style.display = 'block';
    terminalOutput.innerHTML = '';
    terminalScreen.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Arrays contendo as strings de efeito simulando um trace log de segurança antes da requisição ir pro back-end
    const logs = [
        "> sys_sec --auth-mode strict",
        "> Inicializando Motor Criptografico...",
        "> Compilando regras de estado...",
        "> Estabelecendo socket de validacao...",
        "> Analisando payloads..."
    ];
    
    // Laço que escreve o trace log, pausando de 200 a 400ms por linha para um aspecto mais orgânico
    for (let i = 0; i < logs.length; i++) {
        await new Promise(r => setTimeout(r, 200 + Math.random() * 200));
        terminalOutput.innerHTML += `<div class="log-line">${logs[i]}</div>`;
    }
    
    try {
        // Fetch via POST enviando o JSON contendo os textos brutos das textareas
        const response = await fetch('/api/simular', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                automato: automatoText,
                testes: testesText
            })
        });
        
        const data = await response.json();
        
        await new Promise(r => setTimeout(r, 300));
        terminalScreen.style.display = 'none';
        resultsContent.style.display = 'grid';
        resultsContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        if (data.erro) {
            resultsContent.innerHTML = `
                <div class="result-card error" style="grid-column: 1 / -1;">
                    <div class="token-label">FALHA CRÍTICA DE SISTEMA</div>
                    <div class="token-value" style="color: var(--neon-red);">${data.erro}</div>
                </div>
            `;
            return;
        }
        
        // Laço assíncrono para renderizar os cards dos tokens, criando o efeito de 'cascata' que segura a atenção do usuário na UI
        for (let index = 0; index < data.resultados.length; index++) {
            const res = data.resultados[index];
            const card = document.createElement('div');
            card.className = `result-card ${res.aceita ? 'ok' : 'error'}`;
            
            const statusText = res.aceita ? 'ACESSO_CONCEDIDO (OK)' : 'ACESSO_NEGADO (X)';
            
            let html = `
                <div class="token-label">TOKEN // PAYLOAD</div>
                <div class="token-value">${res.palavra}</div>
                <div class="status-badge ${res.aceita ? 'ok' : 'error'}">${statusText}</div>
            `;
            
            if (res.fita !== null) {
                html += `
                    <div class="token-label" style="margin-top: 0.5rem;">FITA // MEMÓRIA DE RASTRO</div>
                    <div class="tape-display">${res.fita}</div>
                `;
            }
            
            if (res.erro) {
                html += `<div class="token-label" style="color: var(--neon-red); margin-top: 0.5rem;">ERRO DE PROCESSAMENTO</div>`;
            }
            
            card.innerHTML = html;
            resultsContent.appendChild(card);
            
            // Empurra o container de rolagem (Câmera) para focar no novo card inserido dinamicamente
            card.scrollIntoView({ behavior: 'smooth', block: 'end' });
            
            // Pausa a thread do JS rapidamente (150ms) para que a animação CSS (slideIn) consiga rodar fluidamente
            await new Promise(r => setTimeout(r, 150));
        }
        
    } catch (error) {
        terminalScreen.style.display = 'none';
        resultsContent.style.display = 'grid';
        resultsContent.innerHTML = `
            <div class="result-card error" style="grid-column: 1 / -1;">
                <div class="token-label">ERRO DE CONEXÃO</div>
                <div class="token-value" style="color: var(--neon-red);">Não foi possível contactar o servidor local.</div>
            </div>
        `;
    }
});
