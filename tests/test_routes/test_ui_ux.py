"""
Testes para UI/UX da aplicação.

Estes testes verificam elementos importantes da interface do usuário,
como responsividade, acessibilidade e funcionalidade dos temas.
"""
import pytest
from flask import url_for
from bs4 import BeautifulSoup
import re

class TestUIUX:
    """
    Testes de UI/UX para a interface do usuário da aplicação TechCare.
    """
    
    def test_viewport_meta_tag(self, client):
        """Testa se a página contém a meta tag viewport correta para responsividade"""
        # Acessa a página inicial
        response = client.get('/')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Procura pela meta tag viewport
        soup = BeautifulSoup(response.data, 'html.parser')
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        
        # Verifica se a meta tag existe e tem o conteúdo correto
        assert viewport_meta is not None
        assert 'width=device-width' in viewport_meta.get('content', '')
        assert 'initial-scale=1' in viewport_meta.get('content', '')
    
    def test_responsive_css_classes(self, client):
        """Testa se os elementos principais usam classes responsivas"""
        # Acessa a página inicial
        response = client.get('/')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Analisa o HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Procura por classes que indicam responsividade
        responsive_elements = soup.find_all(class_=re.compile(r'container|row|col-[\w-]*|d-[\w-]*|flex'))
        
        # Verifica se existem elementos com classes responsivas
        assert len(responsive_elements) > 0, "Não foram encontrados elementos com classes responsivas"
    
    def test_theme_toggle_exists(self, client):
        """Testa se existe um botão/controle para alternar entre temas"""
        # Acessa a página inicial
        response = client.get('/')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Analisa o HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Procura pelo botão/controle para alternar temas
        # Pode estar em diferentes formatos, então buscamos por atributos comuns
        toggle_button = soup.find(id='theme-toggle') or \
                       soup.find(class_=re.compile(r'theme-toggle|toggle-theme|theme-switch|dark-mode-toggle')) or \
                       soup.find('button', text=re.compile(r'tema|mode|dark|light', re.IGNORECASE))
        
        assert toggle_button is not None, "Não foi encontrado botão para alternar temas"
    
    def test_theme_preference_cookie(self, client):
        """Testa se a preferência de tema é armazenada em cookie"""
        # Configura o cookie de tema usando a sintaxe correta do Flask
        with client.session_transaction() as session:
            session['theme'] = 'dark'
        
        # Acessa a página inicial
        response = client.get('/')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Analisa o HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Verifica se o corpo ou html tem classe/atributo para tema escuro
        body = soup.find('body')
        html = soup.find('html')
        
        # Verifica se o tema escuro foi aplicado
        dark_mode_applied = (body and ('dark' in body.get('class', []))) or \
                            (body and ('dark-theme' in body.get('class', []))) or \
                            (body and body.get('data-theme') == 'dark') or \
                            (html and ('dark' in html.get('class', []))) or \
                            (html and ('dark-theme' in html.get('class', []))) or \
                            (html and html.get('data-theme') == 'dark')
        
        assert dark_mode_applied, "O tema escuro não foi aplicado conforme a preferência do cookie"
    
    def test_accessible_elements(self, client):
        """Testa se elementos importantes possuem atributos de acessibilidade"""
        # Acessa a página inicial
        response = client.get('/')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Analisa o HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Verifica imagens com alt text
        images = soup.find_all('img')
        for img in images:
            assert img.has_attr('alt'), f"Imagem sem atributo alt: {img}"
        
        # Verifica se botões têm texto ou aria-label
        buttons = soup.find_all('button')
        for button in buttons:
            # Verifica se o botão tem texto ou aria-label
            has_text = button.text.strip() != ''
            has_aria_label = button.has_attr('aria-label')
            
            assert has_text or has_aria_label, f"Botão sem texto ou aria-label: {button}"
        
        # Verifica se formulários têm labels associados
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all(['input', 'select', 'textarea'])
            for input_elem in inputs:
                # Pula elementos hidden ou submit
                if input_elem.get('type') in ['hidden', 'submit', 'button']:
                    continue
                
                # Verifica se tem id para associação com label
                has_id = input_elem.has_attr('id')
                # Verifica se tem label associado
                has_label = False
                if has_id:
                    label = form.find('label', attrs={'for': input_elem['id']})
                    has_label = label is not None
                
                assert has_id and has_label, f"Input sem label associado: {input_elem}"
    
    def test_dashboard_responsive_layout(self, auth_client, auth):
        """Testa se o layout do dashboard é responsivo"""
        # Faz login
        auth.login()
        
        # Acessa o dashboard
        response = auth_client.get('/dashboard')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Analisa o HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Procura por containers flexíveis ou grids responsivos no conteúdo principal
        main_content = soup.find(id='main-content') or soup.find('main') or soup.find(class_='content')
        
        if main_content:
            responsive_elements = main_content.find_all(class_=re.compile(r'container|row|col-[\w-]*|d-[\w-]*|flex|grid'))
            assert len(responsive_elements) > 0, "Dashboard sem elementos responsivos no conteúdo principal"
        else:
            # Se não encontrar o conteúdo principal específico, verifica em todo o corpo
            responsive_elements = soup.find_all(class_=re.compile(r'container|row|col-[\w-]*|d-[\w-]*|flex|grid'))
            assert len(responsive_elements) > 0, "Dashboard sem elementos responsivos"
    
    def test_color_contrast_for_accessibility(self, client):
        """Testa se as classes CSS indicam preocupação com contraste de cores para acessibilidade"""
        # Acessa a página inicial
        response = client.get('/static/css/style.css')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Converte o CSS em texto
        css_content = response.data.decode('utf-8')
        
        # Verifica se há variáveis de cor definidas (indica sistema de design)
        color_variables = re.findall(r'--[\w-]*color[\w-]*:', css_content)
        assert len(color_variables) > 0, "Não foram encontradas variáveis de cor no CSS"
        
        # Verifica se há classes específicas para contraste
        contrast_patterns = [
            r'\.high-contrast', 
            r'\.theme-dark', 
            r'\.theme-light',
            r'\.accessible',
            r'\.contrast-',
            r'data-theme'
        ]
        
        contrast_found = False
        for pattern in contrast_patterns:
            if re.search(pattern, css_content):
                contrast_found = True
                break
        
        assert contrast_found, "Não foram encontradas classes ou atributos relacionados a contraste no CSS"
    
    def test_mobile_navigation(self, client):
        """Testa se existe navegação adequada para dispositivos móveis"""
        # Acessa a página inicial
        response = client.get('/')
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Analisa o HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Procura por elementos de navegação móvel comum
        mobile_nav_indicators = [
            soup.find(class_=re.compile(r'navbar-toggler|hamburger|mobile-menu-toggle')),
            soup.find(id=re.compile(r'mobile-menu|navbar-toggler|menu-toggle')),
            soup.find('button', attrs={'aria-controls': re.compile(r'nav|menu')}),
            soup.find(class_=re.compile(r'navbar-collapse')),
            soup.find(id=re.compile(r'navbar-collapse'))
        ]
        
        # Verifica se pelo menos um indicador de navegação móvel foi encontrado
        assert any(mobile_nav_indicators), "Não foi encontrada navegação adequada para dispositivos móveis" 