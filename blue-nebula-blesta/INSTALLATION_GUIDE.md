# Blue Nebula Blesta Template - Clean Installation Guide

## 📁 **New Template Structure**

Following Blesta's official documentation, I've created a clean, minimal template that only modifies what's necessary:

```
blue-nebula-blesta/
├── config.json           # Theme configuration
├── structure.pdt         # Main template with Blue Nebula branding
└── css/
    └── overrides.css     # Custom CSS overrides only
```

## 🎯 **What This Template Does**

### **Minimal Changes**
- ✅ **Only modifies structure.pdt** for Blue Nebula branding and layout
- ✅ **Uses custom overrides.css** instead of modifying existing CSS
- ✅ **Keeps all Blesta functionality** intact
- ✅ **Follows official Blesta template guidelines**

### **Blue Nebula Features**
- ✅ **Space theme background** with animated stars
- ✅ **Blue Nebula logo and branding** in header
- ✅ **Dark theme styling** for all components
- ✅ **Professional Blue Nebula colors** throughout
- ✅ **Responsive design** for mobile devices

## 🚀 **Installation Instructions**

### **Step 1: Copy Template to Blesta**

Copy the entire template directory to your Blesta installation:

```bash
# Copy the template directory to Blesta
cp -r /app/blue-nebula-blesta /path/to/blesta/app/views/client/

# Set proper permissions
chown -R www-data:www-data /path/to/blesta/app/views/client/blue-nebula-blesta/
chmod -R 644 /path/to/blesta/app/views/client/blue-nebula-blesta/*
```

### **Step 2: Clear Blesta Cache**

```bash
# Clear view cache to ensure new template is recognized
rm -rf /path/to/blesta/cache/view_cache/*
```

### **Step 3: Activate Template in Blesta Admin**

1. **Login to Blesta Admin Panel**
2. **Navigate to**: Settings → Company → Look and Feel → Template
3. **Select**: "Blue Nebula" from Client Template dropdown
4. **Click**: Save

### **Step 4: Verify Installation**

Visit your client portal and verify:
- [ ] Blue Nebula logo appears in header
- [ ] Space background with stars is visible
- [ ] All text is readable (white/gray on dark background)
- [ ] Cards have dark backgrounds with Blue Nebula styling
- [ ] Footer has Blue Nebula branding
- [ ] Navigation works properly

## 📋 **Template Files Explained**

### **config.json**
```json
{
    "version": "2.0.0",
    "name": "Blue Nebula",
    "description": "Blue Nebula Hosting custom theme...",
    "authors": [{"name": "Blue Nebula Hosting"}]
}
```

### **structure.pdt**
- **Based on default Bootstrap template**
- **Adds Blue Nebula logo** with custom HTML/CSS
- **Includes overrides.css** after default stylesheets
- **Updates page title** to include "Blue Nebula Hosting"
- **Adds service links** (Game Panel, Status)
- **Custom footer** with Blue Nebula branding

### **css/overrides.css**
- **Space background** with animated stars
- **Dark theme colors** for all components
- **Blue Nebula brand colors** (#3b82f6, #8b5cf6)
- **Card styling overrides** to fix white backgrounds
- **Typography improvements** for readability
- **Responsive design** for mobile

## 🎨 **Customization**

### **Logo Customization**
To use your own logo instead of the text-based logo, edit `structure.pdt`:

```html
<!-- Replace this section in structure.pdt -->
<div class="logo-icon">
    <span class="logo-text">BN</span>
</div>

<!-- With your logo image -->
<img src="<?php echo $this->view_dir;?>images/logo.png" alt="Blue Nebula Hosting" style="height: 40px;" />
```

### **Color Customization**
Edit `css/overrides.css` to change colors:

```css
/* Main Blue Nebula colors */
:root {
    --primary-blue: #3b82f6;
    --primary-purple: #8b5cf6;
    --dark-bg: #1f2937;
    --darker-bg: #111827;
}
```

### **Service Links**
Update service links in `structure.pdt`:

```html
<!-- Update these URLs to match your services -->
<a href="https://panel.bluenebulahosting.com" target="_blank">Game Panel</a>
<a href="https://status.bluenebulahosting.com/status/bnh" target="_blank">Status</a>
```

## 🔧 **Troubleshooting**

### **Template Not Appearing in Admin**
1. **Check file permissions**: Ensure web server can read files
2. **Clear cache**: Delete `/path/to/blesta/cache/view_cache/*`
3. **Verify path**: Template should be at `/app/views/client/blue-nebula-blesta/`

### **White Backgrounds Still Showing**
1. **Clear browser cache**: Hard refresh with Ctrl+F5
2. **Check CSS loading**: Verify overrides.css is loading after default CSS
3. **Wait a moment**: Some styling applies progressively

### **Logo Not Displaying**
1. **Check HTML**: Verify logo HTML is correctly placed in structure.pdt
2. **Add image**: If using image logo, ensure file exists and path is correct
3. **Check CSS**: Verify logo styling in overrides.css

## ✅ **Success Checklist**

After installation, you should see:

### **Header**
- [ ] Blue Nebula logo/branding
- [ ] Space background with animated stars
- [ ] Dark navigation with Blue Nebula colors
- [ ] Game Panel and Status links

### **Content Area**
- [ ] Dark cards with visible text
- [ ] Blue Nebula color scheme
- [ ] Readable typography
- [ ] Proper button styling

### **Footer**
- [ ] Blue Nebula branding
- [ ] Gradient border effect
- [ ] Proper dark styling

### **Functionality**
- [ ] All Blesta features work normally
- [ ] Mobile responsive design
- [ ] Forms and inputs styled properly
- [ ] Navigation and dropdowns work

## 🎉 **Advantages of This Approach**

### **Following Best Practices**
- ✅ **Official Blesta guidelines** followed
- ✅ **Minimal modifications** to core files
- ✅ **Easy updates** - only need to update custom files
- ✅ **Maintainable** - clean separation of custom code

### **Professional Implementation**
- ✅ **Clean code structure**
- ✅ **Proper CSS specificity**
- ✅ **Responsive design**
- ✅ **Accessible design patterns**

---

**Blue Nebula Blesta Template v2.0.0**
*Clean, minimal, and following official Blesta guidelines*

**Ready for Production**: ✅ **YES**
**Follows Documentation**: ✅ **YES**
**Easy to Maintain**: ✅ **YES**