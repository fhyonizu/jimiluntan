<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 py-8 px-4">
    <div class="max-w-2xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <router-link to="/" class="text-slate-500 hover:text-purple-600 font-bold">🐾 回首页</router-link>
        <h1 class="text-2xl font-extrabold text-slate-800">📬 通知中心</h1>
        <div class="w-16"></div>
      </div>

      <!-- 好友申请 -->
      <div class="bg-white/60 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 p-6 mb-6">
        <h2 class="text-lg font-bold text-slate-700 mb-4">👥 好友申请</h2>
        <div v-if="friendRequests.length === 0" class="text-center text-slate-400 text-sm py-8">暂无好友申请</div>
        <div v-else class="space-y-3">
          <div v-for="req in friendRequests" :key="req.request_id" class="flex items-center gap-3 bg-white/50 p-3 rounded-xl">
            <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center font-bold text-indigo-500">
              {{ req.username.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1">
              <span class="font-bold text-slate-700">{{ req.username }}</span>
              <span class="text-xs text-slate-400 ml-2">{{ formatTime(req.timestamp) }}</span>
            </div>
            <div class="flex gap-2">
              <button @click="respondFriend(req.request_id, 'accept')" class="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-lg hover:bg-green-600">接受</button>
              <button @click="respondFriend(req.request_id, 'reject')" class="px-3 py-1 bg-red-400 text-white text-xs font-bold rounded-lg hover:bg-red-500">拒绝</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 未读消息 -->
      <div class="bg-white/60 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 p-6">
        <h2 class="text-lg font-bold text-slate-700 mb-4">💬 未读消息</h2>
        <div v-if="unreadMessages.length === 0" class="text-center text-slate-400 text-sm py-8">没有未读消息</div>
        <div v-else class="space-y-3">
          <div v-for="msg in unreadMessages" :key="msg.id" class="bg-white/50 p-3 rounded-xl flex items-start gap-3">
            <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center font-bold text-purple-500 shrink-0">
              {{ msg.sender_name.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-bold text-sm text-slate-700">{{ msg.sender_name }}</div>
              <div class="text-xs text-slate-500 truncate">{{ msg.body }}</div>
              <div class="text-xs text-slate-400 mt-1">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/plugins/axios'
import Showmessage from '@/components/showmessage.vue'

const message = ref()
const friendRequests = ref([])
const unreadMessages = ref([])

onMounted(async () => {
  try {
    const [reqRes, friendsRes] = await Promise.all([
      api.get('/api/social/friend/requests'),
      api.get('/api/social/friends')
    ])
    if (reqRes.data.code === 200) friendRequests.value = reqRes.data.data
    if (friendsRes.data.code === 200) {
      unreadMessages.value = friendsRes.data.data
        .filter(f => f.unread_count > 0 && f.last_msg)
        .map(f => ({
          id: f.id,
          sender_name: f.username,
          body: f.last_msg,
          timestamp: f.last_msg_time
        }))
    }
  } catch (e) { console.error(e) }
})

const respondFriend = async (requestId, action) => {
  try {
    const res = await api.post('/api/social/friend/respond', { request_id: requestId, action })
    if (res.data.code === 200) {
      friendRequests.value = friendRequests.value.filter(r => r.request_id !== requestId)
      message.value.showMessage(action === 'accept' ? '已添加好友！' : '已拒绝')
    }
  } catch (e) { console.error(e) }
}

const formatTime = (t) => t ? new Date(t).toLocaleString() : ''
</script>
