# Guia de Personalização do TechCare

Este guia fornece instruções detalhadas sobre como personalizar a aparência e o comportamento do site TechCare, incluindo alteração de nome, logotipo, cores, imagens e textos.

## Índice
1. [Alteração do Nome e Marca](#alteração-do-nome-e-marca)
2. [Personalização de Cores e Estilos](#personalização-de-cores-e-estilos)
3. [Substituição de Imagens e Ícones](#substituição-de-imagens-e-ícones)
4. [Modificação de Textos e Conteúdo](#modificação-de-textos-e-conteúdo)
5. [Personalização do Chatbot](#personalização-do-chatbot)
6. [Adaptação para Diferentes Idiomas](#adaptação-para-diferentes-idiomas)

## Alteração do Nome e Marca

### Alteração do Nome do Site

Para alterar o nome "TechCare" para sua própria marca:

1. **Arquivos HTML**: Busque e substitua "TechCare" em todos os arquivos HTML:
   - `/index.html`
   - `/diagnostico.html`
   - `/historico.html`
   - `/suporte.html`

   Exemplo de alteração em `index.html`:
   ```html
   <!-- Antes -->
   <a href="index.html" class="logo">TechCare</a>
   
   <!-- Depois -->
   <a href="index.html" class="logo">SuaMarca</a>
   ```

2. **Título das Páginas**: Altere a tag `<title>` em cada arquivo HTML:
   ```html
   <!-- Antes -->
   <title>Diagnóstico - TechCare</title>
   
   <!-- Depois -->
   <title>Diagnóstico - SuaMarca</title>
   ```

3. **Rodapé (Footer)**: Atualize o nome e copyright em cada arquivo HTML:
   ```html
   <!-- Antes -->
   <h3>TechCare</h3>
   <p>&copy; 2025 TechCare. Todos os direitos reservados.</p>
   
   <!-- Depois -->
   <h3>SuaMarca</h3>
   <p>&copy; 2025 SuaMarca. Todos os direitos reservados.</p>
   ```

4. **Manifest.json**: Atualize o nome no arquivo `/manifest.json`:
   ```json
   {
     "name": "SuaMarca",
     "short_name": "SuaMarca",
     "description": "Diagnóstico e manutenção de computadores",
     ...
   }
   ```

5. **Informações de Contato**: Atualize email e telefone no rodapé de cada arquivo HTML:
   ```html
   <!-- Antes -->
   <li><a href="mailto:contato@techcare.com">contato@techcare.com</a></li>
   <li><a href="tel:+551199999999">(11) 9999-9999</a></li>
   
   <!-- Depois -->
   <li><a href="mailto:contato@suamarca.com">contato@suamarca.com</a></li>
   <li><a href="tel:+551188888888">(11) 8888-8888</a></li>
   ```

### Alteração do Slogan e Descrição

1. **Meta Description**: Atualize a meta tag de descrição em cada arquivo HTML:
   ```html
   <!-- Antes -->
   <meta name="description" content="TechCare - Diagnóstico gratuito para seu computador. Identifique problemas e otimize o desempenho do seu sistema.">
   
   <!-- Depois -->
   <meta name="description" content="SuaMarca - Seu slogan personalizado aqui. Descrição adicional do seu serviço.">
   ```

2. **Slogan na Página Inicial**: Atualize o slogan em `/index.html`:
   ```html
   <!-- Antes -->
   <h1>Soluções inteligentes para manutenção de computadores</h1>
   
   <!-- Depois -->
   <h1>Seu slogan personalizado aqui</h1>
   ```

## Personalização de Cores e Estilos

### Alteração das Cores Principais

As cores do site são definidas como variáveis CSS no arquivo `/css/styles.css`. Localize a seção `:root` no início do arquivo:

```css
/* Antes */
:root {
  --primary-color: #3498db;     /* Cor principal (azul) */
  --secondary-color: #2ecc71;   /* Cor secundária (verde) */
  --accent-color: #e74c3c;      /* Cor de destaque (vermelho) */
  --text-color: #2c3e50;        /* Cor do texto (azul escuro) */
  --bg-color: #f8f9fa;          /* Cor de fundo (cinza claro) */
}

/* Depois - exemplo com esquema roxo/laranja */
:root {
  --primary-color: #8e44ad;     /* Cor principal (roxo) */
  --secondary-color: #f39c12;   /* Cor secundária (laranja) */
  --accent-color: #e74c3c;      /* Cor de destaque (vermelho) */
  --text-color: #34495e;        /* Cor do texto (azul escuro) */
  --bg-color: #f8f9fa;          /* Cor de fundo (cinza claro) */
}
```

### Alteração de Fontes

Para alterar as fontes do site, modifique as definições de fonte no arquivo `/css/styles.css`:

```css
/* Antes */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  /* outros estilos */
}

/* Depois - exemplo com fonte diferente */
body {
  font-family: 'Roboto', Arial, sans-serif;
  /* outros estilos */
}
```

Para usar fontes personalizadas, adicione a importação da fonte no início do arquivo `/css/styles.css`:

```css
/* Adicione antes das outras regras CSS */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
```

### Personalização de Botões

Para alterar o estilo dos botões, modifique as classes `.btn`, `.btn-primary`, `.btn-secondary` e `.btn-outline` no arquivo `/css/styles.css`:

```css
/* Exemplo de personalização de botões */
.btn {
  padding: 10px 20px;
  border-radius: 8px;  /* Botões mais arredondados */
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: darken(var(--primary-color), 10%);
  transform: translateY(-2px);  /* Efeito de elevação ao passar o mouse */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
```

## Substituição de Imagens e Ícones

### Ícones do Site

1. **Favicon e Ícones PWA**: Substitua os seguintes arquivos mantendo os mesmos nomes:
   - `/img/favicon.ico` - Ícone da aba do navegador (16x16 ou 32x32 pixels)
   - `/img/icon-192.png` - Ícone para dispositivos móveis (192x192 pixels)
   - `/img/icon-512.png` - Ícone para PWA (512x512 pixels)

   Você pode criar estes ícones usando ferramentas como Adobe Photoshop, GIMP ou serviços online como [Favicon.io](https://favicon.io/).

2. **Verificação após substituição**: Após substituir os ícones, verifique se as referências estão corretas em todos os arquivos HTML:
   ```html
   <link rel="icon" href="img/favicon.ico">
   <link rel="apple-touch-icon" href="img/icon-192.png">
   ```

3. **Manifest.json**: Verifique se as referências aos ícones no arquivo `/manifest.json` estão corretas:
   ```json
   "icons": [
     {
       "src": "img/icon-192.png",
       "sizes": "192x192",
       "type": "image/png"
     },
     {
       "src": "img/icon-512.png",
       "sizes": "512x512",
       "type": "image/png"
     }
   ]
   ```

### Imagens de Conteúdo

1. **Adicionar Novas Imagens**: Coloque suas imagens personalizadas na pasta `/img/` e referencie-as nos arquivos HTML:
   ```html
   <img src="img/sua-imagem.jpg" alt="Descrição da imagem">
   ```

2. **Imagens de Fundo**: Para alterar imagens de fundo definidas via CSS, modifique o arquivo `/css/styles.css`:
   ```css
   /* Antes */
   .hero-section {
     background-image: url('../img/hero-bg.jpg');
     /* outros estilos */
   }
   
   /* Depois */
   .hero-section {
     background-image: url('../img/seu-background.jpg');
     /* outros estilos */
   }
   ```

3. **Otimização de Imagens**: Para melhor desempenho, otimize suas imagens antes de adicioná-las:
   - Use formatos apropriados: JPG para fotografias, PNG para imagens com transparência, SVG para ícones e ilustrações
   - Comprima as imagens usando ferramentas como [TinyPNG](https://tinypng.com/) ou [Squoosh](https://squoosh.app/)
   - Dimensione as imagens para o tamanho exato em que serão exibidas

### Ícones de Interface

O site usa ícones do Font Awesome. Para alterar um ícone:

```html
<!-- Antes -->
<i class="fas fa-tachometer-alt"></i>

<!-- Depois - usando outro ícone do Font Awesome -->
<i class="fas fa-gauge-high"></i>
```

Para ver todos os ícones disponíveis, visite [Font Awesome](https://fontawesome.com/icons).

## Modificação de Textos e Conteúdo

### Textos da Página Inicial

Edite o arquivo `/index.html` para alterar:

1. **Título e Subtítulo**:
   ```html
   <!-- Antes -->
   <h1>Soluções inteligentes para manutenção de computadores</h1>
   <p>Diagnóstico gratuito, otimização avançada e suporte técnico especializado.</p>
   
   <!-- Depois -->
   <h1>Seu título personalizado aqui</h1>
   <p>Sua descrição personalizada dos serviços oferecidos.</p>
   ```

2. **Descrições de Serviços**:
   ```html
   <!-- Exemplo de seção de serviço -->
   <div class="service-card">
     <div class="service-icon">
       <i class="fas fa-tachometer-alt"></i>
     </div>
     <h3>Diagnóstico Completo</h3>
     <p>Seu texto personalizado descrevendo o serviço de diagnóstico.</p>
   </div>
   ```

### Textos da Página de Diagnóstico

Edite o arquivo `/diagnostico.html` para alterar:

1. **Descrições dos Serviços**:
   ```html
   <!-- Exemplo de opção de serviço -->
   <div class="service-option">
     <div class="service-icon">
       <i class="fas fa-tachometer-alt"></i>
     </div>
     <h2>Atualização e Manutenção</h2>
     <p>Sua descrição personalizada do serviço de atualização e manutenção.</p>
     <button id="iniciar-diagnostico" class="btn btn-primary">Iniciar Diagnóstico</button>
   </div>
   ```

2. **Pacotes de Serviço**:
   ```html
   <!-- Exemplo de pacote de serviço -->
   <div class="service-option" id="option-basic">
     <div class="service-header">
       <h3>Seu Nome de Pacote</h3>
       <span class="service-price">R$ XX,XX</span>
     </div>
     <ul id="recomendacoes-basico" class="service-features">
       <!-- Preenchido dinamicamente pelo JavaScript -->
     </ul>
     <button id="selecionar-basico" class="btn btn-outline">Selecionar</button>
   </div>
   ```

### Mensagens do Chatbot

Para personalizar as mensagens do chatbot, edite o arquivo `/js/agente.js`:

```javascript
// Mensagem de boas-vindas
this.mensagemBoasVindas = "Olá! Sou o assistente virtual da SuaMarca. Como posso ajudar você hoje?";

// Base de conhecimento
this.baseConhecimento = {
  "como funciona o diagnóstico": "Sua resposta personalizada sobre como funciona o diagnóstico...",
  "quanto custa": "Sua resposta personalizada sobre preços...",
  // Adicione mais perguntas e respostas
};
```

## Personalização do Chatbot

### Nome e Aparência do Chatbot

1. **Nome do Chatbot**: Altere o nome no arquivo `/diagnostico.html`:
   ```html
   <!-- Antes -->
   <h3><i class="fas fa-robot"></i> Assistente TechCare</h3>
   
   <!-- Depois -->
   <h3><i class="fas fa-robot"></i> Nome do Seu Assistente</h3>
   ```

2. **Cores do Chat**: Personalize as cores no arquivo `/css/chat.css`:
   ```css
   /* Cabeçalho do chat */
   .chat-header {
     background-color: var(--primary-color);  /* Usa a cor principal definida */
     /* outros estilos */
   }
   
   /* Mensagens do usuário */
   .message-user p {
     background-color: #e2f0fd;  /* Altere para sua cor preferida */
     /* outros estilos */
   }
   
   /* Mensagens do agente */
   .message-agent p {
     background-color: #f8f9fa;  /* Altere para sua cor preferida */
     /* outros estilos */
   }
   ```

### Personalização de Respostas Rápidas

Edite as opções de respostas rápidas no arquivo `/diagnostico.html`:

```html
<!-- Antes -->
<div class="quick-responses">
  <button onclick="quickResponse('Como funciona o diagnóstico?')">Como funciona o diagnóstico?</button>
  <button onclick="quickResponse('Meu computador está lento')">Meu computador está lento</button>
  <button onclick="quickResponse('Preciso de ajuda com drivers')">Preciso de ajuda com drivers</button>
</div>

<!-- Depois -->
<div class="quick-responses">
  <button onclick="quickResponse('Sua pergunta personalizada 1?')">Sua pergunta personalizada 1?</button>
  <button onclick="quickResponse('Sua pergunta personalizada 2')">Sua pergunta personalizada 2</button>
  <button onclick="quickResponse('Sua pergunta personalizada 3')">Sua pergunta personalizada 3</button>
</div>
```

## Adaptação para Diferentes Idiomas

### Tradução de Textos

Para adaptar o site para outro idioma:

1. **Altere o atributo `lang` no HTML**:
   ```html
   <!-- Antes -->
   <html lang="pt-BR">
   
   <!-- Depois (exemplo para inglês) -->
   <html lang="en">
   ```

2. **Traduza todos os textos estáticos** nos arquivos HTML:
   - Títulos, subtítulos, parágrafos
   - Textos de botões
   - Mensagens de feedback
   - Rodapé e informações de contato

3. **Traduza as mensagens dinâmicas** no JavaScript:
   - Mensagens do chatbot em `/js/agente.js`
   - Textos de diagnóstico em `/js/diagnostico.js`
   - Recomendações em `/js/relatorio.js`

### Adaptação de Formatos

Para adaptar formatos específicos de cada região:

1. **Formato de moeda**: Altere o formato de preço nos arquivos JavaScript:
   ```javascript
   // Antes (formato brasileiro)
   const preco = `R$ ${valor.toFixed(2).replace('.', ',')}`;
   
   // Depois (exemplo para dólar americano)
   const preco = `$${valor.toFixed(2)}`;
   ```

2. **Formato de data**: Adapte o formato de data nos arquivos JavaScript:
   ```javascript
   // Antes (formato brasileiro)
   const dataFormatada = `${data.getDate()}/${data.getMonth()+1}/${data.getFullYear()}`;
   
   // Depois (exemplo para formato americano)
   const dataFormatada = `${data.getMonth()+1}/${data.getDate()}/${data.getFullYear()}`;
   ```

## Considerações Finais

Ao personalizar o site TechCare:

1. **Faça backup** dos arquivos originais antes de iniciar as alterações
2. **Teste as alterações** em diferentes navegadores e dispositivos
3. **Verifique a responsividade** para garantir que o site funcione bem em dispositivos móveis
4. **Otimize as imagens** para melhor desempenho
5. **Mantenha a consistência** visual em todas as páginas

Após concluir as personalizações, reimplante o site usando o comando de implantação para que as alterações sejam aplicadas ao site publicado.
