<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 font-sans selection:bg-pink-200 overflow-hidden relative">

    <!-- 动态背景 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
      <div class="absolute top-[20%] right-[-10%] w-96 h-96 bg-yellow-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="relative z-50">
      <appheader />
    </div>

    <main class="relative z-10 max-w-5xl mx-auto px-6 py-12">

      <!-- 顶部标题区 -->
      <header class="text-center mb-14">
        <div class="inline-block px-4 py-1.5 rounded-full bg-white/60 text-pink-500 text-sm font-bold mb-6 shadow-sm border border-white/50 backdrop-blur-sm animate-bounce-slow">
          📖 关于本站
        </div>
        <h1 class="text-4xl md:text-6xl font-extrabold text-slate-800 mb-4 tracking-tight">
          基米<span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-pink-500">论坛</span>
        </h1>
        <p class="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
          一个开源的轻量级社区平台，为开发者和技术爱好者提供简洁、高效的交流空间。
        </p>
      </header>

      <!-- 功能特性 -->
      <section class="mb-14">
        <h2 class="text-center text-2xl font-bold text-slate-800 mb-8 flex items-center justify-center gap-2">
          <span>✨</span> 功能特性
        </h2>
        <div class="grid md:grid-cols-3 gap-6">
          <div class="bg-white/40 backdrop-blur-md p-8 rounded-3xl border border-white/50 hover:-translate-y-2 transition-transform duration-300 group">
            <div class="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">📝</div>
            <h3 class="text-xl font-bold text-slate-800 mb-2">内容发布</h3>
            <p class="text-slate-600 text-sm leading-relaxed">
              支持 Markdown 格式的帖子发布与管理，按板块分类浏览，轻松找到感兴趣的内容。
            </p>
          </div>

          <div class="bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-md p-8 rounded-3xl border border-white/60 transform md:-translate-y-4 shadow-xl relative overflow-hidden group">
            <div class="w-14 h-14 bg-pink-100 rounded-2xl flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">💬</div>
            <h3 class="text-xl font-bold text-slate-800 mb-2">实时通讯</h3>
            <p class="text-slate-600 text-sm leading-relaxed">
              基于 WebSocket 的即时私信与通知系统，消息零延迟，沟通无障碍。
            </p>
          </div>

          <div class="bg-white/40 backdrop-blur-md p-8 rounded-3xl border border-white/50 hover:-translate-y-2 transition-transform duration-300 group">
            <div class="w-14 h-14 bg-orange-100 rounded-2xl flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">🤝</div>
            <h3 class="text-xl font-bold text-slate-800 mb-2">社交互动</h3>
            <p class="text-slate-600 text-sm leading-relaxed">
              好友系统、关注动态、表情搜索，构建活跃的社区氛围，让交流更有趣。
            </p>
          </div>
        </div>
      </section>

      <!-- 技术栈 -->
      <section class="mb-14">
        <h2 class="text-center text-2xl font-bold text-slate-800 mb-8 flex items-center justify-center gap-2">
          <span>⚡</span> 驱动本站的技术栈
        </h2>
        <div class="bg-white/30 backdrop-blur-xl rounded-3xl p-8 border border-white/50">
          <div class="flex flex-wrap justify-center gap-6 md:gap-10">
            <div v-for="tech in techStack" :key="tech.name" class="flex flex-col items-center gap-2 group cursor-pointer">
              <div class="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl group-hover:scale-110 transition-transform" :class="tech.color">
                {{ tech.emoji }}
              </div>
              <span class="text-xs font-bold text-slate-500">{{ tech.name }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 项目信息 -->
      <section class="mb-14">
        <h2 class="text-center text-2xl font-bold text-slate-800 mb-8 flex items-center justify-center gap-2">
          <span>📋</span> 项目信息
        </h2>
        <div class="bg-white/40 backdrop-blur-xl rounded-3xl border border-white/50 overflow-hidden">
          <div class="divide-y divide-white/30">
            <div v-for="item in projectInfo" :key="item.label" class="flex justify-between items-center px-8 py-5">
              <span class="text-sm text-slate-500 font-medium">{{ item.label }}</span>
              <span class="text-sm font-bold text-slate-800">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 底部链接 -->
      <div class="text-center py-8">
        <p class="text-slate-500 font-medium mb-6">加入我们，一起交流技术！</p>
        <div class="flex justify-center gap-6">
          <a href="#" class="px-4 py-2 rounded-full bg-slate-800 text-white text-sm font-bold hover:bg-slate-700 transition-colors flex items-center gap-2">
            <span class="text-xl">👾</span> GitHub
          </a>
          <a href="#" class="px-4 py-2 rounded-full bg-pink-500 text-white text-sm font-bold hover:bg-pink-600 transition-colors flex items-center gap-2">
            <span class="text-xl">📺</span> Bilibili
          </a>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import appheader from '../components/appheader.vue'

const techStack = [
  { emoji: 'V', name: 'Vue 3', color: 'text-green-500' },
  { emoji: '⚡', name: 'Vite', color: 'text-purple-500' },
  { emoji: '🎐', name: 'Tailwind', color: 'text-blue-400' },
  { emoji: '🐍', name: 'Flask', color: 'text-slate-700' },
  { emoji: '🔑', name: 'JWT', color: 'text-yellow-500' },
]

const projectInfo = [
  { label: '版本', value: 'v2.1.0' },
  { label: '前端框架', value: 'Vue 3 + Vite + Tailwind CSS' },
  { label: '后端框架', value: 'Flask + SQLAlchemy + SocketIO' },
  { label: '数据库', value: 'SQLite' },
  { label: '实时通信', value: 'WebSocket (Socket.IO)' },
]
</script>
