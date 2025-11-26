<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 font-sans selection:bg-pink-200 overflow-hidden relative">
    
    <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
    <div class="absolute top-[20%] right-[-10%] w-96 h-96 bg-yellow-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
    <div class="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>

    <div class="relative z-50">
      <appheader />
    </div>

    <main class="relative z-10 max-w-5xl mx-auto px-6 py-12">
      
      <div class="text-center mb-16 relative">
        <div class="absolute top-0 left-1/2 -translate-x-32 -translate-y-12 text-6xl opacity-20 rotate-[-15deg] animate-pulse">🐾</div>
        
        <div class="inline-block px-4 py-1.5 rounded-full bg-white/60 text-pink-500 text-sm font-bold mb-6 shadow-sm border border-white/50 backdrop-blur-sm animate-bounce-slow">
          🐱 技术宅的猫窝 · 快乐哈基米
        </div>
        <h1 class="text-4xl md:text-6xl font-extrabold text-slate-800 mb-6 tracking-tight">
          打破 <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-pink-500">次元壁</span> 的
          <br class="md:hidden" />
          技术社区
        </h1>
        <p class="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
          左手写代码，右手撸猫。在这里，我们用 Python 吟唱魔法，用 Vue 构建异世界。
        </p>
      </div>

      <div class="grid md:grid-cols-3 gap-6 mb-16">
        <div class="bg-white/40 backdrop-blur-md p-8 rounded-3xl border border-white/50 hover:-translate-y-2 transition-transform duration-300 group">
          <div class="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">💻</div>
          <h3 class="text-xl font-bold text-slate-800 mb-2">硬核技术栈</h3>
          <p class="text-slate-600 text-sm leading-relaxed">
            探讨 Flask 后端架构，深挖 Vue3 响应式原理。不做 CRUD Boy，要做全栈魔法师。
          </p>
        </div>

        <div class="bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-md p-8 rounded-3xl border border-white/60 transform md:-translate-y-4 shadow-xl relative overflow-hidden group">
          <div class="absolute -right-4 -top-4 text-9xl opacity-10 group-hover:opacity-20 transition-opacity">🎌</div>
          <div class="w-14 h-14 bg-pink-100 rounded-2xl flex items-center justify-center text-3xl mb-4 group-hover:rotate-12 transition-transform">🌸</div>
          <h3 class="text-xl font-bold text-slate-800 mb-2">二次元浓度极高</h3>
          <p class="text-slate-600 text-sm leading-relaxed">
            番剧推荐、手办展示、甚至讨论如何用代码生成老婆。这里是绅士们的绝对领域。
          </p>
        </div>

        <div class="bg-white/40 backdrop-blur-md p-8 rounded-3xl border border-white/50 hover:-translate-y-2 transition-transform duration-300 group">
          <div class="w-14 h-14 bg-orange-100 rounded-2xl flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">🐱</div>
          <h3 class="text-xl font-bold text-slate-800 mb-2">哈基米集结</h3>
          <p class="text-slate-600 text-sm leading-relaxed">
            不管你是技术大牛还是萌新小白，在这里都是可爱的哈基米。互帮互助，拒绝戾气。
          </p>
        </div>
      </div>

      <div class="mb-16">
        <h2 class="text-center text-2xl font-bold text-slate-800 mb-8 flex items-center justify-center gap-2">
          <span>⚡</span> 驱动本站的魔法阵
        </h2>
        <div class="bg-white/30 backdrop-blur-xl rounded-3xl p-8 border border-white/50">
          <div class="flex flex-wrap justify-center gap-6 md:gap-10">
            <div class="flex flex-col items-center gap-2 group cursor-pointer">
              <div class="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl group-hover:scale-110 transition-transform text-green-500">
                V
              </div>
              <span class="text-xs font-bold text-slate-500">Vue 3</span>
            </div>
            <div class="flex flex-col items-center gap-2 group cursor-pointer">
              <div class="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl group-hover:scale-110 transition-transform text-purple-500">
                ⚡
              </div>
              <span class="text-xs font-bold text-slate-500">Vite</span>
            </div>
            <div class="flex flex-col items-center gap-2 group cursor-pointer">
              <div class="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl group-hover:scale-110 transition-transform text-blue-400">
                🎐
              </div>
              <span class="text-xs font-bold text-slate-500">Tailwind</span>
            </div>
            <div class="flex flex-col items-center gap-2 group cursor-pointer">
              <div class="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl group-hover:scale-110 transition-transform text-slate-700">
                🐍
              </div>
              <span class="text-xs font-bold text-slate-500">Flask</span>
            </div>
            <div class="flex flex-col items-center gap-2 group cursor-pointer">
              <div class="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl group-hover:scale-110 transition-transform text-yellow-500">
                🔑
              </div>
              <span class="text-xs font-bold text-slate-500">JWT</span>
            </div>
          </div>
          <div class="text-center mt-6 text-sm text-slate-500">
            Deployed with love & caffeine ☕
          </div>
        </div>
      </div>

      <div class="text-center py-8 relative">
        <div class="hajimi-dance text-6xl mb-4 inline-block cursor-pointer hover:animate-spin">
          😸
        </div>
        <p class="text-slate-500 font-medium">加入我们，一起 <span class="line-through">摸鱼</span> 改变世界！</p>
        
        <div class="mt-6 flex justify-center gap-6">
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
</script>

<style scoped>
/* 经典的哈基米跳跃动画 */
@keyframes hajimi-jump {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-10px) rotate(-5deg); }
  50% { transform: translateY(0) rotate(0deg); }
  75% { transform: translateY(-5px) rotate(5deg); }
}

.hajimi-dance {
  animation: hajimi-jump 2s infinite ease-in-out;
}

/* 背景流动 */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes bounce-slow {
  0%, 100% { transform: translateY(-3px); }
  50% { transform: translateY(3px); }
}
.animate-bounce-slow {
  animation: bounce-slow 3s infinite ease-in-out;
}
</style>