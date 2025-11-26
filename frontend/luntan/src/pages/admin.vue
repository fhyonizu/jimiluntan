<template>
  <div class="min-h-screen bg-slate-900 font-sans selection:bg-purple-500 text-slate-200">
    
    <!-- 1. 左侧导航栏 -->
    <nav class="fixed left-0 top-0 h-full w-64 bg-slate-800/50 backdrop-blur-xl border-r border-slate-700 p-6 z-20 flex flex-col">
      <div class="flex items-center gap-3 mb-10 text-purple-400">
        <span class="text-3xl">🛡️</span>
        <h1 class="text-xl font-bold tracking-wider">控制台</h1>
      </div>
      
      <div class="space-y-2 flex-1">
        <button @click="switchView('dashboard')" :class="navClass('dashboard')">📊 数据概览</button>
        <button @click="switchView('users')" :class="navClass('users')">👥 用户管理</button>
        <button @click="switchView('categories')" :class="navClass('categories')">🌈 板块管理</button>
        <button @click="switchView('posts')" :class="navClass('posts')">📝 文章管理</button>
        <button @click="switchView('comments')" :class="navClass('comments')">💬 评论管理</button>
      </div>

      <router-link to="/" class="block px-4 py-3 mt-8 flex items-center gap-2 text-slate-500 hover:text-white transition-colors border-t border-slate-700/50 pt-6">
        <span>←</span> 返回前台
      </router-link>
    </nav>

    <!-- 2. 主体内容 -->
    <main class="pl-64">
      <header class="h-20 border-b border-slate-800 flex items-center justify-between px-10 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <h2 class="text-lg font-medium text-slate-400">
          当前位置：<span class="text-purple-400 font-bold">{{ viewName }}</span>
        </h2>
        <div class="flex items-center gap-4">
          <div class="text-right hidden sm:block">
            <div class="text-sm font-bold text-white">Admin</div>
            <div class="text-xs text-slate-500">超级管理员</div>
          </div>
          <!-- 管理员自己的头像 -->
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-purple-900/50 overflow-hidden">
             <img v-if="auth.user.avatar" :src="auth.formatUrl(auth.user.avatar)" class="w-full h-full object-cover">
             <span v-else>A</span>
          </div>
        </div>
      </header>

      <div class="p-10 max-w-7xl mx-auto min-h-[calc(100vh-80px)]">
        
        <!-- View 1: 数据概览 (Dashboard) -->
        <div v-if="currentView === 'dashboard'" class="animate-fade-in">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 hover:border-purple-500/50 transition-colors">
              <div class="text-3xl mb-4 bg-slate-700/50 w-12 h-12 rounded-lg flex items-center justify-center">👥</div>
              <div class="text-3xl font-black text-white mb-1">{{ stats.users }}</div>
              <div class="text-xs text-slate-500 font-bold uppercase tracking-wider">总用户数</div>
            </div>
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 hover:border-purple-500/50 transition-colors">
              <div class="text-3xl mb-4 bg-slate-700/50 w-12 h-12 rounded-lg flex items-center justify-center">📝</div>
              <div class="text-3xl font-black text-white mb-1">{{ stats.posts }}</div>
              <div class="text-xs text-slate-500 font-bold uppercase tracking-wider">帖子总数</div>
            </div>
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 hover:border-purple-500/50 transition-colors">
              <div class="text-3xl mb-4 bg-slate-700/50 w-12 h-12 rounded-lg flex items-center justify-center">💬</div>
              <div class="text-3xl font-black text-white mb-1">{{ stats.comments }}</div>
              <div class="text-xs text-slate-500 font-bold uppercase tracking-wider">评论总数</div>
            </div>
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 hover:border-purple-500/50 transition-colors">
              <div class="text-3xl mb-4 bg-slate-700/50 w-12 h-12 rounded-lg flex items-center justify-center">📂</div>
              <div class="text-3xl font-black text-white mb-1">{{ stats.categories }}</div>
              <div class="text-xs text-slate-500 font-bold uppercase tracking-wider">活跃板块</div>
            </div>
          </div>
        </div>

        <!-- View 2: 用户管理 (Users) -->
        <div v-if="currentView === 'users'" class="animate-fade-in">
          <div class="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
             <table class="w-full text-left border-collapse">
               <thead>
                 <tr class="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
                   <th class="p-5 font-bold">用户详情</th>
                   <th class="p-5 font-bold">角色</th>
                   <th class="p-5 font-bold">注册时间</th>
                   <th class="p-5 font-bold text-right">操作</th>
                 </tr>
               </thead>
               <tbody class="divide-y divide-slate-700">
                 <tr v-for="user in userList" :key="user.id" class="hover:bg-slate-700/30 transition-colors">
                   <td class="p-5 flex items-center gap-3">
                     <div class="w-10 h-10 rounded-full bg-slate-600 flex items-center justify-center overflow-hidden border border-slate-500">
                        <!-- 🔥 核心修改：使用 auth.formatUrl 处理头像路径 -->
                        <img v-if="user.avatar" :src="auth.formatUrl(user.avatar)" class="w-full h-full object-cover">
                        <span v-else class="text-sm font-bold">{{ user.username.charAt(0).toUpperCase() }}</span>
                     </div>
                     <div>
                       <div class="font-bold text-white">{{ user.username }}</div>
                       <div class="text-xs text-slate-500">{{ user.email || '未绑定邮箱' }}</div>
                     </div>
                   </td>
                   <td class="p-5">
                     <span :class="['px-2 py-1 rounded text-xs font-bold', user.role === 'admin' ? 'bg-purple-500/20 text-purple-300' : 'bg-slate-700 text-slate-300']">
                       {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                     </span>
                   </td>
                   <td class="p-5 text-sm text-slate-400">{{ formatDate(user.timestamp || new Date()) }}</td>
                   <td class="p-5 text-right">
                     <button @click="deleteUser(user.id)" class="text-slate-500 hover:text-red-400 transition-colors text-sm font-bold bg-slate-900 hover:bg-red-900/30 px-3 py-1.5 rounded border border-slate-700">移除</button>
                   </td>
                 </tr>
               </tbody>
             </table>
             <div v-if="userList.length === 0" class="p-10 text-center text-slate-500">暂无数据</div>
          </div>
        </div>

        <!-- View 3: 板块管理 (Categories) -->
        <div v-if="currentView === 'categories'" class="animate-fade-in">
          <div class="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 mb-8 flex flex-col md:flex-row gap-4 items-end shadow-lg">
            <div class="flex-1 w-full"><label class="block text-xs font-bold text-slate-500 mb-2 uppercase">板块名称</label><input v-model="newCat.name" type="text" placeholder="例如: 摸鱼区" class="w-full bg-slate-900 border border-slate-700 text-white px-4 py-2.5 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all"></div>
            <div><label class="block text-xs font-bold text-slate-500 mb-2 uppercase">图标 (Emoji)</label><input v-model="newCat.icon" type="text" placeholder="🐟" class="bg-slate-900 border border-slate-700 text-white px-4 py-2.5 rounded-lg w-24 text-center focus:outline-none focus:border-purple-500 transition-all"></div>
            <button @click="addCategory" class="w-full md:w-auto px-6 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition-colors shadow-lg shadow-purple-900/40 flex items-center justify-center gap-2"><span>+</span> 创建</button>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="cat in categories" :key="cat.id" class="bg-slate-800 p-5 rounded-xl border border-slate-700 flex justify-between items-center group hover:border-purple-500/30 hover:bg-slate-800/80 transition-all">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-lg bg-slate-700/50 flex items-center justify-center text-2xl">{{ cat.icon }}</div>
                <span class="font-bold text-lg text-slate-200">{{ cat.name }}</span>
              </div>
              <button @click="deleteCategory(cat.id)" class="text-slate-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all p-2 hover:bg-slate-700 rounded-lg">❌</button>
            </div>
          </div>
        </div>

        <!-- View 4: 文章管理 (Posts) -->
        <div v-if="currentView === 'posts'" class="animate-fade-in">
          <div class="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
             <table class="w-full text-left border-collapse">
               <thead>
                 <tr class="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
                   <th class="p-5 font-bold w-1/2">标题</th>
                   <th class="p-5 font-bold">作者</th>
                   <th class="p-5 font-bold">板块</th>
                   <th class="p-5 font-bold">数据</th>
                   <th class="p-5 font-bold text-right">操作</th>
                 </tr>
               </thead>
               <tbody class="divide-y divide-slate-700">
                 <tr v-for="post in postList" :key="post.id" class="hover:bg-slate-700/30 transition-colors group">
                   <td class="p-5">
                     <a :href="`/post/${post.id}`" target="_blank" class="font-bold text-slate-200 hover:text-purple-400 transition-colors block truncate max-w-md">{{ post.title }}</a>
                     <div class="text-xs text-slate-500 mt-1 truncate">{{ post.body.substring(0, 30) }}...</div>
                   </td>
                   <td class="p-5 text-sm text-slate-300">{{ post.author?.username || '未知' }}</td>
                   <td class="p-5">
                     <span class="bg-slate-900 text-slate-400 border border-slate-700 px-2 py-1 rounded text-xs">{{ post.category?.name || '无' }}</span>
                   </td>
                   <td class="p-5 text-xs text-slate-500">
                     <div>👀 {{ post.views }} 浏览</div>
                     <div>📅 {{ formatDate(post.timestamp) }}</div>
                   </td>
                   <td class="p-5 text-right">
                     <button @click="deletePost(post.id)" class="text-slate-500 hover:text-red-400 transition-colors text-sm font-bold bg-slate-900 hover:bg-red-900/30 px-3 py-1.5 rounded border border-slate-700">删除</button>
                   </td>
                 </tr>
               </tbody>
             </table>
             <div v-if="postList.length === 0" class="p-10 text-center text-slate-500">暂无文章</div>
          </div>
        </div>

        <!-- View 5: 评论管理 (Comments) -->
        <div v-if="currentView === 'comments'" class="animate-fade-in">
          <div class="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
             <table class="w-full text-left border-collapse">
               <thead>
                 <tr class="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
                   <th class="p-5 font-bold w-1/2">评论内容</th>
                   <th class="p-5 font-bold">发布人</th>
                   <th class="p-5 font-bold">所属文章</th>
                   <th class="p-5 font-bold text-right">操作</th>
                 </tr>
               </thead>
               <tbody class="divide-y divide-slate-700">
                 <tr v-for="comment in commentList" :key="comment.id" class="hover:bg-slate-700/30 transition-colors">
                   <td class="p-5">
                     <div class="text-sm text-slate-300 line-clamp-2 leading-relaxed">{{ comment.body }}</div>
                     <div class="text-xs text-slate-500 mt-1">{{ formatDate(comment.timestamp) }}</div>
                   </td>
                   <td class="p-5 text-sm font-bold text-slate-400">{{ comment.author?.username || '未知用户' }}</td>
                   <td class="p-5 text-sm text-purple-400 truncate max-w-xs">
                     <a :href="`/post/${comment.post_id}`" target="_blank" class="hover:underline">ID: {{ comment.post_id }}</a>
                   </td>
                   <td class="p-5 text-right">
                     <button @click="deleteComment(comment.id)" class="text-slate-500 hover:text-red-400 transition-colors text-sm font-bold bg-slate-900 hover:bg-red-900/30 px-3 py-1.5 rounded border border-slate-700">删除</button>
                   </td>
                 </tr>
               </tbody>
             </table>
             <div v-if="commentList.length === 0" class="p-10 text-center text-slate-500">暂无评论</div>
          </div>
        </div>

      </div>
    </main>
    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/plugins/axios'
import Showmessage from '@/components/showmessage.vue'
import { useAuthStore } from '@/plugins/auth' // 🔥 引入 Auth Store

// 核心状态
const currentView = ref('dashboard')
const message = ref()
const stats = ref({ users: 0, posts: 0, categories: 0, comments: 0 })
const auth = useAuthStore() // 🔥 实例化

// 数据列表
const categories = ref([])
const userList = ref([])
const postList = ref([])
const commentList = ref([])

// 临时表单
const newCat = ref({ name: '', icon: '' })

// 视图名称映射
const viewName = computed(() => {
  const map = {
    'dashboard': '数据概览',
    'users': '用户管理',
    'categories': '板块管理',
    'posts': '文章管理',
    'comments': '评论管理'
  }
  return map[currentView.value]
})

// 初始化
onMounted(() => {
  fetchStats()
  fetchCategories()
})

// 导航切换
const navClass = (view) => {
  const base = "w-full text-left px-4 py-3 rounded-xl transition-all duration-200 flex items-center gap-3 text-sm font-medium"
  if (currentView.value === view) {
    return `${base} bg-purple-600/20 text-purple-300 border border-purple-500/30 shadow-lg shadow-purple-900/20`
  }
  return `${base} text-slate-400 hover:bg-slate-700/50 hover:text-white`
}

const switchView = (view) => {
  currentView.value = view
  // 切换视图时按需加载数据
  if (view === 'users') fetchUsers()
  if (view === 'posts') fetchPosts()
  if (view === 'comments') fetchComments()
  if (view === 'categories') fetchCategories()
  if (view === 'dashboard') fetchStats()
}

// --- API 请求逻辑 ---

// 1. 概览数据
const fetchStats = () => { 
  api.get('/api/admin/stats').then(res => { if (res.data.code === 200) stats.value = res.data.data }) 
}

// 2. 分类管理
const fetchCategories = () => { 
  api.get('/api/admin/categories').then(res => { if (res.data.code === 200) categories.value = res.data.data }) 
}
const addCategory = () => {
  if (!newCat.value.name) return message.value.showMessage('名字不能为空')
  api.post('/api/admin/categories', newCat.value).then(res => {
    if (res.data.code === 200) { 
      message.value.showMessage('创建成功！'); 
      newCat.value = { name: '', icon: '' }; 
      fetchCategories(); fetchStats() 
    } else { 
      message.value.showMessage(res.data.message) 
    }
  })
}
const deleteCategory = (id) => {
  if (!confirm('确定要删除这个板块吗？')) return
  api.delete(`/api/admin/categories/${id}`).then(res => { 
    if (res.data.code === 200) { message.value.showMessage('已删除'); fetchCategories() } 
  })
}

// 3. 用户管理
const fetchUsers = () => {
  api.get('/api/admin/users').then(res => { if (res.data.code === 200) userList.value = res.data.data })
}
const deleteUser = (id) => {
  if (!confirm('警告：确定要删除该用户吗？此操作不可逆！')) return
  api.delete(`/api/admin/users/${id}`).then(res => {
    if (res.data.code === 200) { message.value.showMessage('用户已删除'); fetchUsers(); fetchStats() }
  })
}

// 4. 文章管理
const fetchPosts = () => {
  api.get('/api/admin/posts').then(res => { if (res.data.code === 200) postList.value = res.data.data })
}
const deletePost = (id) => {
  if (!confirm('确定要删除这篇文章吗？')) return
  api.delete(`/api/admin/posts/${id}`).then(res => {
    if (res.data.code === 200) { message.value.showMessage('文章已删除'); fetchPosts(); fetchStats() }
  })
}

// 5. 评论管理
const fetchComments = () => {
  api.get('/api/admin/comments').then(res => { if (res.data.code === 200) commentList.value = res.data.data })
}
const deleteComment = (id) => {
  if (!confirm('确定删除这条评论？')) return
  api.delete(`/api/admin/comments/${id}`).then(res => {
    if (res.data.code === 200) { message.value.showMessage('评论已删除'); fetchComments(); fetchStats() }
  })
}

// 工具函数
const formatDate = (str) => new Date(str).toLocaleDateString() + ' ' + new Date(str).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>