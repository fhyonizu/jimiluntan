<template>
  <div class="h-screen w-screen bg-slate-50 flex flex-col overflow-hidden font-sans relative">

    <div v-if="loading" class="fixed top-0 left-0 h-1 bg-purple-500 z-[100] transition-all duration-300 ease-out shadow-[0_0_10px_rgba(168,85,247,0.5)]" :style="{ width: progress + '%' }"></div>

    <div class="absolute inset-0 pointer-events-none z-0 opacity-50">
      <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
      <div class="absolute bottom-[-20%] right-[-10%] w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    </div>

    <!-- 顶部导航 -->
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

        <span v-if="isDetailMode && post?.category"
              @click="router.push(`/channel/${post.category.id}`)"
              class="px-2 py-0.5 bg-purple-100 text-purple-600 text-xs rounded-md font-bold whitespace-nowrap flex items-center gap-1 cursor-pointer hover:bg-purple-200 transition-colors">
          <span>{{ post.category.icon }}</span> {{ post.category.name }}
        </span>
      </div>

      <div class="flex items-center gap-3" v-if="auth.isLoggedIn">
        <span class="text-sm font-bold text-slate-600 hidden sm:block">{{ auth.user.username }}</span>
        <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center overflow-hidden border border-white shadow-sm cursor-pointer" @click="router.push('/profile')">
           <img v-if="auth.user.avatar" :src="formatUrl(auth.user.avatar)" class="w-full h-full object-cover">
           <span v-else class="text-xs font-bold text-indigo-500">{{ auth.user.username?.charAt(0).toUpperCase() }}</span>
        </div>
      </div>
    </header>

    <!-- 主体 -->
    <div class="flex-1 flex overflow-hidden z-10 relative">

      <!-- 左侧分区 -->
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

      <button @click="showLeft = !showLeft" class="absolute top-1/2 z-20 -translate-y-1/2 w-6 h-12 bg-white border border-slate-200 rounded-r-lg hidden lg:flex items-center justify-center text-slate-400 hover:text-purple-600 transition-all shadow-sm" :style="{ left: showLeft ? '256px' : '0' }">
        <span :class="showLeft ? '' : 'rotate-180'">‹</span>
      </button>

      <!-- 中间内容 -->
      <main id="main-scroll" class="flex-1 overflow-y-auto custom-scroll scroll-smooth relative bg-slate-50/50">

        <!-- 帖子详情 -->
        <div v-if="isDetailMode" class="max-w-3xl mx-auto py-10 px-6 pb-32 animate-fade-in">
          <div v-if="post" class="bg-white rounded-3xl shadow-sm border border-slate-200 p-8 mb-8">
            <div class="flex items-center gap-4 mb-6">

              <div @click.stop="openProfile(post.author.id)" class="w-12 h-12 rounded-2xl bg-indigo-100 flex items-center justify-center text-xl shadow-inner overflow-hidden cursor-pointer hover:opacity-80 transition-opacity">
                <img v-if="post.author.avatar" :src="formatUrl(post.author.avatar)" class="w-full h-full object-cover">
                <span v-else class="text-indigo-500 font-bold">{{ post.author.username.charAt(0).toUpperCase() }}</span>
              </div>

              <div>
                <div class="font-bold text-slate-800 flex items-center gap-2">
                  {{ post.author.username }}
                  <span class="text-xs bg-yellow-100 text-yellow-600 px-1 rounded ml-1">楼主</span>
                </div>
                <div class="text-xs text-slate-400">{{ formatTimeAgo(post.timestamp) }} · {{ post.views }} 次围观 · ❤️ {{ post.likes || 0 }}</div>
              </div>

              <div class="ml-auto flex items-center gap-2" v-if="auth.isLoggedIn">
                <button @click.stop="toggleLike"
                  :class="['px-3 py-1.5 rounded-xl text-sm font-bold transition-all flex items-center gap-1', liked ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-500 hover:bg-red-50 hover:text-red-500']">
                  <span>{{ liked ? '❤️' : '🤍' }}</span> {{ likeCount }}
                </button>
                <button v-if="canEditPost" @click.stop="goEditPost"
                  class="px-3 py-1.5 bg-amber-100 text-amber-700 rounded-xl text-sm font-bold hover:bg-amber-200 transition-colors">
                  ✏️ 编辑
                </button>
                <button v-if="canEditPost" @click.stop="deletePostConfirm"
                  class="px-3 py-1.5 bg-red-100 text-red-600 rounded-xl text-sm font-bold hover:bg-red-200 transition-colors">
                  🗑️ 删除
                </button>
              </div>
            </div>

            <div class="markdown-body text-slate-700 leading-relaxed" v-html="renderedBody"></div>

            <div class="mt-6 flex gap-2" v-if="post.tags && post.tags.length">
              <span v-for="tag in post.tags" :key="tag" class="text-xs font-bold text-purple-500 bg-purple-50 px-2 py-1 rounded-md">#{{ tag }}</span>
            </div>
          </div>

          <!-- 评论列表 -->
          <div class="space-y-6 relative" v-if="post">
            <div class="text-sm font-bold text-slate-400 mb-4 flex items-center gap-2"><span>💬 共 {{ comments.length }} 条回复</span><div class="h-px flex-1 bg-slate-200"></div></div>

            <div v-for="(comment, idx) in comments" :key="comment.id" :id="'comment-' + comment.id" class="bg-white/80 rounded-2xl p-6 border border-slate-100 hover:shadow-md transition-shadow flex gap-4 group">

              <div @click.stop="openProfile(comment.author.id)" class="shrink-0 w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-sm font-bold text-gray-500 select-none overflow-hidden cursor-pointer hover:ring-2 ring-purple-200 transition-all">
                 <img v-if="comment.author.avatar" :src="formatUrl(comment.author.avatar)" class="w-full h-full object-cover">
                 <span v-else>{{ comment.author.username.charAt(0).toUpperCase() }}</span>
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex justify-between items-center mb-2">
                  <span class="font-bold text-slate-700 text-sm cursor-pointer hover:text-purple-600" @click.stop="openProfile(comment.author.id)">{{ comment.author.username }}</span>
                  <div class="flex items-center gap-2">
                    <button v-if="canEditComment(comment)" @click.stop="startEditComment(comment)" class="text-xs text-slate-400 hover:text-amber-500 opacity-0 group-hover:opacity-100 transition-opacity">✏️</button>
                    <button v-if="canEditComment(comment)" @click.stop="deleteCommentConfirm(comment)" class="text-xs text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">🗑️</button>
                    <span class="text-xs text-slate-400">#{{ idx + 1 }} · {{ formatTimeAgo(comment.timestamp) }}</span>
                  </div>
                </div>
                <div v-if="editingCommentId === comment.id" class="flex gap-2">
                  <textarea v-model="editCommentBody" class="flex-1 bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm focus:outline-none focus:border-purple-400" rows="2"></textarea>
                  <div class="flex flex-col gap-1">
                    <button @click="saveEditComment(comment)" class="text-xs bg-purple-500 text-white px-2 py-1 rounded">保存</button>
                    <button @click="editingCommentId = null" class="text-xs bg-slate-300 text-white px-2 py-1 rounded">取消</button>
                  </div>
                </div>
                <div v-else class="markdown-body comment-body text-slate-600 leading-relaxed break-words" v-html="comment.content_html || ''"></div>
              </div>
            </div>

            <div class="text-center text-slate-400 text-xs py-8">— 已显示全部评论 —</div>
          </div>
        </div>

        <!-- 分区帖子列表 -->
        <div v-else class="max-w-3xl mx-auto py-10 px-6 pb-32 animate-fade-in">
           <div class="mb-6 flex items-center justify-between">
              <h2 class="text-xl font-bold text-slate-700 flex items-center gap-2">
                 <span class="text-2xl">{{ currentCategory?.icon }}</span>
                 {{ currentCategory?.name }}
              </h2>
           </div>

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

           <div v-else-if="categoryPosts.length === 0" class="text-center py-20 text-slate-400 bg-white/40 rounded-3xl border border-white/60">
              <div class="text-4xl mb-2">🍃</div>
              这个分区暂时没有帖子哦
           </div>

           <div v-else class="space-y-4">
              <article v-for="thread in categoryPosts" :key="thread.id"
                @click="router.push(`/post/${thread.id}`)"
                class="bg-white rounded-2xl p-5 border border-slate-200 hover:shadow-md hover:border-purple-200 transition-all cursor-pointer group">
                <div class="flex items-start gap-4">
                  <div class="flex-shrink-0 w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-sm font-bold text-indigo-500 overflow-hidden">
                     <img v-if="thread.author.avatar" :src="formatUrl(thread.author.avatar)" class="w-full h-full object-cover">
                     <span v-else>{{ thread.author.username.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-base font-bold text-slate-800 mb-1 group-hover:text-purple-600 transition-colors">{{ thread.title }}</h3>
                    <p class="text-xs text-slate-500 mb-2 line-clamp-2">{{ thread.excerpt }}</p>
                    <div class="flex items-center gap-3 text-xs text-slate-400">
                       <span class="font-bold text-slate-500">{{ thread.author.username }}</span>
                       <span>·</span>
                       <span>{{ formatTimeAgo(thread.timestamp) }}</span>
                       <span class="ml-auto flex items-center gap-1"><span class="text-xs">👀</span> {{ thread.views }}</span>
                    </div>
                  </div>
                </div>
              </article>
           </div>
        </div>
      </main>

      <!-- 右侧时光轴 -->
      <aside v-if="isDetailMode" class="w-16 bg-white/60 backdrop-blur-md border-l border-slate-200 hidden md:flex flex-col items-center py-10 relative shrink-0">
        <div class="text-xs font-bold text-slate-400 writing-vertical mb-4 opacity-50">START</div>
        <div class="flex-1 w-0.5 bg-slate-200 relative rounded-full my-2">
          <div v-for="(comment, idx) in comments" :key="comment.id"
            @click="scrollToComment(comment.id)"
            class="absolute w-2.5 h-2.5 bg-purple-300 rounded-full -left-[4px] hover:bg-purple-600 hover:scale-150 transition-all cursor-pointer group z-10"
            :style="{ top: getTimelinePosition(comment.timestamp) + '%' }">
            <div class="absolute right-6 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity pointer-events-none shadow-lg">
              #{{ idx + 1 }} {{ formatTime(comment.timestamp) }}
            </div>
          </div>
        </div>
        <div class="text-xs font-bold text-purple-400 writing-vertical mt-4 animate-pulse">NOW</div>
      </aside>

    </div>

    <!-- 底部回复栏 -->
    <footer v-if="isDetailMode" class="reply-composer-shell z-40">
      <div class="max-w-3xl mx-auto relative">

        <!-- 收起状态：回复按钮 -->
        <transition name="slide-fade">
          <div v-if="!showComposer" class="flex items-center justify-center py-3">
            <button @click="showComposer = true" class="composer-expand-button">
              <span class="text-lg">✍️</span>
              <span>写回复</span>
              <span class="text-xs opacity-60">{{ comments.length }} 条讨论</span>
            </button>
          </div>
        </transition>

        <!-- 展开状态：编辑器 -->
        <transition name="composer-reveal">
          <div v-if="showComposer">
            <button @click="showComposer = false" class="composer-collapse-button" title="收起">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>

            <div v-if="showGifPicker" @click="showGifPicker = false" class="fixed inset-0 z-30 bg-transparent"></div>

            <transition name="pop-up">
              <div v-if="showGifPicker" @mousedown.stop @click.stop class="absolute bottom-full left-0 mb-4 w-full sm:w-96 h-80 bg-white rounded-2xl shadow-2xl border border-purple-100 flex flex-col overflow-hidden z-50 picker-panel">
                <div class="p-2 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                  <div class="flex bg-white border border-slate-200 rounded-lg p-0.5 shrink-0">
                    <button
                      type="button"
                      @click="setPickerMode('emoji')"
                      :class="['px-2.5 py-1 rounded-md text-xs font-bold transition-all', pickerMode === 'emoji' ? 'bg-purple-100 text-purple-700 shadow-sm' : 'text-slate-500 hover:text-slate-700']">
                      表情
                    </button>
                    <button
                      type="button"
                      @click="setPickerMode('gif')"
                      :class="['px-2.5 py-1 rounded-md text-xs font-bold transition-all', pickerMode === 'gif' ? 'bg-purple-100 text-purple-700 shadow-sm' : 'text-slate-500 hover:text-slate-700']">
                      动图
                    </button>
                  </div>
                  <input v-if="pickerMode === 'gif'" v-model="gifSearchQuery" @keyup.enter="searchGifs" placeholder="搜索动图..." class="flex-1 min-w-0 bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-purple-400 text-slate-700">
                  <button v-if="pickerMode === 'gif'" @click="searchGifs" class="text-xs bg-slate-200 hover:bg-purple-100 hover:text-purple-600 px-3 py-1.5 rounded-lg font-bold transition-colors">搜</button>
                </div>
                <div v-if="pickerMode === 'emoji'" class="flex-1 overflow-y-auto p-3 grid grid-cols-8 gap-1.5 custom-scroll bg-slate-50/50">
                  <button
                    v-for="emoji in quickEmojis"
                    :key="emoji"
                    type="button"
                    @mousedown.prevent.stop="insertEmoji(emoji)"
                    class="h-9 rounded-lg bg-white border border-slate-100 text-xl hover:bg-purple-50 hover:border-purple-200 hover:scale-105 active:scale-95 transition-all emoji-tile">
                    {{ emoji }}
                  </button>
                </div>
                <div v-else class="flex-1 overflow-y-auto p-2 grid grid-cols-2 gap-2 custom-scroll bg-slate-50/50 relative">
                   <div v-if="loadingGifs" class="absolute inset-0 flex items-center justify-center text-purple-400">
                     <span class="animate-spin text-2xl">⏳</span>
                   </div>
                   <div v-if="gifSource === 'builtin' && !loadingGifs" class="col-span-2 rounded-lg bg-amber-50 border border-amber-100 text-amber-700 px-2 py-1 text-xs">
                     未配置 GIF 搜索源，当前显示内置动图库
                   </div>
                   <div v-if="!loadingGifs && gifSource !== 'builtin' && gifs.length === 0" class="col-span-2 text-center text-slate-400 py-10 text-xs">暂无动图</div>
                   <img v-for="gif in gifs" :key="gif.id" :src="gif.images.fixed_height_small.url"
                        @mousedown.prevent.stop="insertGif(gif)"
                        class="w-full h-24 object-cover rounded-lg cursor-pointer hover:opacity-90 hover:scale-[1.03] active:scale-[0.98] transition-all duration-200 shadow-sm border border-slate-100 bg-slate-200 gif-tile">
                </div>
                <div class="p-1 bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 h-1"></div>
              </div>
            </transition>

            <div class="composer-card">
              <div class="composer-notice">
                <span>请保持友善讨论，支持富文本、图片和动图。</span>
              </div>

              <div class="composer-toolbar" role="toolbar" aria-label="回复工具栏">
                <button @click="toggleGifPicker" :class="{'is-active': showGifPicker}" class="toolbar-button" title="插入表情或动图">☺</button>
                <label class="toolbar-button cursor-pointer relative" title="上传图片">
                  <span>↑</span>
                  <input type="file" class="hidden" accept="image/*" @change="handleImageUpload">
                </label>
                <button @click="openGifPicker" :class="{'is-active': showGifPicker && pickerMode === 'gif'}" class="toolbar-button toolbar-text" title="插入动图">GIF</button>

                <div class="toolbar-separator"></div>
                <button @click="applyInlineStyle('bold')" :class="{'is-active': replyEditor?.isActive('bold')}" class="toolbar-button font-bold" title="加粗">B</button>
                <button @click="applyInlineStyle('italic')" :class="{'is-active': replyEditor?.isActive('italic')}" class="toolbar-button italic font-serif" title="斜体">I</button>
                <button @click="applyInlineStyle('code')" :class="{'is-active': replyEditor?.isActive('code')}" class="toolbar-button font-mono" title="代码">`</button>
                <button @click="applyBlockStyle('heading')" :class="{'is-active': replyEditor?.isActive('heading', { level: 3 })}" class="toolbar-button font-bold" title="标题">H</button>
                <button @click="applyBlockStyle('quote')" :class="{'is-active': replyEditor?.isActive('blockquote')}" class="toolbar-button" title="引用">❝</button>
                <button @click="applyBlockStyle('ul')" :class="{'is-active': replyEditor?.isActive('bulletList')}" class="toolbar-button" title="项目列表">•</button>
                <button @click="applyBlockStyle('ol')" :class="{'is-active': replyEditor?.isActive('orderedList')}" class="toolbar-button toolbar-text" title="编号列表">1.</button>
                <button @click="applyLink" :class="{'is-active': replyEditor?.isActive('link')}" class="toolbar-button" title="链接">↗</button>
              </div>

              <div
                v-if="replyEditor"
                class="rich-editor w-full bg-transparent border-none text-slate-700 p-4 min-h-[112px] max-h-56 overflow-y-auto caret-purple-600 selection:bg-purple-100 selection:text-purple-700 text-sm leading-relaxed custom-scroll"
              >
                <EditorContent :editor="replyEditor" />
              </div>

              <div class="composer-submit">
                 <span :class="['composer-count', replyBody.length > 0 ? 'has-content' : '']">{{ replyBody.length }} / 2000</span>
                 <button @click="submitReply" :disabled="sending || !replyBody.trim()"
                   class="composer-submit-button">
                   <span v-if="sending" class="animate-spin">⏳</span>
                   <span v-else>发送回复</span>
                 </button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </footer>

    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, watch, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import { postsApi, mainApi } from '@/api'
import { useAuthStore } from '@/plugins/auth'
import { useFormatDate } from '@/composables/useFormatDate'
import { useFormatUrl } from '@/composables/useFormatUrl'
import Showmessage from '@/components/showmessage.vue'

const route = useRoute(); const router = useRouter(); const message = ref()
const auth = useAuthStore()
const openProfile = inject('openProfile')
const { formatTimeAgo, formatTime } = useFormatDate()
const { formatUrl } = useFormatUrl()

/** 从渲染后的 HTML 或 Markdown 原文中提取纯文本摘要 */
const toExcerpt = (contentHtml, body) => {
  if (contentHtml) {
    const tmp = document.createElement('div')
    tmp.innerHTML = contentHtml
    const text = tmp.textContent || tmp.innerText || ''
    if (text.trim()) return text
  }
  if (!body) return ''
  return body
    .replace(/!\[.*?\]\(.*?\)/g, '')
    .replace(/\[([^\]]*)\]\(.*?\)/g, '$1')
    .replace(/^[#>\-\*]{1,6}\s?/gm, '')
    .replace(/[*_`~]+/g, '')
    .replace(/\n+/g, ' ')
}

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

// 回复
const showComposer = ref(false)
const replyBody = ref('');
const sending = ref(false)
const showGifPicker = ref(false)
const pickerMode = ref('emoji')
const gifs = ref([])
const gifSource = ref('')
const gifSearchQuery = ref('reaction')
const loadingGifs = ref(false)
const quickEmojis = [
  '😀', '😄', '😂', '🤣', '😊', '😍', '😘', '🥰',
  '😎', '🤔', '😮', '😭', '😤', '👍', '👏', '🙏',
  '🔥', '✨', '🎉', '💯', '❤️', '💜', '💙', '💚',
  '👀', '💬', '🚀', '⭐', '🌈', '🍻', '☕', '🍰',
  '🐱', '🐶', '🦄', '🍃', '⚡', '🎯', '✅', '❌'
]

// 点赞 + 编辑/删除
const liked = ref(false)
const likeCount = ref(0)
const editingCommentId = ref(null)
const editCommentBody = ref('')

const isDetailMode = computed(() => route.name === 'PostDetail')

const renderedBody = computed(() => {
  if (!post.value) return ''
  return post.value.content_html || ''
})

const replyEditor = useEditor({
  extensions: [
    StarterKit,
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        rel: 'noopener noreferrer',
        target: '_blank',
      },
    }),
    Image.configure({ inline: false }),
    Placeholder.configure({
      placeholder: '友善发言，不仅是美德...',
    }),
  ],
  content: '',
  onUpdate: ({ editor }) => {
    replyBody.value = htmlToMarkdown(editor.getHTML())
  },
})

// 进度条
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

// 数据加载
const loadCategories = async () => {
  if (categories.value.length > 0) return
  try {
    const res = await postsApi.categories()
    if(res.data.code === 200) categories.value = res.data.data
  } catch (e) { console.error(e) }
}

const loadPost = async (id) => {
  try {
    const res = await postsApi.detail(id)
    if(res.data.code === 200) {
      post.value = res.data.data;
      comments.value = res.data.data.comments || [];
      likeCount.value = res.data.data.likes || 0;
      fetchLikeStatus(id);
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
    const res = await postsApi.list({ category_id: catId })
    if(res.data.code === 200) {
      categoryPosts.value = res.data.data.map(p => ({
        ...p,
        author: p.author || { username: '未知', avatar: '' },
        excerpt: toExcerpt(p.content_html, p.body).slice(0, 80) + '...',
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

// 图片上传
const handleImageUpload = async (e) => {
  const file = e.target.files[0]
  if(!file) return
  const formData = new FormData()
  formData.append('file', file)
  insertRichText('上传中...')

  try {
    const res = await mainApi.upload(formData)
    if(res.data.code === 200) {
      const fullUrl = formatUrl(res.data.url)
      removeUploadPlaceholder()
      insertRichImage(fullUrl)
    } else {
      removeUploadPlaceholder()
      message.value.showMessage(res.data.message)
    }
  } catch(e) {
    removeUploadPlaceholder()
    message.value.showMessage('图片上传失败')
  }
}

// GIF
const fallbackGifs = [
  { id: 'f1', images: { fixed_height_small: { url: 'https://media.giphy.com/media/JIX9t2j0ZTN9S/200w.gif' }, fixed_height: { url: 'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif' } } },
  { id: 'f2', images: { fixed_height_small: { url: 'https://media.giphy.com/media/8Iv5lqKwKsZ2g/200w.gif' }, fixed_height: { url: 'https://media.giphy.com/media/8Iv5lqKwKsZ2g/giphy.gif' } } }
]

const fetchGifs = async (query = 'reaction') => {
  if (loadingGifs.value) return
  loadingGifs.value = true
  try {
    const res = await mainApi.gifs({ q: query, limit: 20 })
    gifSource.value = res.data.source || ''
    if (res.data.code === 200 && res.data.data.length > 0) {
      gifs.value = res.data.data
    } else {
      gifs.value = fallbackGifs
      gifSource.value = 'fallback'
    }
  } catch (e) {
    gifs.value = fallbackGifs
    gifSource.value = 'fallback'
  } finally {
    loadingGifs.value = false
  }
}

const toggleGifPicker = () => {
  showGifPicker.value = !showGifPicker.value
  if (showGifPicker.value && pickerMode.value === 'gif' && gifs.value.length === 0) fetchGifs()
}

const openGifPicker = () => {
  pickerMode.value = 'gif'
  showGifPicker.value = true
  if (gifs.value.length === 0) fetchGifs()
}

const setPickerMode = (mode) => {
  pickerMode.value = mode
  if (mode === 'gif' && gifs.value.length === 0) fetchGifs()
}

const searchGifs = () => {
  if (!gifSearchQuery.value.trim()) return
  fetchGifs(gifSearchQuery.value)
}

const insertGif = (gif) => {
  const url = gif?.images?.fixed_height?.url || gif?.images?.fixed_height_small?.url
  if (!url) return
  insertRichImage(url)
  showGifPicker.value = false
}

const insertEmoji = (emoji) => {
  insertRichText(emoji)
}

// 富文本回复编辑器。提交时转换成 Markdown，由后端统一渲染和清洗。
const focusEditor = () => {
  replyEditor.value?.chain().focus().run()
}

const applyInlineStyle = (style) => {
  focusEditor()
  if (style === 'bold') replyEditor.value?.chain().focus().toggleBold().run()
  if (style === 'italic') replyEditor.value?.chain().focus().toggleItalic().run()
  if (style === 'code') replyEditor.value?.chain().focus().toggleCode().run()
  syncReplyMarkdown()
}

const applyBlockStyle = (style) => {
  focusEditor()
  if (style === 'heading') replyEditor.value?.chain().focus().toggleHeading({ level: 3 }).run()
  if (style === 'quote') replyEditor.value?.chain().focus().toggleBlockquote().run()
  if (style === 'ul') replyEditor.value?.chain().focus().toggleBulletList().run()
  if (style === 'ol') replyEditor.value?.chain().focus().toggleOrderedList().run()
  syncReplyMarkdown()
}

const applyLink = () => {
  focusEditor()
  const previousUrl = replyEditor.value?.getAttributes('link').href || ''
  const href = window.prompt('输入链接地址', previousUrl)
  if (!href) return
  if (href === previousUrl) return
  replyEditor.value?.chain().focus().extendMarkRange('link').setLink({ href }).run()
  syncReplyMarkdown()
}

const insertRichText = (text) => {
  replyEditor.value?.chain().focus().insertContent(text).run()
  syncReplyMarkdown()
}

const insertRichImage = (url) => {
  replyEditor.value?.chain().focus().setImage({ src: url, alt: 'gif' }).createParagraphNear().run()
  syncReplyMarkdown()
}

const removeUploadPlaceholder = () => {
  const current = replyEditor.value?.getText() || ''
  if (!current.includes('上传中...')) return
  replyEditor.value?.commands.setContent(replyEditor.value.getHTML().replace('上传中...', ''))
  syncReplyMarkdown()
}

const syncReplyMarkdown = () => {
  replyBody.value = htmlToMarkdown(replyEditor.value?.getHTML() || '')
}

const nodeToMarkdown = (node) => {
  if (node.nodeType === Node.TEXT_NODE) return node.textContent || ''
  if (node.nodeType !== Node.ELEMENT_NODE) return ''

  const el = node
  const children = Array.from(el.childNodes).map(nodeToMarkdown).join('')
  const tag = el.tagName.toLowerCase()

  if (tag === 'br') return '\n'
  if (tag === 'h1' || tag === 'h2' || tag === 'h3') return `### ${children.trim()}\n`
  if (tag === 'blockquote') {
    return children
      .split('\n')
      .filter(Boolean)
      .map(line => `> ${line}`)
      .join('\n') + '\n'
  }
  if (tag === 'ul') {
    return Array.from(el.children)
      .map(child => `- ${nodeToMarkdown(child).trim()}`)
      .join('\n') + '\n'
  }
  if (tag === 'ol') {
    return Array.from(el.children)
      .map((child, index) => `${index + 1}. ${nodeToMarkdown(child).trim()}`)
      .join('\n') + '\n'
  }
  if (tag === 'li') return children
  if (tag === 'a') {
    const href = el.getAttribute('href') || ''
    return href ? `[${children || href}](${href})` : children
  }
  if (tag === 'strong' || tag === 'b') return `**${children}**`
  if (tag === 'em' || tag === 'i') return `*${children}*`
  if (tag === 'code') return `\`${children.replace(/`/g, '')}\``
  if (tag === 'img') {
    const src = el.getAttribute('src') || ''
    const alt = el.getAttribute('alt') || 'image'
    return src ? `![${alt}](${src})` : ''
  }
  if (tag === 'div' || tag === 'p') return `${children.trim()}\n`
  return children
}

const htmlToMarkdown = (html) => {
  const template = document.createElement('template')
  template.innerHTML = html || ''
  return Array.from(template.content.childNodes)
    .map(nodeToMarkdown)
    .join('')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

// 提交评论
const submitReply = () => {
  if (!auth.isLoggedIn) return router.push('/login')
  if (!replyBody.value.trim()) return message.value.showMessage('内容不能为空')
  sending.value = true
  postsApi.addComment(post.value.id, { body: replyBody.value }).then(res => {
      if(res.data.code === 200) {
        message.value.showMessage('回复成功');
        replyBody.value = '';
        replyEditor.value?.commands.clearContent()
        loadPost(post.value.id).then(() => {
           setTimeout(() => {
              const main = document.getElementById('main-scroll')
              if(main) main.scrollTo({ top: main.scrollHeight, behavior: 'smooth' })
           }, 100)
        })
      } else { message.value.showMessage(res.data.message) }
  }).catch(err => { message.value.showMessage(err._message || '回复失败') })
  .finally(() => sending.value = false)
}

// 点赞、编辑、删除
const canEditPost = computed(() => {
  if (!auth.isLoggedIn || !post.value) return false
  return auth.user.id === post.value.author.id || auth.isAdmin
})

const canEditComment = (comment) => {
  if (!auth.isLoggedIn) return false
  return auth.user.id === comment.author.id || auth.isAdmin
}

const fetchLikeStatus = async (pid) => {
  try {
    const res = await postsApi.likeStatus(pid)
    if (res.data.code === 200) {
      liked.value = res.data.data.liked
      likeCount.value = res.data.data.count
    }
  } catch (e) { /* ignore */ }
}

const toggleLike = async () => {
  if (!auth.isLoggedIn) return router.push('/login')
  try {
    const res = await postsApi.like(post.value.id)
    if (res.data.code === 200) {
      liked.value = res.data.liked
      likeCount.value = res.data.count
    }
  } catch (e) { console.error(e) }
}

const goEditPost = () => {
  router.push({ path: '/create', query: { edit: post.value.id } })
}

const deletePostConfirm = () => {
  if (!confirm('确定要删除这个帖子吗？此操作不可撤销！')) return
  postsApi.delete(post.value.id).then(res => {
    if (res.data.code === 200) {
      message.value.showMessage('帖子已删除')
      setTimeout(() => router.push('/'), 1000)
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(e => { message.value.showMessage(e._message || '删除失败') })
}

const startEditComment = (comment) => {
  editingCommentId.value = comment.id
  editCommentBody.value = comment.body
}

const saveEditComment = async (comment) => {
  if (!editCommentBody.value.trim()) return
  try {
    const res = await postsApi.editComment(post.value.id, comment.id, { body: editCommentBody.value })
    if (res.data.code === 200) {
      Object.assign(comment, res.data.data)
      editingCommentId.value = null
      message.value.showMessage('评论已更新')
    } else {
      message.value.showMessage(res.data.message)
    }
  } catch (e) { message.value.showMessage(e._message || '更新失败') }
}

const deleteCommentConfirm = (comment) => {
  if (!confirm('确定要删除这条评论吗？')) return
  postsApi.deleteComment(post.value.id, comment.id).then(res => {
    if (res.data.code === 200) {
      comments.value = comments.value.filter(c => c.id !== comment.id)
      message.value.showMessage('评论已删除')
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(e => { message.value.showMessage(e._message || '删除失败') })
}

// 时光轴
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

onUnmounted(() => {
  clearInterval(progressInterval)
  replyEditor.value?.destroy()
})
</script>

<style scoped>
.writing-vertical { writing-mode: vertical-rl; text-orientation: mixed; letter-spacing: 4px; }
.markdown-body :deep(h1) { font-size: 1.8em; font-weight: 800; margin: 0.5em 0; color: #1e293b; }
.markdown-body :deep(h2) { font-size: 1.5em; font-weight: 700; margin: 0.5em 0; color: #334155; }
.markdown-body :deep(p) { margin-bottom: 1em; line-height: 1.75; color: #475569; }
.markdown-body :deep(img) { max-width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1em 0; }
.comment-body {
  font-size: 15.5px;
  line-height: 1.75;
}
.comment-body :deep(p) {
  margin-bottom: 0.55em;
}
.comment-body :deep(p:only-child) {
  margin-bottom: 0;
}
.comment-body :deep(img) {
  max-width: 240px;
}
.reply-composer-shell {
  background: rgba(248, 250, 252, 0.96);
  border-top: 1px solid #cbd5e1;
  padding: 12px 16px 20px;
  box-shadow: 0 -10px 30px rgba(15, 23, 42, 0.08);
}
.composer-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
  overflow: hidden;
}
.composer-notice {
  background: #fffbeb;
  border-bottom: 1px solid #fde68a;
  color: #92400e;
  font-size: 12px;
  line-height: 1.4;
  padding: 8px 12px;
}
.composer-toolbar {
  min-height: 42px;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 5px 8px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  overflow-x: auto;
}
.toolbar-button {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  color: #475569;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
  border: 1px solid transparent;
  background: transparent;
  transition: color 140ms ease, background-color 140ms ease, border-color 140ms ease, transform 120ms ease;
}
.toolbar-button:hover {
  color: #111827;
  background: #e2e8f0;
  border-color: #cbd5e1;
}
.toolbar-button:active {
  transform: translateY(1px);
}
.toolbar-button.is-active {
  color: #6d28d9;
  background: #ede9fe;
  border-color: #c4b5fd;
}
.toolbar-text {
  font-size: 11px;
}
.toolbar-separator {
  width: 1px;
  height: 22px;
  background: #cbd5e1;
  margin: 0 5px;
  flex: 0 0 auto;
}
.rich-editor {
  min-height: 128px;
  max-height: 260px;
  overflow-y: auto;
  background: #ffffff;
  padding: 0;
}
.rich-editor :deep(.ProseMirror) {
  min-height: 128px;
  padding: 14px 16px 18px;
  outline: none;
  color: #334155;
  font-size: 14px;
  line-height: 1.65;
}
.rich-editor :deep(.ProseMirror p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  color: #94a3b8;
  float: left;
  height: 0;
  pointer-events: none;
}
.rich-editor :deep(.ProseMirror p) {
  margin: 0 0 0.65rem;
}
.rich-editor :deep(.ProseMirror h3) {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.35rem 0 0.6rem;
}
.rich-editor :deep(.ProseMirror blockquote) {
  border-left: 3px solid #a78bfa;
  padding-left: 0.85rem;
  color: #64748b;
  margin: 0.65rem 0;
}
.rich-editor :deep(.ProseMirror ul),
.rich-editor :deep(.ProseMirror ol) {
  padding-left: 1.35rem;
  margin: 0.65rem 0;
}
.rich-editor :deep(.ProseMirror ul) { list-style: disc; }
.rich-editor :deep(.ProseMirror ol) { list-style: decimal; }
.rich-editor :deep(.ProseMirror a) {
  color: #6d28d9;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.rich-editor :deep(.ProseMirror img) {
  max-width: 220px;
  max-height: 150px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
  margin: 0.65rem 0;
  border: 1px solid #cbd5e1;
}
.rich-editor :deep(.ProseMirror code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.86em;
  background: #f1f5f9;
  color: #6d28d9;
  padding: 0.1rem 0.3rem;
  border-radius: 0.3rem;
}
.composer-submit {
  min-height: 48px;
  padding: 8px 10px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}
.composer-count {
  font-size: 11px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #94a3b8;
}
.composer-count.has-content {
  color: #64748b;
}
.composer-submit-button {
  min-width: 92px;
  height: 34px;
  border-radius: 6px;
  background: #6d28d9;
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 14px;
  transition: background-color 140ms ease, transform 120ms ease, opacity 140ms ease;
}
.composer-submit-button:hover {
  background: #5b21b6;
}
.composer-submit-button:active {
  transform: translateY(1px);
}
.composer-submit-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.animate-fade-in { animation: fadeIn 400ms var(--ease-apple) both; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(16px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.picker-panel {
  transform-origin: left bottom;
  will-change: opacity, transform;
}
.pop-up-enter-active { transition: opacity 180ms var(--ease-smooth), transform 220ms var(--ease-smooth); }
.pop-up-leave-active { transition: opacity 140ms var(--ease-smooth), transform 160ms var(--ease-smooth); }
.pop-up-enter-from, .pop-up-leave-to { opacity: 0; transform: translateY(8px) scale(0.98); }
.emoji-tile, .gif-tile { will-change: transform; }

/* 回复按钮 - 收起状态 */
.composer-expand-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 28px;
  border-radius: 999px;
  background: linear-gradient(135deg, #6d28d9, #7c3aed);
  color: #ffffff;
  font-size: 14px;
  font-weight: 800;
  box-shadow: 0 4px 16px rgba(109, 40, 217, 0.35);
  transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
  cursor: pointer;
}
.composer-expand-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(109, 40, 217, 0.45);
}
.composer-expand-button:active {
  transform: translateY(0.5px) scale(0.98);
}

/* 收起按钮 */
.composer-collapse-button {
  position: absolute;
  top: -14px;
  right: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
  transition: background 140ms, color 140ms, transform 140ms;
  z-index: 10;
}
.composer-collapse-button:hover {
  background: #e2e8f0;
  color: #334155;
  transform: scale(1.08);
}
.composer-collapse-button:active {
  transform: scale(0.95);
}

/* 展开/收起动画 */
.slide-fade-enter-active { transition: opacity 200ms ease, transform 200ms ease; }
.slide-fade-leave-active { transition: opacity 120ms ease, transform 120ms ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(8px); }

.composer-reveal-enter-active { transition: opacity 260ms ease, transform 300ms cubic-bezier(0.34, 1.56, 0.64, 1); }
.composer-reveal-leave-active { transition: opacity 140ms ease, transform 160ms ease; }
.composer-reveal-enter-from, .composer-reveal-leave-to { opacity: 0; transform: translateY(20px) scale(0.97); }
</style>
