// Arquivo para adicionar funcionalidades interativas avançadas ao site TechCare

// Função para inicializar todas as funcionalidades interativas
document.addEventListener('DOMContentLoaded', function() {
  // Inicializa animações de entrada
  initAnimations();
  
  // Inicializa funcionalidades específicas da página atual
  initPageSpecificFeatures();
  
  // Inicializa o service worker para PWA
  registerServiceWorker();
  
  // Adiciona eventos aos elementos interativos comuns
  setupCommonInteractions();
});

// Registra o service worker para funcionalidades offline
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('Service Worker registrado com sucesso:', registration.scope);
      })
      .catch(error => {
        console.log('Falha ao registrar Service Worker:', error);
      });
  }
}

// Inicializa animações de entrada para elementos
function initAnimations() {
  // Adiciona classe para animação de fade-in no body
  document.body.classList.add('loaded');
  
  // Anima cards com efeito de slide-up em sequência
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 * index);
  });
  
  // Anima botões com efeito de pulse
  const ctaButtons = document.querySelectorAll('.btn-primary, .btn-secondary');
  ctaButtons.forEach(button => {
    button.addEventListener('mouseover', function() {
      this.classList.add('pulse-animation');
    });
    button.addEventListener('mouseout', function() {
      this.classList.remove('pulse-animation');
    });
  });
}

// Inicializa funcionalidades específicas da página atual
function initPageSpecificFeatures() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  
  // Destaca o item de menu atual
  highlightCurrentMenuItem(currentPage);
  
  // Inicializa funcionalidades específicas com base na página atual
  switch(currentPage) {
    case 'index.html':
      initHomePage();
      break;
    case 'diagnostico.html':
      initDiagnosticPage();
      break;
    case 'historico.html':
      initHistoryPage();
      break;
    case 'suporte.html':
      initSupportPage();
      break;
  }
}

// Destaca o item de menu correspondente à página atual
function highlightCurrentMenuItem(currentPage) {
  const menuItems = document.querySelectorAll('.nav-menu a');
  menuItems.forEach(item => {
    const href = item.getAttribute('href');
    if (href === currentPage) {
      item.classList.add('active');
    }
  });
}

// Configura interações comuns a todas as páginas
function setupCommonInteractions() {
  // Adiciona efeito de hover aos cards
  const allCards = document.querySelectorAll('.card');
  allCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
    });
    card.addEventListener('mouseleave', function() {
      this.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    });
  });
  
  // Adiciona comportamento de scroll suave para links internos
  const internalLinks = document.querySelectorAll('a[href^="#"]');
  internalLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// Funcionalidades específicas da página inicial
function initHomePage() {
  console.log('Inicializando funcionalidades da página inicial');
  
  // Adiciona efeito de hover aos cards de serviço
  const serviceCards = document.querySelectorAll('.service-option');
  serviceCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-10px)';
    });
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
    card.addEventListener('click', function() {
      const service = this.getAttribute('data-service');
      if (service) {
        window.location.href = `diagnostico.html?service=${service}`;
      }
    });
  });
  
  // Adiciona carrossel de depoimentos se existir mais de 3
  const testimonials = document.querySelectorAll('.grid-3 .card');
  if (testimonials.length > 3) {
    initTestimonialCarousel(testimonials);
  }
}

// Funcionalidades específicas da página de diagnóstico
function initDiagnosticPage() {
  console.log('Inicializando funcionalidades da página de diagnóstico');
  
  // Verifica se há um serviço especificado na URL
  const urlParams = new URLSearchParams(window.location.search);
  const serviceParam = urlParams.get('service');
  
  if (serviceParam) {
    // Seleciona automaticamente o serviço especificado na URL
    setTimeout(() => {
      selectService(serviceParam);
    }, 500);
  }
  
  // Adiciona eventos aos botões de serviço
  const serviceOptions = document.querySelectorAll('.service-option');
  serviceOptions.forEach(option => {
    option.addEventListener('click', function() {
      const service = this.getAttribute('data-service');
      selectService(service);
    });
  });
  
  // Adiciona eventos aos botões de plano
  const planButtons = document.querySelectorAll('.service-option button');
  planButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.stopPropagation(); // Evita que o clique propague para o card
      const plan = this.parentElement.querySelector('h3').textContent.includes('Básico') ? 'basic' : 'premium';
      selectPlan(plan);
    });
  });
}

// Seleciona um serviço na página de diagnóstico
function selectService(service) {
  console.log(`Serviço selecionado: ${service}`);
  
  // Oculta a seleção de serviço com animação
  const serviceSelection = document.getElementById('service-selection');
  if (serviceSelection) {
    serviceSelection.style.opacity = '0';
    setTimeout(() => {
      serviceSelection.style.display = 'none';
      
      // Mostra o processo de diagnóstico com animação
      const diagnosticProcess = document.getElementById('diagnostic-process');
      if (diagnosticProcess) {
        diagnosticProcess.style.display = 'block';
        setTimeout(() => {
          diagnosticProcess.style.opacity = '1';
        }, 100);
        
        // Inicia a simulação do diagnóstico
        simulateDiagnosticProgress();
      }
    }, 300);
  }
}

// Simula o progresso do diagnóstico com animações
function simulateDiagnosticProgress() {
  const progressBars = document.querySelectorAll('.progress-bar');
  const steps = document.querySelectorAll('.diagnostic-step');
  
  // Atualiza o primeiro passo após 1.5 segundos
  setTimeout(() => {
    if (progressBars[0]) {
      animateProgressBar(progressBars[0], 100);
    }
    if (steps[0]) {
      steps[0].querySelector('i').className = 'fas fa-check-circle';
      steps[0].querySelector('i').style.color = '#2ecc71';
    }
  }, 1500);
  
  // Atualiza o segundo passo após 3 segundos
  setTimeout(() => {
    if (progressBars[1]) {
      animateProgressBar(progressBars[1], 100);
    }
    if (steps[1]) {
      steps[1].querySelector('i').className = 'fas fa-check-circle';
      steps[1].querySelector('i').style.color = '#2ecc71';
    }
  }, 3000);
  
  // Atualiza o terceiro passo após 4.5 segundos
  setTimeout(() => {
    if (progressBars[2]) {
      animateProgressBar(progressBars[2], 100);
    }
    if (steps[2]) {
      steps[2].querySelector('i').className = 'fas fa-check-circle';
      steps[2].querySelector('i').style.color = '#2ecc71';
    }
  }, 4500);
  
  // Atualiza o quarto passo após 6 segundos
  setTimeout(() => {
    if (progressBars[3]) {
      animateProgressBar(progressBars[3], 100);
    }
    if (steps[3]) {
      steps[3].querySelector('i').className = 'fas fa-check-circle';
      steps[3].querySelector('i').style.color = '#2ecc71';
    }
    
    // Após completar, destaca o botão para ver resultados
    const simulateButton = document.querySelector('.btn-primary[onclick="showResults()"]');
    if (simulateButton) {
      simulateButton.classList.add('pulse-animation');
    }
  }, 6000);
}

// Anima uma barra de progresso de forma suave
function animateProgressBar(progressBar, targetValue) {
  let currentValue = parseInt(progressBar.style.width) || 0;
  const increment = (targetValue - currentValue) / 20;
  
  const animation = setInterval(() => {
    currentValue += increment;
    if (currentValue >= targetValue) {
      currentValue = targetValue;
      clearInterval(animation);
    }
    progressBar.style.width = `${currentValue}%`;
    progressBar.textContent = `${Math.round(currentValue)}%`;
  }, 50);
}

// Cancela o diagnóstico e volta para a seleção de serviço
function cancelDiagnostic() {
  const diagnosticProcess = document.getElementById('diagnostic-process');
  const serviceSelection = document.getElementById('service-selection');
  
  if (diagnosticProcess) {
    diagnosticProcess.style.opacity = '0';
    setTimeout(() => {
      diagnosticProcess.style.display = 'none';
      
      // Mostra a seleção de serviço novamente
      if (serviceSelection) {
        serviceSelection.style.display = 'grid';
        setTimeout(() => {
          serviceSelection.style.opacity = '1';
        }, 100);
      }
    }, 300);
  }
}

// Mostra os resultados do diagnóstico
function showResults() {
  const diagnosticProcess = document.getElementById('diagnostic-process');
  const diagnosticResults = document.getElementById('diagnostic-results');
  
  if (diagnosticProcess) {
    diagnosticProcess.style.opacity = '0';
    setTimeout(() => {
      diagnosticProcess.style.display = 'none';
      
      // Mostra os resultados com animação
      if (diagnosticResults) {
        diagnosticResults.style.display = 'block';
        setTimeout(() => {
          diagnosticResults.style.opacity = '1';
          
          // Anima a entrada dos itens de problema
          const issueItems = document.querySelectorAll('.issue-item');
          issueItems.forEach((item, index) => {
            setTimeout(() => {
              item.style.opacity = '1';
              item.style.transform = 'translateX(0)';
            }, 200 * index);
          });
        }, 100);
      }
    }, 300);
  }
}

// Seleciona um plano de serviço
function selectPlan(plan) {
  const serviceOptions = document.querySelectorAll('.service-option');
  
  if (plan === 'basic') {
    if (serviceOptions[0]) {
      serviceOptions[0].style.border = '2px solid var(--primary-color)';
      serviceOptions[0].style.boxShadow = '0 5px 15px rgba(52, 152, 219, 0.2)';
    }
    if (serviceOptions[1]) {
      serviceOptions[1].style.border = '2px solid transparent';
      serviceOptions[1].style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }
    
    // Atualiza o texto do botão de continuar
    const continueButton = document.querySelector('.btn-secondary[onclick="startRepair()"]');
    if (continueButton) {
      continueButton.textContent = 'Continuar com o Plano Básico';
    }
  } else {
    if (serviceOptions[1]) {
      serviceOptions[1].style.border = '2px solid var(--primary-color)';
      serviceOptions[1].style.boxShadow = '0 5px 15px rgba(52, 152, 219, 0.2)';
    }
    if (serviceOptions[0]) {
      serviceOptions[0].style.border = '2px solid transparent';
      serviceOptions[0].style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }
    
    // Atualiza o texto do botão de continuar
    const continueButton = document.querySelector('.btn-secondary[onclick="startRepair()"]');
    if (continueButton) {
      continueButton.textContent = 'Continuar com o Plano Premium';
    }
  }
}

// Inicia o processo de reparo
function startRepair() {
  const diagnosticResults = document.getElementById('diagnostic-results');
  const repairProcess = document.getElementById('repair-process');
  
  if (diagnosticResults) {
    diagnosticResults.style.opacity = '0';
    setTimeout(() => {
      diagnosticResults.style.display = 'none';
      
      // Mostra o processo de reparo com animação
      if (repairProcess) {
        repairProcess.style.display = 'block';
        setTimeout(() => {
          repairProcess.style.opacity = '1';
          
          // Simula o progresso do reparo
          simulateRepairProgress();
        }, 100);
      }
    }, 300);
  }
}

// Simula o progresso do reparo
function simulateRepairProgress() {
  const repairSteps = document.querySelectorAll('.repair-step');
  
  // Atualiza o segundo passo após 3 segundos
  setTimeout(() => {
    if (repairSteps[1]) {
      repairSteps[1].innerHTML = '<p><i class="fas fa-check-circle" style="color: var(--secondary-color);"></i> Otimização de programas de inicialização concluída</p>';
    }
    
    // Inicia o terceiro passo
    if (repairSteps[2]) {
      repairSteps[2].innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Limpando arquivos temporários...</p><div class="progress"><div class="progress-bar" style="width: 0%">0%</div></div>';
      
      // Anima a barra de progresso
      const progressBar = repairSteps[2].querySelector('.progress-bar');
      if (progressBar) {
        animateProgressBar(progressBar, 100);
      }
    }
  }, 3000);
  
  // Atualiza o terceiro passo após 6 segundos
  setTimeout(() => {
    if (repairSteps[2]) {
      repairSteps[2].innerHTML = '<p><i class="fas fa-check-circle" style="color: var(--secondary-color);"></i> Limpeza de arquivos temporários concluída</p>';
    }
    
    // Inicia o quarto passo
    if (repairSteps[3]) {
      repairSteps[3].innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Atualizando antivírus...</p><div class="progress"><div class="progress-bar" style="width: 0%">0%</div></div>';
      
      // Anima a barra de progresso
      const progressBar = repairSteps[3].querySelector('.progress-bar');
      if (progressBar) {
        animateProgressBar(progressBar, 100);
      }
    }
  }, 6000);
  
  // Finaliza o reparo após 9 segundos
  setTimeout(() => {
    if (repairSteps[3]) {
      repairSteps[3].innerHTML = '<p><i class="fas fa-check-circle" style="color: var(--secondary-color);"></i> Atualização do antivírus concluída</p>';
    }
    
    // Adiciona mensagem de conclusão com animação
    const repairProcess = document.getElementById('repair-process');
    if (repairProcess) {
      const conclusionDiv = document.createElement('div');
      conclusionDiv.className = 'alert alert-success';
      conclusionDiv.style.opacity = '0';
      conclusionDiv.innerHTML = '<i class="fas fa-check-circle"></i> <strong>Reparo concluído com sucesso!</strong> Seu computador agora está otimizado e funcionando melhor.';
      
      repairProcess.querySelector('.card').appendChild(conclusionDiv);
      
      // Anima a entrada da mensagem
      setTimeout(() => {
        conclusionDiv.style.opacity = '1';
      }, 100);
      
      // Adiciona botão para voltar à página inicial
      const buttonDiv = document.createElement('div');
      buttonDiv.style.textAlign = 'center';
      buttonDiv.style.marginTop = '20px';
      buttonDiv.style.opacity = '0';
      
      const homeButton = document.createElement('a');
      homeButton.href = 'index.html';
      homeButton.className = 'btn btn-primary';
      homeButton.textContent = 'Voltar à Página Inicial';
      
      buttonDiv.appendChild(homeButton);
      repairProcess.querySelector('.card').appendChild(buttonDiv);
      
      // Anima a entrada do botão
      setTimeout(() => {
        buttonDiv.style.opacity = '1';
      }, 500);
    }
  }, 9000);
}

// Funcionalidades específicas da página de histórico
function initHistoryPage() {
  console.log('Inicializando funcionalidades da página de histórico');
  
  // Adiciona funcionalidade de filtro para itens de histórico
  const filterSelect = document.getElementById('history-filter');
  if (filterSelect) {
    filterSelect.addEventListener('change', function() {
      filterHistoryItems(this.value);
    });
  }
  
  // Adiciona funcionalidade para os botões de detalhes
  const detailButtons = document.querySelectorAll('.history-item .btn-details');
  detailButtons.forEach(button => {
    button.addEventListener('click', function() {
      const historyId = this.getAttribute('data-id');
      showHistoryDetails(historyId);
    });
  });
  
  // Adiciona funcionalidade para os botões de exportar
  const exportButtons = document.querySelectorAll('.history-item .btn-export');
  exportButtons.forEach(button => {
    button.addEventListener('click', function() {
      const historyId = this.getAttribute('data-id');
      exportHistoryReport(historyId);
    });
  });
  
  // Inicializa o gráfico de histórico se existir
  initHistoryChart();
}

// Filtra os itens de histórico por tipo
function filterHistoryItems(filter) {
  const historyItems = document.querySelectorAll('.history-item');
  
  historyItems.forEach(item => {
    const itemType = item.getAttribute('data-type');
    
    if (filter === 'all' || filter === itemType) {
      item.style.display = 'block';
      // Anima o item para aparecer suavemente
      setTimeout(() => {
        item.style.opacity = '1';
        item.style.transform = 'translateY(0)';
      }, 100);
    } else {
      // Anima o item para desaparecer suavemente
      item.style.opacity = '0';
      item.style.transform = 'translateY(10px)';
      setTimeout(() => {
        item.style.display = 'none';
      }, 300);
    }
  });
}

// Funcionalidades específicas da página de suporte
function initSupportPage() {
  console.log('Inicializando funcionalidades da página de suporte');
  
  // Adiciona funcionalidade para abrir o chat de suporte
  const supportChatButton = document.getElementById('support-chat-button');
  if (supportChatButton) {
    supportChatButton.addEventListener('click', function() {
      openSupportChat();
    });
  }
}

// Abre o chat de suporte
function openSupportChat() {
  console.log('Abrindo chat de suporte');
  
  // Implemente a lógica para abrir o chat de suporte
}

// Funcionalidades específicas da página de suporte
function initSupportPage() {
  console.log('Inicializando funcionalidades da página de suporte');
  
  // Adiciona funcionalidade para abrir o chat de suporte
  const supportChatButton = document.getElementById('support-chat-button');
  if (supportChatButton) {
    supportChatButton.addEventListener('click', function() {
      openSupportChat();
    });
  }
}

// Abre o chat de suporte
function openSupportChat() {
  console.log('Abrindo chat de suporte');
  
  // Implemente a lógica para abrir o chat de suporte
}