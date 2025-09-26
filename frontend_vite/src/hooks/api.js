import axios from 'axios'
import { message, notification } from 'antd'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

console.log('🌐 API Base URL:', api.defaults.baseURL)

// 请求拦截器 - 自动添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('🚀 API 请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => {
    // 2xx 范围内的状态码都会触发该函数
    return response
  },
  (error) => {
    // 超出 2xx 范围的状态码都会触发该函数
    console.error('API Error:', error)
    
    if (error.response) {
      // 服务器响应了错误状态码
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          message.error(data?.detail || '请求参数错误')
          break
        case 401:
          message.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          message.error('没有权限访问该资源')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 422:
          // 表单验证错误
          if (data?.detail && Array.isArray(data.detail)) {
            const errorMessages = data.detail.map(err => 
              `${err.loc?.join(' -> ')}: ${err.msg}`
            ).join('\n')
            notification.error({
              message: '表单验证失败',
              description: errorMessages,
              duration: 6
            })
          } else {
            message.error(data?.detail || '数据验证失败')
          }
          break
        case 429:
          message.error('请求过于频繁，请稍后再试')
          break
        case 500:
          notification.error({
            message: '服务器内部错误',
            description: '服务器遇到了问题，请稍后再试或联系管理员',
            duration: 8
          })
          break
        case 502:
        case 503:
        case 504:
          notification.error({
            message: '服务暂时不可用',
            description: '服务器正在维护中，请稍后再试',
            duration: 8
          })
          break
        default:
          message.error(data?.detail || `请求失败 (${status})`)
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      notification.error({
        message: '网络连接失败',
        description: '无法连接到服务器，请检查网络连接或稍后再试',
        duration: 8
      })
    } else {
      // 请求配置出错
      message.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default api