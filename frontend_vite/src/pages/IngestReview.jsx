import React, { useState } from 'react'
import {
  Card,
  Input,
  Button,
  Table,
  Space,
  Tag,
  Modal,
  Form,
  message,
  Typography,
  Select,
  Descriptions,
  Popconfirm,
  Row,
  Col,
  Statistic
} from 'antd'
import {
  SearchOutlined,
  CheckOutlined,
  CloseOutlined,
  EyeOutlined,
  EditOutlined
} from '@ant-design/icons'
import { useIngestSession, useIngest } from '../hooks/useIngest'

const { Title, Text } = Typography

const IngestReview = () => {
  const [sessionId, setSessionId] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [previewItem, setPreviewItem] = useState(null)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [editingItem, setEditingItem] = useState(null)
  const [searchForm] = Form.useForm()
  const [editForm] = Form.useForm()

  // 使用Hook
  const {
    session,
    ingestItems,
    loading,
    approveIngestItem,
    rejectIngestItem,
    batchApprove,
    batchReject
  } = useIngestSession(sessionId)

  const { sessions: ingestSessions } = useIngest()

  // 搜索会话
  const handleSearch = () => {
    const values = searchForm.getFieldsValue()
    if (values.sessionId?.trim()) {
      setSessionId(values.sessionId.trim())
    } else {
      message.warning('请输入Session ID')
    }
  }

  // 单项审核通过
  const handleApprove = async (record) => {
    try {
      await approveIngestItem(record.id)
      message.success('审核通过！')
    } catch (error) {
      console.error('审核失败:', error)
    }
  }

  // 单项驳回
  const handleReject = async (record) => {
    try {
      await rejectIngestItem(record.id, { reason: '手动驳回' })
      message.success('已驳回！')
    } catch (error) {
      console.error('驳回失败:', error)
    }
  }

  // 编辑题目
  const handleEdit = (record) => {
    setEditingItem(record)
    setEditModalVisible(true)
    // 解析OCR结果填充表单
    try {
      const ocrData = typeof record.ocr_json === 'string' ? JSON.parse(record.ocr_json) : record.ocr_json
      editForm.setFieldsValue({
        stem: ocrData?.text || record.question_text || '',
        type: record.candidate_type || 'single',
        difficulty: 2
      })
    } catch (e) {
      editForm.setFieldsValue({
        stem: record.question_text || '',
        type: record.candidate_type || 'single', 
        difficulty: 2
      })
    }
  }

  // 保存编辑
  const handleSaveEdit = async () => {
    try {
      const values = await editForm.validateFields()
      await approveIngestItem(editingItem.id, values)
      setEditModalVisible(false)
      setEditingItem(null)
      editForm.resetFields()
      message.success('题目已成功添加到题库！')
    } catch (error) {
      console.error('保存失败:', error)
    }
  }

  // 预览项目
  const handlePreview = (record) => {
    setPreviewItem(record)
  }

  // 批量审核通过
  const handleBatchApprove = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要审核的项目')
      return
    }
    try {
      await batchApprove(selectedRowKeys)
      setSelectedRowKeys([])
      message.success(`批量审核通过 ${selectedRowKeys.length} 个项目！`)
    } catch (error) {
      console.error('批量审核失败:', error)
    }
  }

  // 批量驳回
  const handleBatchReject = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要驳回的项目')
      return
    }
    try {
      await batchReject(selectedRowKeys, { reason: '批量驳回' })
      setSelectedRowKeys([])
      message.success(`批量驳回 ${selectedRowKeys.length} 个项目！`)
    } catch (error) {
      console.error('批量驳回失败:', error)
    }
  }

  // 表格列定义
  const columns = [
    {
      title: '题目内容',
      dataIndex: 'ocr_json',
      key: 'question_text',
      width: 300,
      ellipsis: true,
      render: (ocr_json) => {
        try {
          const ocrData = typeof ocr_json === 'string' ? JSON.parse(ocr_json) : ocr_json
          const text = ocrData?.text || '无内容'
          return <Text ellipsis={{ tooltip: text }}>{text}</Text>
        } catch (e) {
          return <Text ellipsis>解析失败</Text>
        }
      }
    },
    {
      title: '题目类型',
      dataIndex: 'candidate_type',
      key: 'candidate_type',
      width: 100,
      render: (type) => {
        const typeMap = {
          'single': '单选题',
          'multiple': '多选题',
          'fill': '填空题',
          'judge': '判断题',
          'subjective': '主观题'
        }
        return <Tag>{typeMap[type] || '未知'}</Tag>
      }
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 100,
      render: (confidence) => {
        if (!confidence) return '-'
        const percent = (confidence * 100).toFixed(1)
        const color = confidence > 0.8 ? 'green' : confidence > 0.6 ? 'orange' : 'red'
        return <Tag color={color}>{percent}%</Tag>
      }
    },
    {
      title: '状态',
      dataIndex: 'review_status',
      key: 'review_status',
      width: 100,
      render: (status) => {
        const statusMap = {
          'pending': { color: 'orange', text: '待审核' },
          'approved': { color: 'green', text: '已通过' },
          'rejected': { color: 'red', text: '已驳回' }
        }
        const statusInfo = statusMap[status] || { color: 'default', text: status || '未知' }
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          {record.review_status === 'pending' && (
            <>
              <Button
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Button
                size="small"
                type="primary"
                icon={<CheckOutlined />}
                onClick={() => handleApprove(record)}
              >
                通过
              </Button>
              <Button
                size="small"
                danger
                icon={<CloseOutlined />}
                onClick={() => handleReject(record)}
              >
                驳回
              </Button>
            </>
          )}
        </Space>
      )
    }
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
    getCheckboxProps: (record) => ({
      disabled: record.review_status === 'approved' || record.review_status === 'rejected',
    })
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>拆题入库审核</Title>
      
      {/* 搜索区域 */}
      <Card style={{ marginBottom: 16 }}>
        <Form form={searchForm} layout="inline">
          <Form.Item name="sessionId" label="Session ID">
            <Input
              placeholder="请输入Session ID"
              style={{ width: 300 }}
              onPressEnter={handleSearch}
            />
          </Form.Item>
          <Form.Item>
            <Button 
              type="primary" 
              icon={<SearchOutlined />} 
              onClick={handleSearch}
            >
              查询
            </Button>
          </Form.Item>
        </Form>

        {/* 快速选择会话 */}
        {ingestSessions && ingestSessions.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Text strong>快速选择：</Text>
            <Select
              placeholder="选择拆题会话"
              style={{ width: 300, marginLeft: 8 }}
              onChange={setSessionId}
              value={sessionId}
            >
              {ingestSessions.map(session => (
                <Select.Option key={session.id} value={session.id}>
                  {session.name || session.id} - {session.status}
                </Select.Option>
              ))}
            </Select>
          </div>
        )}
      </Card>

      {/* 会话信息 */}
      {session && (
        <Card style={{ marginBottom: 16 }}>
          <Descriptions title="拆题会话信息" column={3}>
            <Descriptions.Item label="Session ID">{session.id}</Descriptions.Item>
            <Descriptions.Item label="会话名称">{session.name}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={session.status === 'completed' ? 'success' : 'processing'}>
                {session.status === 'completed' ? '已完成' : '进行中'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">{session.created_at || '未知'}</Descriptions.Item>
            <Descriptions.Item label="总项目数">{ingestItems ? ingestItems.length : 0}</Descriptions.Item>
            <Descriptions.Item label="待审核">
              {ingestItems ? ingestItems.filter(item => item.review_status === 'pending').length : 0}
            </Descriptions.Item>
          </Descriptions>
          
          {/* 统计信息 */}
          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={6}>
              <Statistic title="待审核" value={ingestItems ? ingestItems.filter(item => item.review_status === 'pending').length : 0} valueStyle={{ color: '#faad14' }} />
            </Col>
            <Col span={6}>
              <Statistic title="已通过" value={ingestItems ? ingestItems.filter(item => item.review_status === 'approved').length : 0} valueStyle={{ color: '#52c41a' }} />
            </Col>
            <Col span={6}>
              <Statistic title="已驳回" value={ingestItems ? ingestItems.filter(item => item.review_status === 'rejected').length : 0} valueStyle={{ color: '#ff7875' }} />
            </Col>
            <Col span={6}>
              <Statistic title="总项目" value={ingestItems ? ingestItems.length : 0} />
            </Col>
          </Row>
        </Card>
      )}

      {/* 批量操作 */}
      {selectedRowKeys.length > 0 && (
        <Card style={{ marginBottom: 16 }}>
          <Space>
            <Text>已选择 {selectedRowKeys.length} 个项目</Text>
            <Popconfirm
              title="确认批量审核通过选中的项目吗？"
              onConfirm={handleBatchApprove}
            >
              <Button type="primary" icon={<CheckOutlined />}>
                批量通过
              </Button>
            </Popconfirm>
            <Popconfirm
              title="确认批量驳回选中的项目吗？"
              onConfirm={handleBatchReject}
            >
              <Button danger icon={<CloseOutlined />}>
                批量驳回
              </Button>
            </Popconfirm>
          </Space>
        </Card>
      )}

      {/* 拆题项目列表 */}
      <Card>
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={ingestItems || []}
          loading={loading}
          rowKey="id"
          pagination={{
            total: ingestItems ? ingestItems.length : 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`
          }}
        />
      </Card>

      {/* 预览弹窗 */}
      <Modal
        title="题目预览"
        open={!!previewItem}
        onCancel={() => setPreviewItem(null)}
        footer={null}
        width={800}
      >
        {previewItem && (
          <div>
            <Descriptions column={2}>
              <Descriptions.Item label="题目类型">
                {previewItem.candidate_type}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                {previewItem.review_status}
              </Descriptions.Item>
              <Descriptions.Item label="置信度">
                {previewItem.confidence ? (previewItem.confidence * 100).toFixed(1) + '%' : '-'}
              </Descriptions.Item>
            </Descriptions>
            
            <div style={{ marginTop: 16 }}>
              <Text strong>题目内容：</Text>
              <div style={{ marginTop: 8, padding: 16, backgroundColor: '#f5f5f5' }}>
                {(() => {
                  try {
                    const ocrData = typeof previewItem.ocr_json === 'string' ? JSON.parse(previewItem.ocr_json) : previewItem.ocr_json
                    return ocrData?.text || '暂无内容'
                  } catch (e) {
                    return '解析失败'
                  }
                })()}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* 编辑弹窗 */}
      <Modal
        title="编辑题目"
        open={editModalVisible}
        onOk={handleSaveEdit}
        onCancel={() => {
          setEditModalVisible(false)
          setEditingItem(null)
          editForm.resetFields()
        }}
        width={800}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            name="stem"
            label="题目内容"
            rules={[{ required: true, message: '请输入题目内容' }]}
          >
            <Input.TextArea rows={4} placeholder="请输入题目内容" />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="type"
                label="题目类型"
                rules={[{ required: true, message: '请选择题目类型' }]}
              >
                <Select placeholder="请选择题目类型">
                  <Select.Option value="single">单选题</Select.Option>
                  <Select.Option value="multiple">多选题</Select.Option>
                  <Select.Option value="fill">填空题</Select.Option>
                  <Select.Option value="judge">判断题</Select.Option>
                  <Select.Option value="subjective">主观题</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="difficulty"
                label="难度等级"
                rules={[{ required: true, message: '请选择难度等级' }]}
              >
                <Select placeholder="请选择难度等级">
                  <Select.Option value={1}>1星 (很简单)</Select.Option>
                  <Select.Option value={2}>2星 (简单)</Select.Option>
                  <Select.Option value={3}>3星 (中等)</Select.Option>
                  <Select.Option value={4}>4星 (困难)</Select.Option>
                  <Select.Option value={5}>5星 (很困难)</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  )
}

export default IngestReview