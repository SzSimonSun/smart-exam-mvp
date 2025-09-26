import React, { useState, useRef } from 'react'
import { ProTable } from '@ant-design/pro-table'
import { ProForm, ProFormTextArea, ProFormSelect, ProFormDigit } from '@ant-design/pro-form'
import { Card, Button, Drawer, message, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { useQuestions } from '../hooks/useQuestions'
import { useKnowledgePoints } from '../hooks/useKnowledgePoints'

const QuestionBankPro = () => {
  const [drawerVisible, setDrawerVisible] = useState(false)
  const [editingQuestion, setEditingQuestion] = useState(null)
  const tableRef = useRef()
  const [formRef] = ProForm.useForm()
  
  const { questions, loading, createQuestion, updateQuestion, deleteQuestion } = useQuestions()
  const { knowledgePoints } = useKnowledgePoints()
  
  const handleSubmit = async (values) => {
    try {
      if (editingQuestion) {
        await updateQuestion(editingQuestion.id, values)
        message.success('题目更新成功')
      } else {
        await createQuestion(values)
        message.success('题目创建成功')
      }
      
      formRef.resetFields()
      setDrawerVisible(false)
      setEditingQuestion(null)
      tableRef.current?.reload()
    } catch (error) {
      // 错误已在api.js中处理
    }
  }
  
  const columns = [
    {
      title: '题目内容',
      dataIndex: 'stem',
      ellipsis: true,
      width: 300,
      copyable: true
    },
    {
      title: '类型',
      dataIndex: 'type',
      width: 100,
      valueType: 'select',
      valueEnum: {
        single: { text: '单选题', status: 'Processing' },
        multiple: { text: '多选题', status: 'Warning' },
        fill: { text: '填空题', status: 'Default' },
        subjective: { text: '主观题', status: 'Error' }
      }
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      width: 80,
      valueType: 'select',
      valueEnum: {
        1: { text: '简单', status: 'Success' },
        2: { text: '中等', status: 'Processing' },
        3: { text: '困难', status: 'Warning' }
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueType: 'select',
      valueEnum: {
        draft: { text: '草稿', status: 'Default' },
        published: { text: '已发布', status: 'Success' }
      }
    },
    {
      title: '操作',
      valueType: 'option',
      width: 150,
      render: (_, record) => [
        <Button 
          key="edit" 
          type="link" 
          icon={<EditOutlined />} 
          onClick={() => {
            setEditingQuestion(record)
            formRef.setFieldsValue(record)
            setDrawerVisible(true)
          }}
        >
          编辑
        </Button>,
        <Popconfirm 
          key="delete" 
          title="确定删除？" 
          onConfirm={() => deleteQuestion(record.id)}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ]
    }
  ]
  
  return (
    <Card>
      <ProTable
        actionRef={tableRef}
        columns={columns}
        dataSource={questions}
        loading={loading}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button 
            key="create" 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={() => {
              setEditingQuestion(null)
              formRef.resetFields()
              setDrawerVisible(true)
            }}
          >
            新建题目
          </Button>
        ]}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/总共 ${total} 条`
        }}
      />
      
      <Drawer
        title={editingQuestion ? '编辑题目' : '新建题目'}
        width={720}
        open={drawerVisible}
        onClose={() => {
          setDrawerVisible(false)
          setEditingQuestion(null)
        }}
      >
        <ProForm 
          form={formRef} 
          layout="vertical" 
          onFinish={handleSubmit}
          submitter={{
            searchConfig: {
              submitText: editingQuestion ? '更新' : '创建',
              resetText: '重置'
            }
          }}
        >
          <ProFormTextArea 
            name="stem" 
            label="题目内容" 
            rules={[{ required: true, message: '请输入题目内容' }]}
            fieldProps={{ rows: 4, placeholder: '请输入题目内容' }}
          />
          <ProFormSelect 
            name="type" 
            label="题目类型" 
            rules={[{ required: true, message: '请选择题目类型' }]}
            options={[
              { label: '单选题', value: 'single' },
              { label: '多选题', value: 'multiple' },
              { label: '填空题', value: 'fill' },
              { label: '主观题', value: 'subjective' }
            ]}
            placeholder="请选择题目类型"
          />
          <ProFormDigit 
            name="difficulty" 
            label="难度等级" 
            min={1} 
            max={5} 
            rules={[{ required: true, message: '请选择难度等级' }]}
            fieldProps={{ precision: 0 }}
            placeholder="1-5，数字越大难度越高"
          />
        </ProForm>
      </Drawer>
    </Card>
  )
}

export default QuestionBankPro