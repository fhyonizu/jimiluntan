<template>
  <!-- 
    核心修复：
    1. fixed: 即使放在其他组件内部，也会相对于整个屏幕定位。
    2. z-[9999]: 确保它浮在所有内容（包括导航栏、模态框）之上。
    3. top-8: 距离屏幕顶部 32px。
  -->
  <transition name="toast">
    <div v-if="visible" 
      class="fixed top-8 left-1/2 -translate-x-1/2 z-[9999] flex items-center gap-3 px-6 py-3 bg-slate-800/90 text-white rounded-full shadow-2xl border border-slate-700 backdrop-blur-md min-w-fit whitespace-nowrap pointer-events-none"
    >
      <!-- 动态图标 -->
      <span class="text-xl">{{ icon }}</span>
      <span class="font-bold text-sm tracking-wide">{{ text }}</span>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const text = ref('')
const icon = ref('🔔')

// 暴露给父组件的方法
const showMessage = (msg) => {
  text.value = msg
  visible.value = true
  
  // 简单的智能图标判断
  if (msg.includes('成功')) icon.value = '🎉'
  else if (msg.includes('失败') || msg.includes('错误') || msg.includes('空')) icon.value = '💔'
  else if (msg.includes('网络')) icon.value = '🔌'
  else icon.value = '🔔'

  // 3秒后自动消失
  setTimeout(() => {
    visible.value = false
  }, 3000)
}

defineExpose({ showMessage })
</script>

<style scoped>
/* 弹跳动画效果 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px) scale(0.9);
}
</style>