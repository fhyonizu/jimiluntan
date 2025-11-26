import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/plugins/auth'

const routes = [
    // 首页
    { path: '/', component: () => import('@/pages/index.vue') },
    // 登录
    { path: '/login', component: () => import('@/pages/login.vue') },
    // 个人中心
    { path: '/profile', component: () => import('@/pages/profile.vue'), meta: { requiresAuth: true } },
    // 关于
    { path: '/about', component: () => import('@/pages/about.vue') },
    // 发帖
    { path: '/create', component: () => import('@/pages/create.vue'), meta: { requiresAuth: true } },
    // 后台
    { path: '/admin', component: () => import('@/pages/admin.vue'), meta: { requiresAdmin: true } },
    
    // 🔥 关键修改：同一个组件承载两种路由
    // 1. 看帖子详情 (例如 /post/1)
    { 
        path: '/post/:id', 
        name: 'PostDetail',
        component: () => import('@/pages/post.vue') 
    },
    // 2. 看分区列表 (例如 /channel/2) -> 这就是你要的“中间变列表但保留布局”
    { 
        path: '/channel/:id', 
        name: 'ChannelList',
        component: () => import('@/pages/post.vue') 
    },
    {
    path: '/friends',
    name: 'Friends',
    component: () => import('@/pages/Friends.vue'),
    meta: { requiresAuth: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
     scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

router.beforeEach((to, from, next) => {
    const auth = useAuthStore()
    if (to.meta.requiresAdmin && !auth.isAdmin) {
        alert('🚫 喵喵喵？这是禁地！')
        next('/') 
        return
    }
    if (to.meta.requiresAuth && !auth.isLoggedIn) {
        next('/login')
        return
    }
    next()
})

export default router