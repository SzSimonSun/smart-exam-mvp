import { useState, useEffect } from 'react'
import { message } from 'antd'
import api from './api'

// 学生统计数据Hook
export const useStats = (studentId, filters = {}) => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [knowledgePointStats, setKnowledgePointStats] = useState([])

  const fetchStats = async (params = {}) => {
    if (!studentId) return

    setLoading(true)
    try {
      const queryParams = {
        ...filters,
        ...params
      }
      
      const response = await api.get(`/api/students/${studentId}/stats`, { params: queryParams })
      setStats(response.data)
    } catch (error) {
      console.error('获取学生统计失败:', error)
      message.error('获取学生统计失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取知识点掌握度统计
  const fetchKnowledgePointStats = async (params = {}) => {
    if (!studentId) return

    try {
      const queryParams = {
        ...filters,
        ...params
      }
      
      const response = await api.get(`/api/students/${studentId}/knowledge-points/stats`, { params: queryParams })
      setKnowledgePointStats(response.data)
    } catch (error) {
      console.error('获取知识点统计失败:', error)
      message.error('获取知识点统计失败')
    }
  }

  useEffect(() => {
    if (studentId) {
      fetchStats()
      fetchKnowledgePointStats()
    }
  }, [studentId, JSON.stringify(filters)])

  return {
    stats,
    knowledgePointStats,
    loading,
    refetch: fetchStats,
    refetchKnowledgePointStats: fetchKnowledgePointStats
  }
}

// 班级统计Hook
export const useClassStats = (classId, filters = {}) => {
  const [classStats, setClassStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [studentRanking, setStudentRanking] = useState([])

  const fetchClassStats = async (params = {}) => {
    if (!classId) return

    setLoading(true)
    try {
      const queryParams = {
        ...filters,
        ...params
      }
      
      const response = await api.get(`/api/classes/${classId}/stats`, { params: queryParams })
      setClassStats(response.data)
    } catch (error) {
      console.error('获取班级统计失败:', error)
      message.error('获取班级统计失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取学生排名
  const fetchStudentRanking = async (params = {}) => {
    if (!classId) return

    try {
      const queryParams = {
        ...filters,
        ...params
      }
      
      const response = await api.get(`/api/classes/${classId}/ranking`, { params: queryParams })
      setStudentRanking(response.data)
    } catch (error) {
      console.error('获取学生排名失败:', error)
      message.error('获取学生排名失败')
    }
  }

  useEffect(() => {
    if (classId) {
      fetchClassStats()
      fetchStudentRanking()
    }
  }, [classId, JSON.stringify(filters)])

  return {
    classStats,
    studentRanking,
    loading,
    refetch: fetchClassStats,
    refetchStudentRanking: fetchStudentRanking
  }
}

// 错题本Hook
export const useWrongBook = (studentId, filters = {}) => {
  const [wrongQuestions, setWrongQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })

  const fetchWrongQuestions = async (params = {}) => {
    if (!studentId) return

    setLoading(true)
    try {
      const queryParams = {
        page: pagination.current,
        size: pagination.pageSize,
        ...filters,
        ...params
      }
      
      const response = await api.get(`/api/students/${studentId}/wrong-book`, { params: queryParams })
      setWrongQuestions(response.data)
      
      if (response.headers['x-total-count']) {
        setPagination(prev => ({
          ...prev,
          total: parseInt(response.headers['x-total-count'])
        }))
      }
    } catch (error) {
      console.error('获取错题本失败:', error)
      message.error('获取错题本失败')
    } finally {
      setLoading(false)
    }
  }

  // 标记错题为已掌握
  const markAsMastered = async (questionId) => {
    try {
      await api.post(`/api/students/${studentId}/wrong-book/${questionId}/master`)
      message.success('标记成功！')
      
      // 刷新错题列表
      await fetchWrongQuestions()
    } catch (error) {
      console.error('标记失败:', error)
      message.error('标记失败')
      throw error
    }
  }

  useEffect(() => {
    if (studentId) {
      fetchWrongQuestions()
    }
  }, [studentId, pagination.current, pagination.pageSize, JSON.stringify(filters)])

  return {
    wrongQuestions,
    loading,
    pagination,
    fetchWrongQuestions,
    markAsMastered,
    setPagination
  }
}

// 学习报告Hook
export const useStudyReport = (studentId, reportType = 'monthly') => {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)

  const generateReport = async (params = {}) => {
    if (!studentId) return

    setLoading(true)
    try {
      const queryParams = {
        type: reportType,
        ...params
      }
      
      const response = await api.get(`/api/students/${studentId}/report`, { params: queryParams })
      setReport(response.data)
    } catch (error) {
      console.error('生成学习报告失败:', error)
      message.error('生成学习报告失败')
    } finally {
      setLoading(false)
    }
  }

  // 导出报告
  const exportReport = async (format = 'pdf') => {
    if (!studentId) return

    try {
      const response = await api.get(`/api/students/${studentId}/report/export`, {
        params: { format, type: reportType },
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data], { 
        type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `学习报告_${studentId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      message.success('报告导出成功！')
    } catch (error) {
      console.error('导出报告失败:', error)
      message.error('导出报告失败')
      throw error
    }
  }

  return {
    report,
    loading,
    generateReport,
    exportReport
  }
}