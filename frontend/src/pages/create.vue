<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 py-8 px-4 relative overflow-hidden font-sans">

    <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>

    <div class="max-w-6xl mx-auto relative z-10">
      <div class="flex justify-between items-center mb-6">
        <router-link to="/" class="flex items-center text-slate-500 hover:text-purple-600 font-bold transition-colors group">
          <span class="mr-2 text-xl group-hover:-translate-x-1 transition-transform">🐾</span>
          返回首页
        </router-link>
        <h1 class="text-2xl font-extrabold text-slate-800">{{ isEditMode ? '编辑帖子' : '发布新帖' }}</h1>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[600px]">

        <div class="lg:col-span-2 flex flex-col gap-4">

          <input v-model="form.title" type="text" placeholder="请输入吸引猫咪的标题..."
            class="w-full px-6 py-4 bg-white/60 backdrop-blur-xl border-2 border-white/50 rounded-2xl text-xl font-bold text-slate-800 placeholder-slate-400 focus:bg-white focus:border-purple-300 focus:outline-none transition-all shadow-lg">

          <div class="flex-1 bg-white/40 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 p-1 relative flex flex-col">

            <div class="px-4 py-2 border-b border-white/50 flex items-center gap-2 flex-wrap">
              <button @click="insertFormat('**', '**')" :class="btnClass" title="加粗"><b>B</b></button>
              <button @click="insertFormat('*', '*')" :class="btnClass + ' italic'" title="斜体"><i>I</i></button>
              <button @click="insertFormat('> ', '')" :class="btnClass" title="引用">❝❞</button>
              <button @click="insertFormat('`', '`')" :class="btnClass + ' font-mono'" title="代码">`</button>

              <div class="w-px h-4 bg-slate-300 mx-1"></div>

              <div class="relative">
                <button type="button" @click="toggleEmojiPicker" :class="btnClass + ' text-lg'" title="表情">😀</button>
                <div v-if="showEmoji" class="fixed inset-0 z-40" @click="showEmoji = false"></div>
                <transition name="picker-pop">
                <div v-if="showEmoji" @mousedown.stop @click.stop class="absolute top-10 left-0 z-50 shadow-2xl rounded-xl overflow-hidden picker-popover">
                  <EmojiPicker :native="true" @select="onSelectEmoji" />
                </div>
                </transition>
              </div>

              <div class="relative">
                <button type="button" @click="toggleGifPicker" :class="btnClass + ' text-lg'" title="GIF">🐱</button>
                <div v-if="showGif" class="fixed inset-0 z-40" @click="showGif = false"></div>
                <transition name="picker-pop">
                <div v-if="showGif" @mousedown.stop @click.stop class="absolute top-10 left-0 z-50 w-64 bg-white/90 backdrop-blur-xl shadow-2xl rounded-xl p-3 border border-white/50 picker-popover">
                  <div class="grid grid-cols-3 gap-2">
                    <img v-for="(gif, i) in catGifs" :key="i" :src="gif"
                      @mousedown.prevent.stop="insertImage(gif)"
                      class="w-full h-16 object-cover rounded-lg cursor-pointer hover:scale-[1.03] active:scale-[0.98] transition-transform duration-200 border border-slate-200">
                  </div>
                </div>
                </transition>
              </div>

              <div class="w-px h-4 bg-slate-300 mx-1"></div>
              <span class="text-xs text-slate-400 font-bold ml-auto">Markdown 模式</span>
            </div>

            <textarea
              id="editor-textarea"
              ref="editorTextarea"
              v-model="form.body"
              placeholder="在这里写下你的魔法吟唱..."
              class="w-full flex-1 p-5 bg-transparent border-none rounded-b-2xl text-base text-slate-700 placeholder-slate-400 focus:ring-0 resize-none outline-none font-mono leading-relaxed h-96"></textarea>
          </div>
        </div>

        <div class="flex flex-col gap-6">

          <div class="bg-white/60 backdrop-blur-xl shadow-xl rounded-3xl border border-white/60 p-6 space-y-6">

            <div>
              <label class="block text-sm font-bold text-slate-500 mb-2">选择分区 <span class="text-red-400">*</span></label>
              <div v-if="categoriesLoading" class="text-xs text-slate-400 animate-pulse">
                正在加载分区...
              </div>
              <div v-else-if="categories.length === 0" class="text-xs text-red-400">
                (请先去后台创建分区)
              </div>
              <div v-else class="grid grid-cols-2 gap-2">
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

          <div class="flex-1 bg-white/40 backdrop-blur-xl shadow-lg rounded-3xl border border-white/60 p-4 overflow-hidden flex flex-col min-h-[200px]">
             <div class="text-xs font-bold text-slate-400 mb-2 uppercase">实时预览</div>
             <div class="flex-1 overflow-y-auto markdown-body text-sm custom-scroll" v-html="compiledMarkdown"></div>
          </div>

          <button @click="handleSubmit" :disabled="loading"
            class="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-2xl shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 hover:-translate-y-1 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg">
            <span v-if="loading" class="animate-spin">⏳</span>
            <span v-else>🚀</span>
            {{ loading ? '正在上架...' : (isEditMode ? '更新帖子' : '发布帖子') }}
          </button>

        </div>

      </div>
    </div>
    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted, nextTick } from 'vue'
import { postsApi } from '@/api'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/plugins/auth'
import Showmessage from '@/components/showmessage.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const router = useRouter(); const route = useRoute(); const message = ref(); const loading = ref(false); const showEmoji = ref(false); const showGif = ref(false); const editorTextarea = ref(null)
const auth = useAuthStore()

const btnClass = "px-2 py-1 rounded hover:bg-purple-100 text-slate-600 font-bold transition-colors text-sm"
const catGifs = [
  'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif',
  'https://media.giphy.com/media/8Iv5lqKwKsZ2g/giphy.gif',
  'https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif',
  'https://media.giphy.com/media/13CoXDiaCcCoyk/giphy.gif',
  'https://media.giphy.com/media/GeimqsH0TLDt4tScGw/giphy.gif',
  'https://media.giphy.com/media/MDJ9IbxxvDUQM/giphy.gif',
  'https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy.gif',
  'https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif',
  'https://media.giphy.com/media/3orieLHrJOlQHcMvIs/giphy.gif',
  'https://media.giphy.com/media/11sBLVxNs7v6WA/giphy.gif',
  'https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif',
  'https://media.giphy.com/media/dkGhBWE3SyzXW/giphy.gif',
]
const categories = ref([]); const tagInput = ref(''); const categoriesLoading = ref(true)
const form = reactive({ title: '', body: '', category_id: null, tags: [] })
const isEditMode = computed(() => !!route.query.edit)
const editPostId = computed(() => route.query.edit ? parseInt(route.query.edit) : null)

onMounted(() => {
  postsApi.categories().then(res => {
    if(res.data.code === 200) {
      let allCats = res.data.data
      if (!auth.isAdmin) {
        allCats = allCats.filter(c => c.name !== '公告栏')
      }
      categories.value = allCats
      if(categories.value.length > 0 && !isEditMode.value) form.category_id = categories.value[0].id
    }
  }).catch(e => console.error('获取分区失败:', e))
  .finally(() => categoriesLoading.value = false)

  if (isEditMode.value && editPostId.value) {
    loading.value = true
    postsApi.detail(editPostId.value).then(res => {
      if (res.data.code === 200) {
        const p = res.data.data
        if (auth.user.id !== p.author.id && !auth.isAdmin) {
          message.value.showMessage('无权编辑此帖子')
          setTimeout(() => router.push('/'), 1000)
          return
        }
        form.title = p.title
        form.body = p.body
        form.category_id = p.category ? p.category.id : null
        form.tags = p.tags || []
      }
    }).finally(() => loading.value = false)
  }
})

const toggleEmojiPicker = () => {
  showEmoji.value = !showEmoji.value
  if (showEmoji.value) showGif.value = false
}

const toggleGifPicker = () => {
  showGif.value = !showGif.value
  if (showGif.value) showEmoji.value = false
}

const insertFormat = async (prefix, suffix = '') => {
  const textarea = editorTextarea.value
  const text = form.body
  const start = textarea ? textarea.selectionStart : text.length
  const end = textarea ? textarea.selectionEnd : text.length
  form.body = text.substring(0, start) + prefix + text.substring(start, end) + suffix + text.substring(end)
  await nextTick()
  if (textarea) {
    textarea.focus()
    textarea.setSelectionRange(start + prefix.length, end + prefix.length)
  }
}
const onSelectEmoji = (emoji) => { insertFormat(emoji.i, ''); showEmoji.value = false }
const insertImage = (url) => { insertFormat(`\n![GIF](${url})\n`, ''); showGif.value = false }
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

  const request = isEditMode.value
    ? postsApi.update(editPostId.value, form)
    : postsApi.create(form)

  request.then(res => {
      if (res.data.code === 200) {
        message.value.showMessage(isEditMode.value ? '🎉 更新成功！' : '🎉 发布成功！');
        setTimeout(() => router.push('/post/' + (isEditMode.value ? editPostId.value : res.data.data.id)), 1000)
      }
      else { message.value.showMessage(res.data.message); loading.value = false }
    }).catch(err => { console.error(err); message.value.showMessage(err._message || '网络错误'); loading.value = false })
}
</script>

<style scoped>
.markdown-body :deep(p) { margin-bottom: 0.5em; color: #475569; line-height: 1.6; }
.markdown-body :deep(img) { max-width: 100%; border-radius: 8px; margin: 0.5em 0; }
.markdown-body :deep(strong) { color: #7e22ce; }
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.2); border-radius: 10px; }
.custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.4); }
.picker-popover { transform-origin: left top; will-change: opacity, transform; }
.picker-pop-enter-active { transition: opacity 180ms var(--ease-smooth), transform 220ms var(--ease-smooth); }
.picker-pop-leave-active { transition: opacity 130ms var(--ease-smooth), transform 150ms var(--ease-smooth); }
.picker-pop-enter-from, .picker-pop-leave-to { opacity: 0; transform: translateY(-6px) scale(0.98); }
</style>
