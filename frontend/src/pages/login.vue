<template>
  <!-- 全局背景 -->
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 flex items-center justify-center p-4 relative overflow-hidden font-sans">
    <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>

    <div class="w-full max-w-md relative z-10">
      <div class="absolute -top-12 left-0">
        <router-link to="/" class="flex items-center text-sm font-bold text-slate-500 hover:text-purple-600 transition-colors group">
          <span class="mr-1 group-hover:-translate-x-1 transition-transform">←</span> 回到首页
        </router-link>
      </div>

      <div class="bg-white/40 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/60 overflow-hidden relative">
        <Showmessage ref="message" />
        
        <div class="px-8 pt-8 pb-6 text-center">
          <h1 class="text-2xl font-extrabold text-slate-800 mb-2 tracking-tight">
            {{ mode === 'login' ? '欢迎回来 👋' : '加入我们 🚀' }}
          </h1>
          <p class="text-slate-500 text-sm font-medium mb-6">
            {{ mode === 'login' ? '登录账号' : '注册新账号' }}
          </p>

          <!-- 切换开关 -->
          <div class="bg-white/50 p-1 rounded-xl inline-flex relative shadow-inner">
            <div class="absolute top-1 bottom-1 w-[calc(50%-4px)] bg-white rounded-lg shadow-sm transition-all duration-300 ease-out"
                 :class="mode === 'login' ? 'left-1' : 'left-[calc(50%+2px)]'"></div>
            <button type="button" class="relative z-10 w-24 py-1.5 text-sm font-bold transition-colors rounded-lg"
              :class="mode === 'login' ? 'text-purple-600' : 'text-slate-500 hover:text-slate-700'" @click="mode = 'login'">登录</button>
            <button type="button" class="relative z-10 w-24 py-1.5 text-sm font-bold transition-colors rounded-lg"
              :class="mode === 'register' ? 'text-purple-600' : 'text-slate-500 hover:text-slate-700'" @click="mode = 'register'">注册</button>
          </div>
        </div>

        <!-- 登录表单 -->
        <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="px-8 pb-8 space-y-5">
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-500 ml-1">邮箱地址</label>
            <input v-model="loginForm.email" type="email" required placeholder="name@example.com"
              class="w-full px-4 py-3 bg-white/50 border border-transparent rounded-xl text-slate-800 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-purple-300 focus:outline-none transition-all shadow-sm hover:bg-white/80">
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-500 ml-1">密码</label>
            <input v-model="loginForm.password" type="password" required placeholder="••••••••"
              class="w-full px-4 py-3 bg-white/50 border border-transparent rounded-xl text-slate-800 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-purple-300 focus:outline-none transition-all shadow-sm hover:bg-white/80">
          </div>
          <div class="flex items-center justify-between text-sm pt-2">
            <label class="flex items-center cursor-pointer">
              <input v-model="loginForm.remember" type="checkbox" class="w-4 h-4 rounded text-purple-600 focus:ring-purple-500 border-gray-300 bg-white/50">
              <span class="ml-2 text-slate-600 font-medium">记住我</span>
            </label>
          </div>
          <button type="submit" class="w-full py-3.5 px-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:scale-[1.02] active:scale-[0.98] transition-all">🚀 立即登录</button>
        </form>

        <!-- 注册表单 -->
        <form v-else @submit.prevent="handleRegister" class="px-8 pb-8 space-y-4">
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-500 ml-1">昵称</label>
            <input v-model="registerForm.nickname" type="text" required placeholder="取个好听的名字"
              class="w-full px-4 py-3 bg-white/50 border border-transparent rounded-xl text-slate-800 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-purple-300 focus:outline-none transition-all shadow-sm hover:bg-white/80">
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-500 ml-1">邮箱地址</label>
            <input v-model="registerForm.email" type="email" required placeholder="name@example.com"
              class="w-full px-4 py-3 bg-white/50 border border-transparent rounded-xl text-slate-800 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-purple-300 focus:outline-none transition-all shadow-sm hover:bg-white/80">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="block text-xs font-bold text-slate-500 ml-1">密码</label>
              <input v-model="registerForm.password" type="password" required placeholder="至少6位"
                class="w-full px-4 py-3 bg-white/50 border border-transparent rounded-xl text-slate-800 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-purple-300 focus:outline-none transition-all shadow-sm hover:bg-white/80">
            </div>
            <div class="space-y-1">
              <label class="block text-xs font-bold text-slate-500 ml-1">确认密码</label>
              <input v-model="registerForm.passwordConfirm" type="password" required placeholder="确认一下"
                class="w-full px-4 py-3 bg-white/50 border border-transparent rounded-xl text-slate-800 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-purple-300 focus:outline-none transition-all shadow-sm hover:bg-white/80">
            </div>
          </div>
          <label class="flex items-start text-sm text-slate-600 font-medium pt-2 cursor-pointer">
            <input v-model="registerForm.agree" type="checkbox" required class="mt-1 w-4 h-4 rounded text-purple-600 focus:ring-purple-500 border-gray-300 bg-white/50">
            <span class="ml-2">我已阅读并同意用户协议</span>
          </label>
          <button type="submit" class="w-full py-3.5 px-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:scale-[1.02] active:scale-[0.98] transition-all">✨ 创建账号</button>
        </form>
      </div>
      <div class="text-center mt-6 text-slate-500 text-sm font-medium">
        {{ mode === 'login' ? '还没有账号？' : '已经有账号了？' }}
        <button class="text-purple-600 font-bold hover:underline" @click="mode = mode === 'login' ? 'register' : 'login'">
          {{ mode === 'login' ? '免费注册' : '直接登录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import api from '@/plugins/axios.js'
import { reactive, ref } from 'vue'
import Showmessage from '../components/showmessage.vue'
import router from '../router'
import { useAuthStore } from '@/plugins/auth'

const mode = ref('login')
const message = ref()
const loginForm = reactive({ email: '', password: '', remember: false })
const registerForm = reactive({ nickname: '', email: '', password: '', passwordConfirm: '', agree: false })

// 登录逻辑
const handleLogin = () => {
  api.post('/auth/login', loginForm).then(res => {
    if (res.data.code === 200) {
      // 🔥 注意：后端现在返回的是 access_token
      useAuthStore().login(res.data.user, res.data.access_token)
      message.value.showMessage('登录成功！')
      router.push('/')
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(err => handleError(err))
}

// 注册逻辑
const handleRegister = () => {
  if (!registerForm.agree) return message.value.showMessage('请先同意用户协议')
  if (registerForm.password !== registerForm.passwordConfirm) return message.value.showMessage('两次密码不一致')

  api.post('/auth/register', {
    nickname: registerForm.nickname,
    email: registerForm.email,
    password: registerForm.password
  }).then(res => {
    if (res.data.code === 200) {
      message.value.showMessage('注册成功，请登录')
      loginForm.email = registerForm.email
      mode.value = 'login'
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(err => handleError(err))
}

const handleError = (err) => {
  console.error('请求出错:', err)
  if (err.response) {
    message.value.showMessage(err.response.data.message || '服务器错误')
  } else {
    message.value.showMessage('网络连接失败')
  }
}
</script>

<style scoped>
@keyframes blob { 0% { transform: translate(0px, 0px) scale(1); } 33% { transform: translate(30px, -50px) scale(1.1); } 66% { transform: translate(-20px, 20px) scale(0.9); } 100% { transform: translate(0px, 0px) scale(1); } }
.animate-blob { animation: blob 7s infinite; }
</style>