<template>
  <div ref="widgetRef" :style="styleObject" class="fixed z-[9999] transition-all duration-75 ease-out">
    
    <!-- 1. 悬浮球 -->
    <div v-if="!isExpanded" 
         @mousedown="startDrag" @touchstart="startDrag" @click="toggleExpand"
         class="w-14 h-14 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 shadow-lg shadow-purple-500/40 flex items-center justify-center cursor-pointer hover:scale-110 transition-transform relative group select-none touch-none">
       <span class="text-2xl">💬</span>
       <div v-if="totalUnread > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs font-bold flex items-center justify-center border-2 border-white animate-bounce">
         {{ totalUnread }}
       </div>
    </div>

    <!-- 2. 聊天窗口 -->
    <div v-else class="w-80 h-[500px] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-pop-in">
      
      <!-- 顶部 -->
      <div @mousedown="startDrag" @touchstart="startDrag" class="h-10 bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-between px-4 cursor-move shrink-0 select-none touch-none">
        <span class="text-white font-bold text-sm flex items-center gap-2">
           <!-- 点击顶部标题看对方资料 -->
           <span v-if="currentChatUser" @click.stop="openProfile(currentChatUser.id)" class="truncate max-w-[150px] cursor-pointer hover:underline">{{ currentChatUser.username }}</span>
           <span v-else>消息中心</span>
        </span>
        <div class="flex items-center gap-2">
           <button @click.stop="isExpanded = false" class="text-white/80 hover:text-white text-lg font-bold leading-none px-2">_</button>
        </div>
      </div>

      <!-- 内容 -->
      <div class="flex-1 overflow-hidden flex flex-col bg-slate-50 relative">
        
        <!-- A. 聊天界面 -->
        <div v-if="currentChatUser" class="flex-1 flex flex-col h-full">
           <div class="px-3 py-2 bg-white border-b border-slate-100 flex items-center gap-2 shrink-0">
              <button @click="currentChatUser = null" class="text-xs bg-slate-100 px-2 py-1 rounded hover:bg-slate-200 text-slate-600">← 返回列表</button>
           </div>
           
           <!-- 消息记录 -->
           <div ref="msgBox" class="flex-1 overflow-y-auto p-3 space-y-3 custom-scroll">
              <div v-for="msg in messages" :key="msg.id" :class="['flex items-start gap-2', msg.sender_id === auth.user.id ? 'flex-row-reverse' : 'flex-row']">
                 
                 <!-- 聊天头像 -->
                 <div @click.stop="openProfile(msg.sender_id === auth.user.id ? auth.user.id : msg.sender_id)" class="w-8 h-8 rounded-full shrink-0 overflow-hidden bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-500 border border-white shadow-sm cursor-pointer">
                    <img v-if="msg.sender_id === auth.user.id ? auth.user.avatar : msg.sender_avatar" 
                         :src="auth.formatUrl(msg.sender_id === auth.user.id ? auth.user.avatar : msg.sender_avatar)" 
                         class="w-full h-full object-cover">
                    <span v-else>{{ (msg.sender_name || 'U').charAt(0).toUpperCase() }}</span>
                 </div>

                 <!-- 气泡 -->
                 <div :class="['max-w-[70%] px-3 py-2 rounded-xl text-sm break-all shadow-sm', 
                    msg.sender_id === auth.user.id ? 'bg-purple-500 text-white rounded-tr-none' : 'bg-white text-slate-700 rounded-tl-none border border-slate-100']">
                    {{ msg.body }}
                 </div>
              </div>
           </div>

           <!-- 输入框 -->
           <div class="p-3 bg-white border-t border-slate-100 flex gap-2 shrink-0">
              <input v-model="inputText" @keyup.enter="sendMessage" class="flex-1 bg-slate-100 rounded-full px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-purple-300 transition-all" placeholder="说点什么...">
              <button @click="sendMessage" class="w-9 h-9 bg-purple-500 rounded-full text-white flex items-center justify-center hover:bg-purple-600 transition-colors shadow-md">➤</button>
           </div>
        </div>

        <!-- B. 好友列表 -->
        <div v-else class="h-full overflow-y-auto p-2 space-y-2 custom-scroll">
           <div v-if="friends.length === 0" class="text-center text-slate-400 text-xs py-10 flex flex-col gap-2">
             <span>🍃</span><span>暂无好友</span>
           </div>
           
           <div v-for="f in friends" :key="f.id" @click="openChat(f)" 
                class="flex items-center gap-3 p-3 bg-white rounded-xl cursor-pointer hover:bg-purple-50 transition-colors shadow-sm relative group border border-transparent hover:border-purple-100">
              
              <div class="relative shrink-0">
                 <div class="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center overflow-hidden border border-slate-100 text-indigo-500 font-bold text-lg">
                    <img v-if="f.avatar" :src="auth.formatUrl(f.avatar)" class="w-full h-full object-cover">
                    <span v-else>{{ f.username.charAt(0).toUpperCase() }}</span>
                 </div>
                 <div :class="['absolute bottom-0 right-0 w-3 h-3 border-2 border-white rounded-full', f.is_online ? 'bg-green-500' : 'bg-slate-300']"></div>
              </div>

              <div class="flex-1 min-w-0">
                 <div class="flex justify-between items-center mb-1">
                    <span class="font-bold text-slate-700 text-sm truncate">{{ f.username }}</span>
                    <span class="text-[10px] text-slate-400">{{ formatTime(f.last_msg_time) }}</span>
                 </div>
                 <div class="text-xs text-slate-500 truncate">{{ f.last_msg || '暂无消息...' }}</div>
              </div>
              
              <div v-if="f.unread_count > 0" class="w-5 h-5 bg-red-500 rounded-full text-white text-[10px] font-bold flex items-center justify-center shadow-sm">
                 {{ f.unread_count }}
              </div>
           </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch, inject } from 'vue'
import { useAuthStore } from '@/plugins/auth'
import api from '@/plugins/axios'
import { useDraggable, useWindowSize } from '@vueuse/core'

const auth = useAuthStore()
const widgetRef = ref(null)
const { width, height } = useWindowSize()
const openProfile = inject('openProfile') // 注入

const { x, y } = useDraggable(widgetRef, {
  initialValue: { x: window.innerWidth - 100, y: window.innerHeight - 150 },
  preventDefault: false
})

const styleObject = computed(() => {
  const w = isExpanded.value ? 320 : 60
  const h = isExpanded.value ? 500 : 60
  let safeX = Math.min(Math.max(0, x.value), width.value - w)
  let safeY = Math.min(Math.max(0, y.value), height.value - h)
  return { left: `${safeX}px`, top: `${safeY}px` }
})

const isExpanded = ref(false)
const isDragging = ref(false)
const friends = ref([])
const currentChatUser = ref(null)
const messages = ref([])
const inputText = ref('')
const msgBox = ref(null)

const totalUnread = computed(() => friends.value.reduce((sum, f) => sum + (f.unread_count || 0), 0))

let startPos = { x: 0, y: 0 }
const startDrag = (e) => {
  startPos = { x: e.clientX || e.touches[0].clientX, y: e.clientY || e.touches[0].clientY }
  isDragging.value = false
  const onUp = (evt) => {
    const endX = evt.clientX || evt.changedTouches[0].clientX
    const endY = evt.clientY || evt.changedTouches[0].clientY
    if (Math.abs(endX - startPos.x) > 5 || Math.abs(endY - startPos.y) > 5) {
      isDragging.value = true
    }
    document.removeEventListener('mouseup', onUp)
    document.removeEventListener('touchend', onUp)
  }
  document.addEventListener('mouseup', onUp)
  document.addEventListener('touchend', onUp)
}

const toggleExpand = () => {
  if (!isDragging.value) {
    isExpanded.value = !isExpanded.value
    if (isExpanded.value) loadFriends()
  }
}

const loadFriends = async () => {
  try {
    const res = await api.get('/api/social/friends')
    if (res.data.code === 200) friends.value = res.data.data
  } catch (e) {}
}

const openChat = async (user) => {
  currentChatUser.value = user
  if (user.unread_count > 0) {
    user.unread_count = 0
    auth.unreadCount = Math.max(0, auth.unreadCount - 1)
    await api.post('/api/social/message/read', { partner_id: user.id })
  }
  loadHistory(user.id)
}

const loadHistory = async (uid) => {
  const res = await api.get(`/api/social/messages/${uid}`)
  if (res.data.code === 200) {
    messages.value = res.data.data
    scrollToBottom()
  }
}

const sendMessage = () => {
  if (!inputText.value.trim()) return
  // 🔥 修复：只通过 socket 发送，不手动 push 到数组
  // 等待 socket 广播回来后再显示，防止重复
  auth.socket.emit('send_message', { 
    receiver_id: currentChatUser.value.id, 
    body: inputText.value 
  })
  inputText.value = ''
}

watch(() => auth.socket, (socket) => {
  if (!socket) return
  socket.on('new_message', (msg) => {
    if (currentChatUser.value && (msg.sender_id === currentChatUser.value.id || msg.sender_id === auth.user.id)) {
      // 🔥 修复：去重检查
      const exists = messages.value.some(m => m.id === msg.id)
      if (!exists) {
        messages.value.push(msg)
        scrollToBottom()
        if(msg.sender_id !== auth.user.id) api.post('/api/social/message/read', { partner_id: msg.sender_id })
      }
    }
    loadFriends()
  })
}, { immediate: true })

const scrollToBottom = () => nextTick(() => { if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight })
const formatTime = (t) => t ? new Date(t).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) : ''

const open = (user) => {
  isExpanded.value = true
  openChat(user)
}
defineExpose({ open })

onMounted(() => {
  if (auth.isLoggedIn) {
    auth.initSocket()
    loadFriends()
  }
})
</script>

<style scoped>
.animate-pop-in { animation: popIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes popIn { from { transform: scale(0.8); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
</style>