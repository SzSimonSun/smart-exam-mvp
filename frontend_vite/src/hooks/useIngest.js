import { useState, useEffect, useCallback } from 'react'
import { message } from 'antd'
import api from './api'

// 拆题入库Hook
export const useIngest = (filters = {}) => {
  const [sessions, setSessions] = useState([])
  const [sessionLoading, setSessionLoading] = useState(false)
  const [items, setItems] = useState([])
  const [itemsLoading, setItemsLoading] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  })

  const fetchIngestSessions = useCallback(async (params = {}) => {
    setSessionLoading(true)
    try {
      const queryParams = {
        page: pagination.current,
        size: pagination.pageSize,
        ...filters,
        ...params
      }
      
      const response = await api.get('/api/ingest/sessions', { params: queryParams })
      setSessions(response.data || [])
      
      if (response.headers['x-total-count']) {
        setPagination(prev => ({
          ...prev,
          total: parseInt(response.headers['x-total-count'])
        }))
      }
    } catch (error) {
      console.error('获取拆题会话列表失败:', error)
      message.error('获取拆题会话列表失败')
    } finally {
      setSessionLoading(false)
    }
  }, [pagination.current, pagination.pageSize, JSON.stringify(filters)])

  // 获取拆题项目列表
  const fetchIngestItems = useCallback(async (sessionId) => {
    if (!sessionId) return []
    
    setItemsLoading(true)
    try {
      const response = await api.get(`/api/ingest/sessions/${sessionId}/items`)
      const itemsData = response.data || []
      setItems(itemsData)
      return itemsData
    } catch (error) {
      console.error('获取拆题项目失败:', error)
      message.error('获取拆题项目失败')
      return []
    } finally {
      setItemsLoading(false)
    }
  }, [])

  // 创建拆题会话（上传文件）
  const createIngestSession = useCallback(async (file, options = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    
    // 添加其他选项
    Object.keys(options).forEach(key => {
      formData.append(key, options[key])
    })

    try {
      const response = await api.post('/api/ingest/sessions', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      message.success('拆题会话创建成功！')
      
      // 刷新列表
      await fetchIngestSessions()
      
      return response.data
    } catch (error) {
      console.error('创建拆题会话失败:', error)
      message.error('创建拆题会话失败')
      throw error
    }
  }, [fetchIngestSessions])

  // 审核通过
  const approveIngestItem = useCallback(async (itemId, approvalData = {}) => {
    try {
      console.log('📄 开始审核通过:', itemId, approvalData)
      const response = await api.post(`/api/ingest/items/${itemId}/approve`, approvalData, {
        timeout: 30000 // 30秒超时
      })
      console.log('✅ 审核通过成功:', response.data)
      message.success('审核通过！')
      return response.data
    } catch (error) {
      console.error('📛 审核通过失败:', error)
      
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        message.error('审核请求超时，请稍后再试')
      } else if (error.message.includes('message port closed')) {
        message.error('连接中断，请刷新页面后再试')
      } else {
        message.error('审核通过失败')
      }
      throw error
    }
  }, [])

  // 驳回
  const rejectIngestItem = useCallback(async (itemId, rejectionData = {}) => {
    try {
      console.log('📛 开始驳回:', itemId, rejectionData)
      const response = await api.post(`/api/ingest/items/${itemId}/reject`, rejectionData, {
        timeout: 30000 // 30秒超时
      })
      console.log('✅ 驳回成功:', response.data)
      message.success('已驳回！')
      return response.data
    } catch (error) {
      console.error('📛 驳回失败:', error)
      
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        message.error('驳回请求超时，请稍后再试')
      } else if (error.message.includes('message port closed')) {
        message.error('连接中断，请刷新页面后再试')
      } else {
        message.error('驳回失败')
      }
      throw error
    }
  }, [])

  useEffect(() => {
    fetchIngestSessions()
  }, []) // 移除依赖，只在挂载时执行一次

  return {
    sessions,
    sessionLoading,
    items,
    itemsLoading,
    pagination,
    fetchIngestSessions,
    fetchIngestItems,
    createIngestSession,
    approveIngestItem,
    rejectIngestItem,
    setPagination
  }
}

// 单个拆题会话详情Hook
export const useIngestSession = (sessionId) => {
  const [session, setSession] = useState(null)
  const [ingestItems, setIngestItems] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchIngestSession = async () => {
    if (!sessionId) return
    
    setLoading(true)
    try {
      const response = await api.get(`/api/ingest/sessions/${sessionId}`)
      setSession(response.data)
    } catch (error) {
      console.error('获取拆题会话详情失败:', error)
      message.error('获取拆题会话详情失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchIngestItems = async () => {
    if (!sessionId) return
    
    try {
      const response = await api.get(`/api/ingest/sessions/${sessionId}/items`)
      setIngestItems(response.data)
    } catch (error) {
      console.error('获取拆题项目失败:', error)
      message.error('获取拆题项目失败')
    }
  }

  // 审核通过
  const approveIngestItem = async (itemId, approvalData = {}) => {
    try {
      const response = await api.post(`/api/ingest/items/${itemId}/approve`, approvalData)
      message.success('审核通过！')
      
      // 刷新拆题项目列表
      await fetchIngestItems()
      
      return response.data
    } catch (error) {
      console.error('审核通过失败:', error)
      message.error('审核通过失败')
      throw error
    }
  }

  // 驳回
  const rejectIngestItem = async (itemId, rejectionData = {}) => {
    try {
      const response = await api.post(`/api/ingest/items/${itemId}/reject`, rejectionData)
      message.success('已驳回！')
      
      // 刷新拆题项目列表
      await fetchIngestItems()
      
      return response.data
    } catch (error) {
      console.error('驳回失败:', error)
      message.error('驳回失败')
      throw error
    }
  }

  // 批量审核通过
  const batchApprove = async (itemIds, approvalData = {}) => {
    try {
      const response = await api.post('/api/ingest/items/batch-approve', {
        item_ids: itemIds,
        ...approvalData
      })
      message.success(`批量审核通过 ${itemIds.length} 个项目！`)
      
      // 刷新拆题项目列表
      await fetchIngestItems()
      
      return response.data
    } catch (error) {
      console.error('批量审核失败:', error)
      message.error('批量审核失败')
      throw error
    }
  }

  // 批量驳回
  const batchReject = async (itemIds, rejectionData = {}) => {
    try {
      const response = await api.post('/api/ingest/items/batch-reject', {
        item_ids: itemIds,
        ...rejectionData
      })
      message.success(`批量驳回 ${itemIds.length} 个项目！`)
      
      // 刷新拆题项目列表
      await fetchIngestItems()
      
      return response.data
    } catch (error) {
      console.error('批量驳回失败:', error)
      message.error('批量驳回失败')
      throw error
    }
  }

  // 编辑拆题项目
  const editIngestItem = async (itemId, editData) => {
    try {
      const response = await api.put(`/api/ingest/items/${itemId}`, editData)
      message.success('编辑成功！')
      
      // 刷新拆题项目列表
      await fetchIngestItems()
      
      return response.data
    } catch (error) {
      console.error('编辑失败:', error)
      message.error('编辑失败')
      throw error
    }
  }

  // 完成拆题会话
  const completeIngestSession = async () => {
    try {
      const response = await api.post(`/api/ingest/sessions/${sessionId}/complete`)
      message.success('拆题会话已完成！')
      
      // 刷新会话详情
      await fetchIngestSession()
      
      return response.data
    } catch (error) {
      console.error('完成拆题会话失败:', error)
      message.error('完成拆题会话失败')
      throw error
    }
  }

  useEffect(() => {
    if (sessionId) {
      fetchIngestSession()
      fetchIngestItems()
    }
  }, [sessionId])

  return {
    session,
    ingestItems,
    loading,
    fetchIngestSession,
    fetchIngestItems,
    approveIngestItem,
    rejectIngestItem,
    batchApprove,
    batchReject,
    editIngestItem,
    completeIngestSession
  }
}

// 拆题统计Hook
export const useIngestStats = (filters = {}) => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchIngestStats = async (params = {}) => {
    setLoading(true)
    try {
      const queryParams = {
        ...filters,
        ...params
      }
      
      const response = await api.get('/api/ingest/stats', { params: queryParams })
      setStats(response.data)
    } catch (error) {
      console.error('获取拆题统计失败:', error)
      message.error('获取拆题统计失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIngestStats()
  }, [JSON.stringify(filters)])

  return {
    stats,
    loading,
    refetch: fetchIngestStats
  }
}