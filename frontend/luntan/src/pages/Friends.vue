<template>
  <div class="min-h-screen bg-slate-50 pt-20 px-4 pb-10">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-2xl font-black text-slate-800 mb-6 flex items-center gap-2">
        <span>🤝</span> 好友管理
      </h1>

      <!-- 搜索栏 -->
      <div class="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 mb-6 flex gap-2">
        <input v-model="searchQuery" @keyup.enter="handleSearch" placeholder="输入对方邮箱查找好友..." class="flex-1 bg-slate-50 px-4 py-2 rounded-xl outline-none focus:ring-2 focus:ring-purple-300">
        <button @click="handleSearch" class="px-6 py-2 bg-purple-600 text-white font-bold rounded-xl hover:bg-purple-700 transition-colors">搜索</button>
      </div>

      <!-- 分类 Tab -->
      <div class="flex gap-4 mb-6 border-b border-slate-200">
        <button @click="tab = 'list'" :class="['pb-2 px-4 font-bold transition-colors border-b-2', tab === 'list' ? 'border-purple-500 text-purple-600' : 'border-transparent text-slate-400 hover:text-slate-600']">我的好友</button>
        <button @click="tab = 'requests'" :class="['pb-2 px-4 font-bold transition-colors border-b-2 relative', tab === 'requests' ? 'border-purple-500 text-purple-600' : 'border-transparent text-slate-400 hover:text-slate-600']">
           新申请
           <span v-if="requests.length > 0" class="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full animate-ping"></span>
        </button>
      </div>

      <!-- 1. 好友列表 -->
      <div v-if="tab === 'list'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-if="friends.length === 0" class="col-span-full text-center py-12 text-slate-400">暂时没有好友，快去搜索添加吧~</div>
        
        <div v-for="f in friends" :key="f.id" class="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4 hover:shadow-md transition-all group">
           <!-- 头像 (点击看资料) -->
           <div @click.stop="openProfile(f.id)" class="cursor-pointer relative">
             <img :src="auth.formatUrl(f.avatar)" class="w-12 h-12 rounded-full object-cover border border-slate-200">
             <!-- 在线状态 -->
             <div :class="['absolute bottom-0 right-0 w-3 h-3 border-2 border-white rounded-full', f.is_online ? 'bg-green-500' : 'bg-slate-300']"></div>
           </div>
           
           <div class="flex-1 min-w-0">
             <div class="font-bold text-slate-800 truncate">{{ f.username }}</div>
             <div class="text-xs text-slate-400 flex items-center gap-1">
               {{ f.is_online ? '在线' : '离线' }}
             </div>
           </div>
           
           <button @click="startChat(f)" class="px-4 py-1.5 bg-purple-100 text-purple-600 text-xs font-bold rounded-lg hover:bg-purple-200 transition-colors">私聊</button>
        </div>
      </div>

      <!-- 2. 申请列表 -->
      <div v-else class="space-y-4">
        <div v-if="requests.length === 0" class="text-center py-12 text-slate-400">没有新的好友申请</div>
        
        <div v-for="req in requests" :key="req.request_id" class="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between animate-slide-in">
           <div class="flex items-center gap-3">
              <div @click.stop="openProfile(req.user_id)" class="cursor-pointer">
                 <img :src="auth.formatUrl(req.avatar)" class="w-10 h-10 rounded-full border border-slate-200">
              </div>
              <div>
                 <div class="font-bold text-slate-800">{{ req.username }}</div>
                 <div class="text-xs text-slate-400">请求添加你为好友 · {{ new Date(req.timestamp).toLocaleDateString() }}</div>
              </div>
           </div>
           <div class="flex gap-2">
              <button @click="respond(req.request_id, 'accept')" class="px-4 py-1.5 bg-green-500 text-white text-xs font-bold rounded-lg hover:bg-green-600 transition-colors shadow-sm shadow-green-200">同意</button>
              <button @click="respond(req.request_id, 'reject')" class="px-4 py-1.5 bg-slate-100 text-slate-500 text-xs font-bold rounded-lg hover:bg-slate-200 transition-colors">忽略</button>
           </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import api from '@/plugins/axios'
import { useAuthStore } from '@/plugins/auth'

const auth = useAuthStore()
const tab = ref('list')
const friends = ref([])
const requests = ref([])
const searchQuery = ref('')

const openChatWidget = inject('openChatWidget') 
const openProfile = inject('openProfile')

onMounted(() => {
  loadFriends()
  loadRequests()
})

const loadFriends = async () => {
  try {
    const res = await api.get('/api/social/friends')
    if (res.data.code === 200) friends.value = res.data.data
  } catch(e) {}
}

const loadRequests = async () => {
  try {
    const res = await api.get('/api/social/friend/requests')
    if (res.data.code === 200) requests.value = res.data.data
  } catch(e) {}
}

// 搜索好友
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  try {
    const res = await api.get(`/api/social/search?q=${searchQuery.value}`)
    if (res.data.code === 200) {
      // 搜到人了，打开TA的资料卡
      openProfile(res.data.data.id)
      searchQuery.value = ''
    } else {
      alert(res.data.message)
    }
  } catch (e) {
    alert('未找到该用户')
  }
}

const respond = async (reqId, action) => {
  try {
    const res = await api.post('/api/social/friend/respond', { request_id: reqId, action })
    if (res.data.code === 200) {
      loadRequests()
      if (action === 'accept') {
        loadFriends()
        alert('已添加好友！')
      }
    } else {
      alert(res.data.message)
    }
  } catch(e) {
    if (e.response && e.response.status === 403) {
      alert("操作失败：你没有权限处理这条申请")
    }
  }
}

const startChat = (user) => {
  if (openChatWidget) openChatWidget(user)
}
</script>

<style scoped>
.animate-slide-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>