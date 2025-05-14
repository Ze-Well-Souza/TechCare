// Classe para gerenciar a conversão de vídeos e download de redes sociais
class ConversaoTechCare {
    constructor() {
        this.formatosSuportados = {
            video: ['mp4', 'avi', 'mkv', 'mov', 'webm'],
            audio: ['mp3', 'wav', 'ogg', 'aac', 'm4a']
        };
        
        this.redesSociais = [
            { nome: 'YouTube', icone: 'youtube', dominios: ['youtube.com', 'youtu.be'] },
            { nome: 'Instagram', icone: 'instagram', dominios: ['instagram.com'] },
            { nome: 'TikTok', icone: 'tiktok', dominios: ['tiktok.com'] },
            { nome: 'Facebook', icone: 'facebook', dominios: ['facebook.com', 'fb.com'] },
            { nome: 'Twitter', icone: 'twitter', dominios: ['twitter.com', 'x.com'] }
        ];
        
        this.conversaoEmAndamento = false;
        this.downloadEmAndamento = false;
        this.logs = [];
        
        // Inicializar eventos
        this.inicializarEventos();
    }
    
    // Inicializar eventos da interface
    inicializarEventos() {
        // Eventos para conversão de arquivos
        const btnConverterArquivo = document.getElementById('converter-arquivo');
        const inputArquivo = document.getElementById('arquivo-input');
        
        if (btnConverterArquivo && inputArquivo) {
            btnConverterArquivo.addEventListener('click', () => {
                inputArquivo.click();
            });
            
            inputArquivo.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.iniciarConversaoArquivo(e.target.files[0]);
                }
            });
        }
        
        // Eventos para download de vídeos
        const btnBaixarVideo = document.getElementById('baixar-video');
        const inputUrl = document.getElementById('url-input');
        
        if (btnBaixarVideo && inputUrl) {
            btnBaixarVideo.addEventListener('click', () => {
                const url = inputUrl.value.trim();
                if (url) {
                    this.iniciarDownloadVideo(url);
                } else {
                    this.mostrarMensagem('Por favor, insira uma URL válida', 'erro');
                }
            });
            
            // Detectar rede social ao colar URL
            inputUrl.addEventListener('paste', (e) => {
                setTimeout(() => {
                    const url = inputUrl.value.trim();
                    if (url) {
                        const redeSocial = this.detectarRedeSocial(url);
                        if (redeSocial) {
                            this.mostrarMensagem(`URL do ${redeSocial.nome} detectada`, 'info');
                            this.atualizarOpcoesFormato(redeSocial.nome);
                        }
                    }
                }, 100);
            });
        }
        
        // Eventos para opções de formato
        const opcoesFormato = document.querySelectorAll('.format-option');
        if (opcoesFormato.length > 0) {
            opcoesFormato.forEach(opcao => {
                opcao.addEventListener('click', () => {
                    // Remover classe ativa de todas as opções
                    opcoesFormato.forEach(op => op.classList.remove('active'));
                    // Adicionar classe ativa à opção clicada
                    opcao.classList.add('active');
                });
            });
        }
    }
    
    // Detectar rede social a partir da URL
    detectarRedeSocial(url) {
        try {
            const urlObj = new URL(url);
            const dominio = urlObj.hostname.replace('www.', '');
            
            for (const rede of this.redesSociais) {
                if (rede.dominios.some(d => dominio.includes(d))) {
                    return rede;
                }
            }
        } catch (erro) {
            console.error('URL inválida:', erro);
        }
        
        return null;
    }
    
    // Atualizar opções de formato com base na rede social
    atualizarOpcoesFormato(redeSocial) {
        const containerFormatos = document.getElementById('format-options');
        if (!containerFormatos) return;
        
        // Resetar seleção
        const opcoesFormato = containerFormatos.querySelectorAll('.format-option');
        opcoesFormato.forEach(op => op.classList.remove('active'));
        
        // Destacar formatos recomendados
        switch (redeSocial) {
            case 'YouTube':
                // Destacar MP4 e MP3 como recomendados
                opcoesFormato.forEach(op => {
                    if (op.dataset.format === 'mp4' || op.dataset.format === 'mp3') {
                        op.classList.add('recommended');
                    }
                });
                // Selecionar MP4 por padrão
                const mp4Option = Array.from(opcoesFormato).find(op => op.dataset.format === 'mp4');
                if (mp4Option) mp4Option.classList.add('active');
                break;
                
            case 'Instagram':
            case 'TikTok':
                // Destacar MP4 como recomendado
                opcoesFormato.forEach(op => {
                    if (op.dataset.format === 'mp4') {
                        op.classList.add('recommended');
                        op.classList.add('active');
                    }
                });
                break;
                
            case 'Twitter':
            case 'Facebook':
                // Destacar MP4 e GIF como recomendados
                opcoesFormato.forEach(op => {
                    if (op.dataset.format === 'mp4' || op.dataset.format === 'gif') {
                        op.classList.add('recommended');
                    }
                    if (op.dataset.format === 'mp4') {
                        op.classList.add('active');
                    }
                });
                break;
        }
    }
    
    // Iniciar conversão de arquivo
    iniciarConversaoArquivo(arquivo) {
        if (this.conversaoEmAndamento) {
            this.mostrarMensagem('Já existe uma conversão em andamento', 'erro');
            return;
        }
        
        this.conversaoEmAndamento = true;
        this.mostrarMensagem(`Iniciando conversão do arquivo: ${arquivo.name}`, 'info');
        this.adicionarLog(`Iniciando conversão do arquivo: ${arquivo.name}`);
        
        // Verificar tipo de arquivo
        const tipoArquivo = arquivo.type.split('/')[0]; // 'video', 'audio', etc.
        const extensao = arquivo.name.split('.').pop().toLowerCase();
        
        // Verificar se o formato é suportado
        if (tipoArquivo !== 'video' && tipoArquivo !== 'audio') {
            this.mostrarMensagem('Formato de arquivo não suportado. Por favor, selecione um arquivo de vídeo ou áudio.', 'erro');
            this.conversaoEmAndamento = false;
            return;
        }
        
        // Simular processo de conversão
        this.simularProcessoConversao(arquivo, tipoArquivo);
    }
    
    // Simular processo de conversão
    simularProcessoConversao(arquivo, tipoArquivo) {
        const progressoConversao = document.getElementById('conversion-progress');
        const mensagemConversao = document.getElementById('conversion-message');
        
        if (progressoConversao && mensagemConversao) {
            progressoConversao.style.width = '0%';
            progressoConversao.setAttribute('aria-valuenow', 0);
            mensagemConversao.textContent = 'Preparando arquivo para conversão...';
        }
        
        let progresso = 0;
        const intervalo = setInterval(() => {
            progresso += 5;
            
            if (progressoConversao) {
                progressoConversao.style.width = `${progresso}%`;
                progressoConversao.setAttribute('aria-valuenow', progresso);
            }
            
            // Atualizar mensagens em pontos específicos
            if (progresso === 20) {
                if (mensagemConversao) mensagemConversao.textContent = 'Analisando arquivo...';
                this.adicionarLog('Analisando arquivo e verificando integridade');
            } else if (progresso === 40) {
                if (mensagemConversao) mensagemConversao.textContent = 'Processando conteúdo...';
                this.adicionarLog('Processando conteúdo do arquivo');
            } else if (progresso === 60) {
                if (mensagemConversao) mensagemConversao.textContent = 'Convertendo para o formato selecionado...';
                this.adicionarLog('Convertendo para o formato selecionado');
            } else if (progresso === 80) {
                if (mensagemConversao) mensagemConversao.textContent = 'Finalizando conversão...';
                this.adicionarLog('Finalizando processo de conversão');
            }
            
            if (progresso >= 100) {
                clearInterval(intervalo);
                if (mensagemConversao) mensagemConversao.textContent = 'Conversão concluída com sucesso!';
                this.adicionarLog('Conversão concluída com sucesso');
                
                // Mostrar resultado da conversão
                this.mostrarResultadoConversao(arquivo, tipoArquivo);
                
                this.conversaoEmAndamento = false;
            }
        }, 200);
    }
    
    // Mostrar resultado da conversão
    mostrarResultadoConversao(arquivo, tipoArquivo) {
        const resultadoConversao = document.getElementById('conversion-result');
        if (!resultadoConversao) return;
        
        // Determinar formato de saída (simulado)
        const formatoSaida = tipoArquivo === 'video' ? 'mp4' : 'mp3';
        const nomeArquivoSaida = arquivo.name.split('.')[0] + '.' + formatoSaida;
        
        // Mostrar resultado
        resultadoConversao.style.display = 'block';
        resultadoConversao.innerHTML = `
            <h4>Conversão Concluída</h4>
            <p>Arquivo original: ${arquivo.name}</p>
            <p>Arquivo convertido: ${nomeArquivoSaida}</p>
            <p>Tamanho: ${this.formatarTamanho(arquivo.size * 0.8)}</p>
            <a href="#" class="download-link" onclick="alert('Download simulado: ${nomeArquivoSaida}'); return false;">
                <i class="fas fa-download"></i> Baixar Arquivo Convertido
            </a>
        `;
    }
    
    // Iniciar download de vídeo
    iniciarDownloadVideo(url) {
        if (this.downloadEmAndamento) {
            this.mostrarMensagem('Já existe um download em andamento', 'erro');
            return;
        }
        
        this.downloadEmAndamento = true;
        
        // Detectar rede social
        const redeSocial = this.detectarRedeSocial(url);
        if (!redeSocial) {
            this.mostrarMensagem('URL não reconhecida. Por favor, insira uma URL válida de uma rede social suportada.', 'erro');
            this.downloadEmAndamento = false;
            return;
        }
        
        this.mostrarMensagem(`Iniciando download de vídeo do ${redeSocial.nome}`, 'info');
        this.adicionarLog(`Iniciando download de vídeo do ${redeSocial.nome}: ${url}`);
        
        // Obter formato selecionado
        const formatoSelecionado = this.obterFormatoSelecionado();
        
        // Simular processo de download
        this.simularProcessoDownload(url, redeSocial, formatoSelecionado);
    }
    
    // Obter formato selecionado
    obterFormatoSelecionado() {
        const opcaoAtiva = document.querySelector('.format-option.active');
        return opcaoAtiva ? opcaoAtiva.dataset.format : 'mp4'; // Padrão: mp4
    }
    
    // Simular processo de download
    simularProcessoDownload(url, redeSocial, formato) {
        const progressoDownload = document.getElementById('download-progress');
        const mensagemDownload = document.getElementById('download-message');
        
        if (progressoDownload && mensagemDownload) {
            progressoDownload.style.width = '0%';
            progressoDownload.setAttribute('aria-valuenow', 0);
            mensagemDownload.textContent = `Conectando ao ${redeSocial.nome}...`;
        }
        
        let progresso = 0;
        const intervalo = setInterval(() => {
            progresso += 5;
            
            if (progressoDownload) {
                progressoDownload.style.width = `${progresso}%`;
                progressoDownload.setAttribute('aria-valuenow', progresso);
            }
            
            // Atualizar mensagens em pontos específicos
            if (progresso === 20) {
                if (mensagemDownload) mensagemDownload.textContent = 'Extraindo informações do vídeo...';
                this.adicionarLog('Extraindo informações do vídeo');
            } else if (progresso === 40) {
                if (mensagemDownload) mensagemDownload.textContent = 'Baixando conteúdo...';
                this.adicionarLog('Baixando conteúdo do vídeo');
            } else if (progresso === 60) {
                if (mensagemDownload) mensagemDownload.textContent = `Convertendo para ${formato}...`;
                this.adicionarLog(`Convertendo vídeo para formato ${formato}`);
            } else if (progresso === 80) {
                if (mensagemDownload) mensagemDownload.textContent = 'Finalizando download...';
                this.adicionarLog('Finalizando processo de download');
            }
            
            if (progresso >= 100) {
                clearInterval(intervalo);
                if (mensagemDownload) mensagemDownload.textContent = 'Download concluído com sucesso!';
                this.adicionarLog('Download concluído com sucesso');
                
                // Mostrar resultado do download
                this.mostrarResultadoDownload(url, redeSocial, formato);
                
                this.downloadEmAndamento = false;
            }
        }, 200);
    }
    
    // Mostrar resultado do download
    mostrarResultadoDownload(url, redeSocial, formato) {
        const resultadoDownload = document.getElementById('download-result');
        if (!resultadoDownload) return;
        
        // Gerar nome de arquivo simulado
        const idVideo = this.extrairIdVideo(url, redeSocial);
        const nomeArquivo = `${redeSocial.nome.toLowerCase()}_${idVideo}.${formato}`;
        const tamanhoArquivo = this.gerarTamanhoAleatorio(formato);
        
        // Mostrar resultado
        resultadoDownload.style.display = 'block';
        resultadoDownload.innerHTML = `
            <h4>Download Concluído</h4>
            <p>Fonte: ${redeSocial.nome}</p>
            <p>Arquivo: ${nomeArquivo}</p>
            <p>Tamanho: ${tamanhoArquivo}</p>
            <a href="#" class="download-link" onclick="alert('Download simulado: ${nomeArquivo}'); return false;">
                <i class="fas fa-download"></i> Baixar Vídeo
            </a>
        `;
    }
    
    // Extrair ID do vídeo da URL
    extrairIdVideo(url, redeSocial) {
        try {
            const urlObj = new URL(url);
            
            switch (redeSocial.nome) {
                case 'YouTube':
                    // youtube.com/watch?v=VIDEO_ID ou youtu.be/VIDEO_ID
                    if (urlObj.hostname.includes('youtu.be')) {
                        return urlObj.pathname.substring(1);
                    } else {
                        return urlObj.searchParams.get('v') || 'video';
                    }
                    
                case 'Instagram':
                    // instagram.com/p/CODE/ ou instagram.com/reel/CODE/
                    const match = urlObj.pathname.match(/\/(p|reel|tv)\/([^\/]+)/);
                    return match ? match[2] : 'video';
                    
                case 'TikTok':
                    // tiktok.com/@user/video/ID
                    const tiktokMatch = urlObj.pathname.match(/\/video\/(\d+)/);
                    return tiktokMatch ? tiktokMatch[1] : 'video';
                    
                default:
                    return 'video';

(Content truncated due to size limit. Use line ranges to read in chunks)