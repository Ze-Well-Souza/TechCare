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