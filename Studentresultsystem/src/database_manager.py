import sqlite3
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="database/students.db"):
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                section TEXT,
                roll_number INTEGER UNIQUE
            )
        ''')
        
        # Subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY,
                subject_name TEXT UNIQUE,
                max_marks INTEGER DEFAULT 100
            )
        ''')
        
        # Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY,
                student_id INTEGER,
                subject_id INTEGER,
                marks_obtained INTEGER,
                exam_date TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database tables created successfully")
    
    def add_student(self, name, class_name, section, roll_number):
        """Add a new student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (name, class, section, roll_number)
                VALUES (?, ?, ?, ?)
            ''', (name, class_name, section, roll_number))
            conn.commit()
            student_id = cursor.lastrowid
            print(f"✅ Student added: {name} (ID: {student_id})")
            return student_id
        except sqlite3.IntegrityError:
            print(f"❌ Roll number {roll_number} already exists!")
            return None
        finally:
            conn.close()
    
    def add_subject(self, subject_name, max_marks=100):
        """Add a new subject"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO subjects (subject_name, max_marks)
                VALUES (?, ?)
            ''', (subject_name, max_marks))
            conn.commit()
            print(f"✅ Subject added: {subject_name}")
        except sqlite3.IntegrityError:
            print(f"❌ Subject '{subject_name}' already exists!")
        finally:
            conn.close()
    
    def add_result(self, student_id, subject_id, marks_obtained):
        """Add marks for a student in a subject"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check max marks
        cursor.execute('SELECT max_marks FROM subjects WHERE subject_id = ?', (subject_id,))
        max_marks = cursor.fetchone()[0]
        
        if marks_obtained > max_marks:
            print(f"❌ Marks cannot exceed {max_marks}")
            return False
        
        exam_date = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT INTO results (student_id, subject_id, marks_obtained, exam_date)
            VALUES (?, ?, ?, ?)
        ''', (student_id, subject_id, marks_obtained, exam_date))
        
        conn.commit()
        conn.close()
        print(f"✅ Result added for student {student_id}")
        return True
    
    def get_all_students(self):
        """Get all students as DataFrame"""
        query = "SELECT * FROM students"
        return pd.read_sql_query(query, sqlite3.connect(self.db_path))
    
    def get_student_results(self, student_id):
        """Get complete results for a student"""
        query = f'''
            SELECT s.name, s.class, s.section, s.roll_number,
                   sub.subject_name, r.marks_obtained, sub.max_marks
            FROM results r
            JOIN students s ON r.student_id = s.student_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE s.student_id = {student_id}
        '''
        return pd.read_sql_query(query, sqlite3.connect(self.db_path))
    
    def get_class_results(self, class_name):
        """Get results for entire class"""
        query = f'''
            SELECT s.name, s.roll_number, sub.subject_name, r.marks_obtained
            FROM results r
            JOIN students s ON r.student_id = s.student_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE s.class = '{class_name}'
            ORDER BY s.roll_number
        '''
        return pd.read_sql_query(query, sqlite3.connect(self.db_path))
