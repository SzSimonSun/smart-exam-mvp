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
  Row,
  Col,
  Tabs,
  Select,
  Image,
  Descriptions,
  Checkbox,
  Popconfirm,
  Drawer
} from 'antd'
import {
  SearchOutlined,
  CheckOutlined,
  CloseOutlined,
  EditOutlined,
  EyeOutlined,
  FileImageOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { useIngestSession, useIngest } from '../hooks/useIngest'

const { Title, Text } = Typography
const { TabPane } = Tabs

const IngestReview = () => {
  const [sessionId, setSessionId] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [previewItem, setPreviewItem] = useState(null)
  const [editItem, setEditItem] = useState(null)
  const [editDrawerVisible, setEditDrawerVisible] = useState(false)
  const [rejectModalVisible, setRejectModalVisible] = useState(false)
  const [rejectForm] = Form.useForm()
  const [searchForm] = Form.useForm()

  // 使用Hook
  const {
    session,
    ingestItems,
    loading,
    approveIngestItem,
    rejectIngestItem,
    batchApprove,
    batchReject,
    editIngestItem,
    completeIngestSession
  } = useIngestSession(sessionId)

  const { ingestSessions } = useIngest()

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
    } catch (error) {
      // Hook中已处理错误
    }
  }

  // 单项驳回
  const handleReject = (record) => {
    setEditItem(record)
    setRejectModalVisible(true)
  }

  // 确认驳回
  const handleConfirmReject = async () => {
    try {
      const values = await rejectForm.validateFields()
      await rejectIngestItem(editItem.id, { reason: values.reason })
      setRejectModalVisible(false)
      rejectForm.resetFields()
      setEditItem(null)
    } catch (error) {
      // Hook中已处理错误
    }
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
    } catch (error) {
      // Hook中已处理错误
    }
  }

  // 批量驳回
  const handleBatchReject = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要驳回的项目')
      return
    }
    setRejectModalVisible(true)
  }

  // 确认批量驳回
  const handleConfirmBatchReject = async () => {
    try {
      const values = await rejectForm.validateFields()
      await batchReject(selectedRowKeys, { reason: values.reason })
      setRejectModalVisible(false)
      rejectForm.resetFields()
      setSelectedRowKeys([])
    } catch (error) {
      // Hook中已处理错误
    }
  }

  // 编辑项目
  const handleEdit = (record) => {
    setEditItem(record)
    setEditDrawerVisible(true)
  }

  // 预览项目
  const handlePreview = (record) => {
    setPreviewItem(record)
  }

  // 完成拆题会话
  const handleCompleteSession = async () => {
    Modal.confirm({
      title: '确认完成拆题会话？',
      content: '完成后将无法继续审核，请确认所有项目都已处理完毕。',
      onOk: async () => {
        try {
          await completeIngestSession()
        } catch (error) {
          // Hook中已处理错误
        }
      }
    })
  }

  // 表格列定义
  const columns = [
    {
      title: '题目内容',
      dataIndex: 'question_text',
      key: 'question_text',
      width: 300,
      ellipsis: true,
      render: (text, record) => (
        <div>
          <Text ellipsis={{ tooltip: text }}>{text}</Text>
          {record.question_image && (
            <div style={{ marginTop: 4 }}>
              <FileImageOutlined style={{ color: '#1890ff' }} />
              <Text type="secondary"> 包含图片</Text>
            </div>
          )}
        </div>
      )
    },
    {
      title: '题目类型',
      dataIndex: 'question_type',
      key: 'question_type',
      width: 100,
      render: (type) => {
        const typeMap = {
          'single_choice': '单选题',
          'multiple_choice': '多选题',
          'fill_blank': '填空题',
          'subjective': '主观题'
        }
        return <Tag>{typeMap[type] || type}</Tag>
      }
    },
    {
      title: '知识点',
      dataIndex: 'knowledge_points',
      key: 'knowledge_points',
      width: 150,
      render: (points) => (
        <div>
          {points?.map(point => (
            <Tag key={point.id} size="small">{point.name}</Tag>
          ))}
        </div>
      )
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 80,
      render: (difficulty) => {
        const color = {
          'easy': 'green',
          'medium': 'orange', 
          'hard': 'red'
        }[difficulty]
        const text = {
          'easy': '简单',
          'medium': '中等',
          'hard': '困难'
        }[difficulty]
        return <Tag color={color}>{text}</Tag>
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const statusMap = {
          'pending': { color: 'processing', text: '待审核' },
          'approved': { color: 'success', text: '已通过' },
          'rejected': { color: 'error', text: '已驳回' }
        }
        const statusInfo = statusMap[status] || { color: 'default', text: status }
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={record.status === 'approved'}
          >
            编辑
          </Button>
          {record.status === 'pending' && (
            <>
              <Button
                type="link"
                icon={<CheckOutlined />}
                onClick={() => handleApprove(record)}
                style={{ color: '#52c41a' }}
              >
                通过
              </Button>
              <Button
                type="link"
                icon={<CloseOutlined />}
                onClick={() => handleReject(record)}
                style={{ color: '#ff4d4f' }}
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
      disabled: record.status === 'approved'
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
        {ingestSessions.length > 0 && (
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
            <Descriptions.Item label="创建时间">{session.created_at}</Descriptions.Item>
            <Descriptions.Item label="总项目数">{ingestItems.length}</Descriptions.Item>
            <Descriptions.Item label="待审核">
              {ingestItems.filter(item => item.status === 'pending').length}
            </Descriptions.Item>
          </Descriptions>
          
          {session.status !== 'completed' && (
            <div style={{ marginTop: 16 }}>
              <Popconfirm
                title="确认完成拆题会话？"
                description="完成后将无法继续审核"
                onConfirm={handleCompleteSession}
              >
                <Button type="primary" danger>
                  完成拆题会话
                </Button>
              </Popconfirm>
            </div>
          )}
        </Card>
      )}

      {/* 批量操作 */}
      {ingestItems.length > 0 && (
        <Card style={{ marginBottom: 16 }}>
          <Space>
            <Text>已选择 {selectedRowKeys.length} 项</Text>
            <Button
              type="primary"
              icon={<CheckOutlined />}
              onClick={handleBatchApprove}
              disabled={selectedRowKeys.length === 0}
            >
              批量通过
            </Button>
            <Button
              icon={<CloseOutlined />}
              onClick={handleBatchReject}
              disabled={selectedRowKeys.length === 0}
            >
              批量驳回
            </Button>
          </Space>
        </Card>
      )}

      {/* 拆题项目列表 */}
      <Card>
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={ingestItems}
          loading={loading}
          rowKey="id"
          pagination={{
            total: ingestItems.length,
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
                {previewItem.question_type}
              </Descriptions.Item>
              <Descriptions.Item label="难度">
                {previewItem.difficulty}
              </Descriptions.Item>
            </Descriptions>
            
            <div style={{ marginTop: 16 }}>
              <Text strong>题目内容：</Text>
              <div style={{ marginTop: 8, padding: 16, backgroundColor: '#f5f5f5' }}>
                {previewItem.question_text}
              </div>
            </div>

            {previewItem.question_image && (
              <div style={{ marginTop: 16 }}>
                <Text strong>题目图片：</Text>
                <div style={{ marginTop: 8 }}>
                  <Image
                    src={previewItem.question_image}
                    alt="题目图片"
                    style={{ maxWidth: '100%' }}
                  />
                </div>
              </div>
            )}

            {previewItem.options && previewItem.options.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Text strong>选项：</Text>
                <div style={{ marginTop: 8 }}>
                  {previewItem.options.map((option, index) => (
                    <div key={index} style={{ marginBottom: 8 }}>
                      <Text>{String.fromCharCode(65 + index)}. {option}</Text>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ marginTop: 16 }}>
              <Text strong>正确答案：</Text>
              <div style={{ marginTop: 8 }}>
                <Text code>{previewItem.correct_answer}</Text>
              </div>
            </div>

            {previewItem.explanation && (
              <div style={{ marginTop: 16 }}>
                <Text strong>解析：</Text>
                <div style={{ marginTop: 8, padding: 16, backgroundColor: '#f5f5f5' }}>
                  {previewItem.explanation}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* 驳回原因弹窗 */}
      <Modal
        title={editItem ? "驳回原因" : "批量驳回原因"}
        open={rejectModalVisible}
        onOk={editItem ? handleConfirmReject : handleConfirmBatchReject}
        onCancel={() => {
          setRejectModalVisible(false)
          rejectForm.resetFields()
          setEditItem(null)
        }}
      >
        <Form form={rejectForm}>
          <Form.Item
            name="reason"
            label="驳回原因"
            rules={[{ required: true, message: '请输入驳回原因' }]}
          >
            <Input.TextArea
              rows={4}
              placeholder="请输入驳回原因..."
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default IngestReview