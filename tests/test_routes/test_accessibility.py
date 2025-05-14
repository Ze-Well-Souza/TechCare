"""
Testes para verificar a conformidade com os padrões de acessibilidade WCAG 2.1
"""
import pytest
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock

def test_page_title(client):
    """Testa se as páginas têm títulos adequados (WCAG 2.4.2)"""
    pages = ['/', '/login', '/register', '/about']
    
    for page in pages:
        response = client.get(page)
        if response.status_code == 200:
            soup = BeautifulSoup(response.data, 'html.parser')
            title = soup.find('title')
            
            assert title is not None, f"Página {page} não tem elemento title"
            assert len(title.text.strip()) > 0, f"Página {page} tem título vazio"
            assert "TechCare" in title.text, f"Página {page} não menciona o nome da aplicação no título"

def test_image_alt_text(client):
    """Testa se todas as imagens têm texto alternativo (WCAG 1.1.1)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    images = soup.find_all('img')
    
    # Verifica se há pelo menos uma imagem
    if images:
        for img in images:
            assert img.has_attr('alt'), f"Imagem {img.get('src', 'sem src')} não tem atributo alt"

def test_form_labels(client):
    """Testa se todos os campos de formulário têm labels associados (WCAG 3.3.2)"""
    pages_with_forms = ['/login', '/register']
    
    for page in pages_with_forms:
        response = client.get(page)
        if response.status_code == 200:
            soup = BeautifulSoup(response.data, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                inputs = form.find_all(['input', 'select', 'textarea'])
                
                for input_field in inputs:
                    # Ignora campos ocultos e botões
                    if input_field.get('type') in ['hidden', 'submit', 'button']:
                        continue
                    
                    # Verifica se há label associado por for/id
                    input_id = input_field.get('id')
                    if input_id:
                        label = soup.find('label', {'for': input_id})
                        assert label is not None, f"Campo {input_id} na página {page} não tem label associado"

def test_heading_structure(client):
    """Testa a estrutura hierárquica dos cabeçalhos (WCAG 1.3.1)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verifica se há pelo menos um h1
    h1_elements = soup.find_all('h1')
    assert len(h1_elements) > 0, "Página não tem cabeçalho h1"
    
    # Idealmente deveria ter apenas um h1 por página
    assert len(h1_elements) == 1, "Página tem mais de um cabeçalho h1"
    
    # Verifica se h2 vem depois de h1, h3 depois de h2, etc.
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for i in range(1, len(headings)):
        prev_level = int(headings[i-1].name[1])
        curr_level = int(headings[i].name[1])
        
        # Um cabeçalho só pode ser no máximo um nível abaixo do anterior
        assert curr_level <= prev_level + 1, f"Estrutura de cabeçalhos irregular: {headings[i-1].name} seguido por {headings[i].name}"

def test_color_contrast(client):
    """Testa se há indicações de alto contraste (WCAG 1.4.3)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verifica se há classes relacionadas a contraste
    high_contrast_elements = soup.find_all(class_=lambda c: c and ('high-contrast' in c or 'contrast-' in c))
    
    # Ou verifica se há um seletor para aumentar o contraste
    contrast_toggle = (
        soup.find(id='contrast-toggle') or 
        soup.find(class_='contrast-toggle') or
        soup.find('button', string=lambda s: 'contrast' in s.lower() if s else False)
    )
    
    assert high_contrast_elements or contrast_toggle, "Não foram encontradas indicações de suporte a alto contraste"

def test_skip_navigation(client):
    """Testa se existe link para pular a navegação (WCAG 2.4.1)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Procura pelo link "pular para o conteúdo"
    skip_link = (
        soup.find('a', id='skip-nav') or
        soup.find('a', id='skip-navigation') or
        soup.find('a', id='skip-to-content') or
        soup.find('a', string=lambda s: 'pular' in s.lower() if s else False) or
        soup.find('a', string=lambda s: 'skip' in s.lower() if s else False)
    )
    
    assert skip_link is not None, "Link para pular navegação não encontrado"
    
    # Verifica se o link aponta para o conteúdo principal
    href = skip_link.get('href', '')
    assert href.startswith('#'), "Link para pular navegação deve apontar para uma âncora"
    
    # Verifica se o destino existe
    target_id = href[1:]  # Remove o # do início
    target = soup.find(id=target_id)
    assert target is not None, f"Destino do link para pular navegação ({href}) não encontrado"

def test_keyboard_navigation(client):
    """Testa elementos para navegação por teclado (WCAG 2.1.1)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verifica se links e botões têm tabindex adequado ou padrão
    interactive_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
    
    for element in interactive_elements:
        tabindex = element.get('tabindex')
        
        # Se tabindex está definido, não deve ser negativo (exceto -1 para remover do fluxo)
        if tabindex and tabindex != '-1':
            assert int(tabindex) >= 0, f"Elemento {element.name} tem tabindex negativo"
        
        # Se for um botão ou link, deve ter texto ou aria-label
        if element.name in ['a', 'button']:
            text_content = element.get_text().strip()
            aria_label = element.get('aria-label', '')
            
            assert text_content or aria_label, f"Elemento {element.name} não tem texto nem aria-label"

def test_aria_landmarks(client):
    """Testa se a página usa landmarks ARIA (WCAG 1.3.1, 2.4.1)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verifica principais landmarks
    header = soup.find(['header', lambda tag: tag.get('role') == 'banner'])
    assert header is not None, "Landmark header/banner não encontrado"
    
    nav = soup.find(['nav', lambda tag: tag.get('role') == 'navigation'])
    assert nav is not None, "Landmark nav/navigation não encontrado"
    
    main = soup.find(['main', lambda tag: tag.get('role') == 'main'])
    assert main is not None, "Landmark main não encontrado"
    
    # Não obrigatório, mas bom ter
    footer = soup.find(['footer', lambda tag: tag.get('role') == 'contentinfo'])
    assert footer is not None, "Landmark footer/contentinfo não encontrado"

def test_form_validation(client):
    """Testa mensagens de validação de formulários (WCAG 3.3.1, 3.3.3)"""
    # Tenta enviar um formulário de login com dados inválidos
    response = client.post('/login', data={
        'username': '',
        'password': ''
    })
    
    # Verifica se a resposta contém mensagens de erro
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Procura por mensagens de erro
    error_elements = (
        soup.find_all(class_=lambda c: c and 'error' in c) or
        soup.find_all(class_=lambda c: c and 'invalid' in c) or
        soup.find_all('div', {'role': 'alert'})
    )
    
    assert error_elements, "Não foram encontradas mensagens de erro na validação do formulário"
    
    # Verifica se as mensagens de erro estão associadas aos campos
    fields_with_errors = []
    for error in error_elements:
        # Verifica se o erro está próximo de algum campo
        prev_field = error.find_previous(['input', 'select', 'textarea'])
        next_field = error.find_next(['input', 'select', 'textarea'])
        
        if prev_field:
            fields_with_errors.append(prev_field.get('name'))
        elif next_field:
            fields_with_errors.append(next_field.get('name'))
    
    assert 'username' in fields_with_errors or 'password' in fields_with_errors, \
        "Mensagens de erro não estão claramente associadas aos campos com problema"

def test_responsive_text_size(client):
    """Testa se o texto pode ser redimensionado (WCAG 1.4.4)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verifica se a unidade de fonte é relativa (em, rem, %) e não absoluta (px, pt)
    style_tags = soup.find_all('style')
    css_text = ' '.join([style.string for style in style_tags if style.string])
    
    # Procura por declarações de tamanho de fonte
    font_size_px = 'font-size:' in css_text and 'px' in css_text
    font_size_pt = 'font-size:' in css_text and 'pt' in css_text
    
    # Idealmente, não deveria haver tamanhos absolutos
    if font_size_px or font_size_pt:
        # Verifica se há também um controle para ajustar o tamanho do texto
        text_size_control = (
            soup.find(id='text-size') or 
            soup.find(class_='text-size-control') or
            soup.find('button', string=lambda s: 'texto' in s.lower() and 'tamanho' in s.lower() if s else False)
        )
        
        assert text_size_control is not None, "Usa tamanhos de fonte absolutos sem oferecer controle para ajuste"

def test_page_language(client):
    """Testa se a página define o idioma corretamente (WCAG 3.1.1)"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    html = soup.find('html')
    
    assert html.has_attr('lang'), "Página não especifica atributo lang no elemento html"
    assert html['lang'] in ['pt', 'pt-br'], "Página não especifica o idioma português corretamente" 