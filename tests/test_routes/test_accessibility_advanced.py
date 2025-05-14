"""
Testes avançados para funcionalidades de acessibilidade WCAG 2.1
"""
import pytest
from flask import url_for
from bs4 import BeautifulSoup
from unittest.mock import patch

def test_skip_to_content_link(client):
    """Testa se o link para pular para o conteúdo principal está presente."""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    skip_link = soup.find('a', class_='skip-to-content')
    
    assert skip_link is not None
    assert skip_link['href'] == '#main-content'
    assert 'pular para o conteúdo' in skip_link.text.lower()

def test_keyboard_shortcuts_help_button(client):
    """Testa se o botão de ajuda para atalhos de teclado está presente."""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    help_button = soup.find(id='accessibility-help')
    
    assert help_button is not None
    assert 'ajuda' in help_button.text.lower()
    assert 'accessibility' in help_button.attrs.get('class', [''])[0].lower() or 'acessibilidade' in help_button.text.lower()

def test_font_size_controls(client):
    """Testa se os controles de tamanho de fonte estão sendo injetados via JavaScript."""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    script_tags = soup.find_all('script')
    
    # Verifica se o arquivo scripts.js está sendo carregado
    script_src = [s.get('src', '') for s in script_tags]
    assert any('scripts.js' in src for src in script_src)
    
    # Verifica o conteúdo do script para funções de controle de fonte
    inline_scripts = [s.string for s in script_tags if s.string]
    js_content = '\n'.join([s for s in inline_scripts if s])
    
    assert 'font-size' in js_content or 'fontSize' in js_content

def test_high_contrast_toggle(client):
    """Testa se o toggle de alto contraste está presente."""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    contrast_toggle = soup.find(id='contrast-toggle')
    
    assert contrast_toggle is not None
    assert contrast_toggle.name == 'input'
    assert contrast_toggle['type'] == 'checkbox'
    
    # Verifica se o label ou elemento pai tem texto indicando alto contraste
    parent = contrast_toggle.parent
    assert 'contrast' in parent.attrs.get('class', [''])[0] or 'contrast' in parent.attrs.get('title', '').lower()

def test_theme_toggle(client):
    """Testa se o toggle de tema está presente."""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    theme_toggle = soup.find(id='theme-toggle')
    
    assert theme_toggle is not None
    assert theme_toggle.name == 'input'
    assert theme_toggle['type'] == 'checkbox'
    
    # Verifica se tem ícones de sol e lua próximos
    parent = theme_toggle.parent.parent
    sun_icon = parent.find('i', class_=lambda c: c and 'fa-sun' in c)
    moon_icon = parent.find('i', class_=lambda c: c and 'fa-moon' in c)
    
    assert sun_icon is not None
    assert moon_icon is not None

def test_accessibility_keyboard_shortcuts_info(client):
    """Testa se as informações de atalhos de teclado estão presentes."""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    accessibility_info = soup.find(class_='accessibility-info')
    
    assert accessibility_info is not None
    
    # Verifica se contém informações sobre atalhos
    shortcut_items = accessibility_info.find_all('li')
    assert len(shortcut_items) >= 5  # Deve ter pelo menos 5 atalhos listados
    
    shortcut_text = accessibility_info.get_text()
    essential_shortcuts = ['Alt+1', 'Alt+2', 'Alt+3', 'Alt+0']
    for shortcut in essential_shortcuts:
        assert shortcut in shortcut_text

def test_set_theme_endpoint(client):
    """Testa o endpoint de configuração de tema."""
    # Teste com tema escuro
    response = client.post('/set-theme', json={'theme': 'dark'})
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['theme'] == 'dark'
    
    # Verifica se o cookie foi definido
    assert 'theme=dark' in response.headers.get('Set-Cookie', '')
    
    # Teste com tema claro
    response = client.post('/set-theme', json={'theme': 'light'})
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['theme'] == 'light'
    
    # Verifica se o cookie foi definido
    assert 'theme=light' in response.headers.get('Set-Cookie', '')
    
    # Teste com tema inválido
    response = client.post('/set-theme', json={'theme': 'invalid'})
    assert response.status_code == 400
    assert response.json['success'] == False

def test_set_contrast_endpoint(client):
    """Testa o endpoint de configuração de alto contraste."""
    # Teste ativando alto contraste
    response = client.post('/set-contrast', json={'high_contrast': 'true'})
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['high_contrast'] == True
    
    # Verifica se o cookie foi definido
    assert 'high_contrast=true' in response.headers.get('Set-Cookie', '')
    
    # Teste desativando alto contraste
    response = client.post('/set-contrast', json={'high_contrast': 'false'})
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['high_contrast'] == False
    
    # Verifica se o cookie foi definido
    assert 'high_contrast=false' in response.headers.get('Set-Cookie', '')

def test_aria_attributes(client):
    """Testa se elementos importantes têm atributos ARIA apropriados."""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Navegação principal deve ter role e aria-label
    nav = soup.find('nav')
    assert nav is not None
    assert nav.has_attr('class') and 'navbar' in nav['class']
    
    # Botões de alternância devem ter aria-pressed ou papéis apropriados
    toggles = soup.find_all('input', type='checkbox')
    for toggle in toggles:
        label = toggle.find_parent('label')
        if label:
            assert label.has_attr('title') or label.has_attr('aria-label')
    
    # Botões com ícones devem ter texto ou aria-label
    icon_buttons = []
    for i in soup.find_all('i', class_=lambda c: c and ('fa-' in c or 'icon' in c)):
        btn = i.find_parent('button') or i.find_parent('a')
        if btn:
            icon_buttons.append(btn)
    
    for btn in icon_buttons:
        has_accessible_name = (
            btn.string and btn.string.strip() or
            btn.has_attr('aria-label') or
            btn.has_attr('title') or
            btn.find('span', class_=lambda c: c and 'sr-only' in c)
        )
        assert has_accessible_name

def test_wcag_color_contrast():
    """
    Testa se as combinações de cores têm contraste suficiente.
    Nota: Este é um teste simbólico, pois testar automaticamente o contraste
    de cores exigiria carregar a página em um navegador real.
    """
    # Em um ambiente de produção, isso seria testado com ferramentas como
    # axe-core, pa11y ou lighthouse em integração com Selenium ou Playwright
    
    # Verificamos se as variáveis CSS para cores existem
    from pathlib import Path
    css_path = Path('app/static/css/styles.css')
    assert css_path.exists()
    
    css_content = css_path.read_text()
    essential_color_vars = [
        '--primary-color',
        '--text-color',
        '--bg-color',
        '--text-muted'
    ]
    
    for var in essential_color_vars:
        assert var in css_content
    
    # Verificamos se existem classes para alto contraste
    assert '.high-contrast' in css_content 