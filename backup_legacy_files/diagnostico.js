// Arquivo principal para o diagnóstico do sistema
document.addEventListener('DOMContentLoaded', function() {
    // Elementos da interface
    const diagnosticProcess = document.getElementById('diagnostic-process');
    const diagnosticResults = document.getElementById('diagnostic-results');
    const repairProcess = document.getElementById('repair-process');
    const diagnosticProgress = document.getElementById('diagnostic-progress');
    const diagnosticMessage = document.getElementById('diagnostic-message');
    const diagnosticLog = document.getElementById('diagnostic-log');
    const scoreValue = document.getElementById('score-value');
    const scoreDescription = document.getElementById('score-description');
    const iniciarReparo = document.getElementById('iniciar-reparo');
    const chatToggle = document.getElementById('chat-toggle');
    const chatWindow = document.getElementById('chat-window');
    const chatClose = document.getElementById('chat-close');
    const chatSend = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input-field');
    const chatMessages = document.getElementById('chat-messages');

    // Configuração do chat
    chatToggle.addEventListener('click', function() {
        chatWindow.classList.toggle('active');
    });

    chatClose.addEventListener('click', function() {
        chatWindow.classList.remove('active');
    });

    chatSend.addEventListener('click', function() {
        sendMessage();
    });

    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            addUserMessage(message);
            chatInput.value = '';
            
            // Simular resposta do assistente após 1 segundo
            setTimeout(function() {
                respondToMessage(message);
            }, 1000);
        }
    }

    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-user';
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <p>${message}</p>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addAgentMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-agent';
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <p>${message}</p>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function respondToMessage(message) {
        const lowerMessage = message.toLowerCase();
        let response = '';
        
        if (lowerMessage.includes('lento') || lowerMessage.includes('devagar')) {
            response = 'Computadores lentos geralmente têm problemas com memória insuficiente, muitos programas iniciando automaticamente, ou fragmentação de disco. Nosso diagnóstico identificará a causa exata e recomendará soluções.';
        } else if (lowerMessage.includes('driver') || lowerMessage.includes('drivers')) {
            response = 'Drivers desatualizados podem causar problemas de desempenho e compatibilidade. Nosso sistema verifica automaticamente todos os drivers e recomenda atualizações quando necessário.';
        } else if (lowerMessage.includes('virus') || lowerMessage.includes('malware') || lowerMessage.includes('segurança')) {
            response = 'Nossa ferramenta executa uma verificação completa de segurança, utilizando o Windows Defender para identificar e remover ameaças. Também verificamos configurações de segurança inadequadas.';
        } else if (lowerMessage.includes('diagnóstico') || lowerMessage.includes('como funciona')) {
            response = 'Nosso diagnóstico analisa seu processador, memória, disco, drivers, programas de inicialização e segurança. O processo leva cerca de 5 minutos e fornece um relatório detalhado com recomendações personalizadas.';
        } else if (lowerMessage.includes('backup')) {
            response = 'Antes de realizar qualquer correção, nosso sistema faz um backup automático das configurações críticas do sistema para garantir que tudo possa ser restaurado em caso de problemas.';
        } else if (lowerMessage.includes('preço') || lowerMessage.includes('custo') || lowerMessage.includes('valor')) {
            response = 'O diagnóstico é totalmente gratuito. Oferecemos dois pacotes de correção: Básico (R$ 49,90) e Premium (R$ 89,90), com diferentes níveis de otimização e suporte.';
        } else {
            response = 'Estou aqui para ajudar com qualquer dúvida sobre manutenção de computadores. Posso explicar como funciona o diagnóstico, ajudar com problemas específicos ou fornecer informações sobre nossos serviços.';
        }
        
        addAgentMessage(response);
    }

    // Função para adicionar mensagem ao log
    function addLog(message) {
        const now = new Date();
        const timeString = `[${now.getHours()}:${now.getMinutes()}:${now.getSeconds()} ${now.getHours() >= 12 ? 'PM' : 'AM'}]`;
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `<span class="log-time">${timeString}</span> ${message}`;
        diagnosticLog.appendChild(logEntry);
        diagnosticLog.scrollTop = diagnosticLog.scrollHeight;
    }

    // Iniciar diagnóstico automaticamente
    startDiagnostic();

    // Função para iniciar o diagnóstico
    function startDiagnostic() {
        // Mostrar seção de diagnóstico
        diagnosticProcess.style.display = 'block';
        diagnosticResults.style.display = 'none';
        repairProcess.style.display = 'none';
        
        // Resetar progresso
        updateProgress(0, 'Iniciando diagnóstico...');
        diagnosticLog.innerHTML = '';
        
        // Adicionar logs iniciais
        addLog('Iniciando diagnóstico do sistema');
        addLog('Agente TechZe ativado para análise automática');
        
        // Simular diagnóstico
        simulateDiagnostic();
    }

    // Função para atualizar o progresso
    function updateProgress(percent, message) {
        diagnosticProgress.style.width = percent + '%';
        diagnosticProgress.setAttribute('aria-valuenow', percent);
        diagnosticMessage.textContent = message;
    }

    // Função para simular o diagnóstico
    function simulateDiagnostic() {
        const steps = [
            { percent: 5, message: 'Iniciando análise de processador...', log: 'Iniciando análise de processador' },
            { percent: 10, message: 'Verificando modelo e frequência do processador...', log: 'Verificando modelo e frequência do processador' },
            { percent: 15, message: 'Analisando utilização da CPU...', log: 'Analisando utilização da CPU' },
            { percent: 20, message: 'Iniciando análise de memória...', log: 'Iniciando análise de memória' },
            { percent: 25, message: 'Verificando memória total e disponível...', log: 'Verificando memória total e disponível' },
            { percent: 30, message: 'Analisando uso de memória por processos...', log: 'Analisando uso de memória por processos' },
            { percent: 35, message: 'Iniciando análise de disco...', log: 'Iniciando análise de disco' },
            { percent: 40, message: 'Verificando espaço livre em disco...', log: 'Verificando espaço livre em disco' },
            { percent: 45, message: 'Analisando fragmentação do disco...', log: 'Analisando fragmentação do disco' },
            { percent: 50, message: 'Verificando arquivos temporários...', log: 'Verificando arquivos temporários' },
            { percent: 55, message: 'Iniciando análise de drivers...', log: 'Iniciando análise de drivers' },
            { percent: 60, message: 'Verificando drivers desatualizados...', log: 'Verificando drivers desatualizados' },
            { percent: 65, message: 'Analisando drivers com problemas...', log: 'Analisando drivers com problemas' },
            { percent: 70, message: 'Iniciando análise de inicialização...', log: 'Iniciando análise de inicialização' },
            { percent: 75, message: 'Verificando programas de inicialização...', log: 'Verificando programas de inicialização' },
            { percent: 80, message: 'Analisando impacto na performance...', log: 'Analisando impacto na performance' },
            { percent: 85, message: 'Iniciando análise de segurança...', log: 'Iniciando análise de segurança' },
            { percent: 90, message: 'Verificando Windows Defender...', log: 'Verificando Windows Defender' },
            { percent: 95, message: 'Analisando configurações de segurança...', log: 'Analisando configurações de segurança' },
            { percent: 100, message: 'Diagnóstico concluído!', log: 'Diagnóstico concluído com sucesso' }
        ];
        
        let currentStep = 0;
        
        function processNextStep() {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                updateProgress(step.percent, step.message);
                addLog(step.log);
                currentStep++;
                
                // Próximo passo após um tempo aleatório entre 500ms e 1500ms
                const delay = Math.random() * 1000 + 500;
                setTimeout(processNextStep, delay);
            } else {
                // Diagnóstico concluído
                setTimeout(showResults, 1000);
            }
        }
        
        // Iniciar processamento
        processNextStep();
    }

    // Função para mostrar os resultados
    function showResults() {
        // Esconder processo de diagnóstico e mostrar resultados
        diagnosticProcess.style.display = 'none';
        diagnosticResults.style.display = 'block';
        
        // Gerar pontuação aleatória entre 50 e 85
        const score = Math.floor(Math.random() * 36) + 50;
        scoreValue.textContent = score;
        
        // Definir descrição com base na pontuação
        if (score < 60) {
            scoreDescription.textContent = 'Seu sistema precisa de atenção urgente. Encontramos vários problemas que estão afetando significativamente o desempenho.';
        } else if (score < 70) {
            scoreDescription.textContent = 'Seu sistema está com desempenho abaixo do ideal. Recomendamos correções para melhorar a velocidade e estabilidade.';
        } else if (score < 80) {
            scoreDescription.textContent = 'Seu sistema está com desempenho razoável, mas encontramos algumas áreas que podem ser otimizadas.';
        } else {
            scoreDescription.textContent = 'Seu sistema está em boas condições, mas ainda há espaço para algumas melhorias de desempenho.';
        }
        
        // Preencher detalhes dos componentes
        document.getElementById('cpu-details').innerHTML = `
            <p>Utilização média: ${Math.floor(Math.random() * 30) + 20}%</p>
            <p>Processos em segundo plano: ${Math.floor(Math.random() * 10) + 5}</p>
            <p>Status: ${Math.random() > 0.7 ? '<span class="status-warning">Atenção</span>' : '<span class="status-good">Bom</span>'}</p>
        `;
        
        document.getElementById('memory-details').innerHTML = `
            <p>Memória em uso: ${Math.floor(Math.random() * 40) + 40}%</p>
            <p>Memória física: 8GB</p>
            <p>Status: ${Math.random() > 0.6 ? '<span class="status-warning">Atenção</span>' : '<span class="status-good">Bom</span>'}</p>
        `;
        
        document.getElementById('disk-details').innerHTML = `
            <p>Espaço livre: ${Math.floor(Math.random() * 30) + 20}%</p>
            <p>Fragmentação: ${Math.floor(Math.random() * 20) + 5}%</p>
            <p>Status: ${Math.random() > 0.5 ? '<span class="status-warning">Atenção</span>' : '<span class="status-good">Bom</span>'}</p>
        `;
        
        document.getElementById('drivers-details').innerHTML = `
            <p>Drivers desatualizados: ${Math.floor(Math.random() * 5) + 1}</p>
            <p>Drivers com problemas: ${Math.floor(Math.random() * 2)}</p>
            <p>Status: ${Math.random() > 0.4 ? '<span class="status-warning">Atenção</span>' : '<span class="status-good">Bom</span>'}</p>
        `;
        
        document.getElementById('startup-details').innerHTML = `
            <p>Programas na inicialização: ${Math.floor(Math.random() * 10) + 5}</p>
            <p>Impacto na inicialização: ${Math.random() > 0.5 ? 'Alto' : 'Médio'}</p>
            <p>Status: ${Math.random() > 0.3 ? '<span class="status-warning">Atenção</span>' : '<span class="status-good">Bom</span>'}</p>
        `;
        
        document.getElementById('security-details').innerHTML = `
            <p>Proteção em tempo real: ${Math.random() > 0.8 ? 'Desativada' : 'Ativada'}</p>
            <p>Última verificação: ${Math.floor(Math.random() * 30) + 1} dias atrás</p>
            <p>Status: ${Math.random() > 0.7 ? '<span class="status-warning">Atenção</span>' : '<span class="status-good">Bom</span>'}</p>
        `;
        
        // Gerar lista de problemas
        const problemsList = document.getElementById('problems-list');
        const possibleProblems = [
            'Arquivos temporários ocupando espaço em disco',
            'Drivers de vídeo desatualizados',
            'Fragmentação de disco acima do recomendado',
            'Muitos programas iniciando com o Windows',
            'Memória RAM com uso elevado',
            'Windows Defender não atualizado recentemente',
            'Arquivos desnecessários no disco',
            'Serviços em segundo plano consumindo recursos',
            'Configurações de energia não otimizadas',
            'Arquivos de sistema corrompidos'
        ];
        
        // Selecionar aleatoriamente 3-6 problemas
        const numProblems = Math.floor(Math.random() * 4) + 3;
        const selectedProblems = [];
        
        while (selectedProblems.length < numProblems) {
            const randomIndex = Math.floor(Math.random() * possibleProblems.length);
            const problem = possibleProblems[randomIndex];
            
            if (!selectedProblems.includes(problem)) {
                selectedProblems.push(problem);
            }
        }
        
        // Exibir problemas
        if (selectedProblems.length > 0) {
            problemsList.innerHTML = '';
            selectedProblems.forEach(problem => {
                const problemItem = document.createElement('div');
                problemItem.className = 'problem-item';
                problemItem.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${problem}`;
                problemsList.appendChild(problemItem);
            });
        }
        
        // Preencher recomendações
        const basicFeatures = document.getElementById('recomendacoes-basico');
        const premiumFeatures = document.getElementById('recomendacoes-premium');
        
        basicFeatures.innerHTML = `
            <li><i class="fas fa-check"></i> Limpeza de arquivos temporários</li>
            <li><i class="fas fa-check"></i> Otimização de inicialização</li>
            <li><i class="fas fa-check"></i> Atualização de drivers críticos</li>
            <li><i class="fas fa-check"></i> Verificação básica de segurança</li>
        `;
        
        premiumFeatures.innerHTML = `
            <li><i class="fas fa-check"></i> Tudo do pacote básico</li>
            <li><i class="fas fa-check"></i> Desfragmentação completa de disco</li>
            <li><i class="fas fa-check"></i> Atualização de todos os drivers</li>
            <li
(Content truncated due to size limit. Use line ranges to read in chunks)