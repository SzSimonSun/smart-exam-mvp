import React, { useState } from 'react'
import { Card, Form, Input, Button, Select, Table, Space, Row, Col, Steps, message, Divider, Tag } from 'antd'
import { PlusOutlined, DeleteOutlined, ExportOutlined, EyeOutlined } from '@ant-design/icons'
import { usePapers, usePaper } from '../hooks/usePapers'
import { useQuestions } from '../hooks/useQuestions'
import { useKnowledgePoints, useSubjects } from '../hooks/useKnowledgePoints'

const { Option } = Select
const { Step } = Steps
const { TextArea } = Input

export default function PaperBuilder() {
  const [currentStep, setCurrentStep] = useState(0)
  const [selectedPaper, setSelectedPaper] = useState(null)
  const [questionFilters, setQuestionFilters] = useState({})
  const [selectedQuestions, setSelectedQuestions] = useState([])
  const [form] = Form.useForm()
  
  // 使用hooks
  const { papers, createPaper, exportPaper } = usePapers()
  const { paper, updatePaperQuestions } = usePaper(selectedPaper?.id)
  const { questions } = useQuestions(questionFilters)
  const subjects = useSubjects()

  // 步骤
  const steps = [
    { title: '基本信息', description: '设置试卷名称和参数' },
    { title: '选择题目', description: '从题库中选择题目' },
    { title: '试卷预览', description: '预览和导出PDF' }
  ]

  // 创建试卷
  const handleCreatePaper = async (values) => {
    try {
      const paperData = {
        ...values,
        layout_json: {
          sections: [
            { name: '选择题', type: 'single' },
            { name: '填空题', type: 'fill' },
            { name: '判断题', type: 'judge' }
          ]
        }
      }
      const newPaper = await createPaper(paperData)
      setSelectedPaper(newPaper)
      setCurrentStep(1)
      message.success('试卷创建成功！')
    } catch (error) {
      console.error('创建试卷失败:', error)
    }
  }

  // 导出PDF (简化版)
  const handleExportPDF = async () => {
    try {
      // 模拟导出PDF
      message.success('试卷导出成功！')
    } catch (error) {
      console.error('导出失败:', error)
    }
  }

  return (
    <Card title="试卷构建" style={{ marginBottom: 16 }}>
      <div style={{ textAlign: 'center', padding: 40 }}>
        <h3>试卷构建功能</h3>
        <p>完整的试卷构建功能正在开发中...</p>
        
        <div style={{ marginTop: 24 }}>
          <Button type="primary" style={{ marginRight: 8 }}>
            创建新试卷
          </Button>
          <Button icon={<ExportOutlined />} onClick={handleExportPDF}>
            导出PDF
          </Button>
        </div>
        
        <div style={{ marginTop: 24, padding: 16, backgroundColor: '#f6f8fa', borderRadius: 4 }}>
          <h4>预计功能：</h4>
          <ul style={{ textAlign: 'left', display: 'inline-block' }}>
            <li>试卷基本信息设置</li>
            <li>从题库选择题目</li>
            <li>题目分值配置</li>
            <li>试卷预览</li>
            <li>PDF导出</li>
          </ul>
        </div>
      </div>
    </Card>
  )
}
