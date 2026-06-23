import api from '@/plugins/axios'

// Auth
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
}

// Posts
export const postsApi = {
  list: (params) => api.get('/api/posts/', { params }),
  detail: (id) => api.get(`/api/posts/${id}`),
  create: (data) => api.post('/api/posts/', data),
  update: (id, data) => api.put(`/api/posts/${id}`, data),
  delete: (id) => api.delete(`/api/posts/${id}`),
  search: (params) => api.get('/api/posts/search', { params }),
  categories: () => api.get('/api/posts/categories'),
  addComment: (postId, data) => api.post(`/api/posts/${postId}/comments`, data),
  editComment: (postId, commentId, data) => api.put(`/api/posts/${postId}/comments/${commentId}`, data),
  deleteComment: (postId, commentId) => api.delete(`/api/posts/${postId}/comments/${commentId}`),
  like: (postId) => api.post(`/api/posts/${postId}/like`),
  likeStatus: (postId) => api.get(`/api/posts/${postId}/like`),
}

// Social
export const socialApi = {
  userProfile: (userId) => api.get(`/api/social/user/${userId}`),
  search: (q) => api.get('/api/social/search', { params: { q } }),
  friends: () => api.get('/api/social/friends'),
  friendRequests: () => api.get('/api/social/friend/requests'),
  addFriend: (data) => api.post('/api/social/friend/request', data),
  respondFriend: (data) => api.post('/api/social/friend/respond', data),
  sendMessage: (data) => api.post('/api/social/message/send', data),
  markRead: (data) => api.post('/api/social/message/read', data),
  chatHistory: (partnerId) => api.get(`/api/social/messages/${partnerId}`),
  follow: (userId) => api.post(`/api/social/follow/${userId}`),
  followStatus: (userId) => api.get(`/api/social/follow/${userId}`),
}

// Users
export const usersApi = {
  me: () => api.get('/api/users/me'),
  updateMe: (data) => api.put('/api/users/me', data),
}

// Admin
export const adminApi = {
  stats: () => api.get('/api/admin/stats'),
  categories: () => api.get('/api/admin/categories'),
  addCategory: (data) => api.post('/api/admin/categories', data),
  deleteCategory: (id) => api.delete(`/api/admin/categories/${id}`),
  users: (params) => api.get('/api/admin/users', { params }),
  deleteUser: (id) => api.delete(`/api/admin/users/${id}`),
  posts: (params) => api.get('/api/admin/posts', { params }),
  deletePost: (id) => api.delete(`/api/admin/posts/${id}`),
  comments: (params) => api.get('/api/admin/comments', { params }),
  deleteComment: (id) => api.delete(`/api/admin/comments/${id}`),
  // 系统升级
  systemInfo: () => api.get('/api/admin/system/info'),
  checkUpdate: () => api.get('/api/admin/system/check-update'),
  doUpgrade: () => api.post('/api/admin/system/upgrade'),
}

// Main
export const mainApi = {
  upload: (formData) => api.post('/api/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  stats: () => api.get('/api/stats'),
  notices: () => api.get('/api/notices'),
  gifs: (params) => api.get('/api/gifs', { params }),
}
