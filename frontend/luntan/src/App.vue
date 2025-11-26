<template>
  <!-- 路由视图 -->
  <router-view v-slot="{ Component }">
    <component :is="Component" />
  </router-view>
  
  <!-- 全局挂载组件 -->
  <!-- 1. 用户资料弹窗 -->
  <UserProfileModal ref="profileModal" @chat="handleChat" />
  
  <!-- 2. 🔥 悬浮聊天球/窗口 (只有登录才显示) -->
  <!-- 注意：这里引用的是 ChatWidget，不是 ChatWindow -->
  <ChatWidget v-if="authStore.isLoggedIn" ref="chatWidget" />
</template>

<script setup>
import { ref, provide } from 'vue'
import { useAuthStore } from '@/plugins/auth'
import UserProfileModal from '@/components/UserProfileModal.vue'
import ChatWidget from '@/components/ChatWidget.vue' // 🔥 确保引入的是这个新组件

const authStore = useAuthStore()
const profileModal = ref(null)
const chatWidget = ref(null)

// --- 提供全局方法 (Provide) ---

// 1. 打开用户资料卡
const openProfile = (userId) => {
  profileModal.value?.open(userId)
}
provide('openProfile', openProfile)

// 2. 🔥 打开聊天窗口 (修复 Friends.vue 的报错)
const openChatWidget = (user) => {
  if (chatWidget.value) {
    chatWidget.value.open(user)
  } else {
    console.warn("聊天组件尚未加载，请确保已登录")
  }
}
provide('openChatWidget', openChatWidget)

// --- 事件处理 ---

// 当在资料卡里点击“私聊”时
const handleChat = (user) => {
  openChatWidget(user)
}
</script>