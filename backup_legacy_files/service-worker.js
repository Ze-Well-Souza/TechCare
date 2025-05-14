// Service Worker para o site TechCare
// Permite funcionalidades offline e comportamento de PWA

const CACHE_NAME = 'techcare-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/diagnostico.html',
  '/historico.html',
  '/suporte.html',
  '/css/styles.css',
  '/css/responsive.css',
  '/js/main.js',
  '/js/interactive.js',
  '/img/favicon.ico',
  '/img/icon-192.png',
  '/img/icon-512.png',
  '/manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
];

// Instala o Service Worker e faz cache dos recursos essenciais
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Limpa caches antigos quando uma nova versão do Service Worker é ativada
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          return cacheName !== CACHE_NAME;
        }).map(cacheName => {
          return caches.delete(cacheName);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Estratégia de cache: Network First com fallback para cache
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Se a resposta for válida, armazena uma cópia no cache
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Se a rede falhar, tenta buscar do cache
        return caches.match(event.request).then(response => {
          if (response) {
            return response;
          }
          
          // Para requisições de navegação, retorna a página offline
          if (event.request.mode === 'navigate') {
            return caches.match('/index.html');
          }
          
          // Para outros recursos, retorna um erro
          return new Response('Não foi possível carregar o recurso. Verifique sua conexão.', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain'
            })
          });
        });
      })
  );
});

// Sincronização em segundo plano para enviar dados quando a conexão for restaurada
self.addEventListener('sync', event => {
  if (event.tag === 'sync-diagnostico') {
    event.waitUntil(syncDiagnostico());
  }
});

// Função para sincronizar dados de diagnóstico
function syncDiagnostico() {
  return new Promise((resolve, reject) => {
    // Implementação da sincronização de dados
    console.log('Sincronizando dados de diagnóstico...');
    // Simulação de sucesso
    setTimeout(() => {
      console.log('Dados sincronizados com sucesso!');
      resolve();
    }, 2000);
  });
}

// Notificações push
self.addEventListener('push', event => {
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: '/img/icon-192.png',
    badge: '/img/favicon.ico',
    data: {
      url: data.url || '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification('TechCare', options)
  );
});

// Ação ao clicar na notificação
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
