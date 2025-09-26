import { useState, useEffect } from 'react'
import { message } from 'antd'
import api from './api'

// 拆题入库Hook
export const useIngest = (filters = {}) => {
  const [ingestSessions, setIngestSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  })

  const fetchIngestSessions = async (params = {}) => {
    setLoading(true)
    try {
      const queryParams = {
        page: pagination.current,
        size: pagination.pageSize,
        ...filters,
        ...params
      }
      
      const response = await api.get('/api/ingest/sessions', { params: queryParams })
      setIngestSessions(response.data)
      
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
      setLoading(false)
    }
  }

  // 创建拆题会话
  const createIngestSession = async (sessionData) => {
    try {
      const response = await api.post('/api/ingest/sessions', sessionData)
      message.success('拆题会话创建成功！')
      
      // 刷新列表
      await fetchIngestSessions()
      
      return response.data
    } catch (error) {
      console.error('创建拆题会话失败:', error)
      message.error('创建拆题会话失败')
      throw error
    }
  }

  useEffect(() => {
    fetchIngestSessions()
  }, [pagination.current, pagination.pageSize, JSON.stringify(filters)])

  return {
    ingestSessions,
    loading,
    pagination,
    fetchIngestSessions,
    createIngestSession,
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