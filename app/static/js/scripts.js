/**
 * TechCare - JavaScript principal
 * 
 * Este arquivo contém as funções JavaScript principais para toda a aplicação,
 * incluindo inicialização, temas, tooltips, etc.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializa todos os tooltips do Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Inicializa todos os popovers do Bootstrap
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Gerenciamento de tema (claro/escuro)
    setupThemeToggle();
    
    // Animação suave para links de âncora
    setupSmoothScrolling();

    // Gerenciamento de mensagens flash
    setupFlashMessages();
    
    // Configura formato de data e hora para o fuso horário do Brasil
    setupDateTimeFormatting();
    
    // Configura atalhos de teclado para acessibilidade
    setupAccessibilityKeyboardShortcuts();
    
    // Aplica preferências de tamanho de fonte
    setupFontSize();
});

/**
 * Configurar o toggle de tema claro/escuro
 */
function setupThemeToggle() {
    // Verifica preferências do sistema
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Verifica se já existe uma preferência salva, caso contrário usa a preferência do sistema
    let currentTheme = localStorage.getItem('theme');
    if (!currentTheme) {
        currentTheme = prefersDarkScheme.matches ? 'dark' : 'light';
        localStorage.setItem('theme', currentTheme);
    }
    
    // Aplica o tema salvo
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
        document.documentElement.classList.add('dark-theme');
        if (document.querySelector('#theme-toggle')) {
            document.querySelector('#theme-toggle').checked = true;
        }
    }
    
    // Adiciona listener para mudanças nas preferências do sistema
    prefersDarkScheme.addEventListener('change', (e) => {
        // Só altera automaticamente se o usuário não tiver definido uma preferência explícita
        if (!localStorage.getItem('user-theme-preference')) {
            const newTheme = e.matches ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            updateTheme(newTheme);
        }
    });
    
    // Adiciona listener ao toggle de tema
    const themeToggle = document.querySelector('#theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', function(e) {
            const newTheme = e.target.checked ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            // Marca que o usuário fez uma escolha explícita
            localStorage.setItem('user-theme-preference', 'true');
            updateTheme(newTheme);
        });
    }
    
    // Configuração de alto contraste
    setupContrastToggle();
}

/**
 * Configura o toggle de alto contraste
 */
function setupContrastToggle() {
    // Verifica preferências de acessibilidade do sistema
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const prefersContrast = window.matchMedia('(prefers-contrast: more)');
    
    // Verifica se já existe uma preferência salva
    let highContrast = localStorage.getItem('high-contrast');
    
    // Se não houver preferência salva, verifica preferências do sistema
    if (highContrast === null) {
        // Se o usuário prefere contraste ou movimento reduzido, usa alto contraste
        highContrast = prefersContrast.matches || prefersReducedMotion.matches;
        localStorage.setItem('high-contrast', highContrast);
    } else {
        // Converte string para booleano
        highContrast = highContrast === 'true';
    }
    
    // Aplica a configuração de alto contraste
    if (highContrast) {
        document.body.classList.add('high-contrast');
        document.documentElement.classList.add('high-contrast');
    }
    
    // Adiciona listener para mudanças nas preferências do sistema
    prefersContrast.addEventListener('change', (e) => {
        if (!localStorage.getItem('user-contrast-preference')) {
            const newContrast = e.matches;
            localStorage.setItem('high-contrast', newContrast);
            updateContrast(newContrast);
        }
    });
    
    // Adiciona listener ao toggle de alto contraste
    const contrastToggle = document.querySelector('#contrast-toggle');
    if (contrastToggle) {
        // Define o estado inicial
        contrastToggle.checked = highContrast;
        
        // Adiciona listener ao toggle
        contrastToggle.addEventListener('change', function(e) {
            const isHighContrast = e.target.checked;
            // Marca que o usuário fez uma escolha explícita
            localStorage.setItem('user-contrast-preference', 'true');
            localStorage.setItem('high-contrast', isHighContrast);
            
            // Aplica a configuração
            if (isHighContrast) {
                document.body.classList.add('high-contrast');
                document.documentElement.classList.add('high-contrast');
            } else {
                document.body.classList.remove('high-contrast');
                document.documentElement.classList.remove('high-contrast');
            }
            
            // Atualiza no servidor
            updateContrast(isHighContrast);
        });
    }
}

/**
 * Atualiza o tema da aplicação
 */
function updateTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.documentElement.classList.add('dark-theme');
        if (document.querySelector('#theme-toggle')) {
            document.querySelector('#theme-toggle').checked = true;
        }
    } else {
        document.body.classList.remove('dark-theme');
        document.documentElement.classList.remove('dark-theme');
        if (document.querySelector('#theme-toggle')) {
            document.querySelector('#theme-toggle').checked = false;
        }
    }
    
    // Envia preferência para o servidor via fetch (para salvar no cookie)
    fetch('/set-theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ theme: theme })
    }).catch(error => console.error('Erro ao salvar preferência de tema:', error));
}

/**
 * Configura atalhos de teclado para acessibilidade
 */
function setupAccessibilityKeyboardShortcuts() {
    // Adiciona event listener para o botão de ajuda de acessibilidade
    const helpButton = document.getElementById('accessibility-help');
    if (helpButton) {
        helpButton.addEventListener('click', function() {
            showAccessibilityInfo();
        });
    }
    
    document.addEventListener('keydown', function(e) {
        // Alt+1: Ir para o conteúdo principal
        if (e.altKey && e.key === '1') {
            e.preventDefault();
            const mainContent = document.querySelector('main') || document.querySelector('.content');
            if (mainContent) {
                mainContent.setAttribute('tabindex', '-1');
                mainContent.focus();
                mainContent.scrollIntoView();
            }
        }
        
        // Alt+2: Alternar tema claro/escuro
        if (e.altKey && e.key === '2') {
            e.preventDefault();
            const themeToggle = document.querySelector('#theme-toggle');
            if (themeToggle) {
                themeToggle.checked = !themeToggle.checked;
                themeToggle.dispatchEvent(new Event('change'));
            }
        }
        
        // Alt+3: Ativar/desativar alto contraste
        if (e.altKey && e.key === '3') {
            e.preventDefault();
            const contrastToggle = document.querySelector('#contrast-toggle');
            if (contrastToggle) {
                contrastToggle.checked = !contrastToggle.checked;
                contrastToggle.dispatchEvent(new Event('change'));
            } else {
                // Se não houver toggle, alterna diretamente a classe
                document.body.classList.toggle('high-contrast');
                document.documentElement.classList.toggle('high-contrast');
                const isHighContrast = document.body.classList.contains('high-contrast');
                localStorage.setItem('high-contrast', isHighContrast);
                updateContrast(isHighContrast);
            }
        }
        
        // Alt+0: Mostrar informações de acessibilidade
        if (e.altKey && e.key === '0') {
            e.preventDefault();
            showAccessibilityInfo();
        }
        
        // Alt+H: Ir para a página inicial
        if (e.altKey && e.key === 'h') {
            e.preventDefault();
            window.location.href = '/';
        }
        
        // Alt+D: Ir para a página de diagnóstico
        if (e.altKey && e.key === 'd') {
            e.preventDefault();
            const diagnosticLink = document.querySelector('a[href*="diagnostic"]');
            if (diagnosticLink) {
                window.location.href = diagnosticLink.getAttribute('href');
            }
        }
        
        // Alt+R: Ir para a página de drivers
        if (e.altKey && e.key === 'r') {
            e.preventDefault();
            const driversLink = document.querySelector('a[href*="drivers"]');
            if (driversLink) {
                window.location.href = driversLink.getAttribute('href');
            }
        }
        
        // Alt+C: Ir para a página de limpeza
        if (e.altKey && e.key === 'c') {
            e.preventDefault();
            const cleanerLink = document.querySelector('a[href*="cleaner"]');
            if (cleanerLink) {
                window.location.href = cleanerLink.getAttribute('href');
            }
        }
        
        // Alt+F: Aumentar tamanho da fonte
        if (e.altKey && e.key === 'f') {
            e.preventDefault();
            increaseFontSize();
        }
        
        // Alt+G: Diminuir tamanho da fonte
        if (e.altKey && e.key === 'g') {
            e.preventDefault();
            decreaseFontSize();
        }
    });
}

/**
 * Mostra informações sobre atalhos de acessibilidade
 */
function showAccessibilityInfo() {
    const infoElement = document.querySelector('.accessibility-info');
    if (infoElement) {
        // Cria um modal Bootstrap
        const modalHTML = `
            <div class="modal fade" id="accessibilityInfoModal" tabindex="-1" aria-labelledby="accessibilityInfoModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="accessibilityInfoModalLabel">Atalhos de Acessibilidade</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                        </div>
                        <div class="modal-body">
                            <h6>Navegação</h6>
                            <ul>
                                <li><strong>Alt+1</strong>: Ir para o conteúdo principal</li>
                                <li><strong>Alt+H</strong>: Ir para a página inicial</li>
                                <li><strong>Alt+D</strong>: Ir para a página de diagnóstico</li>
                                <li><strong>Alt+R</strong>: Ir para a página de drivers</li>
                                <li><strong>Alt+C</strong>: Ir para a página de limpeza</li>
                            </ul>
                            
                            <h6>Personalização</h6>
                            <ul>
                                <li><strong>Alt+2</strong>: Alternar tema claro/escuro</li>
                                <li><strong>Alt+3</strong>: Alternar alto contraste</li>
                                <li><strong>Alt+F</strong>: Aumentar tamanho da fonte</li>
                                <li><strong>Alt+G</strong>: Diminuir tamanho da fonte</li>
                            </ul>
                            
                            <h6>Geral</h6>
                            <ul>
                                <li><strong>Alt+0</strong>: Mostrar esta ajuda</li>
                                <li><strong>Tab</strong>: Navegar entre os elementos interativos da página</li>
                                <li><strong>Shift+Tab</strong>: Navegar para trás entre os elementos interativos</li>
                                <li><strong>Enter</strong>: Ativar o elemento selecionado</li>
                            </ul>
                            
                            <p class="mt-3">Estas funcionalidades estão disponíveis para melhorar a acessibilidade da aplicação,
                            em conformidade com as diretrizes WCAG 2.1.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Adiciona o modal ao corpo da página
        if (!document.getElementById('accessibilityInfoModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }
        
        // Exibe o modal
        const modal = new bootstrap.Modal(document.getElementById('accessibilityInfoModal'));
        modal.show();
    }
}

/**
 * Atualiza as preferências do usuário para alto contraste
 */
function updateContrast(isHighContrast) {
    // Envia preferência para o servidor via fetch
    fetch('/set-contrast', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ high_contrast: isHighContrast.toString() })
    }).catch(error => console.error('Erro ao salvar preferência de alto contraste:', error));
}

/**
 * Configura o smooth scrolling para links de âncora
 */
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
                
                // Coloca foco no elemento - acessibilidade
                if (targetElement.tabIndex < 0) {
                    targetElement.tabIndex = -1;
                }
                targetElement.focus();
            }
        });
    });
}

/**
 * Configura o fechamento automático de mensagens flash
 */
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    flashMessages.forEach(function(message) {
        // Adiciona botão de fechamento
        if (!message.querySelector('.btn-close')) {
            const closeButton = document.createElement('button');
            closeButton.type = 'button';
            closeButton.className = 'btn-close';
            closeButton.setAttribute('data-bs-dismiss', 'alert');
            closeButton.setAttribute('aria-label', 'Fechar');
            message.appendChild(closeButton);
        }
        
        // Auto fecha após 5 segundos
        setTimeout(function() {
            try {
                const bsAlert = new bootstrap.Alert(message);
                bsAlert.close();
            } catch (e) {
                message.style.display = 'none';
            }
        }, 5000);
    });
}

/**
 * Configura formatação de data e hora para o fuso horário do Brasil
 */
function setupDateTimeFormatting() {
    document.querySelectorAll('.format-datetime').forEach(element => {
        const timestamp = element.getAttribute('data-timestamp');
        if (timestamp) {
            const date = new Date(parseInt(timestamp) * 1000);
            const options = { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            element.textContent = date.toLocaleDateString('pt-BR', options);
        }
    });
    
    document.querySelectorAll('.format-date').forEach(element => {
        const timestamp = element.getAttribute('data-timestamp');
        if (timestamp) {
            const date = new Date(parseInt(timestamp) * 1000);
            const options = { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric'
            };
            element.textContent = date.toLocaleDateString('pt-BR', options);
        }
    });
}

/**
 * Formata bytes para exibição amigável (KB, MB, GB)
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Formata percentual para exibição
 */
function formatPercent(value) {
    return value.toFixed(1) + '%';
}

/**
 * Cria um gráfico de medidor (gauge) para exibir informação
 */
function createGaugeChart(elementId, value, maxValue, redZone = 80, yellowZone = 60) {
    // Verifica se o elemento existe
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Calcula a porcentagem
    const percentage = (value / maxValue) * 100;
    
    // Determina a cor com base nos limiares
    let color = '#28a745'; // Verde
    if (percentage >= redZone) {
        color = '#dc3545'; // Vermelho
    } else if (percentage >= yellowZone) {
        color = '#ffc107'; // Amarelo
    }
    
    // Gera o HTML para o gauge
    element.innerHTML = `
        <div class="gauge-container">
            <div class="gauge">
                <div class="gauge-fill" style="transform: rotate(${percentage * 1.8}deg); background-color: ${color};"></div>
                <div class="gauge-cover">
                    <span class="gauge-value">${value}</span>
                    <span class="gauge-label">${percentage.toFixed(0)}%</span>
                </div>
            </div>
            <div class="gauge-info">${element.getAttribute('data-label') || ''}</div>
        </div>
    `;
}

/**
 * Cria uma tabela de processos
 */
function createProcessTable(elementId, processes) {
    const element = document.getElementById(elementId);
    if (!element || !processes) return;
    
    let tableHTML = `
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>Nome</th>
                    <th>PID</th>
                    <th>CPU %</th>
                    <th>Memória</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    processes.forEach(process => {
        tableHTML += `
            <tr>
                <td>${process.name}</td>
                <td>${process.pid}</td>
                <td>${process.cpu_percent.toFixed(1)}%</td>
                <td>${formatBytes(process.memory_info)}</td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    element.innerHTML = tableHTML;
}

/**
 * Configura o tamanho da fonte com base nas preferências salvas
 */
function setupFontSize() {
    // Verifica se existe uma preferência de tamanho de fonte salva
    const savedFontSize = localStorage.getItem('font-size');
    if (savedFontSize) {
        document.documentElement.style.fontSize = savedFontSize;
    }
    
    // Adiciona botões de acessibilidade para controle de fonte ao final da barra de navegação
    const navbarRight = document.querySelector('.navbar-nav.ms-auto');
    if (navbarRight && !document.querySelector('.font-size-controls')) {
        const fontControls = document.createElement('li');
        fontControls.className = 'nav-item font-size-controls d-flex align-items-center me-3';
        fontControls.innerHTML = `
            <span class="me-2 d-none d-sm-inline text-white" title="Tamanho da fonte"><i class="fas fa-font"></i></span>
            <button class="btn btn-sm btn-outline-light me-1" id="font-decrease" title="Diminuir fonte (Alt+G)">A-</button>
            <button class="btn btn-sm btn-outline-light" id="font-increase" title="Aumentar fonte (Alt+F)">A+</button>
        `;
        navbarRight.insertBefore(fontControls, navbarRight.firstChild);
        
        // Adiciona event listeners aos botões para controle de font-size
        document.getElementById('font-increase').addEventListener('click', function() {
            increaseFontSize();
        });
        
        document.getElementById('font-decrease').addEventListener('click', function() {
            decreaseFontSize();
        });
    }
    
    // Também adiciona keyboard shortcuts para tamanho de fonte
    document.addEventListener('keydown', function(e) {
        // Alt+F: Aumentar tamanho da fonte
        if (e.altKey && e.key === 'f') {
            e.preventDefault();
            increaseFontSize();
        }
        
        // Alt+G: Diminuir tamanho da fonte
        if (e.altKey && e.key === 'g') {
            e.preventDefault();
            decreaseFontSize();
        }
    });
}

/**
 * Aumenta o tamanho da fonte
 */
function increaseFontSize() {
    const currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    const newSize = (currentSize + 1) + 'px';
    document.documentElement.style.fontSize = newSize;
    localStorage.setItem('font-size', newSize);
    console.log('Font size increased to: ' + newSize);
}

/**
 * Diminui o tamanho da fonte
 */
function decreaseFontSize() {
    const currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    if (currentSize > 10) {
        const newSize = (currentSize - 1) + 'px';
        document.documentElement.style.fontSize = newSize;
        localStorage.setItem('font-size', newSize);
        console.log('Font size decreased to: ' + newSize);
    }
}

// Exporta funções para uso global
window.TechCare = {
    formatBytes,
    formatPercent,
    createGaugeChart,
    createProcessTable
}; 