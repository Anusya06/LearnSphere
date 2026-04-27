"""
Persistent Authentication Database
SQLite-based user authentication with bcrypt password hashing
"""
import sqlite3
import bcrypt
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple
import base64


class AuthDatabase:
    """Handle all authentication database operations"""
    
    def __init__(self, db_path: str = "frontend_users.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Create users table if it doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                full_name TEXT,
                password_hash TEXT NOT NULL,
                profile_picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                theme_preference TEXT DEFAULT 'light',
                total_time_spent REAL DEFAULT 0.0,
                streak_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = None,
        profile_picture: str = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Create a new user
        Returns: (success, message, user_data)
        """
        # Validate inputs
        if not username or not email or not password:
            return False, "All fields are required", None
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters", None
        
        # Check if email exists
        if self.email_exists(email):
            return False, "This email is already registered. Please login.", None
        
        # Check if username exists
        if self.username_exists(username):
            return False, "This username is already taken. Please choose another.", None
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Generate default profile picture if not provided
        if not profile_picture:
            profile_picture = f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
        
        # Insert user
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, email, full_name, password_hash, profile_picture, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, full_name, password_hash, profile_picture, datetime.now()))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Get user data
            user_data = self.get_user_by_id(user_id)
            
            return True, "Account created successfully!", user_data
            
        except sqlite3.IntegrityError as e:
            return False, f"Registration failed: {str(e)}", None
        except Exception as e:
            return False, f"An error occurred: {str(e)}", None
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user with email and password
        Returns: (success, message, user_data)
        """
        if not email or not password:
            return False, "Email and password are required", None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user by email
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "Invalid email or password", None
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            conn.close()
            return False, "Invalid email or password", None
        
        # Check if account is active
        if not user['is_active']:
            conn.close()
            return False, "Account is deactivated. Please contact support.", None
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = ? WHERE id = ?
        """, (datetime.now(), user['id']))
        
        conn.commit()
        conn.close()
        
        # Convert to dictionary
        user_data = dict(user)
        # Remove password hash from returned data
        user_data.pop('password_hash', None)
        
        return True, "Login successful!", user_data
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            user_data = dict(user)
            user_data.pop('password_hash', None)
            return user_data
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            user_data = dict(user)
            user_data.pop('password_hash', None)
            return user_data
        return None
    
    def update_user_profile(
        self,
        user_id: int,
        full_name: str = None,
        profile_picture: str = None,
        theme_preference: str = None
    ) -> bool:
        """Update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if full_name is not None:
            updates.append("full_name = ?")
            params.append(full_name)
        
        if profile_picture is not None:
            updates.append("profile_picture = ?")
            params.append(profile_picture)
        
        if theme_preference is not None:
            updates.append("theme_preference = ?")
            params.append(theme_preference)
        
        if not updates:
            conn.close()
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False
    
    def update_user_stats(
        self,
        user_id: int,
        total_time_spent: float = None,
        streak_count: int = None
    ) -> bool:
        """Update user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if total_time_spent is not None:
            updates.append("total_time_spent = ?")
            params.append(total_time_spent)
        
        if streak_count is not None:
            updates.append("streak_count = ?")
            params.append(streak_count)
        
        if not updates:
            conn.close()
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False
    
    def verify_password_by_user_id(self, user_id: int, password_hash: str) -> bool:
        """Verify password hash for a user by user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
            
            # Compare hashes directly (for SHA-256 hashes from settings page)
            conn.close()
            return result['password_hash'] == password_hash or self.verify_password_hash_match(password_hash, result['password_hash'])
        except Exception:
            conn.close()
            return False
    
    def verify_password_hash_match(self, provided_hash: str, stored_hash: str) -> bool:
        """Check if provided hash matches stored hash (for SHA-256 compatibility)"""
        # If stored hash is bcrypt, we can't compare directly
        # This is for SHA-256 hashes from settings page
        return provided_hash == stored_hash
    
    def update_password_hash(self, user_id: int, new_password_hash: str) -> bool:
        """Update password hash directly (for SHA-256 from settings)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current password hash
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "User not found"
        
        # Verify old password
        if not self.verify_password(old_password, result['password_hash']):
            conn.close()
            return False, "Current password is incorrect"
        
        # Hash new password
        new_hash = self.hash_password(new_password)
        
        # Update password
        try:
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            conn.close()
            return True, "Password changed successfully"
        except Exception as e:
            conn.close()
            return False, f"Error changing password: {str(e)}"
    
    def save_profile_picture(self, user_id: int, uploaded_file) -> Tuple[bool, str]:
        """Save uploaded profile picture"""
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = Path("frontend/uploads/profile_pictures")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            file_extension = uploaded_file.name.split('.')[-1]
            filename = f"user_{user_id}.{file_extension}"
            filepath = upload_dir / filename
            
            # Save file
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Update database
            relative_path = f"uploads/profile_pictures/{filename}"
            if self.update_user_profile(user_id, profile_picture=relative_path):
                return True, relative_path
            else:
                return False, "Failed to update database"
                
        except Exception as e:
            return False, f"Error saving file: {str(e)}"
    
    def get_all_users_count(self) -> int:
        """Get total number of users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        
        conn.close()
        return result['count'] if result else 0


# Global database instance
_db_instance = None

def get_auth_db() -> AuthDatabase:
    """Get global auth database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = AuthDatabase()
    return _db_instance
