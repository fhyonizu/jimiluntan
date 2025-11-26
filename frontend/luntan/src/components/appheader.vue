<template>
  <nav
    class="sticky top-0 z-50 w-full bg-white/60 backdrop-blur-md border-b border-white/40 shadow-sm transition-all duration-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">

        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2 group cursor-pointer">
          <span class="text-2xl group-hover:rotate-12 transition-transform">🐱</span>
          <span
            class="text-xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-500">
            基米论坛
          </span>
        </router-link>

        <!-- 右侧菜单 -->
        <div class="flex items-center space-x-6">

          <router-link to="/" class="text-sm font-bold text-slate-600 hover:text-purple-600 transition-colors">
            首页
          </router-link>

          <router-link to="/about" class="text-sm font-bold text-slate-600 hover:text-purple-600 transition-colors">
            关于
          </router-link>
          <!-- 在控制台链接旁边 -->
          <router-link v-if="isLoggedIn" to="/friends"
            class="text-sm font-bold text-slate-600 hover:text-purple-600 transition-colors flex items-center gap-1">
            好友
            <span v-if="auth.friendReqCount > 0" class="w-2 h-2 bg-red-500 rounded-full"></span>
          </router-link>
          <!-- 管理员入口 -->
          <router-link v-if="isAdmin" to="/admin"
            class="px-3 py-1.5 rounded-full bg-slate-800 text-purple-400 text-xs font-bold border border-slate-700 hover:bg-purple-600 hover:text-white hover:border-purple-500 transition-all flex items-center gap-1">
            <span>🛡️</span> 控制台
          </router-link>

          <div class="h-4 w-px bg-slate-300"></div>

          <!-- 未登录状态 -->
          <template v-if="!isLoggedIn">
            <router-link to="/login"
              class="px-5 py-2 text-sm font-bold text-white bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:-translate-y-0.5 transition-all active:scale-95">
              登录 / 注册
            </router-link>
          </template>

          <!-- 已登录状态 -->
          <template v-else>
            <div class="flex items-center gap-4">
              <!-- 个人中心链接 -->
              <router-link to="/profile"
                class="flex items-center gap-2 group bg-white/50 px-3 py-1.5 rounded-full hover:bg-white transition-all border border-transparent hover:border-purple-200">

                <!-- 🔥 头像显示区域 (核心修改) -->
                <div
                  class="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-xs text-white font-bold overflow-hidden shadow-inner">
                  <!-- 直接调用 auth.formatUrl 处理图片路径 -->
                  <img v-if="user.avatar" :src="auth.formatUrl(user.avatar)" class="w-full h-full object-cover" />
                  <!-- 没有头像时显示首字母 -->
                  <span v-else>{{ user.username?.charAt(0).toUpperCase() || 'Me' }}</span>
                </div>

                <span class="text-sm font-bold text-slate-700 group-hover:text-purple-600 transition-colors">
                  {{ user.username }}
                </span>
              </router-link>

              <!-- 登出按钮 -->
              <button @click="handleLogout"
                class="text-slate-400 hover:text-red-500 transition-colors p-1.5 hover:bg-red-50 rounded-full"
                title="退出登录">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </template>

        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../plugins/auth';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';

const auth = useAuthStore();
const router = useRouter();

// 状态解构保持响应式
const { isLoggedIn, user, isAdmin } = storeToRefs(auth);

const handleLogout = () => {
  if (confirm('确定要退出当前账号吗？')) {
    auth.logout();
    router.push('/login');
  }
};
</script>