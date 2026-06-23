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
        <div class="hidden md:flex items-center space-x-6">

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
          
          <!-- 通知铃铛 -->
          <router-link v-if="isLoggedIn" to="/notifications" class="relative text-slate-600 hover:text-purple-600 transition-colors">
            🔔
            <span v-if="auth.unreadCount + auth.friendReqCount > 0" 
              class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-white text-[10px] font-bold flex items-center justify-center">
              {{ Math.min(auth.unreadCount + auth.friendReqCount, 99) }}
            </span>
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
              <router-link to="/profile"
                class="flex items-center gap-2 group bg-white/50 px-3 py-1.5 rounded-full hover:bg-white transition-all border border-transparent hover:border-purple-200">
                <div
                  class="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-xs text-white font-bold overflow-hidden shadow-inner">
                  <img v-if="user.avatar" :src="formatUrl(user.avatar)" class="w-full h-full object-cover" />
                  <span v-else>{{ user.username?.charAt(0).toUpperCase() || 'Me' }}</span>
                </div>
                <span class="text-sm font-bold text-slate-700 group-hover:text-purple-600 transition-colors">
                  {{ user.username }}
                </span>
              </router-link>

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

        <!-- 🔥 移动端汉堡菜单 -->
        <div class="md:hidden flex items-center gap-2">
          <router-link v-if="isLoggedIn" to="/notifications" class="relative text-xl px-2">
            🔔
            <span v-if="auth.unreadCount + auth.friendReqCount > 0"
              class="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full"></span>
          </router-link>
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="text-slate-600 p-2 text-2xl">
            {{ mobileMenuOpen ? '✕' : '☰' }}
          </button>
        </div>
      </div>

      <!-- 🔥 移动端下拉菜单 -->
      <transition name="slide-down">
        <div v-if="mobileMenuOpen" class="md:hidden bg-white/90 backdrop-blur-xl border-t border-slate-200 px-4 py-4 space-y-3">
          <router-link @click="mobileMenuOpen=false" to="/" class="block px-4 py-2 rounded-xl hover:bg-purple-50 text-slate-700 font-bold">🏠 首页</router-link>
          <router-link @click="mobileMenuOpen=false" to="/about" class="block px-4 py-2 rounded-xl hover:bg-purple-50 text-slate-700 font-bold">ℹ️ 关于</router-link>
          <router-link v-if="isLoggedIn" @click="mobileMenuOpen=false" to="/friends" class="block px-4 py-2 rounded-xl hover:bg-purple-50 text-slate-700 font-bold">👥 好友</router-link>
          <router-link v-if="isLoggedIn" @click="mobileMenuOpen=false" to="/notifications" class="block px-4 py-2 rounded-xl hover:bg-purple-50 text-slate-700 font-bold">📬 通知</router-link>
          <router-link v-if="isAdmin" @click="mobileMenuOpen=false" to="/admin" class="block px-4 py-2 rounded-xl hover:bg-purple-50 text-purple-600 font-bold">🛡️ 控制台</router-link>
          <template v-if="isLoggedIn">
            <router-link @click="mobileMenuOpen=false" to="/profile" class="block px-4 py-2 rounded-xl hover:bg-purple-50 text-slate-700 font-bold">👤 个人中心</router-link>
            <button @click="handleLogout(); mobileMenuOpen=false" class="w-full text-left px-4 py-2 rounded-xl hover:bg-red-50 text-red-500 font-bold">🚪 退出登录</button>
          </template>
          <template v-else>
            <router-link @click="mobileMenuOpen=false" to="/login" class="block px-4 py-2 rounded-xl bg-purple-500 text-white font-bold text-center">登录 / 注册</router-link>
          </template>
        </div>
      </transition>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../plugins/auth';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { ref } from 'vue';
import { useFormatUrl } from '@/composables/useFormatUrl';

const auth = useAuthStore();
const router = useRouter();

const { isLoggedIn, user, isAdmin } = storeToRefs(auth);
const mobileMenuOpen = ref(false);
const { formatUrl } = useFormatUrl();

const handleLogout = () => {
  if (confirm('确定要退出当前账号吗？')) {
    auth.logout();
    router.push('/login');
  }
};
</script>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-10px); }
</style>