import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  // 确保这里是你的后端地址
  baseURL: 'http://8.153.108.114:5000', 
  timeout: 10000 // 请求超时时间
})

// 🟢 请求拦截器：每次发请求前，自动带上 Token
api.interceptors.request.use(
  (config) => {
    // 从本地存储获取 token
    const token = localStorage.getItem('token')
    
    // 只有当 token 存在，且不是 "undefined" 这种脏数据时，才添加
    if (token && token !== 'undefined' && token !== 'null') {
      // 注意：Flask-JWT-Extended 默认要求格式为 "Bearer <token>"
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 🔴 响应拦截器：统一处理错误
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 如果后端返回 401 (未授权) 或 422 (Token无效)，强制退出
    if (error.response && (error.response.status === 401 || error.response.status === 422)) {
      console.warn('登录过期或 Token 无效，正在清理...')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 可选：强制跳转回登录页
      // window.location.href = '/login' 
    }
    return Promise.reject(error)
  }
)

export default api