"""
PDF试卷生成服务 - 简化版本
"""
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # 题目样式
        self.question_style = ParagraphStyle(
            'CustomQuestion',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            spaceBefore=10
        )
        
        # 选项样式
        self.option_style = ParagraphStyle(
            'CustomOption',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20
        )
    
    def create_header(self, paper_info: Dict[str, Any], page_num: int = 1) -> List:
        """
        创建页眉
        
        Args:
            paper_info: 试卷信息
            page_num: 页码
            
        Returns:
            页眉元素列表
        """
        elements = []
        
        # 创建页眉表格
        header_data = [
            [f"试卷: {paper_info['name']}", f"第{page_num}页"],
            [f"科目: {paper_info.get('subject', '')}", f"时间: {paper_info.get('duration', 90)}分钟"],
        ]
        
        header_table = Table(header_data, colWidths=[120*mm, 50*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 10*mm))
        
        return elements
    
    def format_question(self, question: Dict[str, Any], seq: int) -> List:
        """
        格式化单个题目
        
        Args:
            question: 题目数据
            seq: 题目序号
            
        Returns:
            题目元素列表
        """
        elements = []
        
        # 题目标题
        question_title = f"{seq}. {question['stem']}"
        elements.append(Paragraph(question_title, self.question_style))
        
        # 选择题选项
        if question['type'] in ['single', 'multiple']:
            options = question.get('options_json', {})
            if isinstance(options, dict):
                for key, value in sorted(options.items()):
                    option_text = f"{key}. {value}"
                    elements.append(Paragraph(option_text, self.option_style))
        
        # 填空题/主观题预留空间
        elif question['type'] in ['fill', 'subjective']:
            # 添加答题区域
            answer_space = "答案：" + "_" * 50
            elements.append(Paragraph(answer_space, self.option_style))
            elements.append(Spacer(1, 20))
        
        # 判断题
        elif question['type'] == 'judge':
            judge_options = "A. 正确    B. 错误"
            elements.append(Paragraph(judge_options, self.option_style))
        
        # 添加题目间距
        elements.append(Spacer(1, 10))
        
        return elements
    
    def generate_paper_pdf(self, paper_info: Dict[str, Any], questions: List[Dict[str, Any]]) -> str:
        """
        生成试卷PDF
        
        Args:
            paper_info: 试卷信息
            questions: 题目列表
            
        Returns:
            生成的PDF文件路径
        """
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=25*mm
        )
        
        elements = []
        
        # 添加页眉
        header_elements = self.create_header(paper_info, page_num=1)
        elements.extend(header_elements)
        
        # 试卷标题
        title = f"{paper_info['name']}"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 20))
        
        # 试卷信息
        info_text = f"科目：{paper_info.get('subject', '')} | 年级：{paper_info.get('grade', '')} | 时长：{paper_info.get('duration', 90)}分钟 | 总分：{paper_info.get('total_score', 100)}分"
        info_style = ParagraphStyle(
            'Info',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(info_text, info_style))
        elements.append(Spacer(1, 20))
        
        # 添加题目
        for i, question in enumerate(questions, 1):
            question_elements = self.format_question(question, i)
            elements.extend(question_elements)
            
            # 每5题后添加更多空间
            if i % 5 == 0:
                elements.append(Spacer(1, 20))
        
        # 生成PDF
        doc.build(elements)
        
        return pdf_path
    
    def generate_answer_sheet_qr(self, paper_id: int, area: str = "answer") -> Dict[str, Any]:
        """
        生成答题卡二维码schema
        
        Args:
            paper_id: 试卷ID
            area: 区域标识
            
        Returns:
            二维码schema数据
        """
        return {
            "paper_id": paper_id,
            "page": 1,
            "area": area,
            "timestamp": datetime.now().isoformat()
        }