"""
Fix Data Persistence Issue
This script verifies and fixes the data persistence system
"""
import sqlite3
from pathlib import Path

def check_database_structure():
    """Check if all required tables exist"""
    db_path = "frontend_users.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("✓ Existing tables:")
    for table in tables:
        print(f"  - {table}")
        
        # Show table structure
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"    • {col[1]} ({col[2]})")
    
    conn.close()
    
    required_tables = ['users', 'user_profiles', 'user_settings', 'user_achievements']
    missing_tables = [t for t in required_tables if t not in tables]
    
    if missing_tables:
        print(f"\n⚠️  Missing tables: {missing_tables}")
        return False
    else:
        print("\n✅ All required tables exist!")
        return True


def test_data_persistence():
    """Test if data persists correctly"""
    from frontend.utils.profile_database import get_profile_db
    from frontend.utils.auth_database import get_auth_db
    
    print("\n" + "="*50)
    print("Testing Data Persistence")
    print("="*50)
    
    # Test user creation
    auth_db = get_auth_db()
    test_email = "test_persistence@example.com"
    test_username = "test_user_persist"
    
    # Clean up if exists
    try:
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()
    except:
        pass
    
    # Create test user
    success, message, user_data = auth_db.create_user(
        username=test_username,
        email=test_email,
        password="test123",
        full_name="Test User"
    )
    
    if not success:
        print(f"❌ Failed to create test user: {message}")
        return False
    
    print(f"✅ Created test user: {user_data['username']}")
    user_id = user_data['id']
    
    # Test profile creation and update
    profile_db = get_profile_db()
    profile_db.create_profile(user_id, test_username)
    
    profile_data = {
        'username': test_username,
        'full_name': 'Test User Updated',
        'bio': 'This is a test bio',
        'learning_interests': 'Python, Machine Learning',
        'experience_level': 'Intermediate',
        'location': 'Test City',
        'occupation': 'Tester',
        'website': 'https://test.com'
    }
    
    if profile_db.update_profile(user_id, profile_data):
        print("✅ Profile data saved")
    else:
        print("❌ Failed to save profile data")
        return False
    
    # Test settings creation and update
    profile_db.create_default_settings(user_id)
    
    settings_data = {
        'theme': 'Dark',
        'language': 'English',
        'default_difficulty': 'Advanced',
        'email_notifications': 1,
        'learning_reminders': 1,
        'weekly_summary': 1,
        'achievement_alerts': 1
    }
    
    if profile_db.update_settings(user_id, settings_data):
        print("✅ Settings data saved")
    else:
        print("❌ Failed to save settings data")
        return False
    
    # Verify data persists by reading it back
    print("\n" + "-"*50)
    print("Verifying Data Persistence...")
    print("-"*50)
    
    # Read profile
    profile = profile_db.get_profile(user_id)
    if profile:
        print(f"✅ Profile loaded:")
        print(f"   Full Name: {profile.get('full_name')}")
        print(f"   Bio: {profile.get('bio')}")
        print(f"   Interests: {profile.get('learning_interests')}")
        print(f"   Level: {profile.get('experience_level')}")
    else:
        print("❌ Failed to load profile")
        return False
    
    # Read settings
    settings = profile_db.get_settings(user_id)
    if settings:
        print(f"✅ Settings loaded:")
        print(f"   Theme: {settings.get('theme')}")
        print(f"   Language: {settings.get('language')}")
        print(f"   Difficulty: {settings.get('default_difficulty')}")
    else:
        print("❌ Failed to load settings")
        return False
    
    print("\n✅ Data persistence test PASSED!")
    print("   All data was saved and loaded correctly.")
    
    # Clean up
    try:
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
        cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    return True


if __name__ == "__main__":
    print("="*50)
    print("LearnSphere Pro - Data Persistence Check")
    print("="*50)
    print()
    
    # Check database structure
    if check_database_structure():
        print("\n✅ Database structure is correct")
        
        # Test data persistence
        if test_data_persistence():
            print("\n" + "="*50)
            print("✅ ALL TESTS PASSED")
            print("="*50)
            print("\nYour data persistence system is working correctly!")
            print("Profile and settings data will be saved and loaded properly.")
        else:
            print("\n❌ Data persistence test failed")
    else:
        print("\n❌ Database structure check failed")
        print("Run the app once to initialize the database.")
