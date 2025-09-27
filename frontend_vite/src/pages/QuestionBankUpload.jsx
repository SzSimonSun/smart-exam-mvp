import React, { useState, useEffect } from 'react'
import { 
  Card, 
  Upload, 
  Button, 
  message, 
  Progress, 
  List, 
  Typography, 
  Tag, 
  Space, 
  Tabs, 
  Empty,
  Spin,
  Alert,
  Row,
  Col,
  Statistic,
  Modal,
  Form,
  Input,
  Select,
  Divider,
  Badge,
  Checkbox,
  Popconfirm,
  Table,
  Switch
} from 'antd'
import { 
  InboxOutlined, 
  FileTextOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  EyeOutlined,
  EditOutlined,
  UploadOutlined,
  ReloadOutlined,
  QuestionCircleOutlined,
  CloseOutlined
} from '@ant-design/icons'
import { useUpload } from '../hooks/useUpload'
import { useIngest } from '../hooks/useIngest'
import { useQuestions } from '../hooks/useQuestions'
import ErrorBoundary from '../components/ErrorBoundary'

const { Title, Text, Paragraph } = Typography
const { Dragger } = Upload
const { TextArea } = Input
const { Option } = Select

export default function QuestionBankUpload() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadedSessions, setUploadedSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [sessionItems, setSessionItems] = useState([])
  const [modalVisible, setModalVisible] = useState(false)
  const [editingItem, setEditingItem] = useState(null)
  const [selectedItems, setSelectedItems] = useState([])
  const [batchMode, setBatchMode] = useState(false)
  const [form] = Form.useForm()

  // 使用hooks
  const { uploadPaperForIngest, uploading, progress } = useUpload()
  const { 
    sessions, 
    sessionLoading, 
    items, 
    itemsLoading,
    createIngestSession,
    fetchIngestSessions,
    fetchIngestItems,
    approveIngestItem,
    rejectIngestItem
  } = useIngest()
  const { createQuestion } = useQuestions()

  // 初始加载会话列表
  useEffect(() => {
    fetchIngestSessions()
  }, [fetchIngestSessions])

  // 文件上传配置
  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.pdf,.png,.jpg,.jpeg,.docx',
    beforeUpload: (file) => {
      const isValidType = file.type === 'application/pdf' || 
                          file.type.startsWith('image/') ||
                          file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      if (!isValidType) {
        message.error('只支持PDF、图片和DOCX格式的文件！')
        return false
      }
      const isLt50M = file.size / 1024 / 1024 < 50
      if (!isLt50M) {
        message.error('文件大小不能超过50MB！')
        return false
      }
      return true
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        console.log('📄 开始上传文件:', file.name)
        const result = await uploadPaperForIngest(file)
        console.log('✅ 上传成功:', result)
        onSuccess(result)
        message.success('试卷上传成功，正在处理中...')
        
        // 刷新会话列表
        await fetchIngestSessions()
        
        // 切换到会话列表标签页
        setActiveTab('sessions')
      } catch (error) {
        console.error('🚫 上传失败:', error)
        onError(error)
        
        // 更友好的错误提示
        if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
          message.error('上传超时，请检查网络连接后重试')
        } else if (error.message && error.message.includes('无法连接')) {
          message.error('无法连接到服务器，请检查后端服务是否正常运行')
        } else if (error.response) {
          const detail = error.response.data?.detail || error.response.data?.message || '未知错误'
          message.error(`上传失败：${detail}`)
        } else {
          message.error('上传失败：' + (error.message || '网络连接失败'))
        }
      }
    }
  }

  // 查看会话详情
  const viewSessionDetails = async (session) => {
    setCurrentSession(session)
    setActiveTab('review')
    
    try {
      const itemsData = await fetchIngestItems(session.id)
      setSessionItems(itemsData || [])
    } catch (error) {
      message.error('获取拆题结果失败')
    }
  }

  // 编辑题目
  const editQuestion = (item) => {
    setEditingItem(item)
    setModalVisible(true)
    
    // 更好的数据解析逻辑
    let questionText = ''
    
    // 优先使用后端返回的 question_text
    if (item.question_text) {
      questionText = item.question_text
    } else {
      // 备用方案：解析 ocr_json
      try {
        const ocrData = typeof item.ocr_json === 'string' 
          ? JSON.parse(item.ocr_json) 
          : (item.ocr_json || {})
        questionText = ocrData.text || ''
      } catch (e) {
        console.warn('解析OCR数据失败:', e)
        questionText = ''
      }
    }
    
    // 填充表单
    form.setFieldsValue({
      stem: questionText || '请输入题目内容',
      type: item.candidate_type || 'single',
      difficulty: 2,
      analysis: '' // 默认为空，由用户填写
    })
  }

  // 保存编辑的题目
  const saveQuestion = async (values) => {
    try {
      console.log('📄 开始保存题目:', editingItem.id, values)
      await approveIngestItem(editingItem.id, values)
      message.success('题目已成功添加到题库！')
      setModalVisible(false)
      
      // 刷新拆题项目列表
      const updatedItems = await fetchIngestItems(currentSession.id)
      setSessionItems(updatedItems || [])
    } catch (error) {
      console.error('📛 保存失败:', error)
      
      if (error.message && error.message.includes('message port closed')) {
        message.error('连接中断，请刷新页面后再试')
        // 建议用户刷新页面
        setTimeout(() => {
          if (confirm('检测到连接问题，是否刷新页面？')) {
            window.location.reload()
          }
        }, 2000)
      } else {
        message.error('保存失败：' + (error.message || '未知错误'))
      }
    }
  }

  // 拒绝题目
  const rejectQuestion = async (item) => {
    try {
      await rejectIngestItem(item.id)
      message.success('已拒绝该题目')
      
      // 刷新拆题项目列表
      const updatedItems = await fetchIngestItems(currentSession.id)
      setSessionItems(updatedItems || [])
    } catch (error) {
      message.error('操作失败：' + (error.message || '未知错误'))
    }
  }

  // 批量选择处理
  const handleSelectItem = (itemId, checked) => {
    if (checked) {
      setSelectedItems([...selectedItems, itemId])
    } else {
      setSelectedItems(selectedItems.filter(id => id !== itemId))
    }
  }

  // 全选/取消全选
  const handleSelectAll = (checked) => {
    if (checked) {
      const pendingItems = sessionItems.filter(item => item.review_status === 'pending')
      setSelectedItems(pendingItems.map(item => item.id))
    } else {
      setSelectedItems([])
    }
  }

  // 批量审核通过
  const handleBatchApprove = async () => {
    if (selectedItems.length === 0) {
      message.warning('请先选择要审核的题目')
      return
    }

    try {
      console.log('📄 开始批量审核通过:', selectedItems.length, '个项目')
      
      // 为每个选中的项目单独调用审核通过接口
      const promises = selectedItems.map(itemId => {
        const item = sessionItems.find(i => i.id === itemId)
        
        // 获取题目文本
        let questionText = ''
        if (item?.question_text) {
          questionText = item.question_text
        } else {
          try {
            const ocrData = typeof item?.ocr_json === 'string' 
              ? JSON.parse(item.ocr_json) 
              : (item?.ocr_json || {})
            questionText = ocrData.text || ''
          } catch (e) {
            questionText = ''
          }
        }
        
        return approveIngestItem(itemId, {
          stem: questionText || '识别题目内容',
          type: item?.candidate_type || 'single',
          difficulty: 2
        })
      })
      
      await Promise.all(promises)
      message.success(`批量审核通过 ${selectedItems.length} 个题目`)
      
      // 清空选择并刷新列表
      setSelectedItems([])
      const updatedItems = await fetchIngestItems(currentSession.id)
      setSessionItems(updatedItems || [])
    } catch (error) {
      console.error('📛 批量审核失败:', error)
      
      if (error.message && error.message.includes('message port closed')) {
        message.error('批量操作连接中断，请刷新页面后再试')
        setTimeout(() => {
          if (confirm('检测到连接问题，是否刷新页面？')) {
            window.location.reload()
          }
        }, 2000)
      } else {
        message.error('批量审核失败：' + (error.message || '未知错误'))
      }
    }
  }

  // 批量拒绝
  const handleBatchReject = async () => {
    if (selectedItems.length === 0) {
      message.warning('请先选择要拒绝的题目')
      return
    }

    try {
      const promises = selectedItems.map(itemId => rejectIngestItem(itemId))
      await Promise.all(promises)
      message.success(`批量拒绝 ${selectedItems.length} 个题目`)
      
      // 清空选择并刷新列表
      setSelectedItems([])
      const updatedItems = await fetchIngestItems(currentSession.id)
      setSessionItems(updatedItems || [])
    } catch (error) {
      message.error('批量拒绝失败：' + (error.message || '未知错误'))
    }
  }

  // 获取审核状态显示
  const getReviewStatus = (item) => {
    switch (item.review_status) {
      case 'approved':
        return <Badge status="success" text="已通过" />
      case 'rejected':
        return <Badge status="error" text="已拒绝" />
      case 'pending':
      default:
        return <Badge status="processing" text="待审核" />
    }
  }

  // 获取题目类型显示
  const getTypeLabel = (type) => {
    const typeMap = {
      'single': '单选题',
      'multiple': '多选题',
      'fill': '填空题',
      'subjective': '主观题'
    }
    return typeMap[type] || type
  }

  return (
    <ErrorBoundary>
      <div style={{ padding: '24px' }}>
        <Title level={2}>试卷拆分入库</Title>
        <Paragraph>
          上传试卷PDF、DOCX或图片文件，系统将自动识别并拆分成单个题目，您可以审核后添加到题库中。
        </Paragraph>

      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'upload',
            label: '上传试卷',
            children: (
              <Card>
                <Dragger {...uploadProps} disabled={uploading}>
                  <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                  </p>
                  <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                  <p className="ant-upload-hint">
                    支持PDF、JPG、PNG、DOCX格式，文件大小不超过50MB
                  </p>
                </Dragger>
                
                {uploading && (
                  <div style={{ marginTop: 16 }}>
                    <Progress 
                      percent={progress} 
                      status="active"
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                    />
                    <Text type="secondary">正在上传文件...</Text>
                  </div>
                )}
              </Card>
            )
          },
          {
            key: 'sessions',
            label: '拆分会话',
            children: (
              <Card 
                title="拆分会话列表" 
                extra={
                  <Button 
                    icon={<ReloadOutlined />} 
                    onClick={fetchIngestSessions}
                    loading={sessionLoading}
                  >
                    刷新
                  </Button>
                }
              >
                {sessionLoading ? (
                  <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
                ) : sessions && sessions.length > 0 ? (
                  <List
                    itemLayout="horizontal"
                    dataSource={sessions}
                    renderItem={session => (
                      <List.Item
                        actions={[
                          <Button 
                            type="primary" 
                            icon={<EyeOutlined />}
                            onClick={() => viewSessionDetails(session)}
                          >
                            查看详情
                          </Button>
                        ]}
                      >
                        <List.Item.Meta
                          avatar={<FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />}
                          title={session.name || `拆分会话 ${session.id}`}
                          description={
                            <Space direction="vertical" size="small">
                              <Text type="secondary">
                                创建时间: {session.created_at ? new Date(session.created_at).toLocaleString() : '-'}
                              </Text>
                              <Space>
                                <Tag color={session.status === 'completed' ? 'green' : session.status === 'processing' ? 'blue' : 'orange'}>
                                  {session.status === 'completed' ? '已完成' : 
                                   session.status === 'processing' ? '处理中' : 
                                   session.status === 'awaiting_review' ? '待审核' : session.status}
                                </Tag>
                                <Text>总题目: {session.total_items || 0}</Text>
                                <Text>已处理: {session.processed_items || 0}</Text>
                              </Space>
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                ) : (
                  <Empty description="暂无拆分会话" />
                )}
              </Card>
            )
          },
          {
            key: 'review',
            label: '题目审核',
            disabled: !currentSession,
            children: currentSession ? (
              <Card 
                title={`审核会话: ${currentSession.name || currentSession.id}`}
                extra={
                  <Space>
                    <Switch 
                      checkedChildren="批量模式" 
                      unCheckedChildren="单个模式"
                      checked={batchMode}
                      onChange={setBatchMode}
                    />
                    <Statistic 
                      title="待审核" 
                      value={sessionItems.filter(item => item.review_status === 'pending').length} 
                      prefix={<QuestionCircleOutlined />}
                    />
                    <Statistic 
                      title="已通过" 
                      value={sessionItems.filter(item => item.review_status === 'approved').length} 
                      prefix={<CheckCircleOutlined />}
                    />
                    <Statistic 
                      title="已拒绝" 
                      value={sessionItems.filter(item => item.review_status === 'rejected').length} 
                      prefix={<CloseCircleOutlined />}
                    />
                  </Space>
                }
              >
                {/* 批量操作栏 */}
                {batchMode && (
                  <Card size="small" style={{ marginBottom: 16, backgroundColor: '#f6f9ff' }}>
                    <Row justify="space-between" align="middle">
                      <Col>
                        <Space>
                          <Checkbox
                            checked={selectedItems.length === sessionItems.filter(item => item.review_status === 'pending').length && selectedItems.length > 0}
                            indeterminate={selectedItems.length > 0 && selectedItems.length < sessionItems.filter(item => item.review_status === 'pending').length}
                            onChange={(e) => handleSelectAll(e.target.checked)}
                          >
                            全选待审核项目
                          </Checkbox>
                          <Text type="secondary">已选择 {selectedItems.length} 个项目</Text>
                        </Space>
                      </Col>
                      <Col>
                        <Space>
                          <Popconfirm
                            title="确认批量审核通过选中的项目吗？"
                            onConfirm={handleBatchApprove}
                            disabled={selectedItems.length === 0}
                          >
                            <Button 
                              type="primary" 
                              icon={<CheckCircleOutlined />}
                              disabled={selectedItems.length === 0}
                            >
                              批量通过
                            </Button>
                          </Popconfirm>
                          <Popconfirm
                            title="确认批量拒绝选中的项目吗？"
                            onConfirm={handleBatchReject}
                            disabled={selectedItems.length === 0}
                          >
                            <Button 
                              danger
                              icon={<CloseCircleOutlined />}
                              disabled={selectedItems.length === 0}
                            >
                              批量拒绝
                            </Button>
                          </Popconfirm>
                        </Space>
                      </Col>
                    </Row>
                  </Card>
                )}
                {itemsLoading ? (
                  <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
                ) : sessionItems && sessionItems.length > 0 ? (
                  <List
                    itemLayout="vertical"
                    dataSource={sessionItems}
                    renderItem={item => {
                      // 更好的数据解析逻辑
                      let questionText = ''
                      
                      // 优先使用后端返回的 question_text
                      if (item.question_text) {
                        questionText = item.question_text
                      } else {
                        // 备用方案：解析 ocr_json
                        try {
                          const ocrData = typeof item.ocr_json === 'string' 
                            ? JSON.parse(item.ocr_json) 
                            : (item.ocr_json || {})
                          questionText = ocrData.text || ''
                        } catch (e) {
                          questionText = ''
                        }
                      }
                      
                      const isPending = item.review_status === 'pending'
                      const isSelected = selectedItems.includes(item.id)
                      
                      return (
                        <List.Item
                          key={item.id}
                          style={{
                            backgroundColor: isSelected ? '#e6f7ff' : 'transparent',
                            border: isSelected ? '1px solid #91d5ff' : '1px solid #f0f0f0',
                            borderRadius: '6px',
                            marginBottom: '8px',
                            padding: '16px'
                          }}
                          actions={
                            isPending ? [
                              batchMode && (
                                <Checkbox
                                  key="select"
                                  checked={isSelected}
                                  onChange={(e) => handleSelectItem(item.id, e.target.checked)}
                                />
                              ),
                              <Button 
                                key="edit"
                                type="primary" 
                                icon={<EditOutlined />}
                                onClick={() => editQuestion(item)}
                              >
                                编辑
                              </Button>,
                              <Button 
                                key="reject"
                                danger 
                                icon={<CloseOutlined />}
                                onClick={() => rejectQuestion(item)}
                              >
                                拒绝
                              </Button>
                            ].filter(Boolean) : [
                              <Tag 
                                key="status"
                                color={item.review_status === 'approved' ? 'green' : 'red'}
                              >
                                {item.review_status === 'approved' ? '已通过' : '已拒绝'}
                              </Tag>
                            ]
                          }
                        >
                          <List.Item.Meta
                            title={
                              <Space>
                                <Text strong>题目 {item.seq || item.id}</Text>
                                <Tag color="blue">
                                  {item.candidate_type === 'single' ? '单选题' :
                                   item.candidate_type === 'multiple' ? '多选题' :
                                   item.candidate_type === 'fill' ? '填空题' :
                                   item.candidate_type === 'subjective' ? '主观题' : '未知'}
                                </Tag>
                                {item.confidence && (
                                  <Tag color={item.confidence > 0.8 ? 'green' : item.confidence > 0.6 ? 'orange' : 'red'}>
                                    置信度: {(item.confidence * 100).toFixed(1)}%
                                  </Tag>
                                )}
                              </Space>
                            }
                            description={
                              <div style={{ marginTop: 8 }}>
                                <pre style={{ 
                                  fontFamily: 'inherit',
                                  fontSize: 'inherit',
                                  lineHeight: 'inherit',
                                  margin: 0,
                                  padding: 0,
                                  whiteSpace: 'pre-wrap',
                                  wordBreak: 'break-word',
                                  backgroundColor: 'transparent'
                                }}>
                                  {questionText || '识别文本为空'}
                                </pre>
                              </div>
                            }
                          />
                        </List.Item>
                      )
                    }}
                  />
                ) : (
                  <Empty description="暂无拆题项目" />
                )}
              </Card>
            ) : (
              <Alert
                message="请先选择一个拆分会话"
                description="从左侧会话列表中选择一个会话进行题目审核"
                type="info"
                showIcon
              />
            )
          }
        ]}
      />

      {/* 编辑题目弹窗 */}
      <Modal
        title="编辑题目"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={saveQuestion}
        >
          <Form.Item
            name="stem"
            label="题目内容"
            rules={[{ required: true, message: '请输入题目内容' }]}
          >
            <TextArea rows={4} placeholder="请输入或修改题目内容" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="type"
                label="题目类型"
                rules={[{ required: true, message: '请选择题目类型' }]}
              >
                <Select placeholder="请选择题目类型">
                  <Option value="single">单选题</Option>
                  <Option value="multiple">多选题</Option>
                  <Option value="fill">填空题</Option>
                  <Option value="subjective">主观题</Option>
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
                  <Option value={1}>1星 (很简单)</Option>
                  <Option value={2}>2星 (简单)</Option>
                  <Option value={3}>3星 (中等)</Option>
                  <Option value={4}>4星 (困难)</Option>
                  <Option value={5}>5星 (很困难)</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="analysis" label="题目解析">
            <TextArea rows={3} placeholder="请输入题目解析（可选）" />
          </Form.Item>

          <Divider />

          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                保存并入库
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
      </div>
    </ErrorBoundary>
  )
}