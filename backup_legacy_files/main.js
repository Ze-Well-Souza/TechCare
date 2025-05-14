// Arquivo JavaScript principal para o site TechCare

// Função para inicializar o site quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
  console.log('TechCare - Site inicializado');
  
  // Registra o service worker para funcionalidades offline
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
      .then(function(registration) {
        console.log('Service Worker registrado com sucesso:', registration.scope);
      })
      .catch(function(error) {
        console.log('Falha ao registrar Service Worker:', error);
      });
  }
  
  // Detecta se o dispositivo é móvel para otimizações específicas
  const isMobile = window.innerWidth <= 768 || 
                  /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  
  if (isMobile) {
    document.body.classList.add('mobile-device');
  }
  
  // Adiciona classe para animação de fade-in no body
  setTimeout(() => {
    document.body.classList.add('loaded');
  }, 100);
});

// Funções para a página de diagnóstico
function showResults() {
  const diagnosticProcess = document.getElementById('diagnostic-process');
  const diagnosticResults = document.getElementById('diagnostic-results');
  
  if (diagnosticProcess && diagnosticResults) {
    diagnosticProcess.style.display = 'none';
    diagnosticResults.style.display = 'block';
  }
}

function cancelDiagnostic() {
  const diagnosticProcess = document.getElementById('diagnostic-process');
  const serviceSelection = document.getElementById('service-selection');
  
  if (diagnosticProcess && serviceSelection) {
    diagnosticProcess.style.display = 'none';
    serviceSelection.style.display = 'grid';
  }
}

function selectPlan(plan) {
  const basicOption = document.querySelectorAll('.service-option')[0];
  const premiumOption = document.querySelectorAll('.service-option')[1];
  const continueButton = document.querySelector('.btn-secondary');
  
  if (plan === 'basic') {
    basicOption.style.border = '2px solid var(--primary-color)';
    premiumOption.style.border = '2px solid transparent';
    continueButton.textContent = 'Continuar com o Plano Básico';
  } else {
    premiumOption.style.border = '2px solid var(--primary-color)';
    basicOption.style.border = '2px solid transparent';
    continueButton.textContent = 'Continuar com o Plano Premium';
  }
}

function startRepair() {
  const diagnosticResults = document.getElementById('diagnostic-results');
  const repairProcess = document.getElementById('repair-process');
  
  if (diagnosticResults && repairProcess) {
    diagnosticResults.style.display = 'none';
    repairProcess.style.display = 'block';
  }
}

// Funções para a página de suporte
function quickResponse(message) {
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.value = message;
    sendMessage();
  }
}

function sendMessage() {
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');
  
  if (chatInput && chatMessages && chatInput.value.trim() !== '') {
    // Adiciona mensagem do usuário
    const userMessage = document.createElement('div');
    userMessage.className = 'message message-user';
    userMessage.innerHTML = `<p>${chatInput.value}</p>`;
    chatMessages.appendChild(userMessage);
    
    // Limpa o input
    const message = chatInput.value;
    chatInput.value = '';
    
    // Mostra "Assistente está digitando..."
    const typingIndicator = document.querySelector('.agent-typing');
    if (typingIndicator) {
      typingIndicator.style.display = 'block';
    }
    
    // Rola o chat para o final
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Simula resposta do assistente após 1.5 segundos
    setTimeout(function() {
      // Remove "Assistente está digitando..."
      if (typingIndicator) {
        typingIndicator.style.display = 'none';
      }
      
      // Adiciona resposta do assistente
      const agentMessage = document.createElement('div');
      agentMessage.className = 'message message-agent';
      
      // Resposta personalizada baseada na mensagem do usuário
      let response = '';
      if (message.toLowerCase().includes('diagnóstico') || message.toLowerCase().includes('diagnostico')) {
        response = `<p>Para iniciar o diagnóstico gratuito, basta clicar no botão "Iniciar Diagnóstico" na página inicial ou acessar diretamente a página de diagnóstico. O processo é simples e rápido, e você receberá um relatório detalhado dos problemas encontrados no seu computador.</p>`;
      } else if (message.toLowerCase().includes('preço') || message.toLowerCase().includes('custo') || message.toLowerCase().includes('valor')) {
        response = `<p>Nossos serviços começam a partir de R$ 49,90 para o Pacote de Otimização Básica. O Pacote Premium custa R$ 89,90 e inclui recursos adicionais como desfragmentação de disco e suporte técnico prioritário por 30 dias. Após o diagnóstico gratuito, você receberá recomendações personalizadas com os preços exatos.</p>`;
      } else if (message.toLowerCase().includes('lento') || message.toLowerCase().includes('devagar')) {
        response = `<p>A lentidão do computador pode ser causada por diversos fatores, como drivers desatualizados, programas de inicialização excessivos, pouco espaço em disco ou malware. Nosso diagnóstico gratuito pode identificar a causa específica no seu caso e recomendar as melhores soluções.</p><p>Recomendo iniciar o diagnóstico clicando <a href="diagnostico.html">aqui</a>.</p>`;
      } else if (message.toLowerCase().includes('técnico') || message.toLowerCase().includes('humano') || message.toLowerCase().includes('pessoa')) {
        response = `<p>Entendo que você prefere falar com um técnico humano. Nosso suporte técnico está disponível de segunda a sexta, das 8h às 20h. Posso transferir seu atendimento agora ou agendar um horário específico para que um técnico entre em contato com você. O que prefere?</p>`;
      } else {
        response = `<p>Obrigado pela sua mensagem. Para que eu possa ajudar melhor, poderia fornecer mais detalhes sobre o problema que está enfrentando com seu computador? Ou, se preferir, pode iniciar um diagnóstico gratuito clicando <a href="diagnostico.html">aqui</a>.</p>`;
      }
      
      agentMessage.innerHTML = response;
      chatMessages.appendChild(agentMessage);
      
      // Rola o chat para o final
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1500);
  }
}

// Função para abrir o chat de suporte
function openChat() {
  window.location.href = 'suporte.html';
}

// Funções para a página de histórico
function filterHistoryItems() {
  // Implementação será adicionada pelo arquivo interactive.js
  console.log('Filtrando itens de histórico...');
}

// Funções para as FAQs
function toggleFaq(id) {
  const answer = document.getElementById(`faq-answer-${id}`);
  const icon = document.getElementById(`faq-icon-${id}`);
  
  if (answer && icon) {
    if (answer.style.display === 'none' || !answer.style.display) {
      answer.style.display = 'block';
      icon.className = 'fas fa-minus';
    } else {
      answer.style.display = 'none';
      icon.className = 'fas fa-plus';
    }
  }
}

// Inicializa os eventos das FAQs
document.addEventListener('DOMContentLoaded', function() {
  const faqItems = document.querySelectorAll('.faq-item h3');
  
  faqItems.forEach((item, index) => {
    item.addEventListener('click', function() {
      toggleFaq(index + 1);
    });
  });
});
