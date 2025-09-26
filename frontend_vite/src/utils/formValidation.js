import React from 'react'
import { ProForm, ProFormText, ProFormTextArea, ProFormSelect, ProFormDigit } from '@ant-design/pro-form'
import { message } from 'antd'

// 表单验证规则
export const formRules = {
  required: { required: true, message: '此字段为必填项' },
  email: {
    type: 'email',
    message: '请输入有效的邮箱地址'
  },
  phone: {
    pattern: /^1[3-9]\d{9}$/,
    message: '请输入有效的手机号码'
  },
  password: {
    min: 6,
    max: 20,
    message: '密码长度应在6-20位之间'
  },
  positiveNumber: {
    min: 1,
    message: '必须是正数'
  },
  maxLength: (max) => ({
    max,
    message: `最多输入${max}个字符`
  }),
  minLength: (min) => ({
    min,
    message: `至少输入${min}个字符`
  }),
  range: (min, max) => ({
    min,
    max,
    message: `长度应在${min}-${max}之间`
  })
}

// 异步验证器
export const asyncValidators = {
  // 检查邮箱是否已存在
  checkEmailExists: async (_, value) => {
    if (!value) return Promise.resolve()
    
    // 模拟API调用
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (value === 'admin@example.com') {
          reject(new Error('该邮箱已被使用'))
        } else {
          resolve()
        }
      }, 300)
    })
  },

  // 检查试卷名称是否重复
  checkPaperNameExists: async (_, value) => {
    if (!value) return Promise.resolve()
    
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (value === '重复试卷名') {
          reject(new Error('试卷名称已存在'))
        } else {
          resolve()
        }
      }, 300)
    })
  }
}

// 表单提交处理
export const handleFormSubmit = async (values, submitFn, options = {}) => {
  const { 
    successMessage = '操作成功',
    errorMessage = '操作失败',
    resetForm = true,
    redirect = null
  } = options

  try {
    const result = await submitFn(values)
    message.success(successMessage)
    
    if (resetForm && typeof resetForm === 'function') {
      resetForm()
    }
    
    if (redirect) {
      window.location.href = redirect
    }
    
    return result
  } catch (error) {
    console.error('Form submit error:', error)
    // 错误已在api.js中统一处理，这里不需要重复显示
    throw error
  }
}

// 通用表单配置
export const commonFormProps = {
  labelCol: { span: 6 },
  wrapperCol: { span: 18 },
  layout: 'horizontal',
  autoComplete: 'off',
  validateTrigger: ['onBlur', 'onChange'],
  preserve: false, // 卸载时清理字段值
  requiredMark: true,
  submitter: {
    searchConfig: {
      submitText: '提交',
      resetText: '重置',
    },
    resetButtonProps: {
      style: {
        display: 'none', // 默认隐藏重置按钮
      },
    },
  },
}

// Pro表单组件配置
export const proFormProps = {
  ...commonFormProps,
  grid: true,
  rowProps: {
    gutter: [16, 16],
  },
  colProps: {
    span: 24,
  },
}

// 表单字段验证集合
export const getFieldRules = (fieldType, options = {}) => {
  const rules = [formRules.required]
  
  switch (fieldType) {
    case 'email':
      rules.push(formRules.email)
      if (options.checkExists) {
        rules.push({ validator: asyncValidators.checkEmailExists })
      }
      break
      
    case 'password':
      rules.push(formRules.password)
      break
      
    case 'phone':
      rules.push(formRules.phone)
      break
      
    case 'text':
      if (options.maxLength) {
        rules.push(formRules.maxLength(options.maxLength))
      }
      if (options.minLength) {
        rules.push(formRules.minLength(options.minLength))
      }
      break
      
    case 'number':
      if (options.positive) {
        rules.push(formRules.positiveNumber)
      }
      break
      
    default:
      break
  }
  
  return rules
}

// 导出常用的Pro表单组件配置
export const ProFormComponents = {
  Text: ProFormText,
  TextArea: ProFormTextArea,
  Select: ProFormSelect,
  Number: ProFormDigit,
}

export default {
  formRules,
  asyncValidators,
  handleFormSubmit,
  commonFormProps,
  proFormProps,
  getFieldRules,
  ProFormComponents
}