import { useState, useEffect } from 'react'
import { message } from 'antd'
import api from './api'

// 获取题目列表的Hook
export const useQuestions = (filters = {}) => {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })

  const fetchQuestions = async (params = {}) => {
    setLoading(true)
    try {
      const queryParams = {
        page: pagination.current,
        size: pagination.pageSize,
        ...filters,
        ...params
      }
      
      const response = await api.get('/api/questions', { params: queryParams })
      setQuestions(response.data)
      
      // 如果后端返回总数，更新分页信息
      if (response.headers['x-total-count']) {
        setPagination(prev => ({
          ...prev,
          total: parseInt(response.headers['x-total-count'])
        }))
      }
    } catch (error) {
      console.error('获取题目列表失败:', error)
      message.error('获取题目列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 创建题目
  const createQuestion = async (questionData) => {
    try {
      const response = await api.post('/api/questions', questionData)
      message.success('题目创建成功！')
      
      // 刷新列表
      await fetchQuestions()
      
      return response.data
    } catch (error) {
      console.error('创建题目失败:', error)
      message.error('创建题目失败')
      throw error
    }
  }

  // 更新题目
  const updateQuestion = async (id, questionData) => {
    try {
      const response = await api.put(`/api/questions/${id}`, questionData)
      message.success('题目更新成功！')
      
      // 刷新列表
      await fetchQuestions()
      
      return response.data
    } catch (error) {
      console.error('更新题目失败:', error)
      message.error('更新题目失败')
      throw error
    }
  }

  // 删除题目
  const deleteQuestion = async (id) => {
    try {
      await api.delete(`/api/questions/${id}`)
      message.success('题目删除成功！')
      
      // 刷新列表
      await fetchQuestions()
    } catch (error) {
      console.error('删除题目失败:', error)
      message.error('删除题目失败')
      throw error
    }
  }

  // 发布题目
  const publishQuestion = async (id) => {
    try {
      await api.post(`/api/questions/${id}/publish`)
      message.success('题目发布成功！')
      
      // 刷新列表
      await fetchQuestions()
    } catch (error) {
      console.error('发布题目失败:', error)
      message.error('发布题目失败')
      throw error
    }
  }

  // 分页改变处理
  const handlePaginationChange = (page, pageSize) => {
    setPagination(prev => ({
      ...prev,
      current: page,
      pageSize: pageSize
    }))
  }

  // 初始加载和依赖更新
  useEffect(() => {
    fetchQuestions()
  }, [pagination.current, pagination.pageSize, JSON.stringify(filters)])

  return {
    questions,
    loading,
    pagination,
    fetchQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    publishQuestion,
    handlePaginationChange
  }
}

// 获取单个题目详情的Hook
export const useQuestion = (id) => {
  const [question, setQuestion] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchQuestion = async () => {
    if (!id) return
    
    setLoading(true)
    try {
      const response = await api.get(`/api/questions/${id}`)
      setQuestion(response.data)
    } catch (error) {
      console.error('获取题目详情失败:', error)
      message.error('获取题目详情失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQuestion()
  }, [id])

  return {
    question,
    loading,
    refetch: fetchQuestion
  }
}