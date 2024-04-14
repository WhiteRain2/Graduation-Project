import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue';
import UserListView from '../views/UserListView';
import UserProfileView from '../views/UserProfileView';
import LoginView from '../views/LoginView';
import NotFoundView from '../views/NotFoundView';

const routes = [
  {
    path: '/myspace/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/myspace/userlist/',
    name: 'userlist',
    component: UserListView
  },
  {
    path: '/myspace/userprofile/:userId/',
    name: 'userprofile',
    component: UserProfileView
  },
  {
    path: '/myspace/login/',
    name: 'login',
    component: LoginView
  },
  {
    path: '/myspace/404/',
    name: '404',
    component: NotFoundView
  },
  {
    path: '/myspace/:catchAll(.*)',
    redirect: "/myspace/404/"
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // 从localStorage而不是store获取登录状态
  const isLoggedIn = localStorage.getItem('isUserLoggedIn');
  const isGoingToLogin = to.name === 'login';

  // 如果用户未登录并且不是正在访问登录页面，则重定向到登录页
  if (!isLoggedIn && !isGoingToLogin) {
    next({ name: 'login' });
  } else {
    // 否则，继续当前的导航
    next();
  }
});

export default router
