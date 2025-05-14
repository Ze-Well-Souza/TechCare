// Relatório de melhorias de hardware para o TechCare
// Este script gera recomendações de upgrade de hardware com base nos resultados do diagnóstico

class RelatorioMelhorias {
  constructor() {
    this.resultadosDiagnostico = null;
    this.recomendacoes = [];
    this.lojas = [
      { nome: "TechShop", url: "https://techshop.com.br", confiabilidade: 4.8 },
      { nome: "HardPlus", url: "https://hardplus.com.br", confiabilidade: 4.7 },
      { nome: "InfoStore", url: "https://infostore.com.br", confiabilidade: 4.6 }
    ];
    this.tecnicos = [
      { nome: "Carlos Silva", especialidade: "Hardware geral", avaliacao: 4.9, regiao: "Zona Sul" },
      { nome: "Ana Oliveira", especialidade: "Notebooks", avaliacao: 4.8, regiao: "Zona Norte" },
      { nome: "Roberto Santos", especialidade: "Desktops e servidores", avaliacao: 4.7, regiao: "Centro" }
    ];
  }

  // Define os resultados do diagnóstico
  definirResultadosDiagnostico(resultados) {
    this.resultadosDiagnostico = resultados;
    this.gerarRecomendacoes();
  }

  // Gera recomendações de hardware com base nos resultados do diagnóstico
  gerarRecomendacoes() {
    if (!this.resultadosDiagnostico) return;

    this.recomendacoes = [];

    // Recomendações de memória RAM
    this.analisarMemoria();

    // Recomendações de armazenamento
    this.analisarArmazenamento();

    // Recomendações de placa de vídeo
    this.analisarPlacaVideo();

    // Recomendações de processador
    this.analisarProcessador();

    // Recomendações de refrigeração
    this.analisarRefrigeracao();

    // Ordena as recomendações por prioridade
    this.recomendacoes.sort((a, b) => b.prioridade - a.prioridade);
  }

  // Analisa a memória e gera recomendações
  analisarMemoria() {
    const memoria = this.resultadosDiagnostico.memoria;
    
    // Verifica se há problemas de memória
    if (memoria.score < 70) {
      // Verifica a quantidade de memória total
      const totalGB = Math.round(memoria.total / 1024);
      
      if (totalGB < 8) {
        // Recomendação para computadores com menos de 8GB
        this.recomendacoes.push({
          tipo: "memoria",
          titulo: "Upgrade de Memória RAM",
          descricao: `Seu computador possui apenas ${totalGB}GB de RAM, o que é insuficiente para uso moderno. Recomendamos aumentar para pelo menos 16GB.`,
          beneficios: [
            "Melhora significativa na velocidade geral do sistema",
            "Capacidade para executar mais programas simultaneamente",
            "Melhor desempenho em aplicativos exigentes como editores de vídeo e jogos"
          ],
          produtos: [
            {
              nome: `Memória RAM ${memoria.tipo} ${memoria.frequencia}MHz 8GB`,
              preco: "R$ 249,90",
              loja: this.lojas[0],
              link: `${this.lojas[0].url}/memoria-ram-8gb`
            },
            {
              nome: `Kit Memória RAM ${memoria.tipo} ${memoria.frequencia}MHz 16GB (2x8GB)`,
              preco: "R$ 479,90",
              loja: this.lojas[1],
              link: `${this.lojas[1].url}/kit-memoria-ram-16gb`
            }
          ],
          dificuldade_instalacao: "Baixa",
          instrucoes_basicas: [
            "Desligue o computador e desconecte o cabo de alimentação",
            "Abra o gabinete (ou o compartimento de memória em notebooks)",
            "Localize os slots de memória RAM",
            "Insira os novos módulos nos slots vazios ou substitua os existentes",
            "Feche o gabinete e ligue o computador"
          ],
          prioridade: 9
        });
      } else if (totalGB < 16 && memoria.utilizacao > 70) {
        // Recomendação para computadores com 8GB mas alto uso
        this.recomendacoes.push({
          tipo: "memoria",
          titulo: "Upgrade de Memória RAM",
          descricao: `Seu computador possui ${totalGB}GB de RAM, mas está utilizando ${Math.round(memoria.utilizacao)}% da capacidade. Recomendamos aumentar para 16GB ou mais.`,
          beneficios: [
            "Melhor desempenho em multitarefas",
            "Redução de travamentos em aplicativos exigentes",
            "Experiência mais fluida ao usar múltiplos programas"
          ],
          produtos: [
            {
              nome: `Memória RAM ${memoria.tipo} ${memoria.frequencia}MHz 8GB`,
              preco: "R$ 249,90",
              loja: this.lojas[0],
              link: `${this.lojas[0].url}/memoria-ram-8gb`
            },
            {
              nome: `Kit Memória RAM ${memoria.tipo} ${memoria.frequencia}MHz 16GB (2x8GB)`,
              preco: "R$ 479,90",
              loja: this.lojas[1],
              link: `${this.lojas[1].url}/kit-memoria-ram-16gb`
            }
          ],
          dificuldade_instalacao: "Baixa",
          instrucoes_basicas: [
            "Desligue o computador e desconecte o cabo de alimentação",
            "Abra o gabinete (ou o compartimento de memória em notebooks)",
            "Localize os slots de memória RAM",
            "Insira os novos módulos nos slots vazios ou substitua os existentes",
            "Feche o gabinete e ligue o computador"
          ],
          prioridade: 7
        });
      }
    }
  }

  // Analisa o armazenamento e gera recomendações
  analisarArmazenamento() {
    const disco = this.resultadosDiagnostico.disco;
    
    // Verifica se há problemas de disco
    if (disco.score < 70) {
      // Verifica o tipo de disco
      if (disco.tipo !== "SSD") {
        // Recomendação para substituir HD por SSD
        this.recomendacoes.push({
          tipo: "armazenamento",
          titulo: "Upgrade para SSD",
          descricao: "Seu computador utiliza um disco rígido tradicional (HDD). Substituir por um SSD pode aumentar drasticamente a velocidade do sistema.",
          beneficios: [
            "Redução de até 70% no tempo de inicialização do sistema",
            "Abertura mais rápida de programas e arquivos",
            "Maior durabilidade e resistência a impactos",
            "Operação silenciosa e com menor consumo de energia"
          ],
          produtos: [
            {
              nome: "SSD 240GB SATA III",
              preco: "R$ 199,90",
              loja: this.lojas[0],
              link: `${this.lojas[0].url}/ssd-240gb`
            },
            {
              nome: "SSD 480GB SATA III",
              preco: "R$ 349,90",
              loja: this.lojas[1],
              link: `${this.lojas[1].url}/ssd-480gb`
            },
            {
              nome: "SSD 1TB SATA III",
              preco: "R$ 599,90",
              loja: this.lojas[2],
              link: `${this.lojas[2].url}/ssd-1tb`
            }
          ],
          dificuldade_instalacao: "Média",
          instrucoes_basicas: [
            "Faça backup de todos os seus dados",
            "Desligue o computador e desconecte o cabo de alimentação",
            "Abra o gabinete e localize o disco rígido atual",
            "Desconecte os cabos de dados e alimentação do disco atual",
            "Instale o SSD no mesmo local e conecte os cabos",
            "Feche o gabinete e ligue o computador",
            "Instale o sistema operacional no novo SSD ou clone o disco atual"
          ],
          prioridade: 10
        });
      } else if (disco.utilizacao > 85) {
        // Recomendação para aumentar capacidade de armazenamento
        const totalGB = Math.round(disco.total / 1024);
        
        this.recomendacoes.push({
          tipo: "armazenamento",
          titulo: "Aumento de Capacidade de Armazenamento",
          descricao: `Seu SSD de ${totalGB}GB está com ${Math.round(disco.utilizacao)}% de ocupação. Recomendamos adicionar mais espaço de armazenamento.`,
          beneficios: [
            "Mais espaço para programas e arquivos",
            "Melhor desempenho do SSD atual (SSDs funcionam melhor quando não estão muito cheios)",
            "Possibilidade de separar sistema operacional e arquivos pessoais"
          ],
          produtos: [
            {
              nome: "SSD 480GB SATA III",
              preco: "R$ 349,90",
              loja: this.lojas[0],
              link: `${this.lojas[0].url}/ssd-480gb`
            },
            {
              nome: "SSD 1TB SATA III",
              preco: "R$ 599,90",
              loja: this.lojas[1],
              link: `${this.lojas[1].url}/ssd-1tb`
            },
            {
              nome: "HD Externo 2TB USB 3.0",
              preco: "R$ 399,90",
              loja: this.lojas[2],
              link: `${this.lojas[2].url}/hd-externo-2tb`
            }
          ],
          dificuldade_instalacao: "Média",
          instrucoes_basicas: [
            "Para SSD interno adicional:",
            "Desligue o computador e desconecte o cabo de alimentação",
            "Abra o gabinete e localize um slot de disco disponível",
            "Instale o novo SSD e conecte os cabos de dados e alimentação",
            "Feche o gabinete e ligue o computador",
            "Inicialize o novo disco no Gerenciamento de Disco do Windows",
            "",
            "Para HD externo:",
            "Simplesmente conecte o disco à porta USB do computador"
          ],
          prioridade: 6
        });
      }
    }
  }

  // Analisa a placa de vídeo e gera recomendações
  analisarPlacaVideo() {
    // Simulação de análise de placa de vídeo
    // Em um sistema real, isso seria baseado em dados reais do diagnóstico
    
    // Verifica se há informações sobre placa de vídeo nos drivers
    const placaVideoInfo = this.resultadosDiagnostico.drivers.desatualizados.find(
      driver => driver.nome.includes("GeForce") || driver.nome.includes("Radeon")
    );
    
    if (placaVideoInfo) {
      // Extrai informações básicas do nome do driver
      const isNvidia = placaVideoInfo.nome.includes("GeForce");
      const isAMD = placaVideoInfo.nome.includes("Radeon");
      const modelo = placaVideoInfo.nome;
      
      // Verifica se é uma placa antiga (simulação)
      const placaAntiga = modelo.includes("GTX 9") || modelo.includes("GTX 10") || 
                         modelo.includes("RX 4") || modelo.includes("RX 5");
      
      if (placaAntiga) {
        this.recomendacoes.push({
          tipo: "placa_video",
          titulo: "Upgrade de Placa de Vídeo",
          descricao: `Sua placa de vídeo (${modelo}) está desatualizada. Um upgrade pode melhorar significativamente o desempenho em jogos e aplicativos gráficos.`,
          beneficios: [
            "Melhor desempenho em jogos modernos",
            "Suporte a recursos gráficos mais avançados",
            "Melhor desempenho em aplicativos de edição de vídeo e modelagem 3D",
            "Suporte a monitores de maior resolução"
          ],
          produtos: [
            {
              nome: isNvidia ? "NVIDIA GeForce RTX 3060 8GB" : "AMD Radeon RX 6600 XT 8GB",
              preco: "R$ 1.899,90",
              loja: this.lojas[0],
              link: `${this.lojas[0].url}/${isNvidia ? 'rtx-3060' : 'rx-6600-xt'}`
            },
            {
              nome: isNvidia ? "NVIDIA GeForce RTX 3070 8GB" : "AMD Radeon RX 6700 XT 12GB",
              preco: "R$ 2.899,90",
              loja: this.lojas[1],
              link: `${this.lojas[1].url}/${isNvidia ? 'rtx-3070' : 'rx-6700-xt'}`
            }
          ],
          dificuldade_instalacao: "Média",
          instrucoes_basicas: [
            "Desligue o computador e desconecte o cabo de alimentação",
            "Abra o gabinete e localize o slot PCIe da placa de vídeo atual",
            "Remova a placa atual (desparafuse e libere a trava do slot)",
            "Insira a nova placa no mesmo slot e fixe-a com parafuso",
            "Conecte os cabos de alimentação necessários",
            "Feche o gabinete e ligue o computador",
            "Instale os drivers mais recentes para a nova placa"
          ],
          prioridade: 5
        });
      }
    }
  }

  // Analisa o processador e gera recomendações
  analisarProcessador() {
    const cpu = this.resultadosDiagnostico.cpu;
    
    // Verifica se há problemas de CPU
    if (cpu.score < 60) {
      // Verifica a temperatura
      if (cpu.temperatura > 80) {
        // Recomendação para melhorar refrigeração
        this.recomendacoes.push({
          tipo: "refrigeracao",
          titulo: "Melhoria de Refrigeração da CPU",
          descricao: `Seu processador está operando em temperatura elevada (${cpu.temperatura}°C). Recomendamos melhorar o sistema de refrigeração.`,
          beneficios: [
            "Redução da temperatura do processador",
            "Melhor desempenho sustentado em cargas intensas",
            "Maior vida útil do processador",
            "Possibilidade de overclock seguro"
          ],
          produtos: [
            {
              nome: "Pasta Térmica de Alta Performance",
              preco: "R$ 29,90",
              loja: this.lojas[0],
              link: `${this.lojas[0].url}/pasta-termica`
            },
            {
              nome: "Cooler para CPU 120mm",
              preco: "R$ 149,90",
              loja: this.lojas[1],
              link: `${this.lojas[1].url}/cooler-cpu-120mm`
            },
            {
              nome: "Water Cooler 240mm",
              preco: "R$ 399,90",
              loja: this.lojas[2],
              link: `${this.lojas[2].url}/water-cooler-240mm`
            }
          ],
          dificuldade_instalacao: "Média-Alta",
          instrucoes_basicas: [
            "Desligue o computador e desconecte o cabo de alimentação",
            "Abra o gabinete e localize o cooler da CPU",
            "Remova o cooler atual com cuidado",
            "Limpe a superfície do processador e aplique nova pasta térmica",
            "Instale o novo cooler seguindo as instruções do fabricante",
            "Conecte o cabo do cooler à placa-mãe",
            "Feche o gabinete e ligue o computador"
          ],
          prioridade: 8
        });
      }
      
      // Verifica se o processador é antigo (simulação)
      // Em um sistema real, isso seria baseado em dados reais do diagnóstico
      if (cpu.modelo.includes("i3") || cpu.modelo.includes("i5-7") || cpu.modelo.includes("i5-8") || 
          cpu.modelo.includes("Ryzen 3") || cpu.modelo.includes("Ryzen 5 1") || cpu.modelo.includes("Ryzen 5 2")) {
        
        // Recomendação para upgrade de processador
        this.recomendacoes.push({
          tipo: "processador",
          titulo: "Upgrade de Processador",
          descricao: `Seu processador (${cpu.modelo}) está limitando o desempenho do sistema. Um upgrade pode melhorar significativamente a velocidade geral.`,
          beneficios: [
            "Melhor desempenho em todas as tarefas",
            "Capacidade para executar aplicativos mais exigentes",
            "Melhor desempenho em multitarefas",
            "Suporte a recursos mais modernos"
          ],
          produtos: [
            {
              nome: cpu.modelo.includes("i") ? "Intel Core i5-12400F" : "AMD Ryzen 5 5600X",
              preco: "R$ 1.199,90",
              loja: this.lojas[0],
              link: `${this.lojas[0].url}/${cpu.modelo.includes("i") ? 'i5-12400f' : 'ryzen-5-5600x'}`
            },
            {
              nome: cpu.modelo.includes("i") ? "Intel Core i7-12700K" : "AMD Ryzen 7 5800X",
              preco: "R$ 2.299,90",
              loja: this.lojas[1],
              link: `${this.lojas[1].url}/${cpu.modelo.includes("i") ? 'i7-12700k' : 'ryzen-7-5800x'}`
            }
          ],
          dificuldade_instalacao: "Alta",
          instrucoes_basicas: [
            "Este é um upgrade complexo que pode exigir a substituição da placa-mãe",
            "Recomendamos consultar um técnico especializado para este serviço",
            "O processo envolve desmontagem significativa do computador",
            "Será necessário reinstalar o sistema operacional em alguns casos"
          ],
         
(Content truncated due to size limit. Use line ranges to read in chunks)