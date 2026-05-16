import xlwings as xw
import pandas as pd
from datetime import datetime

class ExcelExporter:
    def __init__(self):
        self.app = None
        self.wb = None
    
    def export_student_report(self, report, output_path):
        """Export individual student report to Excel"""
        self.app = xw.App(visible=True)
        self.wb = self.app.books.add()
        
        # Student info sheet
        info_sheet = self.wb.sheets[0]
        info_sheet.name = "Student Report"
        
        # Title
        info_sheet.range("A1").value = "STUDENT RESULT REPORT"
        info_sheet.range("A1").font.bold = True
        info_sheet.range("A1").font.size = 16
        info_sheet.range("A2").value = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Student details
        info = report['student_info']
        row = 4
        details = [
            ["Student Name", info['name']],
            ["Class", info['class']],
            ["Section", info['section']],
            ["Roll Number", info['roll_number']]
        ]
        
        for detail in details:
            info_sheet.range(f"A{row}").value = detail[0]
            info_sheet.range(f"A{row}").font.bold = True
            info_sheet.range(f"B{row}").value = detail[1]
            row += 1
        
        # Subject results table
        row += 2
        info_sheet.range(f"A{row}").value = "SUBJECT-WISE PERFORMANCE"
        info_sheet.range(f"A{row}").font.bold = True
        
        row += 1
        headers = ["Subject", "Marks Obtained", "Max Marks", "Percentage", "Grade"]
        for col, header in enumerate(headers, start=1):
            info_sheet.range((row, col)).value = header
            info_sheet.range((row, col)).font.bold = True
        
        # Add data
        for idx, subject in report['subject_results'].iterrows():
            row += 1
            info_sheet.range((row, 1)).value = subject['subject_name']
            info_sheet.range((row, 2)).value = subject['marks_obtained']
            info_sheet.range((row, 3)).value = subject['max_marks']
            info_sheet.range((row, 4)).value = f"{subject['percentage']:.2f}%"
            info_sheet.range((row, 5)).value = subject['grade']
        
        # Summary
        row += 2
        summary = report['summary']
        info_sheet.range(f"A{row}").value = "SUMMARY"
        info_sheet.range(f"A{row}").font.bold = True
        
        row += 1
        summary_data = [
            ["Total Marks Obtained", summary['total_obtained']],
            ["Total Maximum Marks", summary['total_max']],
            ["Overall Percentage", f"{summary['overall_percentage']}%"],
            ["Overall Grade", summary['overall_grade']],
            ["Subjects Passed", f"{summary['subjects_passed']}/{summary['total_subjects']}"]
        ]
        
        for data in summary_data:
            info_sheet.range(f"A{row}").value = data[0]
            info_sheet.range(f"B{row}").value = data[1]
            row += 1
        
        info_sheet.autofit()
        self.wb.save(output_path)
        print(f"✅ Report saved to: {output_path}")
        return self.wb
    
    def export_class_rankings(self, rankings_df, class_name, output_path):
        """Export class rankings to Excel"""
        self.app = xw.App(visible=True)
        self.wb = self.app.books.add()
        
        sheet = self.wb.sheets[0]
        sheet.name = f"Class {class_name} Rankings"
        
        # Title
        sheet.range("A1").value = f"CLASS {class_name} - RANKINGS"
        sheet.range("A1").font.bold = True
        sheet.range("A1").font.size = 16
        sheet.range("A2").value = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Headers
        headers = ["Rank", "Roll Number", "Student Name", "Total Obtained", "Total Max", "Percentage", "Grade"]
        for col, header in enumerate(headers, start=1):
            sheet.range((4, col)).value = header
            sheet.range((4, col)).font.bold = True
        
        # Data
        for idx, row in rankings_df.iterrows():
            row_num = idx + 5
            sheet.range((row_num, 1)).value = row['rank']
            sheet.range((row_num, 2)).value = row['roll_number']
            sheet.range((row_num, 3)).value = row['name']
            sheet.range((row_num, 4)).value = row['total_obtained']
            sheet.range((row_num, 5)).value = row['total_max']
            sheet.range((row_num, 6)).value = f"{row['percentage']:.2f}%"
            sheet.range((row_num, 7)).value = row['grade']
        
        sheet.autofit()
        self.wb.save(output_path)
        print(f"✅ Class rankings saved to: {output_path}")
        return self.wb
    
    def close(self):
        """Close Excel gracefully"""
        if self.wb:
            self.wb.close()
        if self.app:
            self.app.quit()
