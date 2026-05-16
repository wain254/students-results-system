import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from result_calculator import ResultCalculator
from excel_exporter import ExcelExporter

def setup_sample_data(db):
    """Add sample data to demonstrate the system"""
    
    # Add subjects
    subjects = ['Mathematics', 'Physics', 'Chemistry', 'English', 'Computer Science']
    for subject in subjects:
        db.add_subject(subject, 100)
    
    # Add students
    students = [
        ("Alice Johnson", "10", "A", 1),
        ("Bob Smith", "10", "A", 2),
        ("Charlie Brown", "10", "A", 3),
        ("Diana Prince", "10", "A", 4),
        ("Evan Wright", "10", "A", 5)
    ]
    
    student_ids = []
    for student in students:
        student_id = db.add_student(*student)
        if student_id:
            student_ids.append(student_id)
    
    # Add sample results (marks for each student in each subject)
    import random
    for student_id in student_ids:
        for subject_id in range(1, 6):  # 5 subjects
            marks = random.randint(60, 98)
            db.add_result(student_id, subject_id, marks)
    
    print("\n✅ Sample data added successfully!")
    print(f"📚 {len(subjects)} subjects added")
    print(f"👨‍🎓 {len(student_ids)} students added")
    print(f"📊 {len(student_ids) * 5} results recorded")

def main():
    print("=" * 50)
    print("🎓 STUDENT RESULT MANAGEMENT SYSTEM")
    print("=" * 50)
    
    # Initialize
    db = DatabaseManager()
    calculator = ResultCalculator()
    exporter = ExcelExporter()
    
    # Create output directory
    os.makedirs("excel_reports", exist_ok=True)
    
    # Check if database is empty
    students_df = db.get_all_students()
    if students_df.empty:
        print("\n📝 No data found. Setting up sample data...")
        setup_sample_data(db)
    
    while True:
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. View Student Report")
        print("2. View Class Rankings")
        print("3. Add New Student")
        print("4. Add New Result")
        print("5. View All Students")
        print("6. Export to Excel")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            student_id = int(input("Enter Student ID: "))
            report = calculator.get_student_report(student_id)
            
            if report:
                print("\n" + "=" * 40)
                print(f"📊 REPORT FOR {report['student_info']['name']}")
                print("=" * 40)
                print(f"Class: {report['student_info']['class']}-{report['student_info']['section']}")
                print(f"Roll Number: {report['student_info']['roll_number']}")
                print("\n📚 Subject Results:")
                print(report['subject_results'].to_string(index=False))
                print("\n📈 Summary:")
                for key, value in report['summary'].items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            else:
                print(f"❌ No results found for Student ID {student_id}")
        
        elif choice == '2':
            class_name = input("Enter Class (e.g., 10): ")
            rankings = calculator.get_class_rankings(class_name)
            
            if rankings is not None:
                print("\n" + "=" * 40)
                print(f"🏆 CLASS {class_name} RANKINGS")
                print("=" * 40)
                print(rankings[['rank', 'roll_number', 'name', 'percentage', 'grade']].to_string(index=False))
            else:
                print(f"❌ No data found for Class {class_name}")
        
        elif choice == '3':
            name = input("Student Name: ")
            class_name = input("Class: ")
            section = input("Section: ")
            roll_number = int(input("Roll Number: "))
            db.add_student(name, class_name, section, roll_number)
        
        elif choice == '4':
            student_id = int(input("Student ID: "))
            print("Available Subjects:")
            print("1. Mathematics (ID: 1)")
            print("2. Physics (ID: 2)")
            print("3. Chemistry (ID: 3)")
            print("4. English (ID: 4)")
            print("5. Computer Science (ID: 5)")
            subject_id = int(input("Subject ID: "))
            marks = int(input("Marks Obtained: "))
            db.add_result(student_id, subject_id, marks)
        
        elif choice == '5':
            students = db.get_all_students()
            print("\n📋 ALL STUDENTS:")
            print(students.to_string(index=False))
        
        elif choice == '6':
            print("\n📁 EXPORT TO EXCEL")
            print("1. Export Individual Student Report")
            print("2. Export Class Rankings")
            
            export_choice = input("Choose: ")
            
            if export_choice == '1':
                student_id = int(input("Student ID: "))
                report = calculator.get_student_report(student_id)
                if report:
                    filename = f"excel_reports/Student_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    wb = exporter.export_student_report(report, filename)
                    print(f"\n✨ Report generated! Excel will open automatically.")
                    input("\nPress Enter to close Excel...")
                    exporter.close()
                else:
                    print("❌ Student not found")
            
            elif export_choice == '2':
                class_name = input("Class: ")
                rankings = calculator.get_class_rankings(class_name)
                if rankings is not None:
                    filename = f"excel_reports/Class_{class_name}_Rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    wb = exporter.export_class_rankings(rankings, class_name, filename)
                    print(f"\n✨ Rankings exported! Excel will open automatically.")
                    input("\nPress Enter to close Excel...")
                    exporter.close()
                else:
                    print("❌ No data found")
        
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
