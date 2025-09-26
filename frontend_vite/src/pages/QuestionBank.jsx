import React, { useState } from 'react'
import { Table, Button, Space, Tag, Drawer, Form, Input, Select, InputNumber, message, Card, Row, Col, Divider } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { useQuestions } from '../hooks/useQuestions'
import { useKnowledgePoints } from '../hooks/useKnowledgePoints'

const { Option } = Select
const { TextArea } = Input

export default function QuestionBank() {
  const [filters, setFilters] = useState({})
  const [drawerVisible, setDrawerVisible] = useState(false)
  const [editingQuestion, setEditingQuestion] = useState(null)
  const [form] = Form.useForm()
  
  // 使用hooks
  const { questions, loading, pagination, createQuestion, updateQuestion, deleteQuestion, publishQuestion, handlePaginationChange } = useQuestions(filters)
  const { knowledgePoints } = useKnowledgePoints()

  // 获取题型标签
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

  // 获取难度颜色
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

  // 打开新建/编辑抽屉
  const showDrawer = (question = null) => {
    setEditingQuestion(question)
    setDrawerVisible(true)
    
    if (question) {
      // 编辑模式，填充表单
      form.setFieldsValue({
        ...question,
        knowledge_point_ids: question.knowledge_points?.map(kp => kp.id) || []
      })
    } else {
      // 新建模式，清空表单
      form.resetFields()
    }
  }

  // 关闭抽屉
  const closeDrawer = () => {
    setDrawerVisible(false)
    setEditingQuestion(null)
    form.resetFields()
  }

  // 提交表单
  const onFinish = async (values) => {
    try {
      if (editingQuestion) {
        await updateQuestion(editingQuestion.id, values)
      } else {
        await createQuestion(values)
      }
      closeDrawer()
    } catch (error) {
      console.error('操作失败:', error)
    }
  }

  // 删除题目
  const handleDelete = async (id) => {
    try {
      await deleteQuestion(id)
    } catch (error) {
      console.error('删除失败:', error)
    }
  }

  // 发布题目
  const handlePublish = async (id) => {
    try {
      await publishQuestion(id)
    } catch (error) {
      console.error('发布失败:', error)
    }
  }

  // 表格列定义
  const columns = [
    { title: 'ID', dataIndex: 'id', width: 80 },
    { title: '题干', dataIndex: 'stem', width: 300, ellipsis: true },
    {
      title: '题型',
      dataIndex: 'type',
      width: 120,
      render: (type) => <Tag color="blue">{getTypeLabel(type)}</Tag>
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      width: 100,
      render: (difficulty) => (
        <Tag color={getDifficultyColor(difficulty)}>
          {difficulty}星
        </Tag>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => (
        <Tag color={status === 'published' ? 'green' : 'orange'}>
          {status === 'published' ? '已发布' : '草稿'}
        </Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (date) => date ? new Date(date).toLocaleString() : '-'
    },
    {
      title: '操作',
      width: 250,
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />}>
            查看
          </Button>
          <Button size="small" icon={<EditOutlined />} onClick={() => showDrawer(record)}>
            编辑
          </Button>
          {record.status === 'draft' && (
            <Button size="small" type="primary" onClick={() => handlePublish(record.id)}>
              发布
            </Button>
          )}
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      {/* 页面头部 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <h2>题库管理</h2>
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => showDrawer()}>
            新建题目
          </Button>
        </Col>
      </Row>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onValuesChange={(_, allValues) => setFilters(allValues)}>
          <Form.Item name="type" label="题型">
            <Select placeholder="全部题型" style={{ width: 120 }} allowClear>
              <Option value="single">单选题</Option>
              <Option value="multiple">多选题</Option>
              <Option value="fill">填空题</Option>
              <Option value="judge">判断题</Option>
              <Option value="subjective">主观题</Option>
            </Select>
          </Form.Item>
          <Form.Item name="difficulty" label="难度">
            <Select placeholder="全部难度" style={{ width: 120 }} allowClear>
              <Option value={1}>1星</Option>
              <Option value={2}>2星</Option>
              <Option value={3}>3星</Option>
              <Option value={4}>4星</Option>
              <Option value={5}>5星</Option>
            </Select>
          </Form.Item>
          <Form.Item name="q" label="关键词">
            <Input placeholder="搜索题干" style={{ width: 200 }} allowClear />
          </Form.Item>
        </Form>
      </Card>

      {/* 题目表格 */}
      <Table
        rowKey="id"
        columns={columns}
        dataSource={questions}
        loading={loading}
        pagination={{
          ...pagination,
          onChange: handlePaginationChange,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 道题目`
        }}
      />

      {/* 新建/编辑抽屉 */}
      <Drawer
        title={editingQuestion ? '编辑题目' : '新建题目'}
        width={720}
        open={drawerVisible}
        onClose={closeDrawer}
        footer={
          <div style={{ textAlign: 'right' }}>
            <Button onClick={closeDrawer} style={{ marginRight: 8 }}>
              取消
            </Button>
            <Button type="primary" onClick={() => form.submit()}>
              {editingQuestion ? '更新' : '创建'}
            </Button>
          </div>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            type: 'single',
            difficulty: 2
          }}
        >
          <Form.Item
            name="stem"
            label="题干"
            rules={[{ required: true, message: '请输入题干' }]}
          >
            <TextArea rows={4} placeholder="请输入题目内容" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="type"
                label="题型"
                rules={[{ required: true, message: '请选择题型' }]}
              >
                <Select placeholder="请选择题型">
                  <Option value="single">单选题</Option>
                  <Option value="multiple">多选题</Option>
                  <Option value="fill">填空题</Option>
                  <Option value="judge">判断题</Option>
                  <Option value="subjective">主观题</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="difficulty"
                label="难度"
                rules={[{ required: true, message: '请选择难度' }]}
              >
                <InputNumber min={1} max={5} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="knowledge_point_ids" label="知识点">
            <Select
              mode="multiple"
              placeholder="请选择知识点"
              options={knowledgePoints.map(kp => ({
                label: `${kp.subject} > ${kp.module} > ${kp.point}`,
                value: kp.id
              }))}
            />
          </Form.Item>

          <Divider />

          <Form.Item name="analysis" label="解析">
            <TextArea rows={3} placeholder="请输入题目解析" />
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  )
}
