/**
 * TechZe - Manutenção Guiada
 * Script para gerenciar o guia passo a passo de manutenção
 */

// Banco de dados de guias de manutenção
const guiasManutencao = {
    // Guia para resolver lentidão do computador
    lentidao: {
        titulo: "Otimização de Desempenho do Computador",
        descricao: "Siga os passos abaixo para melhorar a velocidade do seu computador",
        etapas: [
            {
                titulo: "Verificar programas em execução",
                descricao: "Vamos verificar quais programas estão consumindo recursos do seu sistema.",
                instrucoes: `
                    <ol>
                        <li>Pressione as teclas <strong>Ctrl + Shift + Esc</strong> simultaneamente para abrir o Gerenciador de Tarefas</li>
                        <li>Clique na aba <strong>Processos</strong> no topo da janela</li>
                        <li>Clique no cabeçalho <strong>CPU</strong> ou <strong>Memória</strong> para ordenar os processos por uso de recursos</li>
                        <li>Identifique programas que estão consumindo muitos recursos (valores altos de CPU ou Memória)</li>
                    </ol>
                `,
                detalhes: `
                    <div class="info-box">
                        <h4><i class="fas fa-info-circle"></i> Informação importante</h4>
                        <p>Programas que consomem mais de 30% da CPU ou mais de 500 MB de memória constantemente podem estar causando lentidão no seu sistema.</p>
                    </div>
                `,
                imagemUrl: "img/gerenciador-tarefas.jpg"
            },
            {
                titulo: "Encerrar programas desnecessários",
                descricao: "Vamos encerrar programas que estão consumindo recursos desnecessariamente.",
                instrucoes: `
                    <ol>
                        <li>No Gerenciador de Tarefas, selecione um programa que você não está usando atualmente e que está consumindo muitos recursos</li>
                        <li>Clique no botão <strong>Finalizar tarefa</strong> no canto inferior direito</li>
                        <li>Confirme a operação se solicitado</li>
                        <li>Repita para outros programas desnecessários</li>
                    </ol>
                `,
                detalhes: `
                    <div class="warning-box">
                        <h4><i class="fas fa-exclamation-triangle"></i> Atenção</h4>
                        <p>Não encerre processos do sistema (como aqueles listados como "Sistema" ou "Windows"). Foque em aplicativos que você reconhece como não essenciais no momento.</p>
                    </div>
                `,
                imagemUrl: "img/finalizar-tarefa.jpg"
            },
            {
                titulo: "Limpar arquivos temporários",
                descricao: "Arquivos temporários ocupam espaço e podem reduzir o desempenho do sistema.",
                instrucoes: `
                    <ol>
                        <li>Pressione as teclas <strong>Windows + R</strong> para abrir a janela Executar</li>
                        <li>Digite <strong>%temp%</strong> e pressione Enter</li>
                        <li>Selecione todos os arquivos (Ctrl + A)</li>
                        <li>Pressione a tecla Delete</li>
                        <li>Confirme a exclusão. Alguns arquivos podem estar em uso e não serão excluídos, o que é normal</li>
                    </ol>
                `,
                detalhes: `
                    <div class="tip-box">
                        <h4><i class="fas fa-lightbulb"></i> Dica</h4>
                        <p>Execute esta limpeza regularmente, pelo menos uma vez por mês, para manter seu computador funcionando de forma eficiente.</p>
                    </div>
                `,
                imagemUrl: "img/temp-files.jpg"
            },
            {
                titulo: "Desativar programas de inicialização",
                descricao: "Muitos programas iniciam automaticamente com o Windows e continuam consumindo recursos.",
                instrucoes: `
                    <ol>
                        <li>No Gerenciador de Tarefas (Ctrl + Shift + Esc), clique na aba <strong>Inicializar</strong></li>
                        <li>Revise a lista de programas que iniciam com o Windows</li>
                        <li>Clique com o botão direito em programas não essenciais (especialmente aqueles marcados como "Alto impacto")</li>
                        <li>Selecione <strong>Desabilitar</strong> no menu de contexto</li>
                        <li>Repita para outros programas desnecessários na inicialização</li>
                    </ol>
                `,
                detalhes: `
                    <div class="info-box">
                        <h4><i class="fas fa-info-circle"></i> O que manter habilitado?</h4>
                        <p>Mantenha habilitados: antivírus, drivers de hardware essenciais, e programas que você usa constantemente.</p>
                    </div>
                `,
                imagemUrl: "img/startup-programs.jpg"
            },
            {
                titulo: "Reiniciar o computador",
                descricao: "Reiniciar o computador aplica todas as alterações e limpa a memória do sistema.",
                instrucoes: `
                    <ol>
                        <li>Salve todos os arquivos abertos em seus aplicativos</li>
                        <li>Clique no menu Iniciar do Windows</li>
                        <li>Clique em Energia (ícone de energia) e selecione <strong>Reiniciar</strong></li>
                        <li>Aguarde o computador reiniciar completamente</li>
                        <li>Após o reinício, observe se houve melhoria no desempenho</li>
                    </ol>
                `,
                detalhes: `
                    <div class="tip-box">
                        <h4><i class="fas fa-lightbulb"></i> Por que reiniciar?</h4>
                        <p>Reiniciar libera memória, encerra processos em segundo plano, e permite que as alterações de sistema sejam aplicadas corretamente.</p>
                    </div>
                `,
                imagemUrl: "img/restart-computer.jpg"
            }
        ]
    },
    
    // Guia para liberar espaço em disco
    espaco: {
        titulo: "Liberação de Espaço em Disco",
        descricao: "Siga os passos abaixo para identificar e remover arquivos desnecessários e liberar espaço",
        etapas: [
            {
                titulo: "Verificar espaço em disco atual",
                descricao: "Primeiro, vamos verificar quanto espaço você tem disponível atualmente.",
                instrucoes: `
                    <ol>
                        <li>Abra o Explorador de Arquivos (ícone de pasta na barra de tarefas ou pressione Windows + E)</li>
                        <li>No painel esquerdo, clique em <strong>Este Computador</strong></li>
                        <li>Observe o espaço livre e usado nos seus discos, especialmente o disco C:</li>
                    </ol>
                `,
                detalhes: `
                    <div class="info-box">
                        <h4><i class="fas fa-info-circle"></i> Informação</h4>
                        <p>É recomendado manter pelo menos 15-20% do espaço total do disco livre para o funcionamento adequado do sistema.</p>
                    </div>
                `,
                imagemUrl: "img/verificar-espaco.jpg"
            },
            {
                titulo: "Executar a Limpeza de Disco do Windows",
                descricao: "O Windows tem uma ferramenta integrada para liberar espaço de forma segura.",
                instrucoes: `
                    <ol>
                        <li>Clique com o botão direito no disco C: e selecione <strong>Propriedades</strong></li>
                        <li>Na janela de propriedades, clique no botão <strong>Limpeza de Disco</strong></li>
                        <li>Aguarde a análise inicial</li>
                        <li>Marque todas as caixas de seleção dos tipos de arquivos que podem ser excluídos</li>
                        <li>Clique em <strong>OK</strong></li>
                        <li>Confirme a exclusão clicando em <strong>Excluir arquivos</strong></li>
                    </ol>
                `,
                detalhes: `
                    <div class="tip-box">
                        <h4><i class="fas fa-lightbulb"></i> Dica extra</h4>
                        <p>Para uma limpeza mais profunda, clique em <strong>Limpar arquivos do sistema</strong> após a primeira análise para incluir arquivos adicionais como atualizações antigas do Windows.</p>
                    </div>
                `,
                imagemUrl: "img/limpeza-disco.jpg"
            },
            {
                titulo: "Desinstalar programas não utilizados",
                descricao: "Remova programas que você não usa mais para liberar espaço valioso.",
                instrucoes: `
                    <ol>
                        <li>Abra o menu Iniciar e digite <strong>Painel de Controle</strong>, depois clique no resultado</li>
                        <li>Clique em <strong>Programas e Recursos</strong> ou <strong>Desinstalar um programa</strong></li>
                        <li>Revise a lista de programas instalados</li>
                        <li>Clique com o botão direito em programas que você não usa mais e selecione <strong>Desinstalar</strong></li>
                        <li>Siga as instruções na tela para concluir a desinstalação</li>
                    </ol>
                `,
                detalhes: `
                    <div class="warning-box">
                        <h4><i class="fas fa-exclamation-triangle"></i> Atenção</h4>
                        <p>Não desinstale programas se você não tiver certeza do que são. Alguns programas são necessários para o funcionamento do hardware ou do sistema.</p>
                    </div>
                `,
                imagemUrl: "img/desinstalar-programas.jpg"
            },
            {
                titulo: "Encontrar e remover arquivos grandes",
                descricao: "Localize arquivos que ocupam muito espaço e que você pode não precisar mais.",
                instrucoes: `
                    <ol>
                        <li>Abra o Explorador de Arquivos (Windows + E)</li>
                        <li>Na barra de pesquisa, digite <strong>size:gigantic</strong> para encontrar arquivos muito grandes</li>
                        <li>Revise os resultados e identifique arquivos que podem ser excluídos ou movidos para um armazenamento externo</li>
                        <li>Para arquivos que você deseja manter, considere mover para um disco externo ou nuvem</li>
                    </ol>
                `,
                detalhes: `
                    <div class="info-box">
                        <h4><i class="fas fa-info-circle"></i> Pesquisas por tamanho</h4>
                        <p>Você pode usar diferentes termos de pesquisa como: size:empty (0 KB), size:tiny (0-10 KB), size:small (10-100 KB), size:medium (100 KB-1 MB), size:large (1-16 MB), size:huge (16-128 MB) e size:gigantic (>128 MB)</p>
                    </div>
                `,
                imagemUrl: "img/arquivos-grandes.jpg"
            }
        ]
    },
    
    // Estrutura para os outros tipos de manutenção
    inicializacao: {
        titulo: "Aceleração da Inicialização do Windows",
        descricao: "Siga os passos abaixo para reduzir o tempo de inicialização do seu computador",
        etapas: [
            // Exemplo de primeira etapa
            {
                titulo: "Medir o tempo atual de inicialização",
                descricao: "Vamos primeiro verificar quanto tempo seu sistema leva para iniciar atualmente.",
                instrucoes: `
                    <ol>
                        <li>Pressione as teclas Windows + R para abrir a janela Executar</li>
                        <li>Digite <strong>eventvwr.msc</strong> e pressione Enter</li>
                        <li>No Visualizador de Eventos, expanda <strong>Logs do Windows</strong> e clique em <strong>Sistema</strong></li>
                        <li>No painel direito, clique em <strong>Filtrar Log Atual</strong></li>
                        <li>No campo "Origens do evento", selecione <strong>Diagnóstico de Desempenho</strong></li>
                        <li>Clique em OK para aplicar o filtro</li>
                        <li>Procure eventos com ID 100 (indica tempo de inicialização)</li>
                        <li>Anote o tempo de inicialização para comparação posterior</li>
                    </ol>
                `,
                detalhes: `
                    <div class="info-box">
                        <h4><i class="fas fa-info-circle"></i> Informação</h4>
                        <p>Um tempo de inicialização saudável depende do seu hardware, mas geralmente menos de 30 segundos é considerado bom para SSDs e menos de 60 segundos para HDDs.</p>
                    </div>
                `,
                imagemUrl: "img/tempo-inicializacao.jpg"
            }
            // Outras etapas seriam adicionadas aqui
        ]
    }
    
    // Outros guias de manutenção seriam adicionados aqui
};

// Configuração inicial quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const problemSelection = document.getElementById('problem-selection');
    const guidedSteps = document.getElementById('guided-steps');
    const completionSection = document.getElementById('completion-section');
    
    const guideTitle = document.getElementById('guide-title');
    const guideDescription = document.getElementById('guide-description');
    const progressLabels = document.getElementById('progress-labels');
    const guideProgress = document.getElementById('guide-progress');
    
    const stepCurrent = document.getElementById('step-current');
    const stepTotal = document.getElementById('step-total');
    const stepTitle = document.getElementById('step-title');
    const stepDescription = document.getElementById('step-description');
    const stepImage = document.getElementById('step-image');
    const stepDetails = document.getElementById('step-details');
    
    const prevStepBtn = document.getElementById('prev-step');
    const nextStepBtn = document.getElementById('next-step');
    const stepCompleteBtn = document.getElementById('step-complete');
    const stepHelpBtn = document.getElementById('step-help');
    
    const completionList = document.getElementById('completion-list');
    const saveReportBtn = document.getElementById('save-report');
    const newMaintenanceBtn = document.getElementById('new-maintenance');
    
    // Estado atual do guia
    let currentGuide = null;
    let currentStepIndex = 0;
    let completedSteps = [];
    
    // Adicionar event listeners para os botões de seleção de problema
    const problemButtons = document.querySelectorAll('.select-problem');
    problemButtons.forEach(button => {
        button.addEventListener('click', function() {
            const problemCard = this.closest('.problem-card');
            const problemType = problemCard.getAttribute('data-problem');
            startGuide(problemType);
        });
    });
    
    // Botões de navegação entre etapas
    prevStepBtn.addEventListener('click', function() {
        navigateStep(-1);
    });
    
    nextStepBtn.addEventListener('click', function() {
        navigateStep(1);
    });
    
    // Botão de etapa concluída
    stepCompleteBtn.addEventListener('click', function() {
        markStepComplete();
    });
    
    // Botão de ajuda
    stepHelpBtn.addEventListener('click', function() {
        requestHelp();
    });
    
    // Botão para iniciar nova manutenção
    newMaintenanceBtn.addEventListener('click', function() {
        resetGuide();
    });
    
    // Botão para salvar relatório
    saveReportBtn.addEventListener('click', function() {
        saveMaintenanceReport();
    });
    
    // Função para iniciar um guia específico
    function startGuide(guideType) {
        // Verifica se o guia existe
        if (!guiasManutencao[guideType]) {
            showMessage('Desculpe, este guia ainda não está disponível. Estamos trabalhando nisso!');
            return;
        }
        
        // Define o guia atual
        currentGuide = guiasManutencao[guideType];
        currentStepIndex = 0;
        completedSteps = [];
        
        // Atualiza a interface
        guideTitle.textContent = currentGuide.titulo;
        guideDescription.textContent = currentGuide.descricao;
        
        // Configura o progresso
        updateProgressLabels();
        updateProgress();
        
        // Carrega a primeira etapa
        loadStep(0);
        
        // Exibe a seção de guia passo a passo
        problemSelection.style.display = 'none';
        guidedSteps.style.display = 'block';
        completionSection.style.display = 'none';
        
        // Registra no histórico (simulado)
        logMaintenanceStart(guideType);
    }
    
    // Função para carregar uma etapa específica
    function loadStep(index) {
        if (!currentGuide || index < 0 || index >= currentGuide.etapas.length) {
            return;
        }
        
        const step = currentGuide.etapas[index];
        
        // Atualiza os indicadores de etapa
        stepCurrent.textContent = index + 1;
        stepTotal.textContent = currentGuide.etapas.length;
        
        // Atualiza o conteúdo da etapa
        stepTitle.textContent = step.titulo;
        stepDescription.textContent = step.descricao;
        stepDetails.innerHTML = step.detalhes || '';
        
        // Adiciona imagem se disponível
        if (step.imagemUrl) {
            stepImage.innerHTML = `<img src="${step.imagemUrl}" alt="${step.titulo}" class="step-img">`;
        } else {
            stepImage.innerHTML = `<div class="placeholder-image"><i class="fas fa-image"></i></div>`;
        }
        
        // Atualiza as instruções
        const instructionsElement = document.createElement('div');
        instructionsElement.className = 'step-instructions-content';
        instructionsElement.innerHTML = step.instrucoes;
        
        // Limpa as instruções anteriores e adiciona as novas
        const oldInstructions = document.querySelector('.step-instructions-content');
        if (oldInstructions) {
            oldInstructions.remove();
        }
        
        document.querySelector('.step-instructions').insertBefore(
            instructionsElement, 
            stepImage
        );
        
        // Atualiza os botões de navegação
        prevStepBtn.disabled = index === 0;
        nextStepBtn.disabled = !isStepCompleted(index);
        
        // Verifica se a etapa atual já foi concluída
        stepCompleteBtn.disabled = isStepCompleted(index);
        stepCompleteBtn.textContent = isStepCompleted(index) ? 
            'Etapa já concluída' : 'Sim, concluí esta etapa';
        
        // Atualiza o progresso visual
        updateProgress();
    }
    
    // Função para navegar entre etapas
    function navigateStep(direction) {
        const newIndex = currentStepIndex + direction;
        
        if (newIndex >= 0 && newIndex < currentGuide.etapas.length) {
            currentStepIndex = newIndex;
            loadStep(currentStepIndex);
        } else if (newIndex >= currentGuide.etapas.length && completedSteps.length === currentGuide.etapas.length) {
            // Se todas as etapas foram concluídas, mostrar a tela de conclusão
            showCompletion();
        }
    }
    
    // Função para marcar uma etapa como concluída
    function markStepComplete() {
        if (!isStepCompleted(currentStepIndex)) {
            completedSteps.push(currentStepIndex);
            
            // Habilita o botão próximo
            nextStepBtn.disabled = false;
            
            // Atualiza o botão de conclusão
            stepCompleteBtn.disabled = true;
            stepCompleteBtn.textContent = 'Etapa já concluída';
            
            // Atualiza o progresso
            updateProgress();
            
            // Registra a conclusão da etapa (simulado)
            logStepCompletion(currentStepIndex);
            
            // Se todas as etapas foram concluídas, habilita o último passo
            if (completedSteps.length === currentGuide.etapas.length) {
                showMessage('Você concluiu todas as etapas! Clique em "Próxima Etapa" para ver o resumo.');
            } else if (currentStepIndex < currentGuide.etapas.length - 1) {
                // Avança automaticamente para a próxima etapa após um breve momento
                setTimeout(() => {
                    navigateStep(1);
                }, 1000);
            }
        }
    }
    
    // Função para verificar se uma etapa foi concluída
    function isStepCompleted(index) {
        return completedSteps.includes(index);
    }
    
    // Função para atualizar os rótulos de progresso
    function updateProgressLabels() {
        progressLabels.innerHTML = '';
        
        currentGuide.etapas.forEach((step, index) => {
            const label = document.createElement('div');
            label.className = 'progress-label';
            label.textContent = `${index + 1}`;
            label.setAttribute('data-step', index);
            
            // Adicionar tooltips com os títulos das etapas
            label.title = step.titulo;
            
            progressLabels.appendChild(label);
        });
    }
    
    // Função para atualizar a barra de progresso
    function updateProgress() {
        // Calcula o progresso como porcentagem
        const progressPercent = (completedSteps.length / currentGuide.etapas.length) * 100;
        
        // Atualiza a barra de progresso
        guideProgress.style.width = `${progressPercent}%`;
        guideProgress.setAttribute('aria-valuenow', progressPercent);
        guideProgress.textContent = `${Math.round(progressPercent)}%`;
        
        // Atualiza as labels de progresso
        const labels = document.querySelectorAll('.progress-label');
        labels.forEach(label => {
            const stepIndex = parseInt(label.getAttribute('data-step'));
            
            if (isStepCompleted(stepIndex)) {
                label.classList.add('completed');
            } else {
                label.classList.remove('completed');
            }
            
            if (stepIndex === currentStepIndex) {
                label.classList.add('current');
            } else {
                label.classList.remove('current');
            }
        });
    }
    
    // Função para mostrar a seção de conclusão
    function showCompletion() {
        // Preenche a lista de etapas concluídas
        completionList.innerHTML = '';
        currentGuide.etapas.forEach((step, index) => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `<i class="fas fa-check-circle"></i> ${step.titulo}`;
            completionList.appendChild(listItem);
        });
        
        // Exibe a seção de conclusão
        problemSelection.style.display = 'none';
        guidedSteps.style.display = 'none';
        completionSection.style.display = 'block';
        
        // Registra a conclusão da manutenção (simulado)
        logMaintenanceCompletion();
    }
    
    // Função para resetar o guia
    function resetGuide() {
        currentGuide = null;
        currentStepIndex = 0;
        completedSteps = [];
        
        // Retorna à seleção de problemas
        problemSelection.style.display = 'block';
        guidedSteps.style.display = 'none';
        completionSection.style.display = 'none';
    }
    
    // Função para solicitar ajuda
    function requestHelp() {
        // Simula a abertura do chat com uma pergunta específica
        const chatToggle = document.getElementById('chat-toggle');
        const chatWindow = document.getElementById('chat-window');
        const chatInput = document.getElementById('chat-input-field');
        const chatSend = document.getElementById('chat-send');
        
        // Abre o chat se não estiver aberto
        if (!chatWindow.classList.contains('active')) {
            chatToggle.click();
        }
        
        // Preenche o campo de entrada com uma pergunta relacionada à etapa atual
        if (currentGuide && currentGuide.etapas[currentStepIndex]) {
            const etapaAtual = currentGuide.etapas[currentStepIndex];
            chatInput.value = `Preciso de ajuda com: ${etapaAtual.titulo}`;
            
            // Simula o clique no botão de envio
            setTimeout(() => {
                chatSend.click();
            }, 500);
        }
    }
    
    // Função para salvar relatório (simulado)
    function saveMaintenanceReport() {
        alert('Relatório de manutenção salvo! Em um sistema real, isto seria salvo no seu histórico e poderia ser exportado como PDF.');
    }
    
    // Função para mostrar mensagens ao usuário
    function showMessage(message) {
        // Implementação simples usando alert
        // Em um sistema real, seria melhor usar um toast ou notificação na interface
        alert(message);
    }
    
    // Funções de log simuladas (em um sistema real, enviariam dados para o servidor)
    function logMaintenanceStart(guideType) {
        console.log(`Manutenção iniciada: ${guideType} - ${new Date().toISOString()}`);
    }
    
    function logStepCompletion(stepIndex) {
        console.log(`Etapa concluída: ${stepIndex + 1} - ${currentGuide.etapas[stepIndex].titulo} - ${new Date().toISOString()}`);
    }
    
    function logMaintenanceCompletion() {
        console.log(`Manutenção concluída: ${currentGuide.titulo} - ${new Date().toISOString()}`);
    }
});

// Função para resposta rápida no chat (necessária por ser chamada diretamente no HTML)
function quickResponse(message) {
    const chatInput = document.getElementById('chat-input-field');
    const chatSend = document.getElementById('chat-send');
    
    chatInput.value = message;
    chatSend.click();
} 