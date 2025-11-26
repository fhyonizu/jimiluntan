<template>
  <div class="h-screen w-screen bg-slate-50 flex flex-col overflow-hidden font-sans relative">
    
    <!-- 顶部加载条 -->
    <div v-if="loading" class="fixed top-0 left-0 h-1 bg-purple-500 z-[100] transition-all duration-300 ease-out shadow-[0_0_10px_rgba(168,85,247,0.5)]" :style="{ width: progress + '%' }"></div>

    <!-- 背景动画 -->
    <div class="absolute inset-0 pointer-events-none z-0 opacity-50">
      <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
      <div class="absolute bottom-[-20%] right-[-10%] w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    </div>

    <!-- 1. 顶部导航 -->
    <header class="h-16 bg-white/70 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-6 z-30 shrink-0">
      <div class="flex items-center gap-4 overflow-hidden">
        <button @click="$router.push('/')" class="p-2 rounded-full hover:bg-slate-100 transition-colors text-slate-500" title="回首页">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
        </button>
        
        <h1 class="text-lg font-bold text-slate-800 truncate max-w-md flex items-center gap-2">
          <span v-if="isDetailMode">{{ post?.title || '加载中...' }}</span>
          <span v-else class="flex items-center gap-2">
             <span class="text-xl">{{ currentCategory?.icon }}</span>
             <span>{{ currentCategory?.name || '全部' }}</span>
             <span class="text-xs text-slate-400 font-normal">频道</span>
          </span>
        </h1>

        <!-- 所属分区标签 -->
        <span v-if="isDetailMode && post?.category" 
              @click="router.push(`/channel/${post.category.id}`)"
              class="px-2 py-0.5 bg-purple-100 text-purple-600 text-xs rounded-md font-bold whitespace-nowrap flex items-center gap-1 cursor-pointer hover:bg-purple-200 transition-colors">
          <span>{{ post.category.icon }}</span> {{ post.category.name }}
        </span>
      </div>
      
      <!-- 右上角用户信息 -->
      <div class="flex items-center gap-3" v-if="auth.isLoggedIn">
        <span class="text-sm font-bold text-slate-600 hidden sm:block">{{ auth.user.username }}</span>
        
        <!-- 🔥 自己的头像：使用 auth.formatUrl 处理 -->
        <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center overflow-hidden border border-white shadow-sm cursor-pointer" @click="router.push('/profile')">
           <img v-if="auth.user.avatar" :src="auth.formatUrl(auth.user.avatar)" class="w-full h-full object-cover">
           <span v-else class="text-xs font-bold text-indigo-500">{{ auth.user.username?.charAt(0).toUpperCase() }}</span>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <div class="flex-1 flex overflow-hidden z-10 relative">
      
      <!-- 2. 左侧分区列表 (仅在大屏显示) -->
      <transition name="slide-left">
        <aside v-if="showLeft" class="w-64 bg-white/60 backdrop-blur-xl border-r border-slate-200 flex flex-col h-full shrink-0 hidden lg:flex">
          <div class="p-4 font-bold text-slate-500 text-xs uppercase tracking-wider"><span>🧭</span> 传送门</div>
          <div class="flex-1 overflow-y-auto p-2 space-y-1 custom-scroll">
            <div v-for="cat in categories" :key="cat.id" 
              @click="router.push(`/channel/${cat.id}`)"
              :class="['px-4 py-3 rounded-xl cursor-pointer transition-colors flex items-center gap-3 font-medium', 
                (!isDetailMode && currentCategory?.id === cat.id) ? 'bg-purple-100 text-purple-700 shadow-sm' : 'text-slate-700 hover:bg-white/80']">
              <span class="text-xl">{{ cat.icon }}</span>
              <span>{{ cat.name }}</span>
            </div>
          </div>
        </aside>
      </transition>

      <!-- 左侧折叠按钮 -->
      <button @click="showLeft = !showLeft" class="absolute top-1/2 z-20 -translate-y-1/2 w-6 h-12 bg-white border border-slate-200 rounded-r-lg hidden lg:flex items-center justify-center text-slate-400 hover:text-purple-600 transition-all shadow-sm" :style="{ left: showLeft ? '256px' : '0' }">
        <span :class="showLeft ? '' : 'rotate-180'">‹</span>
      </button>

      <!-- 3. 中间内容区 -->
      <main id="main-scroll" class="flex-1 overflow-y-auto custom-scroll scroll-smooth relative bg-slate-50/50">
        
        <!-- 🅰️ 模式 A: 帖子详情 -->
        <div v-if="isDetailMode" class="max-w-3xl mx-auto py-10 px-6 pb-32 animate-fade-in">
          <div v-if="post" class="bg-white rounded-3xl shadow-sm border border-slate-200 p-8 mb-8">
            <div class="flex items-center gap-4 mb-6">
              
              <!-- 🔥 楼主头像 (点击弹窗查看资料) -->
              <div @click.stop="openProfile(post.author.id)" class="w-12 h-12 rounded-2xl bg-indigo-100 flex items-center justify-center text-xl shadow-inner overflow-hidden cursor-pointer hover:opacity-80 transition-opacity">
                <!-- 使用 auth.formatUrl 自动拼接 IP -->
                <img v-if="post.author.avatar" :src="auth.formatUrl(post.author.avatar)" class="w-full h-full object-cover">
                <span v-else class="text-indigo-500 font-bold">{{ post.author.username.charAt(0).toUpperCase() }}</span>
              </div>
              
              <div>
                <div class="font-bold text-slate-800 flex items-center gap-2">
                  {{ post.author.username }} 
                  <span class="text-xs bg-yellow-100 text-yellow-600 px-1 rounded ml-1">楼主</span>
                </div>
                <div class="text-xs text-slate-400">{{ formatDate(post.timestamp) }} · {{ post.views }} 次围观</div>
              </div>
            </div>
            
            <!-- 帖子正文 (Markdown 渲染) -->
            <div class="markdown-body text-slate-700 leading-relaxed" v-html="renderedBody"></div>
            
            <!-- 标签 -->
            <div class="mt-6 flex gap-2" v-if="post.tags && post.tags.length">
              <span v-for="tag in post.tags" :key="tag" class="text-xs font-bold text-purple-500 bg-purple-50 px-2 py-1 rounded-md">#{{ tag }}</span>
            </div>
          </div>

          <!-- 评论列表 -->
          <div class="space-y-6 relative" v-if="post">
            <div class="text-sm font-bold text-slate-400 mb-4 flex items-center gap-2"><span>💬 共 {{ comments.length }} 条回复</span><div class="h-px flex-1 bg-slate-200"></div></div>
            
            <div v-for="(comment, idx) in comments" :key="comment.id" :id="'comment-' + comment.id" class="bg-white/80 rounded-2xl p-6 border border-slate-100 hover:shadow-md transition-shadow flex gap-4 group">
              
              <!-- 🔥 评论者头像 (点击弹窗查看资料) -->
              <div @click.stop="openProfile(comment.author.id)" class="shrink-0 w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-sm font-bold text-gray-500 select-none overflow-hidden cursor-pointer hover:ring-2 ring-purple-200 transition-all">
                 <img v-if="comment.author.avatar" :src="auth.formatUrl(comment.author.avatar)" class="w-full h-full object-cover">
                 <span v-else>{{ comment.author.username.charAt(0).toUpperCase() }}</span>
              </div>
              
              <div class="flex-1 min-w-0">
                <div class="flex justify-between items-center mb-2">
                  <span class="font-bold text-slate-700 text-sm cursor-pointer hover:text-purple-600" @click.stop="openProfile(comment.author.id)">{{ comment.author.username }}</span>
                  <span class="text-xs text-slate-400">#{{ idx + 1 }} · {{ formatTimeAgo(comment.timestamp) }}</span>
                </div>
                <div class="text-slate-600 text-sm leading-relaxed break-words" v-html="renderMarkdown(comment.body)"></div>
              </div>
            </div>
            
            <div class="text-center text-slate-400 text-xs py-8">已经到底啦，快来发表神评吧 ~ 🐱</div>
          </div>
        </div>

        <!-- 🅱️ 模式 B: 分区帖子列表 (当不是详情模式时显示) -->
        <div v-else class="max-w-3xl mx-auto py-10 px-6 pb-32 animate-fade-in">
           <div class="mb-6 flex items-center justify-between">
              <h2 class="text-xl font-bold text-slate-700 flex items-center gap-2">
                 <span class="text-2xl">{{ currentCategory?.icon }}</span>
                 {{ currentCategory?.name }}
              </h2>
           </div>

           <!-- 骨架屏 -->
           <div v-if="isListLoading" class="space-y-4">
              <div v-for="i in 4" :key="i" class="bg-white rounded-2xl p-5 h-32 border border-slate-100 animate-pulse flex flex-col justify-between">
                <div class="flex gap-4">
                   <div class="w-10 h-10 bg-slate-200 rounded-full shrink-0"></div>
                   <div class="flex-1 space-y-2">
                      <div class="h-4 bg-slate-200 rounded w-2/5"></div>
                      <div class="h-3 bg-slate-200 rounded w-full"></div>
                   </div>
                </div>
              </div>
           </div>

           <!-- 空状态 -->
           <div v-else-if="categoryPosts.length === 0" class="text-center py-20 text-slate-400 bg-white/40 rounded-3xl border border-white/60">
              <div class="text-4xl mb-2">🍃</div>
              这个分区暂时没有帖子哦
           </div>

           <!-- 帖子列表项 -->
           <div v-else class="space-y-4">
              <article v-for="thread in categoryPosts" :key="thread.id" 
                @click="router.push(`/post/${thread.id}`)"
                class="bg-white rounded-2xl p-5 border border-slate-200 hover:shadow-md hover:border-purple-200 transition-all cursor-pointer group">
                <div class="flex items-start gap-4">
                  <!-- 列表中的头像 (这里不需要弹窗，纯展示) -->
                  <div class="flex-shrink-0 w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-sm font-bold text-indigo-500 overflow-hidden">
                     <img v-if="thread.author.avatar" :src="auth.formatUrl(thread.author.avatar)" class="w-full h-full object-cover">
                     <span v-else>{{ thread.author.username.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-base font-bold text-slate-800 mb-1 group-hover:text-purple-600 transition-colors">{{ thread.title }}</h3>
                    <p class="text-xs text-slate-500 mb-2 line-clamp-2">{{ thread.body.replace(/[#*`]/g, '').slice(0, 80) }}...</p>
                    <div class="flex items-center gap-3 text-xs text-slate-400">
                       <span class="font-bold text-slate-500">{{ thread.author.username }}</span>
                       <span>·</span>
                       <span>{{ formatDate(thread.timestamp) }}</span>
                       <span class="ml-auto flex items-center gap-1"><span class="text-xs">👀</span> {{ thread.views }}</span>
                    </div>
                  </div>
                </div>
              </article>
           </div>
        </div>
      </main>

      <!-- 4. 右侧时光轴 (仅在详情模式) -->
      <aside v-if="isDetailMode" class="w-16 bg-white/60 backdrop-blur-md border-l border-slate-200 hidden md:flex flex-col items-center py-10 relative shrink-0">
        <div class="text-xs font-bold text-slate-400 writing-vertical mb-4 opacity-50">START</div>
        <div class="flex-1 w-0.5 bg-slate-200 relative rounded-full my-2">
          <div v-for="(comment, idx) in comments" :key="comment.id"
            @click="scrollToComment(comment.id)"
            class="absolute w-2.5 h-2.5 bg-purple-300 rounded-full -left-[4px] hover:bg-purple-600 hover:scale-150 transition-all cursor-pointer group z-10"
            :style="{ top: getTimelinePosition(comment.timestamp) + '%' }">
            <div class="absolute right-6 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity pointer-events-none shadow-lg">
              #{{ idx + 1 }} {{ formatTimeSimple(comment.timestamp) }}
            </div>
          </div>
        </div>
        <div class="text-xs font-bold text-purple-400 writing-vertical mt-4 animate-pulse">NOW</div>
      </aside>

    </div>

    <!-- 5. 底部回复栏 (含 GIF 和 图片上传) -->
    <footer v-if="isDetailMode" class="bg-white/80 backdrop-blur-xl border-t border-slate-200 p-4 z-40 transition-all pb-8">
      <div class="max-w-3xl mx-auto relative">
        
        <!-- GIF 面板 -->
        <transition name="pop-up">
          <div v-if="showGifPicker" class="absolute bottom-full left-0 mb-4 w-full sm:w-96 h-80 bg-white rounded-2xl shadow-2xl border border-purple-100 flex flex-col overflow-hidden z-50">
            <!-- 搜索头 -->
            <div class="p-3 border-b border-slate-100 bg-slate-50 flex gap-2">
              <input v-model="gifSearchQuery" @keyup.enter="searchGifs" placeholder="搜索 Giphy 表情..." class="flex-1 bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-purple-400 text-slate-700">
              <button @click="searchGifs" class="text-xs bg-slate-200 hover:bg-purple-100 hover:text-purple-600 px-3 rounded-lg font-bold transition-colors">搜</button>
            </div>
            <!-- GIF 列表 -->
            <div class="flex-1 overflow-y-auto p-2 grid grid-cols-2 gap-2 custom-scroll bg-slate-50/50 relative">
               <div v-if="loadingGifs" class="absolute inset-0 flex items-center justify-center text-purple-400">
                 <span class="animate-spin text-2xl">⏳</span>
               </div>
               <div v-else-if="gifs.length === 0" class="col-span-2 text-center text-slate-400 py-10 text-xs">没有找到表情包喵 ~</div>
               <img v-for="gif in gifs" :key="gif.id" :src="gif.images.fixed_height_small.url" 
                    @click="insertGif(gif)"
                    class="w-full h-24 object-cover rounded-lg cursor-pointer hover:opacity-80 hover:scale-105 transition-all shadow-sm border border-slate-100 bg-slate-200">
            </div>
            <div class="p-1 bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 h-1"></div>
          </div>
        </transition>

        <!-- 输入框主体 -->
        <div class="bg-white rounded-2xl shadow-lg border border-slate-200 focus-within:ring-4 focus-within:ring-purple-100 focus-within:border-purple-400 transition-all relative group overflow-hidden">
          
          <!-- 工具栏 -->
          <div class="flex items-center gap-1 p-2 border-b border-slate-50 bg-slate-50/50">
            <!-- GIF 按钮 -->
            <button @click="toggleGifPicker" :class="{'bg-purple-100 text-purple-600': showGifPicker}" class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors relative" title="插入表情包">
              <span class="text-lg">🦄</span>
            </button>
            
            <!-- 🔥 图片上传按钮 -->
            <label class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors cursor-pointer relative" title="上传图片">
              <span class="text-lg">📷</span>
              <input type="file" class="hidden" accept="image/*" @change="handleImageUpload">
            </label>

            <div class="w-px h-4 bg-slate-300 mx-1"></div>
            <!-- Markdown 工具 -->
            <button @click="insertMarkdown('**', '**')" class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 font-bold text-xs" title="加粗">B</button>
            <button @click="insertMarkdown('*', '*')" class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 italic text-xs font-serif" title="斜体">I</button>
            <button @click="insertMarkdown('`', '`')" class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 text-xs font-mono" title="代码">Code</button>
          </div>

          <!-- 文本域 -->
          <textarea 
            ref="replyTextarea"
            v-model="replyBody" 
            rows="3" 
            placeholder="友善发言，不仅是美德... (支持 Markdown / 拖拽上传图片)" 
            class="w-full bg-transparent border-none focus:ring-0 text-slate-700 placeholder-slate-400 p-4 min-h-[100px] resize-none caret-purple-600 selection:bg-purple-100 selection:text-purple-700 text-sm leading-relaxed"
          ></textarea>

          <!-- 发送按钮 -->
          <div class="absolute bottom-3 right-3 flex items-center gap-2">
             <span v-if="replyBody.length > 0" class="text-xs text-slate-300 font-mono">{{ replyBody.length }} chars</span>
             <button @click="submitReply" :disabled="sending || !replyBody.trim()" 
               class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-bold rounded-xl shadow-lg shadow-purple-200 transition-all disabled:opacity-50 disabled:shadow-none hover:-translate-y-0.5 active:translate-y-0 flex items-center gap-2">
               <span v-if="sending" class="animate-spin">⏳</span>
               <span v-else>发送 <span class="ml-1 opacity-70">↵</span></span>
             </button>
          </div>
        </div>
        
        <!-- 遮罩 (关闭 GIF) -->
        <div v-if="showGifPicker" @click="showGifPicker = false" class="fixed inset-0 z-40 bg-transparent"></div>
      </div>
    </footer>

    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, watch, inject } from 'vue' // 🔥 引入 inject 用于弹窗
import { useRoute, useRouter } from 'vue-router'
import api from '@/plugins/axios'
import { useAuthStore } from '@/plugins/auth'
import Showmessage from '@/components/showmessage.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute(); const router = useRouter(); const message = ref()
// 🔥 1. 引入 auth store
const auth = useAuthStore()
// 🔥 2. 注入全局的打开资料卡方法
const openProfile = inject('openProfile')

// 核心数据
const post = ref(null); 
const comments = ref([]); 
const categories = ref([]);
const categoryPosts = ref([]); 
const currentCategory = ref(null)

// UI 状态
const showLeft = ref(true); 
const loading = ref(false); 
const isListLoading = ref(false); 
const progress = ref(0); 
let progressInterval = null

// 回复相关
const replyBody = ref(''); 
const sending = ref(false)
const replyTextarea = ref(null) 
const showGifPicker = ref(false)
const gifs = ref([])
const gifSearchQuery = ref('reaction')
const loadingGifs = ref(false)

const isDetailMode = computed(() => route.name === 'PostDetail')

const renderedBody = computed(() => {
  if (!post.value) return ''
  return DOMPurify.sanitize(marked.parse(post.value.body))
})

const renderMarkdown = (text) => DOMPurify.sanitize(marked.parse(text))

// --- 进度条逻辑 ---
const startProgress = () => {
  loading.value = true
  progress.value = 0
  clearInterval(progressInterval)
  progressInterval = setInterval(() => {
    if (progress.value < 90) progress.value += Math.max(1, (90 - progress.value) / 10)
  }, 200)
}
const completeProgress = () => {
  clearInterval(progressInterval)
  progress.value = 100
  setTimeout(() => loading.value = false, 300)
}

// --- 数据加载 ---
const loadCategories = async () => {
  if (categories.value.length > 0) return 
  try {
    const res = await api.get('/api/posts/categories')
    if(res.data.code === 200) categories.value = res.data.data
  } catch (e) { console.error(e) }
}

const loadPost = async (id) => {
  try {
    const res = await api.get(`/api/posts/${id}`)
    if(res.data.code === 200) { 
      post.value = res.data.data; 
      comments.value = res.data.data.comments || [] 
    } else { 
      message.value.showMessage('帖子不存在'); 
      setTimeout(() => router.push('/'), 2000) 
    }
  } catch (e) { console.error(e) }
}

const loadCategoryPosts = async (catId) => {
  categoryPosts.value = [] 
  isListLoading.value = true
  try {
    const res = await api.get('/api/posts/', { params: { category_id: catId } })
    if(res.data.code === 200) {
      categoryPosts.value = res.data.data.map(p => ({
        ...p,
        author: p.author || { username: '未知', avatar: '' },
        body: p.body || ''
      }))
    }
  } catch(e) { console.error(e) } 
  finally { isListLoading.value = false }
}

const loadData = async () => {
  startProgress()
  const mainScroll = document.getElementById('main-scroll')
  if(mainScroll) mainScroll.scrollTop = 0
  
  await loadCategories()
  
  if (isDetailMode.value) {
    post.value = null 
    await loadPost(route.params.id)
  } else {
    const catId = Number(route.params.id)
    currentCategory.value = categories.value.find(c => c.id === catId)
    await loadCategoryPosts(catId)
  }
  completeProgress()
}

watch(() => route.fullPath, loadData, { immediate: true })

// --- 🔥 图片上传逻辑 ---
const handleImageUpload = async (e) => {
  const file = e.target.files[0]
  if(!file) return
  
  const formData = new FormData()
  formData.append('file', file)
  
  // 插入占位符
  insertTextAtCursor('![上传中...]()')
  
  try {
    const res = await api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if(res.data.code === 200) {
      // 🔥 关键：使用 auth.formatUrl 处理后端返回的相对路径
      const fullUrl = auth.formatUrl(res.data.url)
      // 替换占位符为真实 Markdown 图片
      replyBody.value = replyBody.value.replace('![上传中...]()', `![image](${fullUrl})`)
    } else {
      replyBody.value = replyBody.value.replace('![上传中...]()', '')
      message.value.showMessage(res.data.message)
    }
  } catch(e) {
    replyBody.value = replyBody.value.replace('![上传中...]()', '')
    message.value.showMessage('图片上传失败')
  }
}

// --- GIF 逻辑 ---
const fallbackGifs = [
  { id: 'f1', images: { fixed_height_small: { url: 'https://media.giphy.com/media/JIX9t2j0ZTN9S/200w.gif' }, fixed_height: { url: 'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif' } } },
  { id: 'f2', images: { fixed_height_small: { url: 'https://media.giphy.com/media/8Iv5lqKwKsZ2g/200w.gif' }, fixed_height: { url: 'https://media.giphy.com/media/8Iv5lqKwKsZ2g/giphy.gif' } } }
]

const fetchGifs = async (query = 'reaction') => {
  if (loadingGifs.value) return
  loadingGifs.value = true
  try {
    const apiKey = 'MQpoBG43QMhuChyMCWnms3COEumxQMdF' 
    const url = `https://api.giphy.com/v1/gifs/search?api_key=${apiKey}&q=${query}&limit=20&rating=g`
    const controller = new AbortController()
    setTimeout(() => controller.abort(), 3000)
    const res = await fetch(url, { signal: controller.signal })
    const data = await res.json()
    if (data.data && data.data.length > 0) gifs.value = data.data
    else gifs.value = fallbackGifs
  } catch (e) {
    gifs.value = fallbackGifs
  } finally {
    loadingGifs.value = false
  }
}

const toggleGifPicker = () => {
  showGifPicker.value = !showGifPicker.value
  if (showGifPicker.value && gifs.value.length === 0) fetchGifs()
}

const searchGifs = () => {
  if (!gifSearchQuery.value.trim()) return
  fetchGifs(gifSearchQuery.value)
}

const insertGif = (gif) => {
  const markdownImage = `![gif](${gif.images.fixed_height.url})`
  insertTextAtCursor(markdownImage)
  showGifPicker.value = false 
}

// --- Markdown 工具 ---
const insertMarkdown = (prefix, suffix) => {
  const textarea = replyTextarea.value
  if (!textarea) return
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = replyBody.value
  replyBody.value = text.substring(0, start) + prefix + text.substring(start, end) + suffix + text.substring(end)
  setTimeout(() => { textarea.focus(); textarea.setSelectionRange(start + prefix.length, end + prefix.length) }, 0)
}

const insertTextAtCursor = (textToInsert) => {
  const textarea = replyTextarea.value
  if (!textarea) { replyBody.value += textToInsert; return }
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = replyBody.value
  replyBody.value = text.substring(0, start) + "\n" + textToInsert + "\n" + text.substring(end)
}

// --- 提交评论 ---
const submitReply = () => {
  if (!auth.isLoggedIn) return router.push('/login')
  if (!replyBody.value.trim()) return message.value.showMessage('内容不能为空')
  sending.value = true
  api.post(`/api/posts/${post.value.id}/comments`, { body: replyBody.value }).then(res => {
      if(res.data.code === 200) { 
        message.value.showMessage('回复成功'); 
        replyBody.value = ''; 
        loadPost(post.value.id).then(() => {
           setTimeout(() => {
              const main = document.getElementById('main-scroll')
              if(main) main.scrollTo({ top: main.scrollHeight, behavior: 'smooth' })
           }, 100)
        })
      } else { message.value.showMessage(res.data.message) }
  }).finally(() => sending.value = false)
}

// --- 辅助功能 ---
const getTimelinePosition = (timestamp) => {
  if (comments.value.length < 2) return 50 
  const start = new Date(post.value.timestamp).getTime(); 
  const end = new Date(comments.value[comments.value.length - 1].timestamp).getTime(); 
  const total = end - start; if (total === 0) return 100; 
  return ((new Date(timestamp).getTime() - start) / total) * 80 + 10
}

const scrollToComment = (id) => { 
  const el = document.getElementById('comment-' + id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' }) 
}

const formatDate = (str) => new Date(str).toLocaleDateString()
const formatTimeSimple = (str) => {
  const d = new Date(str)
  return `${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}
const formatTimeAgo = (str) => new Date(str).toLocaleString()

onUnmounted(() => clearInterval(progressInterval))
</script>

<style scoped>
.writing-vertical { writing-mode: vertical-rl; text-orientation: mixed; letter-spacing: 4px; }
.markdown-body :deep(h1) { font-size: 1.8em; font-weight: 800; margin: 0.5em 0; color: #1e293b; }
.markdown-body :deep(h2) { font-size: 1.5em; font-weight: 700; margin: 0.5em 0; color: #334155; }
.markdown-body :deep(p) { margin-bottom: 1em; line-height: 1.75; color: #475569; }
.markdown-body :deep(img) { max-width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1em 0; }
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes blob { 0% { transform: translate(0px, 0px) scale(1); } 33% { transform: translate(30px, -50px) scale(1.1); } 66% { transform: translate(-20px, 20px) scale(0.9); } 100% { transform: translate(0px, 0px) scale(1); } }
.animate-blob { animation: blob 7s infinite; }
/* Pop-up 动画 */
.pop-up-enter-active, .pop-up-leave-active { transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.pop-up-enter-from, .pop-up-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }
</style>