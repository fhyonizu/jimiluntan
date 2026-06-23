<template>
  <router-view v-slot="{ Component, route }">
    <transition name="page" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>

  <UserProfileModal ref="profileModal" @chat="handleChat" />
  <ChatWidget v-if="authStore.isLoggedIn" ref="chatWidget" />

  <!-- 全局路由消息 toast -->
  <transition name="toast">
    <div v-if="globalMsg" class="fixed top-8 left-1/2 -translate-x-1/2 z-[9999] flex items-center gap-3 px-6 py-3 bg-red-500/90 text-white rounded-full shadow-2xl backdrop-blur-md whitespace-nowrap pointer-events-none">
      <span class="text-xl">⚠️</span>
      <span class="font-bold text-sm tracking-wide">{{ globalMsg }}</span>
    </div>
  </transition>
</template>

<script setup>
import { ref, provide, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/plugins/auth'
import UserProfileModal from '@/components/UserProfileModal.vue'
import ChatWidget from '@/components/ChatWidget.vue'

const authStore = useAuthStore()
const route = useRoute()
const profileModal = ref(null)
const chatWidget = ref(null)
const globalMsg = ref('')

// 监听路由 query.msg
watch(() => route.query.msg, (msg) => {
  if (msg) {
    globalMsg.value = msg
    setTimeout(() => { globalMsg.value = '' }, 3000)
  }
}, { immediate: true })

const openProfile = (userId) => {
  profileModal.value?.open(userId)
}
provide('openProfile', openProfile)

const openChatWidget = (user) => {
  if (chatWidget.value) {
    chatWidget.value.open(user)
  }
}
provide('openChatWidget', openChatWidget)

const handleChat = (user) => {
  openChatWidget(user)
}
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 400ms var(--ease-spring); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, -16px) scale(0.9); }
</style>
