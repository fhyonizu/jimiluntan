<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 flex items-center justify-center p-4 relative overflow-hidden font-sans">
    <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>

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

          <div class="bg-white/50 p-1 rounded-xl inline-flex relative shadow-inner">
            <div class="absolute top-1 bottom-1 w-[calc(50%-4px)] bg-white rounded-lg shadow-sm transition-all duration-300 ease-out"
                 :class="mode === 'login' ? 'left-1' : 'left-[calc(50%+2px)]'"></div>
            <button type="button" class="relative z-10 w-24 py-1.5 text-sm font-bold transition-colors rounded-lg"
              :class="mode === 'login' ? 'text-purple-600' : 'text-slate-500 hover:text-slate-700'" @click="mode = 'login'">登录</button>
            <button type="button" class="relative z-10 w-24 py-1.5 text-sm font-bold transition-colors rounded-lg"
              :class="mode === 'register' ? 'text-purple-600' : 'text-slate-500 hover:text-slate-700'" @click="mode = 'register'">注册</button>
          </div>
        </div>

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
            <button type="button" @click="showResetModal = true" class="text-purple-600 font-bold hover:underline">忘记密码？</button>
          </div>
          <button type="submit" class="w-full py-3.5 px-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:scale-[1.02] active:scale-[0.98] transition-all">🚀 立即登录</button>
        </form>

        <!-- 忘记密码弹窗 -->
        <transition name="fade">
          <div v-if="showResetModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="showResetModal = false">
            <div class="bg-white rounded-3xl w-full max-w-sm shadow-2xl p-8 relative animate-pop">
              <h2 class="text-xl font-extrabold text-slate-800 mb-2">🔑 重置密码</h2>
              <p class="text-sm text-slate-500 mb-5">提交申请后，管理员审核通过将为您生成临时密码。</p>
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-bold text-slate-500 mb-1 ml-1">注册邮箱</label>
                  <input v-model="resetEmail" type="email" required placeholder="请输入您的注册邮箱"
                    class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-purple-300 focus:outline-none">
                </div>
                <div v-if="resetResult" :class="['p-3 rounded-xl text-sm font-bold', resetSuccess ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-500']">
                  {{ resetResult }}
                </div>
              </div>
              <div class="flex gap-3 mt-6">
                <button @click="showResetModal = false; resetResult = ''; resetEmail = ''" class="flex-1 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-100 transition-colors">取消</button>
                <button @click="handlePasswordReset" :disabled="resetLoading" class="flex-1 py-3 rounded-xl font-bold text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-lg transition-all disabled:opacity-50">
                  {{ resetLoading ? '提交中...' : '提交申请' }}
                </button>
              </div>
            </div>
          </div>
        </transition>

        <form v-if="mode !== 'login'" @submit.prevent="handleRegister" class="px-8 pb-8 space-y-4">
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
import { authApi } from '@/api'
import { reactive, ref } from 'vue'
import Showmessage from '../components/showmessage.vue'
import router from '../router'
import { useAuthStore } from '@/plugins/auth'

const mode = ref('login')
const message = ref()
const loginForm = reactive({ email: '', password: '', remember: false })
const registerForm = reactive({ nickname: '', email: '', password: '', passwordConfirm: '', agree: false })

// 密码重置
const showResetModal = ref(false)
const resetEmail = ref('')
const resetLoading = ref(false)
const resetResult = ref('')
const resetSuccess = ref(false)

const handlePasswordReset = () => {
  if (!resetEmail.value.trim()) { resetResult.value = '请输入邮箱'; resetSuccess.value = false; return }
  resetLoading.value = true
  resetResult.value = ''
  authApi.requestPasswordReset({ email: resetEmail.value.trim() }).then(res => {
    resetSuccess.value = true
    resetResult.value = res.data.message || '申请已提交'
  }).catch(err => {
    resetSuccess.value = false
    resetResult.value = err._message || '提交失败'
  }).finally(() => { resetLoading.value = false })
}

const handleLogin = () => {
  authApi.login(loginForm).then(res => {
    if (res.data.code === 200) {
      useAuthStore().login(res.data.user, res.data.access_token)
      message.value.showMessage('登录成功！')
      router.push('/')
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(err => {
    message.value.showMessage(err._message || '登录失败')
  })
}

const handleRegister = () => {
  if (!registerForm.agree) return message.value.showMessage('请先同意用户协议')
  if (registerForm.password !== registerForm.passwordConfirm) return message.value.showMessage('两次密码不一致')

  authApi.register({
    nickname: registerForm.nickname,
    email: registerForm.email,
    password: registerForm.password
  }).then(res => {
    if (res.data.code === 200 || res.data.code === 201) {
      message.value.showMessage('注册成功，请登录')
      loginForm.email = registerForm.email
      mode.value = 'login'
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(err => {
    message.value.showMessage(err._message || '注册失败')
  })
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@keyframes popIn { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.animate-pop { animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
</style>
