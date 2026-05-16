import pandas as pd
import sqlite3

class ResultCalculator:
    def __init__(self, db_path="database/students.db"):
        self.db_path = db_path
    
    def calculate_percentage(self, marks_obtained, max_marks):
        """Calculate percentage"""
        return (marks_obtained / max_marks) * 100
    
    def calculate_grade(self, percentage):
        """Calculate grade based on percentage"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'
    
    def get_student_report(self, student_id):
        """Generate complete report for a student"""
        conn = sqlite3.connect(self.db_path)
        
        # Get student info and marks
        query = '''
            SELECT s.name, s.class, s.section, s.roll_number,
                   sub.subject_name, r.marks_obtained, sub.max_marks
            FROM results r
            JOIN students s ON r.student_id = s.student_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE s.student_id = ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(student_id,))
        conn.close()
        
        if df.empty:
            return None
        
        # Calculate totals
        total_obtained = df['marks_obtained'].sum()
        total_max = df['max_marks'].sum()
        overall_percentage = (total_obtained / total_max) * 100
        
        # Subject-wise performance
        df['percentage'] = df.apply(
            lambda x: self.calculate_percentage(x['marks_obtained'], x['max_marks']), 
            axis=1
        )
        df['grade'] = df['percentage'].apply(self.calculate_grade)
        
        report = {
            'student_info': {
                'name': df['name'].iloc[0],
                'class': df['class'].iloc[0],
                'section': df['section'].iloc[0],
                'roll_number': df['roll_number'].iloc[0]
            },
            'subject_results': df[['subject_name', 'marks_obtained', 'max_marks', 'percentage', 'grade']],
            'summary': {
                'total_obtained': total_obtained,
                'total_max': total_max,
                'overall_percentage': round(overall_percentage, 2),
                'overall_grade': self.calculate_grade(overall_percentage),
                'subjects_passed': len(df[df['percentage'] >= 40]),
                'total_subjects': len(df)
            }
        }
        
        return report
    
    def get_class_rankings(self, class_name):
        """Generate class rankings based on performance"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT s.student_id, s.name, s.roll_number,
                   SUM(r.marks_obtained) as total_obtained,
                   SUM(sub.max_marks) as total_max
            FROM results r
            JOIN students s ON r.student_id = s.student_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE s.class = '{class_name}'
            GROUP BY s.student_id
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return None
        
        df['percentage'] = (df['total_obtained'] / df['total_max']) * 100
        df['grade'] = df['percentage'].apply(self.calculate_grade)
        df['rank'] = df['percentage'].rank(ascending=False, method='min').astype(int)
        
        return df.sort_values('rank')
