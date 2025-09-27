// 全局错误处理工具
import { message, Modal } from 'antd'

class ErrorHandler {
  constructor() {
    this.setupGlobalErrorHandlers()
  }

  setupGlobalErrorHandlers() {
    // 捕获未处理的Promise错误
    window.addEventListener('unhandledrejection', (event) => {
      console.error('🚨 未处理的Promise错误:', event.reason)
      this.handleError(event.reason)
      // 阻止默认的错误处理
      event.preventDefault()
    })

    // 捕获全局JavaScript错误
    window.addEventListener('error', (event) => {
      console.error('🚨 全局JavaScript错误:', event.error)
      this.handleError(event.error)
    })

    // 捕获React错误边界无法捕获的错误
    const originalConsoleError = console.error
    console.error = (...args) => {
      const errorMessage = args.join(' ')
      if (errorMessage.includes('message port closed')) {
        this.handleMessagePortError()
      }
      originalConsoleError.apply(console, args)
    }
  }

  handleError(error) {
    if (!error) return

    const errorMessage = error.message || error.toString()

    // 处理"message port closed"错误
    if (errorMessage.includes('message port closed')) {
      this.handleMessagePortError()
      return
    }

    // 处理网络超时错误
    if (errorMessage.includes('timeout') || error.code === 'ECONNABORTED') {
      message.error('请求超时，请检查网络连接后重试')
      return
    }

    // 处理网络连接错误
    if (errorMessage.includes('Network Error') || errorMessage.includes('Failed to fetch')) {
      message.error('网络连接失败，请检查网络后重试')
      return
    }

    // 其他未知错误
    console.error('未处理的错误:', error)
  }

  handleMessagePortError() {
    // 避免重复显示错误对话框
    if (this.messagePortErrorShown) return
    this.messagePortErrorShown = true

    Modal.error({
      title: '🔌 连接错误',
      content: '检测到浏览器扩展冲突或连接问题。常见解决方案：\n\n1. 禁用所有浏览器扩展后重试\n2. 使用无痕/隐私浏览模式\n3. 清除浏览器缓存和Cookie\n4. 刷新页面重新加载\n\n注：此错误通常由浏览器扩展程序引起，特别是广告拦截器、开发者工具扩展等',
      width: 480,
      onOk: () => {
        this.messagePortErrorShown = false
        // 询问用户是否要刷新页面
        Modal.confirm({
          title: '刷新页面',
          content: '是否刷新页面以重新加载应用？',
          onOk: () => {
            window.location.reload()
          },
          onCancel: () => {
            message.info('如果问题持续，请尝试禁用浏览器扩展')
          }
        })
      }
    })
  }

  // 手动触发错误处理（用于API调用）
  static handleApiError(error) {
    const instance = new ErrorHandler()
    instance.handleError(error)
  }

  // 为API请求提供重试机制
  static async retryApiCall(apiCall, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await apiCall()
      } catch (error) {
        console.warn(`API调用失败，第${i + 1}次重试:`, error.message)
        
        if (i === maxRetries - 1) {
          // 最后一次重试失败，抛出错误
          this.handleApiError(error)
          throw error
        }
        
        // 等待后重试
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
      }
    }
  }
}

// 创建全局实例
const globalErrorHandler = new ErrorHandler()

export default ErrorHandler
export { globalErrorHandler }