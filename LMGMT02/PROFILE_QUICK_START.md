# 🚀 Profile System - Quick Start Guide

## Start Testing NOW (3 Steps)

### Step 1: Start the App
```bash
cd frontend
streamlit run Home.py
```

### Step 2: Login and Navigate
1. Login with your credentials
2. Click **"👤 Profile"** in sidebar

### Step 3: Test Features

---

## Quick Tests

### ✅ Test 1: Edit Profile (2 minutes)
1. Click **"✏️ Edit Profile"** tab
2. Fill in your information:
   - Full Name: Your name
   - Bio: A short description
   - Learning Interests: Your interests (comma-separated)
   - Experience Level: Select your level
3. Click **"💾 Save Profile"**
4. Should see: ✅ "Profile saved successfully!"
5. **Logout and login again**
6. Profile should still show your data ✅

### ✅ Test 2: Upload Profile Picture (1 minute)
1. In **"✏️ Edit Profile"** tab
2. Scroll to **"📸 Profile Picture"**
3. Click **"Upload Profile Picture"**
4. Select an image (PNG/JPG)
5. Preview should appear
6. Click **"💾 Save Profile Picture"**
7. Profile header should update ✅
8. **Logout and login again**
9. Picture should still be there ✅

### ✅ Test 3: Change Settings (1 minute)
1. Click **"⚙️ Settings"** tab
2. Change some settings:
   - Theme: Select different theme
   - Default Difficulty: Change level
   - Toggle some notifications
3. Click **"💾 Save Settings"**
4. Should see: ✅ "Settings saved successfully!"
5. **Logout and login again**
6. Settings should be preserved ✅

### ✅ Test 4: View Achievements (30 seconds)
1. Click **"🏆 Achievements"** tab
2. Should see 8 achievements
3. Some should be unlocked (colored)
4. Some should be locked (grayed out)
5. Unlocked achievements based on your activity ✅

### ✅ Test 5: Check Statistics (30 seconds)
1. Click **"📊 Statistics"** tab
2. Should see real numbers:
   - Topics Learned: Your actual count
   - Quizzes Taken: Your actual count
   - Average Score: Your actual average
   - Tasks Completed: Your actual count
3. Should see recent activity feed
4. Shows your recent topics and quizzes ✅

---

## What to Look For

### ✅ Profile Header
- Shows your uploaded picture or default avatar
- Shows your full name (or username if not set)
- Shows your username and email
- Shows experience level badge
- Shows bio if you entered one

### ✅ Sidebar Stats
- **Topics Learned**: Real count from database
- **Quizzes Taken**: Real count from database
- **Average Score**: Calculated from your quizzes
- **Tasks Done**: Real count from roadmaps

### ✅ Data Persistence
- All changes save to database
- Data loads automatically on login
- No data loss on page refresh
- Works across different sessions

---

## Common Issues

### Profile Picture Not Showing?
- Make sure file is PNG, JPG, or JPEG
- File size should be reasonable (< 5MB)
- Click "Save Profile Picture" after upload
- Refresh page to see changes

### Statistics Showing Zero?
- Generate some topics in Learn page
- Take some quizzes in Quiz page
- Complete some roadmap tasks
- Then check Statistics tab again

### Settings Not Saving?
- Make sure to click "Save Settings" button
- Check for success message
- Logout and login to verify

---

## Integration with Other Pages

### Learn Page
- Generate topics → Updates "Topics Learned"
- Complete roadmap tasks → Updates "Tasks Done"
- Unlocks achievements automatically

### Quiz Page
- Take quizzes → Updates "Quizzes Taken"
- Quiz scores → Updates "Average Score"
- High scores → Unlocks achievements

### Analytics Page
- All data synced with Profile statistics
- Same database tables used

---

## Achievement Unlocking

Achievements unlock automatically when you:

1. **First Steps** - Generate your first topic
2. **Knowledge Seeker** - Learn 5 topics
3. **Dedicated Learner** - Complete 10 topics
4. **Quiz Taker** - Complete your first quiz
5. **Quiz Master** - Get 80%+ average score
6. **Perfectionist** - Score 100% on a quiz
7. **Task Master** - Complete 10 roadmap tasks
8. **Dedicated Worker** - Complete 25 roadmap tasks

Check Achievements tab to see your progress!

---

## Files Involved

### New Files:
- `frontend/utils/profile_database.py` - Database management
- `frontend/pages/5_Profile.py` - Profile page (rewritten)

### Database Tables:
- `user_profiles` - Profile information
- `user_settings` - User preferences
- `user_achievements` - Unlocked achievements

---

## Next Steps

After testing the profile:

1. ✅ Generate some topics in Learn page
2. ✅ Take some quizzes in Quiz page
3. ✅ Complete some roadmap tasks
4. ✅ Return to Profile to see updated statistics
5. ✅ Watch achievements unlock automatically

---

## Status: ✅ READY TO TEST

Everything is implemented and working. Just start the app and test!

**Enjoy your personalized learning profile!** 🎉
