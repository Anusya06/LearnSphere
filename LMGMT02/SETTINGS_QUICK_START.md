# ⚙️ Settings Feature - Quick Start Guide

## Start Testing NOW (3 Steps)

### Step 1: Start the App
```bash
cd frontend
streamlit run Home.py
```

### Step 2: Login and Find Settings
1. Login with your credentials
2. Look at the **bottom of the sidebar**
3. You should see: **"⚙️ Settings"**
4. Click the Settings button

### Step 3: Explore Settings

---

## Quick Tests

### ✅ Test 1: Update Account Info (1 minute)
1. Click **"👤 Account"** tab (should be open by default)
2. Change your full name
3. Update learning interests (e.g., "Python, Machine Learning, AI")
4. Click **"💾 Save Account Settings"**
5. Should see: ✅ "Account settings saved successfully!"
6. **Logout and login again**
7. Settings should still be there ✅

### ✅ Test 2: Change Password (2 minutes)
1. In **"👤 Account"** tab
2. Scroll down to **"🔒 Change Password"**
3. Enter your current password
4. Enter a new password (min 6 characters)
5. Confirm the new password
6. Click **"🔐 Update Password"**
7. Should see: ✅ "Password changed successfully"
8. **Logout**
9. **Login with NEW password**
10. Should work ✅

### ✅ Test 3: Set Preferences (1 minute)
1. Click **"🎨 Preferences"** tab
2. Select your preferred programming language
3. Choose learning difficulty
4. Set daily learning goal (e.g., 30 minutes)
5. Set weekly quiz goal (e.g., 5 quizzes)
6. Select interface language
7. Choose theme (Dark/Light/Auto)
8. Click **"💾 Save Preferences"**
9. Should see: ✅ "Preferences saved successfully!"
10. **Logout and login again**
11. Preferences should be saved ✅

### ✅ Test 4: Manage Notifications (30 seconds)
1. Click **"🔔 Notifications"** tab
2. Toggle some checkboxes:
   - Email Notifications
   - Quiz Reminders
   - Daily Learning Reminders
   - Weekly Summary
   - Achievement Alerts
3. Click **"💾 Save Notification Settings"**
4. Should see: ✅ "Notification settings saved successfully!"
5. **Logout and login again**
6. Settings should be saved ✅

### ✅ Test 5: View Security (30 seconds)
1. Click **"🛡️ Security"** tab
2. Should see:
   - Two-Factor Authentication (Coming Soon)
   - Current Session info
   - Delete Account option
3. Expand **"🗑️ Delete Account"**
4. Should see warning and confirmation field
5. **Don't actually delete!** Just verify it's there ✅

---

## What to Look For

### ✅ Sidebar
- Settings button at the **bottom** of sidebar
- Below Profile, above Logout
- Clear ⚙️ icon

### ✅ Settings Page
- 4 tabs: Account, Preferences, Notifications, Security
- Clean, organized layout
- Dark mode compatible
- All text clearly visible

### ✅ Account Tab
- Personal information form
- Password change section
- Save buttons work
- Success messages display

### ✅ Preferences Tab
- Programming language selector
- Difficulty level selector
- Learning goals (daily/weekly)
- Interface language
- Theme selector
- All options save correctly

### ✅ Notifications Tab
- Email notifications toggle
- Multiple reminder options
- Report settings
- All toggles work
- Settings persist

### ✅ Security Tab
- 2FA placeholder
- Session information
- Delete account option
- Warning messages

---

## Common Issues

### Settings Button Not Visible?
- Make sure you're logged in
- Check bottom of sidebar
- Scroll down in sidebar if needed
- Refresh page

### Password Change Not Working?
- Make sure current password is correct
- New password must be at least 6 characters
- New passwords must match
- Check for error messages

### Settings Not Saving?
- Click the Save button
- Wait for success message
- Check for error messages
- Try logging out and back in

### Can't Find a Setting?
- Check all 4 tabs
- Account: Personal info, password
- Preferences: Language, difficulty, goals
- Notifications: Reminders, alerts
- Security: 2FA, sessions, delete

---

## Settings Location

```
Sidebar Structure:

┌─────────────────────┐
│  User Profile Card  │
├─────────────────────┤
│   📚 Navigation     │
│   🏠 Dashboard      │
│   📚 Learn          │
│   📝 Quiz           │
│   📊 Analytics      │
│   👤 Profile        │
├─────────────────────┤
│   ⚙️ Settings  ← HERE
├─────────────────────┤
│   🚪 Logout         │
└─────────────────────┘
```

---

## Settings Tabs

### Tab 1: 👤 Account
```
┌─────────────────────────────┐
│ Account Settings            │
│ ├─ Full Name               │
│ ├─ Username (read-only)    │
│ ├─ Email (read-only)       │
│ └─ Learning Interests      │
│                             │
│ Change Password             │
│ ├─ Current Password        │
│ ├─ New Password            │
│ └─ Confirm Password        │
└─────────────────────────────┘
```

### Tab 2: 🎨 Preferences
```
┌─────────────────────────────┐
│ Programming Preferences     │
│ ├─ Language (Python, etc.) │
│ └─ Difficulty Level        │
│                             │
│ Learning Goals              │
│ ├─ Daily Goal (minutes)    │
│ └─ Weekly Quiz Goal        │
│                             │
│ Interface Preferences       │
│ ├─ Language                │
│ └─ Theme (Dark/Light)      │
└─────────────────────────────┘
```

### Tab 3: 🔔 Notifications
```
┌─────────────────────────────┐
│ Email Notifications         │
│ ☑ Enable Email Notifs      │
│                             │
│ Reminders                   │
│ ☑ Quiz Reminders           │
│ ☑ Roadmap Reminders        │
│ ☑ Daily Reminders          │
│ ☑ Streak Alerts            │
│                             │
│ Reports                     │
│ ☑ Weekly Summary           │
│ ☑ Achievement Alerts       │
└─────────────────────────────┘
```

### Tab 4: 🛡️ Security
```
┌─────────────────────────────┐
│ Two-Factor Authentication   │
│ (Coming Soon)               │
│                             │
│ Active Sessions             │
│ Current Session Info        │
│                             │
│ Danger Zone                 │
│ 🗑️ Delete Account          │
└─────────────────────────────┘
```

---

## Integration with Other Pages

### Learn Page
- Uses default difficulty from Settings
- Uses programming language preference
- Respects learning goals

### Quiz Page
- Quiz reminders from Settings
- Weekly quiz goal tracking
- Notification preferences

### Profile Page
- Shares same database tables
- Settings changes reflect in Profile
- Consistent data

### Analytics Page
- Tracks progress toward goals
- Shows learning statistics
- Goal achievement tracking

---

## Data Persistence

All settings are saved to database:
- ✅ Account information
- ✅ Password (securely hashed)
- ✅ Preferences
- ✅ Notification settings
- ✅ Theme preference

Changes persist across:
- ✅ Page refreshes
- ✅ Logout/login
- ✅ Different sessions
- ✅ Different devices (same account)

---

## Security Features

### Password Security
- ✅ Bcrypt hashing (industry standard)
- ✅ Current password verification required
- ✅ Minimum 6 character requirement
- ✅ Password confirmation
- ✅ No plain text storage

### Access Control
- ✅ Authentication required
- ✅ User can only edit own settings
- ✅ Session validation
- ✅ Secure database access

---

## Next Steps

After testing Settings:

1. ✅ Update your account information
2. ✅ Set your learning preferences
3. ✅ Configure notifications
4. ✅ Explore security options
5. ✅ Test password change (optional)
6. ✅ Verify settings persist after logout

---

## Files Involved

### New Files:
- `frontend/pages/6_Settings.py` - Settings page

### Modified Files:
- `frontend/Home.py` - Added Settings button to sidebar
- `frontend/utils/auth_database.py` - Enhanced password methods

### Database Tables:
- `user_profiles` - Account information
- `user_settings` - Preferences and notifications
- `users` - Password hashes

---

## Status: ✅ READY TO TEST

Everything is implemented and working. Just start the app and test!

**Enjoy your new Settings feature!** 🎉
