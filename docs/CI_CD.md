# CI/CD e Automação de Qualidade - TechCare

## Pipeline Automatizado (GitHub Actions)

O projeto utiliza um pipeline de integração contínua (CI) com as seguintes etapas:

1. **Checkout do código:**
   - Baixa o código do repositório.
2. **Configuração do Python:**
   - Usa Python 3.12 para garantir compatibilidade.
3. **Instalação de dependências:**
   - Instala todas as dependências do projeto e ferramentas de teste/lint.
4. **Lint (flake8):**
   - Verifica se o código segue padrões de estilo e boas práticas.
5. **Testes automatizados:**
   - Executa todos os testes com pytest e gera relatório de cobertura.
6. **Cobertura mínima:**
   - O pipeline falha se a cobertura global ficar abaixo de 60%.
7. **Publicação de artefatos:**
   - O relatório HTML de cobertura é publicado como artefato do workflow.

## Como acessar o relatório de cobertura
- Após cada execução do workflow, acesse a aba "Actions" do GitHub.
- Clique no workflow mais recente e baixe o artefato `cobertura_html`.
- Abra o arquivo `index.html` para visualizar o relatório completo.

## Boas práticas para contribuir
- Sempre rode os testes localmente antes de abrir um Pull Request.
- Mantenha a cobertura de código acima de 60%.
- Corrija todos os avisos de lint antes de submeter código.
- Adicione testes para novas funcionalidades e cenários de erro.

## Expansão futura
- Integração com Codecov ou SonarCloud para análise de cobertura e qualidade.
- Deploy automatizado para ambiente de staging/homologação.
- Testes E2E automatizados para interface web. 