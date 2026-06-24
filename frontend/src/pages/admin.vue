<template>
  <div class="min-h-screen bg-slate-900 font-sans selection:bg-purple-500 text-slate-200">

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
        <button @click="switchView('resets')" :class="navClass('resets')">🔑 重置申请</button>
        <button @click="switchView('upgrade')" :class="navClass('upgrade')">🚀 系统升级</button>
      </div>

      <router-link to="/" class="block px-4 py-3 mt-8 flex items-center gap-2 text-slate-500 hover:text-white transition-colors border-t border-slate-700/50 pt-6">
        <span>←</span> 返回前台
      </router-link>
    </nav>

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
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-purple-900/50 overflow-hidden">
             <img v-if="auth.user.avatar" :src="formatUrl(auth.user.avatar)" class="w-full h-full object-cover">
             <span v-else>A</span>
          </div>
        </div>
      </header>

      <div class="p-10 max-w-7xl mx-auto min-h-[calc(100vh-80px)]">

        <!-- Dashboard -->
        <div v-if="currentView === 'dashboard'" class="animate-fade-in">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
            <div v-for="(item, idx) in dashboardCards" :key="idx" class="bg-slate-800 p-6 rounded-2xl border border-slate-700 hover:border-purple-500/50 transition-colors">
              <div class="text-3xl mb-4 bg-slate-700/50 w-12 h-12 rounded-lg flex items-center justify-center">{{ item.icon }}</div>
              <div class="text-3xl font-black text-white mb-1">{{ item.value }}</div>
              <div class="text-xs text-slate-500 font-bold uppercase tracking-wider">{{ item.label }}</div>
            </div>
          </div>
        </div>

        <!-- Users -->
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
                      <img v-if="user.avatar" :src="formatUrl(user.avatar)" class="w-full h-full object-cover">
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
                  <td class="p-5 text-sm text-slate-400">{{ formatDateTime(user.timestamp || new Date()) }}</td>
                  <td class="p-5 text-right">
                    <button @click="deleteUser(user.id)" class="text-slate-500 hover:text-red-400 transition-colors text-sm font-bold bg-slate-900 hover:bg-red-900/30 px-3 py-1.5 rounded border border-slate-700">移除</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="userList.length === 0" class="p-10 text-center text-slate-500">暂无数据</div>
          </div>
        </div>

        <!-- Categories -->
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

        <!-- Posts -->
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
                    <div>📅 {{ formatDateTime(post.timestamp) }}</div>
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

        <!-- Comments -->
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
                    <div class="text-xs text-slate-500 mt-1">{{ formatDateTime(comment.timestamp) }}</div>
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

        <!-- Password Reset Requests -->
        <div v-if="currentView === 'resets'" class="animate-fade-in space-y-4">
          <div class="flex gap-3 mb-2">
            <button v-for="s in ['pending', 'approved', 'rejected', 'all']" :key="s" @click="resetStatusFilter = s; fetchPasswordResets()"
              :class="['px-4 py-2 text-sm font-bold rounded-lg transition-colors', resetStatusFilter === s ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700']">
              {{ {pending: '待处理', approved: '已批准', rejected: '已拒绝', all: '全部'}[s] }}
            </button>
          </div>
          <div class="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
                  <th class="p-5 font-bold">用户</th>
                  <th class="p-5 font-bold">邮箱</th>
                  <th class="p-5 font-bold">状态</th>
                  <th class="p-5 font-bold">申请时间</th>
                  <th class="p-5 font-bold text-right">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-700">
                <tr v-for="r in resetList" :key="r.id" class="hover:bg-slate-700/30 transition-colors">
                  <td class="p-5 text-sm font-bold text-slate-200">{{ r.username }}</td>
                  <td class="p-5 text-sm text-slate-400">{{ r.email }}</td>
                  <td class="p-5">
                    <span :class="['px-2 py-1 rounded text-xs font-bold', r.status === 'pending' ? 'bg-amber-500/20 text-amber-300' : r.status === 'approved' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300']">
                      {{ {pending: '待处理', approved: '已批准', rejected: '已拒绝'}[r.status] }}
                    </span>
                  </td>
                  <td class="p-5 text-sm text-slate-500">{{ formatDateTime(r.timestamp) }}</td>
                  <td class="p-5 text-right space-x-2">
                    <button v-if="r.status === 'pending'" @click="approveReset(r.id)" class="text-green-400 hover:text-green-300 text-sm font-bold bg-green-900/20 hover:bg-green-900/40 px-3 py-1.5 rounded border border-green-800/50 transition-colors">批准</button>
                    <button v-if="r.status === 'pending'" @click="rejectReset(r.id)" class="text-red-400 hover:text-red-300 text-sm font-bold bg-red-900/20 hover:bg-red-900/40 px-3 py-1.5 rounded border border-red-800/50 transition-colors">拒绝</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="resetList.length === 0" class="p-10 text-center text-slate-500">暂无申请</div>
          </div>
          <!-- 批准后显示临时密码 -->
          <div v-if="approvedResult" class="bg-green-900/30 border border-green-500/30 rounded-xl p-5">
            <div class="text-green-400 font-bold mb-2">✅ 临时密码已生成，请将此信息告知用户：</div>
            <div class="bg-slate-950 rounded-lg p-4 font-mono text-sm text-slate-200 space-y-1">
              <div>用户名: <span class="text-green-400">{{ approvedResult.username }}</span></div>
              <div>邮箱: <span class="text-green-400">{{ approvedResult.email }}</span></div>
              <div>临时密码: <span class="text-yellow-400 text-lg font-black">{{ approvedResult.temp_password }}</span></div>
            </div>
            <p class="text-amber-400 text-xs mt-2">⚠️ 请妥善保管，用户首次登录后应立即修改密码</p>
          </div>
        </div>

        <!-- System Upgrade -->
        <div v-if="currentView === 'upgrade'" class="animate-fade-in space-y-6">

          <!-- System Info -->
          <div class="bg-slate-800 rounded-2xl border border-slate-700 p-6">
            <h3 class="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">🖥️ 系统信息</h3>
            <div v-if="sysInfoLoading" class="text-slate-500 animate-pulse py-4 text-center">加载中...</div>
            <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                <div class="text-xs text-slate-500 mb-1 font-bold">当前版本</div>
                <div class="text-xl font-black text-purple-400">v{{ sysInfo.version || '?' }}</div>
              </div>
              <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                <div class="text-xs text-slate-500 mb-1 font-bold">运行环境</div>
                <div class="text-sm font-bold" :class="sysInfo.is_docker ? 'text-blue-400' : 'text-green-400'">
                  {{ sysInfo.is_docker ? '🐳 Docker' : sysInfo.git_available ? '🖥️ 宿主机 (Git)' : '🖥️ 宿主机' }}
                </div>
              </div>
              <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                <div class="text-xs text-slate-500 mb-1 font-bold">Git 分支</div>
                <div class="text-sm font-bold text-slate-200">{{ sysInfo.git_branch || '-' }}</div>
                <div class="text-xs text-slate-500 mt-0.5">{{ sysInfo.git_commit ? `@${sysInfo.git_commit}` : '' }}</div>
              </div>
              <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                <div class="text-xs text-slate-500 mb-1 font-bold">工作区</div>
                <div v-if="sysInfo.git_dirty" class="text-xs font-bold text-amber-400">⚡ 有未提交改动</div>
                <div v-else class="text-xs font-bold text-green-400">✓ 干净</div>
              </div>
            </div>
            <div v-if="sysInfo.git_remote_url" class="mt-3 text-xs text-slate-600 truncate">
              远程: {{ sysInfo.git_remote_url }}
            </div>
          </div>

          <!-- Check Update -->
          <div class="bg-slate-800 rounded-2xl border border-slate-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-bold text-slate-100 flex items-center gap-2">🔄 检查更新</h3>
              <button @click="doCheckUpdate" :disabled="checkingUpdate || !sysInfo.git_available"
                class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2">
                <span v-if="checkingUpdate" class="animate-spin">⏳</span>
                <span v-else>🔍</span>
                {{ checkingUpdate ? '检查中...' : '检查更新' }}
              </button>
            </div>

            <div v-if="!sysInfo.git_available" class="text-amber-400 text-sm py-4 text-center">
              ⚠️ 当前环境不支持 git 操作，无法自动升级。请手动部署。
            </div>

            <div v-else-if="updateInfo === null && !checkingUpdate" class="text-slate-500 text-sm py-4 text-center">
              点击"检查更新"查看是否有新版本
            </div>

            <template v-if="updateInfo">
              <!-- Already latest -->
              <div v-if="!updateInfo.has_update" class="py-6 text-center">
                <div class="text-4xl mb-2">✅</div>
                <div class="text-green-400 font-bold">当前已是最新版本</div>
                <div class="text-xs text-slate-500 mt-1">v{{ updateInfo.local_version }} · {{ updateInfo.local_commit }}</div>
              </div>

              <!-- New version available -->
              <div v-else class="space-y-4">
                <div class="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-xl p-4 border border-purple-500/30">
                  <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-3">
                      <span class="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs font-bold rounded">NEW</span>
                      <span class="text-lg font-black text-slate-100">v{{ updateInfo.remote_version }}</span>
                    </div>
                    <span class="text-xs text-slate-500">当前: v{{ updateInfo.local_version }}</span>
                  </div>
                  <div class="text-xs text-slate-400">
                    {{ updateInfo.remote_branch }} · {{ updateInfo.remote_commit }}
                  </div>
                </div>

                <!-- Changelog -->
                <div v-if="updateInfo.changelog" class="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                  <div class="text-xs font-bold text-slate-500 mb-2">📋 更新日志</div>
                  <div class="text-sm text-slate-300 font-mono whitespace-pre-line leading-relaxed">{{ updateInfo.changelog }}</div>
                </div>

                <!-- Upgrade button -->
                <button @click="doUpgrade" :disabled="upgrading"
                  class="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-xl text-lg shadow-lg shadow-green-900/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                  <span v-if="upgrading" class="animate-spin">⏳</span>
                  <span v-else>🚀</span>
                  {{ upgrading ? '升级中，请勿关闭...' : '一键升级' }}
                </button>
              </div>
            </template>
          </div>

          <!-- Upgrade Logs -->
          <div v-if="upgradeLogs.length > 0 || upgrading" class="bg-slate-800 rounded-2xl border border-slate-700 p-6">
            <h3 class="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              📜 升级日志
              <span v-if="upgrading" class="animate-pulse text-xs text-purple-400">进行中...</span>
            </h3>
            <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 max-h-80 overflow-y-auto custom-scroll">
              <div v-for="(log, i) in upgradeLogs" :key="i" :class="[
                'py-0.5',
                log.includes('✗') ? 'text-red-400' : log.includes('✓') ? 'text-green-400' : 'text-slate-300'
              ]">{{ log }}</div>
              <div v-if="upgrading" class="animate-pulse text-purple-400 py-0.5">▌</div>
            </div>
            <div v-if="upgradeResult" class="mt-3 p-3 rounded-lg text-sm font-bold"
              :class="upgradeResult.success ? 'bg-green-900/30 text-green-400 border border-green-500/30' : 'bg-red-900/30 text-red-400 border border-red-500/30'">
              {{ upgradeResult.message }}
            </div>
          </div>
        </div>

      </div>
    </main>
    <Showmessage ref="message" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminApi } from '@/api'
import { useFormatDate } from '@/composables/useFormatDate'
import { useFormatUrl } from '@/composables/useFormatUrl'
import Showmessage from '@/components/showmessage.vue'
import { useAuthStore } from '@/plugins/auth'

const currentView = ref('dashboard')
const message = ref()
const stats = ref({ users: 0, posts: 0, categories: 0, comments: 0 })
const auth = useAuthStore()
const { formatDateTime } = useFormatDate()
const { formatUrl } = useFormatUrl()

const categories = ref([])
const userList = ref([])
const postList = ref([])
const commentList = ref([])
const resetList = ref([])
const newCat = ref({ name: '', icon: '' })
const resetStatusFilter = ref('pending')
const approvedResult = ref(null)

// -- Upgrade State --
const sysInfo = ref({ version: '', is_docker: false, git_available: false, git_branch: '', git_commit: '', git_dirty: false, git_remote_url: '' })
const sysInfoLoading = ref(false)
const updateInfo = ref(null)
const checkingUpdate = ref(false)
const upgrading = ref(false)
const upgradeLogs = ref([])
const upgradeResult = ref(null)

const dashboardCards = computed(() => [
  { icon: '👥', value: stats.value.users, label: '总用户数' },
  { icon: '📝', value: stats.value.posts, label: '帖子总数' },
  { icon: '💬', value: stats.value.comments, label: '评论总数' },
  { icon: '📂', value: stats.value.categories, label: '活跃板块' },
])

const viewName = computed(() => {
  const map = { 'dashboard': '数据概览', 'users': '用户管理', 'categories': '板块管理', 'posts': '文章管理', 'comments': '评论管理', 'resets': '重置申请', 'upgrade': '系统升级' }
  return map[currentView.value]
})

onMounted(() => {
  fetchStats()
  fetchCategories()
  loadSystemInfo()
})

const navClass = (view) => {
  const base = "w-full text-left px-4 py-3 rounded-xl transition-all duration-200 flex items-center gap-3 text-sm font-medium"
  if (currentView.value === view) return `${base} bg-purple-600/20 text-purple-300 border border-purple-500/30 shadow-lg shadow-purple-900/20`
  return `${base} text-slate-400 hover:bg-slate-700/50 hover:text-white`
}

const switchView = (view) => {
  currentView.value = view
  if (view === 'users') fetchUsers()
  if (view === 'posts') fetchPosts()
  if (view === 'comments') fetchComments()
  if (view === 'resets') fetchPasswordResets()
  if (view === 'categories') fetchCategories()
  if (view === 'dashboard') fetchStats()
  if (view === 'upgrade') loadSystemInfo()
}

// -- CRUD APIs --
const fetchStats = () => { adminApi.stats().then(res => { if (res.data.code === 200) stats.value = res.data.data }) }
const fetchCategories = () => { adminApi.categories().then(res => { if (res.data.code === 200) categories.value = res.data.data }) }
const addCategory = () => {
  if (!newCat.value.name) return message.value.showMessage('名字不能为空')
  adminApi.addCategory(newCat.value).then(res => {
    if (res.data.code === 200) { message.value.showMessage('创建成功！'); newCat.value = { name: '', icon: '' }; fetchCategories(); fetchStats() }
    else { message.value.showMessage(res.data.message) }
  }).catch(err => message.value.showMessage(err._message || '创建失败'))
}
const deleteCategory = (id) => {
  if (!confirm('确定要删除这个板块吗？')) return
  adminApi.deleteCategory(id).then(res => { if (res.data.code === 200) { message.value.showMessage('已删除'); fetchCategories() } })
}

const fetchUsers = () => { adminApi.users().then(res => { if (res.data.code === 200) userList.value = res.data.data }) }
const deleteUser = (id) => {
  if (!confirm('警告：确定要删除该用户吗？此操作不可逆！')) return
  adminApi.deleteUser(id).then(res => { if (res.data.code === 200) { message.value.showMessage('用户已删除'); fetchUsers(); fetchStats() } })
}

const fetchPosts = () => { adminApi.posts().then(res => { if (res.data.code === 200) postList.value = res.data.data }) }
const deletePost = (id) => {
  if (!confirm('确定要删除这篇文章吗？')) return
  adminApi.deletePost(id).then(res => { if (res.data.code === 200) { message.value.showMessage('文章已删除'); fetchPosts(); fetchStats() } })
}

const fetchComments = () => { adminApi.comments().then(res => { if (res.data.code === 200) commentList.value = res.data.data }) }
const deleteComment = (id) => {
  if (!confirm('确定删除这条评论？')) return
  adminApi.deleteComment(id).then(res => { if (res.data.code === 200) { message.value.showMessage('评论已删除'); fetchComments(); fetchStats() } })
}

// -- Password Reset APIs --
const fetchPasswordResets = () => {
  adminApi.passwordResets({ status: resetStatusFilter.value }).then(res => {
    if (res.data.code === 200) resetList.value = res.data.data
  })
}
const approveReset = (id) => {
  if (!confirm('批准后将为该用户生成随机临时密码，确认？')) return
  approvedResult.value = null
  adminApi.approvePasswordReset(id).then(res => {
    if (res.data.code === 200) {
      approvedResult.value = res.data.data
      message.value.showMessage('已批准，临时密码已生成')
      fetchPasswordResets()
    } else {
      message.value.showMessage(res.data.message)
    }
  }).catch(err => message.value.showMessage(err._message || '操作失败'))
}
const rejectReset = (id) => {
  if (!confirm('确定拒绝此申请？')) return
  adminApi.rejectPasswordReset(id).then(res => {
    if (res.data.code === 200) { message.value.showMessage('已拒绝'); fetchPasswordResets() }
    else { message.value.showMessage(res.data.message) }
  }).catch(err => message.value.showMessage(err._message || '操作失败'))
}

// -- Upgrade APIs --
const loadSystemInfo = async () => {
  sysInfoLoading.value = true
  try {
    const res = await adminApi.systemInfo()
    if (res.data.code === 200) sysInfo.value = res.data.data
  } catch (e) { console.error(e) }
  finally { sysInfoLoading.value = false }
}

const doCheckUpdate = async () => {
  checkingUpdate.value = true
  updateInfo.value = null
  try {
    const res = await adminApi.checkUpdate()
    if (res.data.code === 200) {
      updateInfo.value = res.data.data
      if (res.data.data.has_update) {
        message.value.showMessage('🔄 发现新版本！')
      } else {
        message.value.showMessage('✅ 已是最新版本')
      }
    } else {
      message.value.showMessage(res.data.message || '检查更新失败')
    }
  } catch (err) {
    message.value.showMessage(err._message || '检查更新失败')
  } finally {
    checkingUpdate.value = false
  }
}

const doUpgrade = async () => {
  if (!confirm('确认执行升级？升级期间服务可能短暂中断。')) return
  upgrading.value = true
  upgradeLogs.value = []
  upgradeResult.value = null

  try {
    const res = await adminApi.doUpgrade()
    if (res.data.code === 200) {
      upgradeLogs.value = res.data.data.logs || []
      upgradeResult.value = { success: true, message: res.data.message }
      message.value.showMessage('🚀 ' + res.data.message)
      // 刷新系统信息
      setTimeout(() => { loadSystemInfo(); updateInfo.value = null }, 2000)
    } else {
      upgradeLogs.value = res.data.logs || []
      upgradeResult.value = { success: false, message: res.data.message }
      message.value.showMessage(res.data.message || '升级失败')
    }
  } catch (err) {
    upgradeResult.value = { success: false, message: err._message || '升级请求失败' }
    message.value.showMessage(err._message || '升级请求失败')
  } finally {
    upgrading.value = false
  }
}
</script>
