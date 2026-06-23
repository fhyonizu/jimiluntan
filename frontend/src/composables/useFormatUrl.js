import api from '@/plugins/axios'

/**
 * 统一 URL 格式化 composable
 * 把后端返回的相对路径 (/static/uploads/xxx) 转为完整 URL
 */
export function useFormatUrl() {
  const formatUrl = (path) => {
    if (!path) return ''
    if (path.startsWith('http://') || path.startsWith('https://')) return path
    const baseUrl = api.defaults.baseURL || ''
    const origin = baseUrl.replace(/\/api\/?$/, '')
    return `${origin}${path}`
  }

  return { formatUrl }
}
