import { useState, useEffect } from 'react'
import { message } from 'antd'
import api from './api'

// 获取知识点列表的Hook
export const useKnowledgePoints = (filters = {}) => {
  const [knowledgePoints, setKnowledgePoints] = useState([])
  const [loading, setLoading] = useState(false)
  const [treeData, setTreeData] = useState([])

  const fetchKnowledgePoints = async (params = {}) => {
    setLoading(true)
    try {
      const queryParams = {
        ...filters,
        ...params
      }
      
      const response = await api.get('/api/knowledge-points', { params: queryParams })
      setKnowledgePoints(response.data)
      
      // 将平铺数据转换为树形结构
      const tree = buildTree(response.data)
      setTreeData(tree)
      
    } catch (error) {
      console.error('获取知识点列表失败:', error)
      message.error('获取知识点列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 构建树形结构
  const buildTree = (flatData) => {
    const tree = []
    const subjectMap = {}

    flatData.forEach(item => {
      const { subject, module, point, subskill } = item
      
      // 按学科分组
      if (!subjectMap[subject]) {
        subjectMap[subject] = {
          key: subject,
          title: subject,
          children: {}
        }
        tree.push(subjectMap[subject])
      }

      // 按模块分组
      if (module && !subjectMap[subject].children[module]) {
        subjectMap[subject].children[module] = {
          key: `${subject}-${module}`,
          title: module,
          children: {}
        }
      }

      // 添加知识点
      if (point) {
        const pointKey = `${subject}-${module}-${point}`
        if (!subjectMap[subject].children[module].children[pointKey]) {
          subjectMap[subject].children[module].children[pointKey] = {
            key: pointKey,
            title: point,
            data: item,
            children: []
          }
        }

        // 添加子技能
        if (subskill) {
          subjectMap[subject].children[module].children[pointKey].children.push({
            key: item.code || `${pointKey}-${subskill}`,
            title: subskill,
            data: item,
            isLeaf: true
          })
        }
      }
    })

    // 转换为Antd Tree需要的格式
    const convertToAntdTree = (node) => {
      if (Array.isArray(node)) {
        return node.map(convertToAntdTree)
      }
      
      const result = {
        key: node.key,
        title: node.title,
        data: node.data
      }

      if (node.children) {
        if (Array.isArray(node.children)) {
          result.children = node.children.map(convertToAntdTree)
        } else {
          result.children = Object.values(node.children).map(convertToAntdTree)
        }
      }

      return result
    }

    return convertToAntdTree(tree)
  }

  // 创建知识点
  const createKnowledgePoint = async (kpData) => {
    try {
      const response = await api.post('/api/knowledge-points', kpData)
      message.success('知识点创建成功！')
      
      // 刷新列表
      await fetchKnowledgePoints()
      
      return response.data
    } catch (error) {
      console.error('创建知识点失败:', error)
      message.error('创建知识点失败')
      throw error
    }
  }

  // 更新知识点
  const updateKnowledgePoint = async (id, kpData) => {
    try {
      const response = await api.put(`/api/knowledge-points/${id}`, kpData)
      message.success('知识点更新成功！')
      
      // 刷新列表
      await fetchKnowledgePoints()
      
      return response.data
    } catch (error) {
      console.error('更新知识点失败:', error)
      message.error('更新知识点失败')
      throw error
    }
  }

  // 删除知识点
  const deleteKnowledgePoint = async (id) => {
    try {
      await api.delete(`/api/knowledge-points/${id}`)
      message.success('知识点删除成功！')
      
      // 刷新列表
      await fetchKnowledgePoints()
    } catch (error) {
      console.error('删除知识点失败:', error)
      message.error('删除知识点失败')
      throw error
    }
  }

  // 根据学科筛选
  const filterBySubject = (subject) => {
    return knowledgePoints.filter(kp => kp.subject === subject)
  }

  // 根据关键词搜索
  const searchKnowledgePoints = (keyword) => {
    if (!keyword) return knowledgePoints
    
    return knowledgePoints.filter(kp => 
      kp.point?.toLowerCase().includes(keyword.toLowerCase()) ||
      kp.module?.toLowerCase().includes(keyword.toLowerCase()) ||
      kp.subskill?.toLowerCase().includes(keyword.toLowerCase())
    )
  }

  // 初始加载
  useEffect(() => {
    fetchKnowledgePoints()
  }, [JSON.stringify(filters)])

  return {
    knowledgePoints,
    treeData,
    loading,
    fetchKnowledgePoints,
    createKnowledgePoint,
    updateKnowledgePoint,
    deleteKnowledgePoint,
    filterBySubject,
    searchKnowledgePoints
  }
}

// 获取学科列表的Hook
export const useSubjects = () => {
  const [subjects, setSubjects] = useState([])
  const { knowledgePoints } = useKnowledgePoints()

  useEffect(() => {
    const uniqueSubjects = [...new Set(knowledgePoints.map(kp => kp.subject))]
    setSubjects(uniqueSubjects)
  }, [knowledgePoints])

  return subjects
}