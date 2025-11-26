<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 py-8 px-4 relative overflow-hidden font-sans">
    
    <!-- 背景装饰 -->
    <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>

    <div class="max-w-6xl mx-auto relative z-10">
      <!-- 顶部导航 -->
      <div class="flex justify-between items-center mb-6">
        <router-link to="/" class="flex items-center text-slate-500 hover:text-purple-600 font-bold transition-colors group">
          <span class="mr-2 text-xl group-hover:-translate-x-1 transition-transform">🐾</span> 
          放弃发帖
        </router-link>
        <h1 class="text-2xl font-extrabold text-slate-800">发布新罐头 🥫</h1>
      </div>

      <!-- 核心区域：左右分栏 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[600px]">
        
        <!-- 左侧：编辑区 (占2份宽度) -->
        <div class="lg:col-span-2 flex flex-col gap-4">
          
          <!-- 1. 标题输入 -->
          <input v-model="form.title" type="text" placeholder="请输入吸引猫咪的标题..." 
            class="w-full px-6 py-4 bg-white/60 backdrop-blur-xl border-2 border-white/50 rounded-2xl text-xl font-bold text-slate-800 placeholder-slate-400 focus:bg-white focus:border-purple-300 focus:outline-none transition-all shadow-lg">

          <!-- 2. 工具栏 + 编辑器 -->
          <div class="flex-1 bg-white/40 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 p-1 relative flex flex-col">
            
            <!-- 魔法工具栏 -->
            <div class="px-4 py-2 border-b border-white/50 flex items-center gap-2 flex-wrap">
              <!-- 基础格式 -->
              <button @click="insertFormat('**', '**')" :class="btnClass" title="加粗"><b>B</b></button>
              <button @click="insertFormat('*', '*')" :class="btnClass + ' italic'" title="斜体"><i>I</i></button>
              <button @click="insertFormat('> ', '')" :class="btnClass" title="引用">❝❞</button>
              <button @click="insertFormat('`', '`')" :class="btnClass + ' font-mono'" title="代码">`</button>
              
              <div class="w-px h-4 bg-slate-300 mx-1"></div>
              
              <!-- Emoji 按钮 -->
              <div class="relative">
                <button @click="showEmoji = !showEmoji" :class="btnClass + ' text-lg'" title="表情">😀</button>
                <div v-if="showEmoji" class="absolute top-10 left-0 z-50 shadow-2xl rounded-xl overflow-hidden">
                  <div class="fixed inset-0 z-[-1]" @click="showEmoji = false"></div>
                  <EmojiPicker :native="true" @select="onSelectEmoji" />
                </div>
              </div>

              <!-- GIF 按钮 -->
              <div class="relative">
                <button @click="showGif = !showGif" :class="btnClass + ' text-lg'" title="哈基米GIF">🐱</button>
                <div v-if="showGif" class="absolute top-10 left-0 z-50 w-64 bg-white/90 backdrop-blur-xl shadow-2xl rounded-xl p-3 border border-white/50">
                  <div class="fixed inset-0 z-[-1]" @click="showGif = false"></div>
                  <div class="grid grid-cols-3 gap-2">
                    <img v-for="(gif, i) in catGifs" :key="i" :src="gif" 
                      @click="insertImage(gif)"
                      class="w-full h-16 object-cover rounded-lg cursor-pointer hover:scale-105 transition-transform border border-slate-200">
                  </div>
                </div>
              </div>

              <div class="w-px h-4 bg-slate-300 mx-1"></div>
              <span class="text-xs text-slate-400 font-bold ml-auto">Markdown 模式</span>
            </div>

            <!-- 文本域 -->
            <textarea 
              id="editor-textarea"
              v-model="form.body" 
              placeholder="在这里写下你的魔法吟唱..." 
              class="w-full flex-1 p-5 bg-transparent border-none rounded-b-2xl text-base text-slate-700 placeholder-slate-400 focus:ring-0 resize-none outline-none font-mono leading-relaxed h-96"></textarea>
          </div>
        </div>

        <!-- 右侧：设置与预览 (占1份宽度) -->
        <div class="flex flex-col gap-6">
          
          <!-- 3. 选项卡片 -->
          <div class="bg-white/60 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 p-6 space-y-6">
            
            <!-- 分区选择 (从后端加载) -->
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-2">选择分区 <span class="text-red-400">*</span></label>
              <div v-if="categories.length === 0" class="text-xs text-red-400">
                (请先去后台创建分区)
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div v-for="cat in categories" :key="cat.id" 
                  @click="form.category_id = cat.id"
                  :class="[
                    'cursor-pointer px-3 py-2 rounded-xl border-2 flex items-center gap-2 transition-all',
                    form.category_id === cat.id 
                      ? 'border-purple-400 bg-purple-50 text-purple-700' 
                      : 'border-transparent bg-white/50 hover:bg-white text-slate-600'
                  ]">
                  <span>{{ cat.icon }}</span>
                  <span class="font-bold text-sm">{{ cat.name }}</span>
                </div>
              </div>
            </div>

            <!-- 标签输入 -->
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-2">添加标签 (回车确认)</label>
              <div class="flex flex-wrap gap-2 mb-2">
                <span v-for="(tag, i) in form.tags" :key="i" 
                  class="bg-pink-100 text-pink-600 px-2 py-1 rounded-lg text-xs font-bold flex items-center gap-1 animate-pop">
                  #{{ tag }}
                  <button @click="removeTag(i)" class="hover:text-pink-800">×</button>
                </span>
              </div>
              <input 
                v-model="tagInput" 
                @keydown.enter.prevent="addTag"
                type="text" placeholder="例如: Vue3" 
                class="w-full px-4 py-2 bg-white/50 border border-white rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-pink-300 focus:outline-none transition-all">
            </div>

          </div>

          <!-- 4. 实时预览 (小窗口) -->
          <div class="flex-1 bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl border border-white/60 p-4 overflow-hidden flex flex-col min-h-[200px]">
             <div class="text-xs font-bold text-slate-400 mb-2 uppercase">实时预览</div>
             <div class="flex-1 overflow-y-auto markdown-body text-sm custom-scroll" v-html="compiledMarkdown"></div>
          </div>

          <!-- 发布按钮 -->
          <button @click="handleSubmit" :disabled="loading"
            class="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-2xl shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:-translate-y-1 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg">
            <span v-if="loading" class="animate-spin">⏳</span>
            <span v-else>🚀</span>
            {{ loading ? '正在上架...' : '发布帖子' }}
          </button>

        </div>

      </div>
    </div>
    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import api from '@/plugins/axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/plugins/auth' // 1. 引入 Auth Store
import Showmessage from '@/components/showmessage.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const router = useRouter(); const message = ref(); const loading = ref(false); const showEmoji = ref(false); const showGif = ref(false)
const auth = useAuthStore() // 2. 使用 Store

const btnClass = "px-2 py-1 rounded hover:bg-purple-100 text-slate-600 font-bold transition-colors text-sm"
const catGifs = ['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDQyZnJ6Y2o5YnJ6Y2o5YnJ6Y2o5YnJ6Y2o5YnJ6Y2o5eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GeimqsH0TLDt4tScGw/giphy.gif', 'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif', 'https://media.giphy.com/media/MDJ9IbxxvDUQM/giphy.gif', 'https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif', 'https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy.gif', 'https://media.giphy.com/media/13CoXDiaCcCoyk/giphy.gif']
const categories = ref([]); const tagInput = ref('')
const form = reactive({ title: '', body: '', category_id: null, tags: [] })

onMounted(() => {
  api.get('/api/posts/categories').then(res => {
    if(res.data.code === 200) {
      let allCats = res.data.data
      
      // 🔥 3. 核心逻辑：如果不是管理员，过滤掉“公告栏”
      if (!auth.isAdmin) {
        allCats = allCats.filter(c => c.name !== '公告栏')
      }
      
      categories.value = allCats
      if(categories.value.length > 0) form.category_id = categories.value[0].id
    }
  })
})

const insertFormat = (prefix, suffix) => {
  const textarea = document.getElementById('editor-textarea'); const start = textarea.selectionStart; const end = textarea.selectionEnd
  form.body = form.body.substring(0, start) + prefix + form.body.substring(start, end) + suffix + form.body.substring(end)
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + prefix.length, end + prefix.length)
  }, 0)
}
const onSelectEmoji = (emoji) => { insertFormat(emoji.i, ''); showEmoji.value = false }
const insertImage = (url) => { insertFormat(`\n![哈基米](${url})\n`, ''); showGif.value = false }
const addTag = () => { const val = tagInput.value.trim(); if (val && !form.tags.includes(val) && form.tags.length < 5) form.tags.push(val); tagInput.value = '' }
const removeTag = (i) => form.tags.splice(i, 1)

const compiledMarkdown = computed(() => {
  if (!form.body) return '<div class="text-slate-400 italic">等待输入...</div>'
  return DOMPurify.sanitize(marked.parse(form.body))
})

const handleSubmit = () => {
  if (!form.title.trim() || !form.body.trim()) return message.value.showMessage('标题和内容不能为空！')
  if (!form.category_id) return message.value.showMessage('请选择一个分区！')
  loading.value = true
  api.post('/api/posts/', form).then(res => {
      if (res.data.code === 200) { message.value.showMessage('🎉 发布成功！'); setTimeout(() => router.push('/'), 1000) } 
      else { message.value.showMessage(res.data.message); loading.value = false }
    }).catch(err => { console.error(err); message.value.showMessage('网络错误'); loading.value = false })
}
</script>

<style scoped>
/* 标签弹出动画 */
@keyframes pop { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.animate-pop { animation: pop 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }

/* Markdown 样式 */
.markdown-body :deep(p) { margin-bottom: 0.5em; color: #475569; line-height: 1.6; }
.markdown-body :deep(img) { max-width: 100%; border-radius: 8px; margin: 0.5em 0; }
.markdown-body :deep(strong) { color: #7e22ce; }

/* 滚动条美化 */
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.2); border-radius: 10px; }
.custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.4); }

/* 动画 */
@keyframes blob { 0% { transform: translate(0px, 0px) scale(1); } 33% { transform: translate(30px, -50px) scale(1.1); } 66% { transform: translate(-20px, 20px) scale(0.9); } 100% { transform: translate(0px, 0px) scale(1); } }
.animate-blob { animation: blob 7s infinite; }
</style>