<template>
  <transition name="fade">
    <div v-if="visible" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm" @click.self="close">
      <div class="bg-white rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl animate-pop">
        
        <div class="h-24 bg-gradient-to-r from-purple-400 to-pink-400 relative">
          <button @click="close" class="absolute top-2 right-2 text-white/80 hover:text-white bg-black/20 rounded-full p-1">✕</button>
        </div>
        
        <div class="px-6 pb-6 relative text-center">
          <!-- 🔥 头像 -->
          <div class="w-24 h-24 rounded-full border-4 border-white bg-indigo-100 absolute -top-12 left-1/2 -translate-x-1/2 overflow-hidden shadow-md flex items-center justify-center text-3xl font-black text-indigo-500 select-none">
             <img v-if="user.avatar" :src="getFullUrl(user.avatar)" class="w-full h-full object-cover">
             <span v-else>{{ (user.username || 'U').charAt(0).toUpperCase() }}</span>
          </div>
          
          <div class="mt-14">
            <h3 class="text-xl font-black text-slate-800 flex items-center justify-center gap-2">
              {{ user.username }}
              <span :class="['w-2.5 h-2.5 rounded-full', user.is_online ? 'bg-green-500' : 'bg-slate-300']" :title="user.is_online?'在线':'离线'"></span>
            </h3>
            <p class="text-sm text-slate-500">{{ user.email }}</p>
            <div class="mt-4 p-3 bg-slate-50 rounded-xl text-sm text-slate-600 italic">
               "{{ user.about_me || '这只猫很神秘...' }}"
            </div>
            
            <div class="mt-6 flex gap-3" v-if="auth.isLoggedIn && !user.is_self">
               <button v-if="!user.is_friend" @click="addFriend" class="flex-1 py-2 rounded-xl bg-purple-100 text-purple-600 font-bold hover:bg-purple-200 transition-colors">➕ 加好友</button>
               <button v-else class="flex-1 py-2 rounded-xl bg-slate-100 text-slate-400 font-bold cursor-default">已是好友</button>
               <button @click="startChat" class="flex-1 py-2 rounded-xl bg-pink-500 text-white font-bold hover:bg-pink-600 shadow-lg shadow-pink-200 transition-colors">💬 私聊</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/plugins/axios'
import { useAuthStore } from '@/plugins/auth'

const visible = ref(false)
const user = ref({})
const auth = useAuthStore()
const emit = defineEmits(['chat'])

const getFullUrl = (path) => auth.formatUrl(path)

const open = async (userId) => {
  try {
    const res = await api.get(`/api/social/user/${userId}`)
    if(res.data.code === 200) {
      user.value = res.data.data
      visible.value = true
    }
  } catch(e) {}
}

const addFriend = async () => {
  try {
    const res = await api.post('/api/social/friend/request', { user_id: user.value.id })
    alert(res.data.message)
    user.value.is_friend = true 
  } catch(e) {}
}

const startChat = () => {
  visible.value = false
  emit('chat', user.value)
}

const close = () => visible.value = false
defineExpose({ open })
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.animate-pop { animation: pop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes pop { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>