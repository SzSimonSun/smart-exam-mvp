import React, { createContext, useContext, useState, useEffect } from 'react'
import { message } from 'antd'
import api from './api'

const AuthContext = createContext(undefined)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)
  const [isInitialized, setIsInitialized] = useState(false)

  console.log('🔐 AuthProvider:', { 
    token: token ? '已存在' : '无', 
    user: user?.name || '未登录', 
    loading, 
    initialized: isInitialized 
  })

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const response = await api.get('/api/users/me')
      console.log('✅ 用户登录成功:', response.data.name || response.data.email)
      setUser(response.data)
    } catch (error) {
      console.error('获取用户信息失败:', error.message)
      // Token无效，清除本地存储
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  // 登录
  const login = async (email, password) => {
    try {
      setLoading(true)
      console.log('🚀 开始登录请求:', email)
      
      const response = await api.post('/api/auth/login', { email, password })
      const { access_token } = response.data
      console.log('✅ 登录API调用成功')

      // 设置 token
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // 获取用户信息
      console.log('🚀 获取用户信息...')
      const userResponse = await api.get('/api/users/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      })
      
      console.log('✅ 用户信息获取成功:', userResponse.data.name || userResponse.data.email)
      setUser(userResponse.data)
      
      message.success('登录成功！')
      return true
    } catch (error) {
      console.error('📛 登录失败:', error)
      message.error('登录失败，请检查邮箱和密码')
      return false
    } finally {
      setLoading(false)
      console.log('🏁 登录流程结束')
    }
  }

  // 登出
  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    message.success('已退出登录')
  }

  // 初始化时检查token并获取用户信息
  useEffect(() => {
    // 防止重复初始化
    if (isInitialized) return
    
    const initAuth = async () => {
      // 如果没有token，直接设置loading为false
      if (!token) {
        console.log('没有token，跳过API调用')
        setLoading(false)
        setIsInitialized(true)
        return
      }
      
      // 有token时才调用API
      await fetchCurrentUser()
      setIsInitialized(true)
    }
    
    initAuth()
  }, []) // 只在组件挂载时执行一次

  const value = {
    user,
    token,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// 使用认证的Hook
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}