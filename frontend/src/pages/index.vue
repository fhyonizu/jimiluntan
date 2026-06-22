<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 font-sans selection:bg-pink-200">
    
    <!-- 动态背景 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
      <div class="absolute top-[-10%] right-[-10%] w-96 h-96 bg-yellow-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="relative z-50">
      <appheader />
    </div>

    <!-- 顶部欢迎区 -->
    <header class="relative z-10 px-6 py-10 md:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl p-8 md:p-12 relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-r from-white/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
          
          <div class="flex flex-col md:flex-row justify-between gap-8 items-center relative z-10">
            <div class="text-center md:text-left">
              <div class="inline-block px-4 py-1.5 rounded-full bg-white/60 text-pink-500 text-sm font-bold mb-4 shadow-sm border border-white/50 backdrop-blur-sm animate-bounce-slow">
                🐾 欢迎来到哈基米星球
              </div>
              <h1 class="text-5xl md:text-6xl font-extrabold text-slate-800 mb-4 tracking-tight drop-shadow-sm">
                基米<span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-pink-500">论坛</span> 🐱
              </h1>
              <p class="text-lg text-slate-600 mb-8 font-medium max-w-lg mx-auto md:mx-0">
               我要玩嘎啦给木
              </p>
              
              <div class="flex gap-4 justify-center md:justify-start">
                <button @click="goNewPost"
                  class="px-8 py-3.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-full shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-300 transform hover:-translate-y-1 active:scale-95 flex items-center gap-2">
                  <span>🐟</span> 开个罐头 (发帖)
                </button>
                <button v-if="!auth.isLoggedIn" @click="goLogin"
                  class="px-8 py-3.5 bg-white/80 text-slate-700 font-bold rounded-full shadow-md border border-white/60 hover:bg-white transition-all duration-300 transform hover:-translate-y-1 active:scale-95">
                  加入猫窝
                </button>
              </div>
              
              <!-- 搜索栏 -->
              <div class="mt-6 flex items-center gap-2 max-w-md mx-auto md:mx-0">
                <input v-model="searchQuery" @keyup.enter="doSearch"
                  placeholder="搜索帖子..." 
                  class="flex-1 px-4 py-2.5 bg-white/60 backdrop-blur-md border border-white/60 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-purple-300 focus:bg-white transition-all" />
                <button @click="doSearch"
                  class="px-5 py-2.5 bg-slate-700 text-white text-sm font-bold rounded-full hover:bg-slate-800 transition-all flex items-center gap-1">
                  🔍 搜索
                </button>
              </div>
            </div>

            <div class="flex gap-4 md:gap-6">
              <div v-for="(item, idx) in statsList" :key="idx"
                class="flex flex-col items-center justify-center w-24 h-24 md:w-28 md:h-28 bg-white/40 backdrop-blur-md rounded-2xl border border-white/60 shadow-lg hover:bg-white/60 transition-all duration-300 transform hover:scale-110 hover:-rotate-3 cursor-default">
                <div class="text-3xl mb-1">{{ item.icon }}</div>
                <div class="text-xl font-black text-slate-700">{{ item.value }}</div>
                <div class="text-xs text-slate-500 font-bold">{{ item.label }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="relative z-10 mx-auto max-w-7xl px-6 pb-20 md:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">

        <!-- 左侧：分区导航 -->
        <aside class="lg:col-span-1">
          <div class="sticky top-24">
            <div class="bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl p-6 border border-white/50 shadow-purple-100/50">
              <h2 class="text-lg font-bold text-slate-700 mb-4 px-2 flex items-center gap-2">
                🧶 领地巡逻
              </h2>
              <ul class="space-y-3">
                <li v-for="cat in categories" :key="cat.id" @click="switchCategory(cat.id)"
                  class="cursor-pointer transition-all duration-300">
                  <div :class="[
                    'relative px-4 py-3 rounded-2xl transition-all duration-300 border-2 overflow-hidden group',
                    activeCategoryId === cat.id
                      ? 'bg-purple-500 border-purple-500 text-white shadow-lg shadow-purple-500/30 scale-105'
                      : 'bg-white/50 border-transparent hover:border-purple-200 hover:bg-white text-slate-600 hover:shadow-md'
                  ]">
                    <div class="relative z-10 flex items-center justify-between">
                      <span class="font-bold flex items-center gap-2">
                        <span class="text-xl">{{ cat.icon }}</span> {{ cat.name }}
                      </span>
                      <svg v-if="activeCategoryId === cat.id" class="w-5 h-5 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </aside>

        <!-- 中间：帖子列表 -->
        <section class="lg:col-span-2 space-y-6 min-h-[500px]">
          <!-- 筛选栏 -->
          <div class="bg-white/40 backdrop-blur-xl shadow-lg rounded-2xl px-6 py-3 flex items-center justify-between shadow-sm z-20 relative">
            <h2 class="font-bold text-slate-700 flex items-center gap-2">
              <span class="w-2 h-6 bg-pink-400 rounded-full"></span>
              {{ currentCategoryName }} · 动态
            </h2>

            <div class="relative">
              <button @click="isSortDropdownOpen = !isSortDropdownOpen" @blur="closeDropdownWithDelay"
                class="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-600 bg-white/50 hover:bg-white rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-purple-300 active:scale-95">
                <span>{{ currentSortLabel }}</span>
                <svg class="w-4 h-4 transition-transform duration-300" :class="isSortDropdownOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
              </button>
              
              <transition enter-active-class="transition duration-200 ease-out" enter-from-class="transform scale-95 opacity-0 translate-y-2" enter-to-class="transform scale-100 opacity-100 translate-y-0" leave-active-class="transition duration-150 ease-in" leave-from-class="transform scale-100 opacity-100 translate-y-0" leave-to-class="transform scale-95 opacity-0 translate-y-2">
                <div v-if="isSortDropdownOpen" class="absolute right-0 top-full mt-2 w-40 bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-white/60 overflow-hidden z-50 origin-top-right p-1">
                  <ul class="text-sm font-bold text-slate-600">
                    <li @click="selectSort('latest')" class="px-4 py-2.5 rounded-xl cursor-pointer flex items-center gap-2 transition-colors" :class="sortBy === 'latest' ? 'bg-purple-100 text-purple-600' : 'hover:bg-purple-50 hover:text-purple-500'"><span>🌿</span> 新鲜猫薄荷</li>
                    <li @click="selectSort('hot')" class="px-4 py-2.5 rounded-xl cursor-pointer flex items-center gap-2 transition-colors" :class="sortBy === 'hot' ? 'bg-orange-100 text-orange-600' : 'hover:bg-orange-50 hover:text-orange-500'"><span>🥫</span> 热门猫罐头</li>
                  </ul>
                </div>
              </transition>
            </div>
          </div>

          <!-- 帖子内容列表 -->
          <div class="space-y-4">
            
            <!-- 首次加载的骨架屏 -->
            <div v-if="firstLoading" class="space-y-4">
               <div v-for="i in 4" :key="'skeleton-'+i" class="bg-white/40 h-32 rounded-3xl animate-pulse border border-white/30"></div>
            </div>

            <!-- 空状态 -->
            <div v-if="!firstLoading && threads.length === 0" class="bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl p-12 text-center">
              <div class="text-6xl mb-4 animate-bounce">😿</div>
              <p class="text-slate-500 font-medium">哎呀，这个分区连根猫毛都没有~</p>
              <button @click="goNewPost" class="mt-4 text-purple-600 font-bold hover:underline">要不你来发第一贴？</button>
            </div>

            <!-- 帖子渲染 -->
            <article v-for="(thread, idx) in threads" :key="thread.id" @click="router.push('/post/' + thread.id)"
              class="bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl p-5 md:p-6 hover:bg-white transition-all duration-300 transform hover:-translate-y-1.5 hover:shadow-xl hover:shadow-purple-100 cursor-pointer group border border-white/60"
              :style="{ animation: `slideInUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) ${idx * 50}ms both` }">
              
              <div class="flex items-start gap-4">
                <!-- 🔥 更新后的头像显示逻辑 -->
                <div class="flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-200 to-purple-200 flex items-center justify-center shadow-inner overflow-hidden">
                   
                   <img v-if="thread.avatar" :src="auth.formatUrl(thread.avatar)" class="w-full h-full object-cover" />
                   <span v-else class="text-xl select-none">{{ thread.author?.charAt(0).toUpperCase() || '😺' }}</span>
                </div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 text-xs font-bold text-slate-400 mb-1">
                    <span class="bg-blue-100 text-blue-600 px-2 py-0.5 rounded-lg">{{ thread.author }}</span>
                    <span>•</span>
                    <span>{{ formatDate(thread.timestamp) }}</span>
                    <span v-for="tag in thread.tags" :key="tag" class="bg-pink-100 text-pink-500 px-1.5 py-0.5 rounded ml-1">#{{tag}}</span>
                  </div>
                  <h3 class="text-lg font-extrabold text-slate-800 mb-2 group-hover:text-purple-600 transition-colors line-clamp-1">{{ thread.title }}</h3>
                  <p class="text-sm text-slate-500 mb-3 line-clamp-2 leading-relaxed">{{ thread.excerpt }}</p>
                  <div class="flex items-center gap-4">
                    <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 group-hover:bg-purple-50 transition-colors"><span class="text-sm">🐾</span><span class="text-xs font-bold text-slate-600">详情</span></div>
                    <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 group-hover:bg-pink-50 transition-colors"><span class="text-sm">👀</span><span class="text-xs font-bold text-slate-600">{{ thread.views }}</span></div>
                  </div>
                </div>
              </div>
            </article>

            <!-- 底部加载更多骨架屏 -->
            <div v-if="isLoadingMore" class="space-y-4 pt-2">
               <div v-for="i in 2" :key="'more-skeleton-'+i" class="bg-white/40 h-28 rounded-3xl animate-pulse border border-white/30 flex items-center justify-center text-slate-400 text-sm font-bold">
                  正在搬运更多罐头... 🐟
               </div>
            </div>

            <!-- 到底了 -->
            <div v-if="!hasMore && threads.length > 0" class="text-center py-8 text-slate-400 text-xs font-bold">
               — 已经到底啦，喵呜 —
            </div>

            <!-- 哨兵元素 -->
            <div ref="loadSentinel" class="h-4 w-full"></div>

          </div>
        </section>

        <!-- 右侧：热门与公告 -->
        <aside class="lg:col-span-1 space-y-6">
          <div class="bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl p-6 border border-white/50 relative overflow-hidden">
             <div class="absolute -right-4 -top-4 w-20 h-20 bg-orange-100 rounded-full blur-2xl opacity-50"></div>
            <h2 class="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2 relative z-10">🔥 必吃榜 (热门)</h2>
            <ul class="space-y-4 relative z-10">
              <li v-for="(hot, idx) in hotThreads" :key="hot.id" class="group cursor-pointer" @click="router.push('/post/' + hot.id)">
                <div class="flex gap-3 items-start">
                  <span class="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-lg bg-orange-100 text-orange-500 text-xs font-black mt-0.5 group-hover:scale-110 transition-transform">{{ idx + 1 }}</span>
                  <div>
                    <div class="text-sm font-bold text-slate-700 group-hover:text-orange-500 transition-colors line-clamp-2">{{ hot.title }}</div>
                    <div class="text-xs text-slate-400 mt-1 font-medium">{{ hot.views }} 热度</div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
          
          <!-- 公告栏 -->
          <div class="bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl p-6 border border-white/50 bg-gradient-to-b from-white/40 to-blue-50/40">
            <h2 class="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">📢 管理员通知</h2>
            <ul class="space-y-3" v-if="notices.length > 0">
              <li v-for="notice in notices" :key="notice.id" 
                  @click="router.push('/post/' + notice.id)"
                  class="bg-white/60 p-3 rounded-xl hover:scale-105 transition-transform duration-300 cursor-pointer shadow-sm border border-white/50">
                <div class="text-xs font-extrabold text-blue-500 mb-1">📅 {{ formatDate(notice.time) }}</div>
                <div class="text-sm font-bold text-slate-700 line-clamp-1">{{ notice.title }}</div>
              </li>
            </ul>
            <div v-else class="text-xs text-slate-400 text-center py-4">暂无公告喵~</div>
          </div>
        </aside>

      </div>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/plugins/auth.js'
import appheader from '../components/appheader.vue'
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/plugins/axios'

const auth = useAuthStore(); 
const router = useRouter(); 
const route = useRoute()

// 数据状态
const threads = ref([])
const categories = ref([])
const hotThreads = ref([])
const notices = ref([])
const siteStats = ref({ total_posts: 0, today_posts: 0, online_users: 0 })

// 筛选与分页状态
const activeCategoryId = ref('all')
const sortBy = ref('latest')
const isSortDropdownOpen = ref(false)

// 加载状态
const firstLoading = ref(true) 
const isLoadingMore = ref(false) 
const hasMore = ref(true) 
const page = ref(1) 
const pageSize = 10 
const loadSentinel = ref(null)
let observer = null

// 搜索
const searchQuery = ref('')
const doSearch = () => {
  const q = searchQuery.value.trim()
  if (!q) return
  router.push({ path: '/', query: { search: q } })
}

onMounted(async () => {
  await fetchCategories()
  await fetchStats()
  await fetchNotices()
  
  if (route.query.category) {
    const targetId = Number(route.query.category)
    if (!isNaN(targetId)) activeCategoryId.value = targetId
  }
  
  if (route.query.search) {
    searchQuery.value = route.query.search
    await searchPosts(route.query.search)
  } else {
    await fetchPosts(true)
  }
  setupIntersectionObserver()
})

watch(sortBy, () => fetchPosts(true))

const switchCategory = (id) => {
  if (activeCategoryId.value === id) return
  activeCategoryId.value = id
  fetchPosts(true)
}

const fetchPosts = async (isReset = false) => {
  if (isReset) {
    firstLoading.value = true
    page.value = 1
    threads.value = []
    hasMore.value = true
  } else {
    if (isLoadingMore.value || !hasMore.value) return
    isLoadingMore.value = true
  }

  try {
    const params = {
      page: page.value,
      per_page: pageSize,
      sort: sortBy.value
    }
    if (activeCategoryId.value !== 'all') {
      params.category_id = activeCategoryId.value
    }

    // 保持原有的 /api/... 路径
    const res = await api.get('/api/posts/', { params })
    
    if(res.data.code === 200) {
      const newPosts = res.data.data.map(post => ({
        id: post.id,
        categoryId: post.category ? post.category.id : null, 
        title: post.title,
        excerpt: (post.body || '').slice(0, 60).replace(/[#*`]/g, '') + '...', 
        author: post.author.username,
        avatar: post.author.avatar, // 这里拿到的是相对路径
        timestamp: post.timestamp,
        views: post.views,
        tags: post.tags || []
      }))

      if (isReset) {
        threads.value = newPosts
      } else {
        threads.value.push(...newPosts)
      }

      // 使用后端返回的分页信息，避免 off-by-one
      if (res.data.total !== undefined) {
        hasMore.value = page.value < res.data.pages
      } else {
        hasMore.value = newPosts.length >= pageSize
      }
      if (newPosts.length > 0) page.value++
      
      if (isReset) {
         hotThreads.value = [...threads.value].sort((a,b) => b.views - a.views).slice(0, 5)
      }
    }
  } catch (e) { 
    console.error(e) 
  } finally {
    firstLoading.value = false
    isLoadingMore.value = false
  }
}

const setupIntersectionObserver = () => {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore.value && !isLoadingMore.value && !firstLoading.value) {
      fetchPosts(false)
    }
  }, {
    root: null, rootMargin: '100px', threshold: 0.1
  })
  nextTick(() => {
    if (loadSentinel.value) observer.observe(loadSentinel.value)
  })
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/api/posts/categories')
    if(res.data.code === 200) {
      categories.value = [
        { id: 'all', name: '全区动态', icon: '🌍' },
        ...res.data.data
      ]
    }
  } catch (e) { console.error('获取分区失败:', e) }
}

const fetchStats = async () => {
  try {
    const res = await api.get('/api/stats')
    if (res.data.code === 200) siteStats.value = res.data.data
  } catch (e) { console.error('获取统计失败:', e) }
}

const fetchNotices = async () => {
  try {
    const res = await api.get('/api/notices')
    if (res.data.code === 200) notices.value = res.data.data
  } catch (e) { console.error('获取公告失败:', e) }
}

const searchPosts = async (q) => {
  firstLoading.value = true
  try {
    const res = await api.get('/api/posts/search', { params: { q, page: 1, per_page: 50 } })
    if (res.data.code === 200) {
      threads.value = res.data.data.map(post => ({
        id: post.id,
        categoryId: post.category ? post.category.id : null,
        title: post.title,
        excerpt: (post.body || '').slice(0, 60).replace(/[#*`]/g, '') + '...',
        author: post.author.username,
        avatar: post.author.avatar,
        timestamp: post.timestamp,
        views: post.views,
        tags: post.tags || []
      }))
      hasMore.value = false
      hotThreads.value = [...threads.value].sort((a,b) => b.views - a.views).slice(0, 5)
    }
  } catch (e) { console.error(e) }
  finally { firstLoading.value = false }
}

const currentCategoryName = computed(() => {
  if (route.query.search) return `🔍 搜索: "${route.query.search}"`
  const found = categories.value.find(c => c.id === activeCategoryId.value)
  return found ? found.name : '全区动态'
})

const currentSortLabel = computed(() => sortBy.value === 'latest' ? '🌿 新鲜猫薄荷' : '🥫 热门猫罐头')
const statsList = computed(() => [
  { label: '罐头储存', value: siteStats.value.total_posts, icon: '🥫' },
  { label: '今日投喂', value: siteStats.value.today_posts, icon: '🐟' },
  { label: '在线猫猫', value: siteStats.value.online_users, icon: '😺' },
])

const selectSort = (type) => { sortBy.value = type; isSortDropdownOpen.value = false }
const closeDropdownWithDelay = () => setTimeout(() => isSortDropdownOpen.value = false, 200)
const goLogin = () => router.push('/login')
const goNewPost = () => { if (auth.isLoggedIn) router.push('/create'); else router.push('/login') }
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString()

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
@keyframes blob { 0% { transform: translate(0px, 0px) scale(1); } 33% { transform: translate(30px, -50px) scale(1.1); } 66% { transform: translate(-20px, 20px) scale(0.9); } 100% { transform: translate(0px, 0px) scale(1); } }
.animate-blob { animation: blob 7s infinite; }
.animate-bounce-slow { animation: bounce-slow 3s infinite ease-in-out; }
@keyframes bounce-slow { 0%, 100% { transform: translateY(-3px); } 50% { transform: translateY(3px); } }
@keyframes slideInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
</style>