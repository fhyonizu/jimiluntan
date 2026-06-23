import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/plugins/auth'

const routes = [
    { path: '/', component: () => import('@/pages/index.vue') },
    { path: '/login', component: () => import('@/pages/login.vue') },
    { path: '/profile', component: () => import('@/pages/profile.vue'), meta: { requiresAuth: true } },
    { path: '/about', component: () => import('@/pages/about.vue') },
    { path: '/create', component: () => import('@/pages/create.vue'), meta: { requiresAuth: true } },
    { path: '/admin', component: () => import('@/pages/admin.vue'), meta: { requiresAdmin: true } },
    {
        path: '/post/:id',
        name: 'PostDetail',
        component: () => import('@/pages/post.vue')
    },
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
    },
    {
        path: '/notifications',
        name: 'Notifications',
        component: () => import('@/pages/Notifications.vue'),
        meta: { requiresAuth: true }
    },
    { path: '/:pathMatch(.*)*', component: () => import('@/pages/NotFound.vue') }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) return savedPosition
        return { top: 0 }
    }
})

router.beforeEach((to, from, next) => {
    const auth = useAuthStore()
    if (to.meta.requiresAdmin && !auth.isAdmin) {
        // 用 query 传递消息，避免 alert
        next({ path: '/', query: { msg: '权限不足，仅管理员可访问' } })
        return
    }
    if (to.meta.requiresAuth && !auth.isLoggedIn) {
        next('/login')
        return
    }
    next()
})

export default router
