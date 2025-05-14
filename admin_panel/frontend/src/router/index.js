import { createRouter, createWebHistory } from 'vue-router';
import AuthService from '@/services/auth.service';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/AdminDashboardView.vue'),
    meta: { requiresAuth: true, roles: ['admin_master'] }
  },
  {
    path: '/tecnico/dashboard',
    name: 'TecnicoDashboard',
    component: () => import('@/views/TecnicoDashboardView.vue'),
    meta: { requiresAuth: true, roles: ['admin_tecnico'] }
  },
  {
    path: '/visualizador/dashboard',
    name: 'VisualizadorDashboard',
    component: () => import('@/views/VisualizadorDashboardView.vue'),
    meta: { requiresAuth: true, roles: ['visualizador'] }
  },
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = AuthService.isAuthenticated();
  const userRole = AuthService.getUserRole();

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      return next('/login');
    }

    if (to.meta.roles && !to.meta.roles.includes(userRole)) {
      return next('/login');
    }
  }

  if (to.meta.requiresGuest && isAuthenticated) {
    switch(userRole) {
      case 'admin_master':
        return next('/admin/dashboard');
      case 'admin_tecnico':
        return next('/tecnico/dashboard');
      case 'visualizador':
        return next('/visualizador/dashboard');
      default:
        return next('/login');
    }
  }

  next();
});

export default router;
