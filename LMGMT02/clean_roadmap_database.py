"""
Clean Roadmap Database - Remove arr_week from stored roadmaps
This script cleans existing roadmap data in the database
"""
import sqlite3
import json
import re


def clean_roadmap_text(text: str) -> str:
    """Clean roadmap text by removing unwanted prefixes"""
    if not text:
        return text
    
    patterns_to_remove = [
        r'\.?arr[_\s]?[Ww]eek:?\s*',
        r'\.?[Aa]rr[_\s]?[Ww]eek:?\s*',
        r'\.?week[_\s]?title:?\s*',
        r'\.?week[_\s]?tasks:?\s*',
        r'\.?arr[_\s]?title:?\s*',
        r'\.?arr[_\s]?tasks:?\s*',
        r'^[Ww]eek\s+\d+\s*[-:]\s*',
        r'^[Ww]eek:?\s*',
        r'^\d+\.\s*',
        r'^-\s*',
        r'^\*\s*',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    text = ' '.join(text.split())
    text = text.lstrip('.')
    
    return text.strip()


def clean_database():
    """Clean all roadmap data in the database"""
    db_path = "frontend_users.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("="*70)
        print("Cleaning Roadmap Database")
        print("="*70)
        print()
        
        cleaned_count = 0
        
        # Clean learning_roadmaps table
        if 'learning_roadmaps' in tables:
            print("📋 Cleaning learning_roadmaps table...")
            
            cursor.execute("SELECT id, week_title, task_name FROM learning_roadmaps")
            rows = cursor.fetchall()
            
            for row_id, week_title, task_name in rows:
                cleaned_title = clean_roadmap_text(week_title) if week_title else week_title
                cleaned_task = clean_roadmap_text(task_name) if task_name else task_name
                
                if cleaned_title != week_title or cleaned_task != task_name:
                    cursor.execute("""
                        UPDATE learning_roadmaps 
                        SET week_title = ?, task_name = ?
                        WHERE id = ?
                    """, (cleaned_title, cleaned_task, row_id))
                    cleaned_count += 1
                    print(f"  ✅ Cleaned row {row_id}")
                    if week_title != cleaned_title:
                        print(f"     Title: '{week_title}' → '{cleaned_title}'")
                    if task_name != cleaned_task:
                        print(f"     Task: '{task_name}' → '{cleaned_task}'")
            
            conn.commit()
            print(f"✅ Cleaned {cleaned_count} rows in learning_roadmaps")
            print()
        
        # Clean generated_content table (roadmap_json field)
        if 'generated_content' in tables:
            print("📋 Cleaning generated_content table...")
            
            cursor.execute("SELECT id, roadmap_json FROM generated_content WHERE roadmap_json IS NOT NULL")
            rows = cursor.fetchall()
            
            json_cleaned = 0
            for row_id, roadmap_json in rows:
                if not roadmap_json:
                    continue
                
                try:
                    roadmap_data = json.loads(roadmap_json)
                    
                    if "weeks" in roadmap_data:
                        modified = False
                        
                        for week in roadmap_data["weeks"]:
                            if "title" in week:
                                original_title = week["title"]
                                cleaned_title = clean_roadmap_text(original_title)
                                if cleaned_title != original_title:
                                    week["title"] = cleaned_title
                                    modified = True
                            
                            if "tasks" in week:
                                cleaned_tasks = []
                                for task in week["tasks"]:
                                    cleaned_task = clean_roadmap_text(task)
                                    cleaned_tasks.append(cleaned_task)
                                    if cleaned_task != task:
                                        modified = True
                                week["tasks"] = cleaned_tasks
                        
                        if modified:
                            cleaned_json = json.dumps(roadmap_data)
                            cursor.execute("""
                                UPDATE generated_content 
                                SET roadmap_json = ?
                                WHERE id = ?
                            """, (cleaned_json, row_id))
                            json_cleaned += 1
                            print(f"  ✅ Cleaned JSON in row {row_id}")
                
                except json.JSONDecodeError:
                    print(f"  ⚠️  Skipped row {row_id} (invalid JSON)")
                    continue
            
            conn.commit()
            print(f"✅ Cleaned {json_cleaned} JSON roadmaps in generated_content")
            print()
        
        conn.close()
        
        print("="*70)
        print("✅ Database Cleaning Complete!")
        print("="*70)
        print()
        print(f"Total items cleaned: {cleaned_count + json_cleaned}")
        print()
        print("Next steps:")
        print("1. Restart your Streamlit app")
        print("2. Navigate to Learn page")
        print("3. Check the Roadmap tab")
        print("4. ✅ arr_week text should be gone!")
        print()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print()
    print("This script will clean all roadmap data in your database")
    print("to remove 'arr_week' and similar internal variable names.")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        clean_database()
    else:
        print("❌ Cancelled")
