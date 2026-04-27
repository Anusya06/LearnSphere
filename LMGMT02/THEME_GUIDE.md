# 🎨 LearnSphere Pro - Dark/Light Mode Guide

## ✨ Theme Toggle Feature

LearnSphere Pro now includes a beautiful dark/light mode toggle that adjusts all colors, fonts, and UI elements automatically!

---

## 🔄 How to Switch Themes

### Method 1: Sidebar Toggle (Recommended)
1. **Look at the top of the sidebar**
2. **Find the theme toggle button**: 🌙 (for dark mode) or ☀️ (for light mode)
3. **Click the button** to instantly switch themes
4. The entire app updates immediately!

### Method 2: Profile Settings
1. Go to **👤 Profile** page
2. Find the **Theme** setting
3. Select "Light" or "Dark"
4. Changes apply instantly

---

## 🎨 What Changes in Each Theme?

### 🌙 Dark Mode
- **Background**: Dark gradients (#1a1a1a to #2d2d2d)
- **Text**: White (#ffffff) for primary, light gray (#b0b0b0) for secondary
- **Cards**: Dark gray (#2d2d2d)
- **Inputs**: Dark backgrounds with light text
- **Borders**: Subtle dark borders (#404040)
- **Shadows**: Deeper, more dramatic shadows
- **Sidebar**: Dark gradient background

### ☀️ Light Mode
- **Background**: Light gradients (#f9fafb to #c3cfe2)
- **Text**: Dark gray (#1f2937) for primary, medium gray (#6b7280) for secondary
- **Cards**: White (#ffffff)
- **Inputs**: White backgrounds with dark text
- **Borders**: Light gray borders (#e5e7eb)
- **Shadows**: Soft, subtle shadows
- **Sidebar**: Gradient purple background

---

## 🎯 Theme Features

### Automatic Adjustments
✅ **All text colors** - Readable in both modes
✅ **Background colors** - Comfortable for eyes
✅ **Input fields** - Proper contrast
✅ **Buttons** - Maintain gradient design
✅ **Cards** - Appropriate backgrounds
✅ **Charts** - Plotly charts adapt
✅ **Code blocks** - Syntax highlighting
✅ **Sidebar** - Themed navigation
✅ **Expanders** - Themed containers
✅ **Metrics** - Themed stat cards

### Smooth Transitions
- All color changes animate smoothly (0.3s transition)
- No jarring switches
- Professional appearance

### Persistent Theme
- Your theme choice is saved in session
- Stays consistent across all pages
- Resets when you close the browser

---

## 💡 Theme Best Practices

### When to Use Dark Mode
- 🌙 **Night time** - Easier on eyes in low light
- 💻 **Long sessions** - Reduces eye strain
- 🎮 **Focus mode** - Less distracting
- 🎨 **Personal preference** - Some prefer dark aesthetics

### When to Use Light Mode
- ☀️ **Daytime** - Better in bright environments
- 📊 **Data analysis** - Charts may be clearer
- 📝 **Reading heavy content** - Traditional reading experience
- 🎨 **Personal preference** - Classic, clean look

---

## 🛠️ Technical Details

### Theme Implementation
- **CSS Variables**: Dynamic color system
- **Session State**: Theme stored in `st.session_state.theme`
- **Auto-reload**: Instant theme switching with `st.rerun()`
- **Consistent**: All pages use the same theme helper

### Color Palette

**Dark Mode:**
```css
--bg-primary: #1a1a1a
--bg-secondary: #2d2d2d
--bg-tertiary: #3a3a3a
--text-primary: #ffffff
--text-secondary: #b0b0b0
--border-color: #404040
```

**Light Mode:**
```css
--bg-primary: #f9fafb
--bg-secondary: #ffffff
--bg-tertiary: #f3f4f6
--text-primary: #1f2937
--text-secondary: #6b7280
--border-color: #e5e7eb
```

### Files Modified
1. `frontend/Home.py` - Added theme toggle and CSS loader
2. `frontend/utils/theme_helper.py` - Theme utility functions
3. `frontend/styles/custom.css` - CSS variables and theme support
4. `frontend/components/ui_components.py` - Theme toggle component
5. All page files - Theme CSS loading

---

## 🎨 Customization

### Want to customize colors?

Edit `frontend/utils/theme_helper.py`:

```python
# For dark mode
if theme == "dark":
    theme_css = """
    :root {
        --bg-primary: #YOUR_COLOR !important;
        --text-primary: #YOUR_COLOR !important;
        /* ... more colors ... */
    }
    """
```

### Want to add more themes?

1. Add theme option to session state
2. Create new color palette in theme_helper.py
3. Add theme selector in sidebar

---

## 🐛 Troubleshooting

### Theme not switching?
1. **Refresh the page** (F5 or Ctrl+R)
2. **Clear browser cache**
3. **Check if button is clickable**
4. **Restart Streamlit** if needed

### Colors look wrong?
1. **Hard refresh** (Ctrl+Shift+R or Cmd+Shift+R)
2. **Check browser compatibility** (works best in Chrome/Firefox)
3. **Update Streamlit** to latest version

### Theme resets on page change?
- This is normal - theme is session-based
- Will persist during your session
- Resets when you close browser

---

## 🎉 Enjoy Your Theme!

Switch between dark and light mode anytime to find what works best for you!

**Quick Toggle**: Click the 🌙/☀️ button in the sidebar!

---

## 📸 Screenshots

### Light Mode
- Clean, professional appearance
- High contrast for readability
- Perfect for daytime use

### Dark Mode
- Modern, sleek design
- Easy on the eyes
- Great for night sessions

---

**Pro Tip**: Try dark mode during evening study sessions to reduce eye strain! 🌙✨
