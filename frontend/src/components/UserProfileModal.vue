<template>
  <transition name="modal">
    <div v-if="visible" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm" @click.self="close">
      <div class="bg-white rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl">

        <div class="h-24 bg-gradient-to-r from-purple-400 to-pink-400 relative">
          <button @click="close" class="absolute top-2 right-2 text-white/80 hover:text-white bg-black/20 rounded-full p-1">✕</button>
        </div>

        <div class="px-6 pb-6 relative text-center">
          <!-- 头像 -->
          <div class="w-24 h-24 rounded-full border-4 border-white bg-indigo-100 absolute -top-12 left-1/2 -translate-x-1/2 overflow-hidden shadow-md flex items-center justify-center text-3xl font-black text-indigo-500 select-none">
             <img v-if="user.avatar" :src="formatUrl(user.avatar)" class="w-full h-full object-cover">
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
import { socialApi } from '@/api'
import { useAuthStore } from '@/plugins/auth'
import { useFormatUrl } from '@/composables/useFormatUrl'

const visible = ref(false)
const user = ref({})
const auth = useAuthStore()
const emit = defineEmits(['chat'])
const { formatUrl } = useFormatUrl()

const open = async (userId) => {
  try {
    const res = await socialApi.userProfile(userId)
    if(res.data.code === 200) {
      user.value = res.data.data
      visible.value = true
    }
  } catch(e) {}
}

const addFriend = async () => {
  try {
    const res = await socialApi.addFriend({ user_id: user.value.id })
    if (res.data.code === 200) {
      user.value.is_friend = true
    }
    // 用简单的 toast 提示
    alert(res.data.message)
  } catch(e) {
    alert(e._message || '请求失败')
  }
}

const startChat = () => {
  visible.value = false
  emit('chat', user.value)
}

const close = () => visible.value = false
defineExpose({ open })
</script>
