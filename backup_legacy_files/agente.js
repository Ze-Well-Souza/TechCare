// Agente interativo (chatbot) para o TechZe
// Este script implementa um assistente virtual que fornece orientações de manutenção

class AgenteInterativo {
  constructor() {
    this.historico = [];
    this.contexto = {};
    this.ultimaManutencao = null;
    this.etapaAtual = null;
    this.db = null;
    
    // Inicializa a conexão com o banco de dados se disponível
    if (typeof DiagnosticoDatabase !== 'undefined') {
      this.db = new DiagnosticoDatabase();
    }
    
    // Base de conhecimento para respostas
    this.baseConhecimento = {
      saudacoes: [
        "Olá! Sou o assistente virtual da TechZe. Estou aqui para ajudar com a manutenção do seu computador.",
        "Bem-vindo à TechZe! Estou aqui para guiá-lo pelas etapas de manutenção do seu computador.",
        "Olá! Sou especialista em guiar manutenções de computadores. Como posso ajudar hoje?"
      ],
      manutencao: {
        processo: "Nossa manutenção guiada divide tarefas complexas em passos simples que você mesmo pode realizar. Você escolhe o problema a resolver, e eu te mostro exatamente o que fazer, com instruções detalhadas e imagens.",
        beneficios: "Ao realizar a manutenção você mesmo, você não só economiza dinheiro, mas também aprende sobre seu computador e pode resolver problemas futuros mais facilmente.",
        dificuldade: "Não se preocupe! As instruções são detalhadas e projetadas para qualquer pessoa seguir, mesmo sem conhecimento técnico. Se tiver dúvidas, estou aqui para ajudar a cada passo."
      },
      problemas_comuns: {
        lentidao: "A lentidão do computador pode ser causada por vários fatores. Nosso guia de otimização de desempenho vai te mostrar como: 1) Encerrar programas que consomem muitos recursos, 2) Limpar arquivos temporários, 3) Desativar programas de inicialização desnecessários, 4) Verificar se há vírus ou malware.",
        espaco_disco: "Para liberar espaço em disco, nosso guia te mostrará como: 1) Identificar arquivos grandes que podem ser movidos ou excluídos, 2) Usar a ferramenta de Limpeza de Disco do Windows, 3) Desinstalar programas não utilizados, 4) Verificar arquivos duplicados.",
        inicializacao: "Para acelerar a inicialização do Windows, você aprenderá a: 1) Desativar programas de inicialização desnecessários, 2) Verificar serviços que podem ser otimizados, 3) Configurar o Modo de Inicialização Rápida, 4) Verificar a fragmentação do disco (para HDDs).",
        drivers: "Manter seus drivers atualizados é importante para o desempenho e compatibilidade. Nosso guia mostra como: 1) Identificar drivers desatualizados, 2) Baixar atualizações do site do fabricante, 3) Instalar corretamente os drivers, 4) Verificar se há problemas após a atualização.",
        seguranca: "Para manter seu computador seguro, nosso guia ensina a: 1) Verificar se o Windows Defender está ativo, 2) Executar uma verificação completa do sistema, 3) Atualizar o Windows com patches de segurança, 4) Verificar configurações de firewall."
      },
      dicas_manutencao: {
        frequencia: "Recomendamos realizar uma manutenção básica mensalmente (limpeza de arquivos temporários e verificação de inicialização) e uma manutenção completa a cada 3-6 meses.",
        prevencao: "Para evitar problemas futuros: 1) Não instale software desnecessário, 2) Mantenha o Windows e antivírus atualizados, 3) Faça backups regulares, 4) Não sobrecarregue o disco rígido (mantenha pelo menos 15% livre).",
        hardware: "Se após a otimização de software seu computador ainda estiver lento, pode ser hora de considerar upgrades de hardware: adicionar mais RAM, substituir um HD por SSD, ou em casos extremos, atualizar o processador."
      },
      resolucao_problemas: {
        etapa_falhou: "Se você não consegue completar uma etapa, podemos tentar uma abordagem alternativa. Me diga exatamente em qual ponto você está tendo dificuldade, e o que acontece quando tenta seguir as instruções.",
        erro_windows: "Se você encontrou uma mensagem de erro, me informe o código ou texto exato. Isso ajudará a identificar a causa específica e a solução apropriada.",
        aplicativo_travado: "Se um aplicativo travar durante a manutenção, você pode forçar o encerramento pelo Gerenciador de Tarefas (Ctrl+Shift+Esc). Selecione o aplicativo e clique em 'Finalizar Tarefa'. Em seguida, podemos tentar uma abordagem alternativa.",
        permissao_admin: "Algumas tarefas de manutenção exigem permissões de administrador. Se você vir um prompt de controle de conta de usuário (UAC), clique em 'Sim' para permitir a operação. Se não tiver acesso de administrador, talvez precise de assistência do administrador do sistema."
      }
    };
  }
  
  // Processa a mensagem do usuário e retorna uma resposta
  async processarMensagem(mensagem) {
    try {
      // Adiciona a mensagem ao histórico
      this.historico.push({ tipo: 'usuario', texto: mensagem });
      
      // Analisa a mensagem e gera uma resposta
      const resposta = await this.gerarResposta(mensagem);
      
      // Adiciona a resposta ao histórico
      this.historico.push({ tipo: 'agente', texto: resposta });
      
      return resposta;
    } catch (error) {
      console.error('Erro ao processar mensagem:', error);
      return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.";
    }
  }
  
  // Gera uma resposta com base na mensagem do usuário
  async gerarResposta(mensagem) {
    // Converte a mensagem para minúsculas para facilitar a comparação
    const mensagemLower = mensagem.toLowerCase();
    
    // Verifica o contexto atual da conversa
    if (this.etapaAtual) {
      return this.responderSobreEtapaAtual(mensagemLower);
    }
    
    // Verifica se é uma saudação
    if (this.ehSaudacao(mensagemLower)) {
      return this.obterRespostaAleatoria(this.baseConhecimento.saudacoes);
    }
    
    // Verifica se é uma pergunta sobre manutenção guiada
    if (this.contemPalavrasChave(mensagemLower, ['como funciona', 'manutenção guiada', 'como usar', 'guia', 'passo a passo'])) {
      return this.baseConhecimento.manutencao.processo;
    }
    
    // Verifica se é uma pergunta sobre dificuldade
    if (this.contemPalavrasChave(mensagemLower, ['difícil', 'dificil', 'complicado', 'complexo', 'não sei', 'nao sei'])) {
      return this.baseConhecimento.manutencao.dificuldade;
    }
    
    // Verifica se é uma pergunta sobre problemas de lentidão
    if (this.contemPalavrasChave(mensagemLower, ['lento', 'devagar', 'lentidão', 'lentidao', 'travando'])) {
      return this.baseConhecimento.problemas_comuns.lentidao;
    }
    
    // Verifica se é uma pergunta sobre espaço em disco
    if (this.contemPalavrasChave(mensagemLower, ['espaço', 'espaco', 'disco cheio', 'armazenamento', 'liberar', 'hd', 'ssd'])) {
      return this.baseConhecimento.problemas_comuns.espaco_disco;
    }
    
    // Verifica se é uma pergunta sobre inicialização
    if (this.contemPalavrasChave(mensagemLower, ['inicialização', 'inicializacao', 'iniciar', 'demora para ligar', 'boot'])) {
      return this.baseConhecimento.problemas_comuns.inicializacao;
    }
    
    // Verifica se é uma pergunta sobre drivers
    if (this.contemPalavrasChave(mensagemLower, ['driver', 'drivers', 'atualizar drivers', 'hardware'])) {
      return this.baseConhecimento.problemas_comuns.drivers;
    }
    
    // Verifica se é uma pergunta sobre segurança
    if (this.contemPalavrasChave(mensagemLower, ['segurança', 'seguranca', 'vírus', 'virus', 'malware', 'defender'])) {
      return this.baseConhecimento.problemas_comuns.seguranca;
    }
    
    // Verifica se é uma pergunta sobre frequência de manutenção
    if (this.contemPalavrasChave(mensagemLower, ['frequência', 'frequencia', 'frequente', 'regularmente', 'quando fazer'])) {
      return this.baseConhecimento.dicas_manutencao.frequencia;
    }
    
    // Verifica se é uma pergunta sobre prevenção
    if (this.contemPalavrasChave(mensagemLower, ['prevenir', 'prevenção', 'prevencao', 'evitar', 'futuro'])) {
      return this.baseConhecimento.dicas_manutencao.prevencao;
    }
    
    // Verifica se o usuário está com problemas em uma etapa
    if (this.contemPalavrasChave(mensagemLower, ['não consigo', 'nao consigo', 'problema', 'dificuldade', 'ajuda com', 'etapa'])) {
      if (this.contemPalavrasChave(mensagemLower, ['erro', 'mensagem de erro', 'aviso'])) {
        return this.baseConhecimento.resolucao_problemas.erro_windows;
      } else if (this.contemPalavrasChave(mensagemLower, ['travou', 'travado', 'congelou'])) {
        return this.baseConhecimento.resolucao_problemas.aplicativo_travado;
      } else if (this.contemPalavrasChave(mensagemLower, ['permissão', 'permissao', 'administrador', 'admin'])) {
        return this.baseConhecimento.resolucao_problemas.permissao_admin;
      } else {
        return this.baseConhecimento.resolucao_problemas.etapa_falhou;
      }
    }
    
    // Verifica se é uma pergunta sobre hardware
    if (this.contemPalavrasChave(mensagemLower, ['hardware', 'upgrade', 'melhorar', 'comprar', 'peça', 'peca'])) {
      return this.baseConhecimento.dicas_manutencao.hardware;
    }
    
    // Resposta padrão para mensagens não reconhecidas
    return "Posso ajudar com orientações para manutenção do seu computador. Você pode me perguntar sobre como resolver problemas de lentidão, liberar espaço em disco, acelerar a inicialização, atualizar drivers ou melhorar a segurança. Se estiver seguindo nosso guia passo a passo e precisar de ajuda com alguma etapa específica, me avise.";
  }
  
  // Responde sobre a etapa atual que o usuário está realizando
  responderSobreEtapaAtual(mensagem) {
    // Verifica se o usuário está com dificuldade
    if (this.contemPalavrasChave(mensagem, ['não consigo', 'nao consigo', 'dificuldade', 'problema', 'como faço'])) {
      return `Para a etapa de "${this.etapaAtual.titulo}", aqui está uma explicação mais detalhada:\n\n${this.etapaAtual.instrucoes_detalhadas || this.etapaAtual.instrucoes}\n\nSe ainda estiver com dificuldade, podemos tentar uma abordagem alternativa. Me diga exatamente onde você está travando.`;
    }
    
    // Verifica se o usuário está perguntando por que esta etapa é necessária
    if (this.contemPalavrasChave(mensagem, ['por que', 'porque', 'qual motivo', 'para que'])) {
      return `Esta etapa é importante porque ${this.etapaAtual.justificativa || 'ajuda a melhorar o desempenho do seu computador'}. ${this.etapaAtual.beneficio || 'Ao completá-la, você notará melhorias significativas no funcionamento do sistema.'}`;
    }
    
    // Verifica se o usuário completou a etapa
    if (this.contemPalavrasChave(mensagem, ['concluí', 'conclui', 'terminei', 'feito', 'pronto'])) {
      return "Excelente! Você pode marcar esta etapa como concluída no guia e avançar para a próxima. Se tiver dúvidas sobre a próxima etapa, estou aqui para ajudar.";
    }
    
    // Verifica se o usuário está perguntando sobre próximos passos
    if (this.contemPalavrasChave(mensagem, ['próximo', 'proximo', 'próxima', 'proxima', 'depois'])) {
      return "Após concluir esta etapa, você pode clicar no botão 'Sim, concluí esta etapa' para avançar para a próxima tarefa. O guia te levará sequencialmente pelos passos necessários para resolver o problema.";
    }
    
    // Resposta padrão sobre a etapa atual
    return `Você está na etapa "${this.etapaAtual.titulo}". Se estiver com dúvidas específicas sobre como realizar esta etapa, ou se encontrou algum problema, me informe para que eu possa ajudar melhor.`;
  }
  
  // Verifica se a mensagem é uma saudação
  ehSaudacao(mensagem) {
    const saudacoes = ['olá', 'ola', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'e aí', 'e ai', 'hello', 'hi'];
    return saudacoes.some(saudacao => mensagem.includes(saudacao));
  }
  
  // Verifica se a mensagem contém palavras-chave
  contemPalavrasChave(mensagem, palavrasChave) {
    return palavrasChave.some(palavra => mensagem.includes(palavra));
  }
  
  // Obtém uma resposta aleatória de uma lista
  obterRespostaAleatoria(respostas) {
    const indice = Math.floor(Math.random() * respostas.length);
    return respostas[indice];
  }
  
  // Define a etapa atual que o usuário está realizando
  definirEtapaAtual(etapa) {
    this.etapaAtual = etapa;
  }
  
  // Define a última manutenção realizada
  definirUltimaManutencao(manutencao) {
    this.ultimaManutencao = manutencao;
  }
  
  // Obtém o histórico de mensagens
  obterHistorico() {
    return this.historico;
  }
  
  // Limpa o histórico de mensagens
  limparHistorico() {
    this.historico = [];
  }
  
  // Define o contexto da conversa
  definirContexto(chave, valor) {
    this.contexto[chave] = valor;
  }
  
  // Obtém um valor do contexto da conversa
  obterContexto(chave) {
    return this.contexto[chave];
  }
  
  // Limpa o contexto da conversa
  limparContexto() {
    this.contexto = {};
  }
}

// Se estamos em um ambiente de navegador, disponibilizamos globalmente
if (typeof window !== 'undefined') {
  window.AgenteInterativo = AgenteInterativo;
} 