import React, { useState, useEffect } from 'react'
import { Table, Button, Space, Tag, message, Spin } from 'antd'
import axios from 'axios'

export default function QuestionBank(){
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/questions', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setQuestions(response.data)
    } catch (error) {
      console.error('加载题目失败:', error)
      message.error('加载题目失败')
    } finally {
      setLoading(false)
    }
  }

  const getTypeLabel = (type) => {
    const typeMap = {
      'single': '单选题',
      'multiple': '多选题', 
      'fill': '填空题',
      'judge': '判断题',
      'subjective': '主观题'
    }
    return typeMap[type] || type
  }

  const getDifficultyColor = (difficulty) => {
    const colorMap = {
      1: 'green',
      2: 'blue', 
      3: 'orange',
      4: 'red',
      5: 'purple'
    }
    return colorMap[difficulty] || 'default'
  }

  const columns = [
    { title:'ID', dataIndex:'id', width:80 },
    { title:'题干', dataIndex:'stem', width:300 },
    { 
      title:'题型', 
      dataIndex:'type', 
      width:120,
      render: (type) => <Tag color="blue">{getTypeLabel(type)}</Tag>
    },
    { 
      title:'难度', 
      dataIndex:'difficulty', 
      width:100,
      render: (difficulty) => (
        <Tag color={getDifficultyColor(difficulty)}>
          {difficulty}星
        </Tag>
      )
    },
    {
      title:'状态',
      dataIndex:'status',
      width:100,
      render: (status) => (
        <Tag color={status === 'published' ? 'green' : 'orange'}>
          {status === 'published' ? '已发布' : '草稿'}
        </Tag>
      )
    },
    {
      title:'创建时间',
      dataIndex:'created_at',
      width:180,
      render: (date) => date ? new Date(date).toLocaleString() : '-'
    },
    { 
      title:'操作', 
      width:200,
      render:(_, record) => (
        <Space>
          <Button size="small">编辑</Button>
          <Button size="small" type="primary">加入试卷</Button>
          {record.status === 'draft' && (
            <Button size="small" type="link">发布</Button>
          )}
        </Space>
      ) 
    }
  ]

  if (loading) {
    return (
      <div style={{display: 'flex', justifyContent: 'center', padding: 50}}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <div style={{marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <h2>题库管理</h2>
        <Button type="primary">新建题目</Button>
      </div>
      <Table 
        rowKey="id" 
        columns={columns} 
        dataSource={questions}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 道题目`
        }}
      />
    </div>
  )
}
