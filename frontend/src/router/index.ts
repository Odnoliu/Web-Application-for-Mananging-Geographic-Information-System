import { createRouter, createWebHistory } from 'vue-router';
import UserLogin from '@/views/user/UserLogin.vue';
import Home from '@/views/user/Home.vue';
import UserRegister from '../views/user/UserRegister.vue';
import UserVectorProject from '@/views/user/project/UserVectorProject.vue';
import Project_Loading from '@/components/Loading/Project_Loading.vue';
import axios from 'axios';

const routes = [
  { path: '/loading', component: Project_Loading},
  { path: '/', redirect: '/login' },
  { path: '/login', component: UserLogin },
  { path: '/register', component: UserRegister },
  {
    path: '/home',
    component: Home,
    meta: { requiresAuth: true },
  },
  {
    path: '/vector_project/:encodedId',
    name: 'UserVectorProject',
    component: UserVectorProject,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('access_token');
  if (to.path == '/home' && to.query.access_token) {
    return next(); // Cho phép vào /home để Home.vue xử lý query parameter
  }
  if (to.meta.requiresAuth) {
    if (!token) {
      return next('/login');
    }

    try {
      const response = await axios.get('http://localhost:8000/user/check_role', {
        headers: { Authorization: `Bearer ${token}` },
      });

      const userRole = response.data.role;

      if (to.meta.requiresAdmin && userRole !== 'Admin role') {
        return next('/home');
      }

      next();
    } catch (error) {
      console.error('Lỗi kiểm tra vai trò:', error);
      localStorage.removeItem('access_token');
      return next('/login');
    }
  } else {
    next();
  }
});

export default router;