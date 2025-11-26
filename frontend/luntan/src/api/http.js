// src/api/http.js
import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:5000', // 也可以用 Vite 代理时写成 '/api'
  timeout: 10000,
})

// 请求拦截器：每个请求都自动带上 Authorization 头
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：如果后端返回 401，可以在这里做统一处理
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // token 过期/无效，清理并跳转登录
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default instance
