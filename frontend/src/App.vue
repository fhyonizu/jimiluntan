<template>
  <!-- 路由视图 + Apple-Style 页面过渡 -->
  <router-view v-slot="{ Component, route }">
    <transition name="page" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
  
  <!-- 全局挂载组件 -->
  <UserProfileModal ref="profileModal" @chat="handleChat" />
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