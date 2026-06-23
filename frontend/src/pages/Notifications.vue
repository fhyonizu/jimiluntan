<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 py-8 px-4">
    <div class="max-w-2xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <router-link to="/" class="inline-flex items-center gap-1 text-slate-500 hover:text-purple-600 font-medium transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
          返回主页
        </router-link>
        <h1 class="text-2xl font-extrabold text-slate-800">📬 通知中心</h1>
        <button @click="collapseAll = !collapseAll" class="w-9 h-9 flex items-center justify-center rounded-xl bg-white/60 border border-white/60 text-slate-500 hover:text-purple-600 hover:bg-white hover:border-purple-200 hover:scale-110 active:scale-95 transition-all duration-200 shadow-sm" :title="collapseAll ? '展开' : '收起'">
          <svg class="w-4 h-4 transition-transform duration-300" :class="{ 'rotate-180': collapseAll }" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        </button>
      </div>

      <!-- 好友申请 -->
      <div class="bg-white/60 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 mb-6 overflow-hidden transition-all duration-300">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-slate-700">👥 好友申请</h2>
            <button @click="sections.requests = !sections.requests" class="w-8 h-8 flex items-center justify-center rounded-lg bg-white/50 text-slate-400 hover:text-purple-600 hover:bg-white hover:scale-110 active:scale-95 transition-all duration-200">
              <svg class="w-4 h-4 transition-transform duration-300" :class="{ 'rotate-180': sections.requests }" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
            </button>
          </div>
          <div v-show="sections.requests">
            <div v-if="friendRequests.length === 0" class="text-center text-slate-400 text-sm py-8">暂无好友申请</div>
            <div v-else class="space-y-3">
              <div v-for="req in friendRequests" :key="req.request_id" class="flex items-center gap-3 bg-white/50 p-3 rounded-xl">
                <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center font-bold text-indigo-500">
                  {{ req.username.charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1">
                  <span class="font-bold text-slate-700">{{ req.username }}</span>
                  <span class="text-xs text-slate-400 ml-2">{{ formatTimeAgo(req.timestamp) }}</span>
                </div>
                <div class="flex gap-2">
                  <button @click="respondFriend(req.request_id, 'accept')" class="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-lg hover:bg-green-600 active:scale-95 transition-all">接受</button>
                  <button @click="respondFriend(req.request_id, 'reject')" class="px-3 py-1 bg-red-400 text-white text-xs font-bold rounded-lg hover:bg-red-500 active:scale-95 transition-all">拒绝</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 未读消息 -->
      <div class="bg-white/60 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 overflow-hidden transition-all duration-300">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-slate-700">💬 未读消息</h2>
            <button @click="sections.messages = !sections.messages" class="w-8 h-8 flex items-center justify-center rounded-lg bg-white/50 text-slate-400 hover:text-purple-600 hover:bg-white hover:scale-110 active:scale-95 transition-all duration-200">
              <svg class="w-4 h-4 transition-transform duration-300" :class="{ 'rotate-180': sections.messages }" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
            </button>
          </div>
          <div v-show="sections.messages">
            <div v-if="unreadMessages.length === 0" class="text-center text-slate-400 text-sm py-8">没有未读消息</div>
            <div v-else class="space-y-3">
              <div v-for="msg in unreadMessages" :key="msg.id" class="bg-white/50 p-3 rounded-xl flex items-start gap-3">
                <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center font-bold text-purple-500 shrink-0">
                  {{ msg.sender_name.charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="font-bold text-sm text-slate-700">{{ msg.sender_name }}</div>
                  <div class="text-xs text-slate-500 truncate">{{ msg.body }}</div>
                  <div class="text-xs text-slate-400 mt-1">{{ formatTimeAgo(msg.timestamp) }}</div>
                </div>
              </div>
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
import { socialApi } from '@/api'
import { useFormatDate } from '@/composables/useFormatDate'
import Showmessage from '@/components/showmessage.vue'

const message = ref()
const friendRequests = ref([])
const unreadMessages = ref([])
const collapseAll = ref(false)
const sections = ref({ requests: false, messages: false })
const { formatTimeAgo } = useFormatDate()

onMounted(async () => {
  try {
    const [reqRes, friendsRes] = await Promise.all([
      socialApi.friendRequests(),
      socialApi.friends()
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
    const res = await socialApi.respondFriend({ request_id: requestId, action })
    if (res.data.code === 200) {
      friendRequests.value = friendRequests.value.filter(r => r.request_id !== requestId)
      message.value.showMessage(action === 'accept' ? '已添加好友！' : '已拒绝')
    }
  } catch (e) { console.error(e) }
}
</script>
