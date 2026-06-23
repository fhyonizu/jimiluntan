<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 py-12 px-4 sm:px-6 relative overflow-hidden font-sans">
    <div class="absolute top-0 left-0 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    <div class="absolute top-0 right-0 w-96 h-96 bg-yellow-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
    <div class="absolute bottom-0 left-20 w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>

    <div class="max-w-5xl mx-auto relative z-10">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-extrabold text-slate-800 tracking-tight">
            个人<span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-pink-500">中心</span> 🪐
          </h1>
          <p class="mt-2 text-slate-500 font-medium">欢迎回家，这里是你的专属空间。</p>
        </div>
        <router-link to="/" class="group flex items-center gap-2 px-5 py-2.5 bg-white/50 backdrop-blur-md rounded-full text-slate-600 font-bold hover:bg-white hover:text-purple-600 transition-all shadow-sm">
          <span>🏠</span> <span class="group-hover:translate-x-1 transition-transform">返回首页</span>
        </router-link>
      </div>

      <div v-if="!isLoggedIn" class="bg-white/40 backdrop-blur-xl shadow-xl rounded-3xl p-12 text-center border border-white/60">
        <div class="text-6xl mb-4 animate-bounce">🛸</div>
        <h2 class="text-2xl font-bold text-slate-800 mb-2">你还没有登录哦</h2>
        <router-link to="/login" class="inline-flex items-center px-8 py-3 mt-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-full shadow-lg hover:scale-105 transition-transform">立即登录 / 注册</router-link>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white/40 backdrop-blur-xl shadow-xl rounded-3xl p-8 border border-white/60 relative overflow-hidden group">
            <div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-blue-400 to-purple-400 opacity-20"></div>

            <div class="relative flex flex-col sm:flex-row items-center sm:items-end gap-6 pt-4">
              <div class="relative">
                <div class="w-28 h-28 rounded-full bg-white p-1 shadow-lg">
                  <div class="w-full h-full rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-4xl text-white font-bold overflow-hidden select-none">
                     <img v-if="user.avatar" :src="formatUrl(user.avatar)" class="w-full h-full object-cover" />
                     <span v-else>{{ user.username?.charAt(0).toUpperCase() || 'U' }}</span>
                  </div>
                </div>
                <div :class="['absolute bottom-2 right-2 w-5 h-5 border-4 border-white rounded-full', user.is_online ? 'bg-green-400' : 'bg-slate-300']"></div>
              </div>

              <div class="text-center sm:text-left flex-1 pb-2">
                <h2 class="text-2xl font-black text-slate-800 flex items-center justify-center sm:justify-start gap-2">
                  {{ user.username }}
                  <span class="px-2 py-0.5 rounded-md bg-yellow-100 text-yellow-700 text-xs font-bold border border-yellow-200">LV.1 萌新</span>
                </h2>
                <p class="text-slate-500 font-medium mt-1">{{ user.email }}</p>
                <div class="mt-3 flex flex-wrap gap-2 justify-center sm:justify-start">
                  <span class="px-3 py-1 rounded-full bg-white/50 text-slate-600 text-xs font-bold border border-white/50">👤 用户名: @{{ user.username }}</span>
                  <span class="px-3 py-1 rounded-full bg-white/50 text-slate-600 text-xs font-bold border border-white/50">📅 注册时间: {{ formatDate(user.member_since) }}</span>
                </div>
              </div>
            </div>

            <div class="mt-8 border-t border-white/50 pt-6">
              <h3 class="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2"><span>📝</span> 个人简介</h3>
              <div class="bg-white/40 rounded-2xl p-4 text-slate-600 font-medium min-h-[100px] border border-white/50">
                {{ user.about_me || '这个人很懒，还没有写简介...' }}
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
             <div class="bg-white/40 backdrop-blur-xl p-4 rounded-3xl border border-white/60 text-center shadow-sm hover:scale-105 transition-transform">
                <div class="text-2xl mb-1">✍️</div><div class="text-xl font-black text-slate-800">{{ user.posts_count || 0 }}</div><div class="text-xs text-slate-500 font-bold">发布帖子</div>
             </div>
             <div class="bg-white/40 backdrop-blur-xl p-4 rounded-3xl border border-white/60 text-center shadow-sm hover:scale-105 transition-transform">
                <div class="text-2xl mb-1">👀</div><div class="text-xl font-black text-slate-800">-</div><div class="text-xs text-slate-500 font-bold">被关注</div>
             </div>
          </div>

          <div class="bg-white/40 backdrop-blur-xl shadow-xl rounded-3xl p-6 border border-white/60">
            <h3 class="text-lg font-bold text-slate-700 mb-4 px-2">⚙️ 快捷设置</h3>
            <ul class="space-y-2">
              <li>
                <button @click="openEditModal" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/50 hover:bg-white text-slate-700 font-bold transition-all text-left group">
                  <span class="group-hover:scale-110 transition-transform">✏️</span> 编辑资料
                </button>
              </li>
              <li>
                <button @click="handleLogout" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-red-50/50 hover:bg-red-50 text-red-500 font-bold transition-all text-left group mt-4">
                  <span class="group-hover:scale-110 transition-transform">🚪</span> 退出登录
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="isEditing" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="isEditing = false">
        <div class="bg-white rounded-3xl w-full max-w-md shadow-2xl p-8 relative animate-pop">
          <h2 class="text-2xl font-extrabold text-slate-800 mb-6">装修你的小窝 🛠️</h2>

          <div class="space-y-4">
            <div class="flex items-center gap-4 p-3 bg-slate-50 rounded-xl border border-slate-100">
               <div class="w-16 h-16 rounded-full bg-slate-200 overflow-hidden shrink-0 border-2 border-white shadow-sm">
                  <img v-if="editForm.avatar" :src="formatUrl(editForm.avatar)" class="w-full h-full object-cover">
                  <span v-else class="flex w-full h-full items-center justify-center text-2xl">😺</span>
               </div>
               <div class="flex-1">
                 <div class="text-xs font-bold text-slate-500 mb-2">更换头像</div>
                 <label class="inline-block px-4 py-2 bg-purple-100 text-purple-600 rounded-lg cursor-pointer hover:bg-purple-200 font-bold text-xs transition-colors">
                    📤 上传图片
                    <input type="file" class="hidden" accept="image/*" @change="handleAvatarUpload">
                 </label>
                 <div v-if="uploading" class="text-xs text-purple-400 mt-1 animate-pulse">上传中...</div>
               </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-500 mb-1 ml-1">昵称</label>
              <input v-model="editForm.nickname" type="text" class="w-full px-4 py-3 bg-slate-50 rounded-xl font-bold text-slate-700 focus:ring-2 focus:ring-purple-300 outline-none">
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-500 mb-1 ml-1">个人简介</label>
              <textarea v-model="editForm.about_me" rows="3" class="w-full px-4 py-3 bg-slate-50 rounded-xl text-slate-700 focus:ring-2 focus:ring-purple-300 outline-none resize-none"></textarea>
            </div>
          </div>

          <div class="flex gap-3 mt-8">
            <button @click="isEditing = false" class="flex-1 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-100 transition-colors">取消</button>
            <button @click="saveProfile" :disabled="saving" class="flex-1 py-3 rounded-xl font-bold text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-lg hover:scale-[1.02] transition-all disabled:opacity-50">
              {{ saving ? '保存中...' : '确认保存' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/plugins/auth'
import { storeToRefs } from 'pinia'
import { usersApi, mainApi } from '@/api'
import { useFormatDate } from '@/composables/useFormatDate'
import { useFormatUrl } from '@/composables/useFormatUrl'
import Showmessage from '@/components/showmessage.vue'

const authStore = useAuthStore()
const router = useRouter()
const message = ref()
const { user, isLoggedIn, token } = storeToRefs(authStore)
const { formatDate } = useFormatDate()
const { formatUrl } = useFormatUrl()

const isEditing = ref(false)
const saving = ref(false)
const uploading = ref(false)
const editForm = reactive({ nickname: '', about_me: '', avatar: '' })

const openEditModal = () => {
  editForm.nickname = user.value.username
  editForm.about_me = user.value.about_me
  editForm.avatar = user.value.avatar
  isEditing.value = true
}

const handleAvatarUpload = async (e) => {
  const file = e.target.files[0]
  if(!file) return

  const formData = new FormData()
  formData.append('file', file)

  uploading.value = true
  try {
    const res = await mainApi.upload(formData)
    if(res.data.code === 200) {
      editForm.avatar = res.data.url
      message.value.showMessage('头像上传成功')
    } else {
      message.value.showMessage(res.data.message)
    }
  } catch(e) {
    message.value.showMessage('上传失败，请检查网络')
  } finally {
    uploading.value = false
  }
}

const saveProfile = () => {
  if(!editForm.nickname) return message.value.showMessage('昵称不能为空')

  saving.value = true
  usersApi.updateMe(editForm).then(res => {
    if(res.data.code === 200) {
      message.value.showMessage('保存成功！')
      authStore.login(res.data.data, token.value)
      isEditing.value = false
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(err => {
    message.value.showMessage(err._message || '网络错误')
  }).finally(() => {
    saving.value = false
  })
}

const handleLogout = () => {
  if(confirm('确定要退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@keyframes popIn { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.animate-pop { animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
</style>
