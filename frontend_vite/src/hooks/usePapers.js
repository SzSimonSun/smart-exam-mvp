import { useState, useEffect } from 'react'
import { message } from 'antd'
import api from './api'

// 试卷管理Hook
export const usePapers = (filters = {}) => {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  })

  const fetchPapers = async (params = {}) => {
    setLoading(true)
    try {
      const queryParams = {
        page: pagination.current,
        size: pagination.pageSize,
        ...filters,
        ...params
      }
      
      const response = await api.get('/api/papers', { params: queryParams })
      setPapers(response.data)
      
      // 更新分页信息
      if (response.headers['x-total-count']) {
        setPagination(prev => ({
          ...prev,
          total: parseInt(response.headers['x-total-count'])
        }))
      }
    } catch (error) {
      console.error('获取试卷列表失败:', error)
      message.error('获取试卷列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 创建试卷
  const createPaper = async (paperData) => {
    try {
      const response = await api.post('/api/papers', paperData)
      message.success('试卷创建成功！')
      
      // 刷新列表
      await fetchPapers()
      
      return response.data
    } catch (error) {
      console.error('创建试卷失败:', error)
      message.error('创建试卷失败')
      throw error
    }
  }

  // 更新试卷
  const updatePaper = async (id, paperData) => {
    try {
      const response = await api.put(`/api/papers/${id}`, paperData)
      message.success('试卷更新成功！')
      
      // 刷新列表
      await fetchPapers()
      
      return response.data
    } catch (error) {
      console.error('更新试卷失败:', error)
      message.error('更新试卷失败')
      throw error
    }
  }

  // 删除试卷
  const deletePaper = async (id) => {
    try {
      await api.delete(`/api/papers/${id}`)
      message.success('试卷删除成功！')
      
      // 刷新列表
      await fetchPapers()
    } catch (error) {
      console.error('删除试卷失败:', error)
      message.error('删除试卷失败')
      throw error
    }
  }

  // 导出试卷PDF
  const exportPaper = async (id, options = {}) => {
    try {
      const response = await api.post(`/api/papers/${id}/export`, options, {
        responseType: 'blob'
      })
      
      // 创建下载链接
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `试卷_${id}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      message.success('试卷导出成功！')
    } catch (error) {
      console.error('导出试卷失败:', error)
      message.error('导出试卷失败')
      throw error
    }
  }

  // 复制试卷
  const duplicatePaper = async (id) => {
    try {
      const response = await api.post(`/api/papers/${id}/duplicate`)
      message.success('试卷复制成功！')
      
      // 刷新列表
      await fetchPapers()
      
      return response.data
    } catch (error) {
      console.error('复制试卷失败:', error)
      message.error('复制试卷失败')
      throw error
    }
  }

  useEffect(() => {
    fetchPapers()
  }, [pagination.current, pagination.pageSize, JSON.stringify(filters)])

  return {
    papers,
    loading,
    pagination,
    fetchPapers,
    createPaper,
    updatePaper,
    deletePaper,
    exportPaper,
    duplicatePaper,
    setPagination
  }
}

// 获取单个试卷详情的Hook
export const usePaper = (id) => {
  const [paper, setPaper] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchPaper = async () => {
    if (!id) return
    
    setLoading(true)
    try {
      const response = await api.get(`/api/papers/${id}`)
      setPaper(response.data)
    } catch (error) {
      console.error('获取试卷详情失败:', error)
      message.error('获取试卷详情失败')
    } finally {
      setLoading(false)
    }
  }

  const updatePaperQuestions = async (questions) => {
    try {
      const response = await api.put(`/api/papers/${id}/questions`, { questions })
      message.success('试卷题目更新成功！')
      
      // 刷新试卷详情
      await fetchPaper()
      
      return response.data
    } catch (error) {
      console.error('更新试卷题目失败:', error)
      message.error('更新试卷题目失败')
      throw error
    }
  }

  useEffect(() => {
    fetchPaper()
  }, [id])

  return {
    paper,
    loading,
    refetch: fetchPaper,
    updatePaperQuestions
  }
}

// 试卷预览Hook
export const usePaperPreview = (id) => {
  const [previewData, setPreviewData] = useState(null)
  const [loading, setLoading] = useState(false)

  const generatePreview = async () => {
    if (!id) return
    
    setLoading(true)
    try {
      const response = await api.get(`/api/papers/${id}/preview`)
      setPreviewData(response.data)
    } catch (error) {
      console.error('生成试卷预览失败:', error)
      message.error('生成试卷预览失败')
    } finally {
      setLoading(false)
    }
  }

  return {
    previewData,
    loading,
    generatePreview
  }
}