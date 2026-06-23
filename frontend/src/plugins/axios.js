import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 10000
})

// 请求拦截器：自动带 Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token && token !== 'undefined' && token !== 'null') {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data || {}

      // 401 / 422 → 登录过期，清理并跳转
      if (status === 401 || status === 422) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        // 避免在登录页循环跳转
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }

      // 把后端 message 挂到 error 上，方便组件使用
      error._message = data.message || `请求失败 (${status})`
    } else if (error.request) {
      error._message = '网络连接失败，请检查网络'
    } else {
      error._message = '请求发送失败'
    }
    return Promise.reject(error)
  }
)

export default api
