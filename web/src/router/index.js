import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue';
import UserListView from '../views/UserListView';
import LoginView from '../views/LoginView';
import RegisterView from '../views/RegisterView';
import UserProfileView from '@/views/UserProfileView.vue';
import NotFoundView from '../views/NotFoundView';
import store from '@/store';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true } // 需要登录权限
  },
  {
    path: '/userlist/',
    name: 'userlist',
    component: UserListView,
    meta: { requiresAuth: true } // 需要登录权限
  },
  {
    path: '/login/',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false } // 不需要登录权限
  },
  {
    path: '/register/',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false } // 不需要登录权限
  },
  {
    path:'/userprofile/',
    name:'userprofile',
    component:UserProfileView,
    meta: { requiresAuth: true }

  },
  {
    path: '/404/',
    name: '404',
    component: NotFoundView,
    meta: { requiresAuth: false } // 不需要登录权限
  },
  {
    path: '/:catchAll(.*)',
    redirect: "/myspace/404/",
    meta: { requiresAuth: false } // 不需要登录权限
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = store.state.user.is_login;
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    // 如果访问的路由需要授权但用户未登录，重定向到登录页
    next({ name: 'login' });
  } else {
    // 否则，继续当前的导航
    next();
  }
});

export default router
