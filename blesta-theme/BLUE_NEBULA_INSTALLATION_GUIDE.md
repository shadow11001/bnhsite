# Blue Nebula Hosting - Blesta Theme Installation Guide

## Overview

This guide will help you install the Blue Nebula Hosting theme for Blesta, which has been properly integrated with your existing Bootstrap theme structure rather than creating a completely new theme.

## What's Included

- **structure.pdt** - Modified Bootstrap template with Blue Nebula branding and space theme
- **theme.css** - Enhanced Bootstrap theme CSS with Blue Nebula styling
- **config.json** - Updated theme configuration
- **images/** - Blue Nebula logo and favicon files

## Key Features

✅ **Space Theme Background** - Animated starfield with Blue Nebula gradient
✅ **Blue Nebula Branding** - Custom logo integration and company branding
✅ **Mobile Menu Fixed** - Enhanced mobile navigation functionality
✅ **Text Visibility Fixed** - Proper contrast and readability
✅ **Range Sliders Fixed** - VPS and hosting plan sliders work properly
✅ **Cart Page Fixed** - Proper styling and functionality
✅ **Form Enhancements** - Better form styling and user experience
✅ **Responsive Design** - Mobile-first responsive layout

## Installation Steps

### Step 1: Backup Your Current Theme

Before installing, backup your current Blesta theme:

```bash
# Navigate to your Blesta directory
cd /path/to/blesta

# Backup current Bootstrap theme
cp -r views/client/bootstrap views/client/bootstrap_backup
```

### Step 2: Upload Theme Files

1. **Upload structure.pdt**:
   ```bash
   cp /app/blesta-theme/structure.pdt /path/to/blesta/views/client/bootstrap/
   ```

2. **Upload theme.css**:
   ```bash
   cp /app/blesta-theme/theme.css /path/to/blesta/views/client/bootstrap/css/
   ```

3. **Upload config.json**:
   ```bash
   cp /app/blesta-theme/config.json /path/to/blesta/views/client/bootstrap/
   ```

4. **Upload images** (optional - for logo):
   ```bash
   cp -r /app/blesta-theme/images/* /path/to/blesta/views/client/bootstrap/images/
   ```

### Step 3: Configure Theme in Blesta Admin

1. **Login to Blesta Admin Panel**
2. **Go to Settings → Company → Look and Feel**
3. **Select "Blue Nebula Bootstrap" theme**
4. **Configure theme colors** (if needed):
   - Primary Color: `#3b82f6` (Blue Nebula Blue)
   - Secondary Color: `#8b5cf6` (Blue Nebula Purple)
   - Success Color: `#10b981` (Blue Nebula Green)
   - Warning Color: `#f59e0b` (Blue Nebula Yellow)
   - Danger Color: `#ef4444` (Blue Nebula Red)

### Step 4: Upload Your Logo (Optional)

1. **Upload your logo** to `/path/to/blesta/views/client/bootstrap/images/logo.png`
2. **Upload favicon** to `/path/to/blesta/views/client/bootstrap/images/favicon.ico`
3. **Configure logo in Blesta**:
   - Go to Settings → Company → General
   - Upload your logo file
   - Set logo height if needed

### Step 5: Test the Theme

1. **Visit your client portal** (e.g., `https://billing.yourdomain.com`)
2. **Test key functionality**:
   - Login/logout
   - Mobile menu (hamburger menu)
   - Order forms and cart
   - VPS configuration sliders
   - Service management pages

## Theme Customization

### Colors

The theme uses CSS variables for easy customization. Main colors:

```css
/* Primary Blue Nebula Colors */
--primary-blue: #3b82f6;
--primary-purple: #8b5cf6;
--secondary-blue: #60a5fa;
--accent-green: #10b981;

/* Background Colors */
--dark-bg: #0f0f10;
--card-bg: #1f2937;
--border-color: #374151;

/* Text Colors */
--text-primary: #ffffff;
--text-secondary: #d1d5db;
--text-muted: #9ca3af;
```

### Navigation Links

The theme includes pre-configured links to:
- **Game Panel**: `https://panel.bluenebulahosting.com`
- **Status Page**: `https://status.bluenebulahosting.com/status/bnh`

Update these URLs in `structure.pdt` if your URLs are different.

### Logo Configuration

The theme expects a logo file at `images/logo.png`. If your logo file has a different name or format:

1. Update the logo path in `structure.pdt`:
   ```php
   <img src="<?php echo $this->view_dir;?>images/your-logo.png" alt="Your Company Name" />
   ```

2. Update the company name in the footer:
   ```php
   &copy; <?php echo date('Y');?> Your Company Name. All rights reserved.
   ```

## Troubleshooting

### Logo Not Showing

1. **Check file path**: Ensure logo is at `images/logo.png`
2. **Check file permissions**: Logo file should be readable by web server
3. **Check image format**: Use PNG, JPG, or SVG formats
4. **Clear browser cache**: Force refresh with Ctrl+F5 or Cmd+Shift+R

### Mobile Menu Not Working

1. **Check JavaScript**: Ensure jQuery is loaded
2. **Check Bootstrap version**: Theme requires Bootstrap 4.6+
3. **Check console errors**: Open browser developer tools for JavaScript errors

### Text Not Visible

1. **Check CSS loading**: Ensure theme.css is properly loaded
2. **Check color contrast**: Verify text colors against background
3. **Force refresh**: Clear browser cache and reload

### Cart Page Issues

1. **Check form styling**: Ensure forms have proper CSS classes
2. **Check AJAX functionality**: Verify jQuery and Bootstrap JS are loaded
3. **Check error messages**: Look for JavaScript console errors

## Features Explained

### Space Theme Background

The theme includes an animated starfield background with Blue Nebula gradient:

```css
body::before {
    /* Blue Nebula gradient background */
    background: linear-gradient(135deg, #0f0f10 0%, #1e1b4b 50%, #312e81 100%);
}

body::after {
    /* Animated stars */
    animation: sparkle 30s linear infinite;
}
```

### Enhanced Mobile Menu

The mobile menu has been enhanced with:
- Improved toggle functionality
- Better touch support
- Proper collapse/expand animation
- Click-outside-to-close functionality

### Range Slider Fixes

VPS and hosting plan sliders now include:
- Custom styling that matches the theme
- Real-time price updates
- Better hover effects
- Improved mobile support

### Cart Page Enhancements

The cart page has been specifically enhanced with:
- Proper background styling
- Better item visibility
- Enhanced summary section
- Improved button styling

## Support

If you encounter any issues with the theme:

1. **Check the troubleshooting section** above
2. **Verify all files are uploaded** correctly
3. **Check Blesta error logs** for any PHP errors
4. **Test with different browsers** to isolate browser-specific issues
5. **Check your customizations** if you've made any modifications

## File Structure

```
bootstrap/
├── config.json              # Theme configuration
├── structure.pdt            # Main template with Blue Nebula branding
├── css/
│   ├── theme.css           # Enhanced Bootstrap theme with Blue Nebula styling
│   └── [other Blesta CSS files]
├── images/
│   ├── logo.png            # Blue Nebula logo
│   ├── favicon.ico         # Blue Nebula favicon
│   └── [other images]
└── [other Blesta theme files]
```

## Updates

This theme is based on the Blesta Bootstrap theme and maintains compatibility with:
- Blesta 5.0.0+
- Bootstrap 4.6+
- Font Awesome 5+
- jQuery 3.6+

When updating Blesta, make sure to:
1. **Backup your customized files** before updating
2. **Re-apply your customizations** after updating
3. **Test thoroughly** after updates

---

**Blue Nebula Hosting Theme v2.0.0**
*Built on Bootstrap 4.6 with Blue Nebula customizations*