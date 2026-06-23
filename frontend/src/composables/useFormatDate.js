/**
 * 统一日期格式化 composable
 */
export function useFormatDate() {
  /**
   * 格式化为日期 (YYYY/M/D)
   */
  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString()
  }

  /**
   * 智能相对时间 (刚刚 / x分钟前 / x小时前 / x天前 / 日期)
   */
  const formatTimeAgo = (dateStr) => {
    if (!dateStr) return ''
    const now = Date.now()
    const d = new Date(dateStr).getTime()
    const diff = Math.floor((now - d) / 1000)
    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
    if (diff < 2592000) return `${Math.floor(diff / 86400)} 天前`
    return new Date(dateStr).toLocaleDateString()
  }

  /**
   * 格式化为时间 (HH:MM)
   */
  const formatTime = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  /**
   * 格式化为日期+时间
   */
  const formatDateTime = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleString()
  }

  return { formatDate, formatTimeAgo, formatTime, formatDateTime }
}
