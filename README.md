# Asset Management System

A comprehensive Django-based asset management system with role-based access control, built for efficient tracking and management of company assets.

## 🚀 Features

### 🔐 Authentication & Authorization
- **Django Authentication**: Secure login/logout system
- **Role-based Access Control**: Three user roles with different permissions
  - **Admin**: Full system access, manage users and assets
  - **Asset Incharge**: Assign/return assets, edit asset details
  - **User**: View only assigned assets

### 🖥️ Asset Management
- **CRUD Operations**: Create, read, update, delete assets
- **Detailed Asset Information**: Serial number, display name, department, category, status, company
- **Asset Categories**: Laptop, Desktop, Monitor, Printer, Mobile, Tablet, Other
- **Status Tracking**: Available, Assigned, Under Maintenance, Retired
- **Click-to-view Details**: Click serial numbers for detailed asset view

### 📊 Dashboard
- **Role-specific Dashboards**: Customized views based on user role
- **Asset Statistics**: Total, assigned, available, and maintenance counts
- **Recent Activity**: Latest asset assignments and returns
- **Bootstrap Cards**: Clean, responsive card-based layout

### 📦 Assignment System
- **Easy Assignment**: Dropdown-based user selection for asset assignment
- **Assignment History**: Complete tracking of asset assignments and returns
- **Auto-timestamps**: Automatic recording of assignment and return dates
- **Assignment Notes**: Optional notes for each assignment

### 💅 UI/UX
- **Responsive Design**: Bootstrap 5-based responsive interface
- **Modern Interface**: Clean, professional design with custom theming
- **Navigation**: Intuitive sidebar navigation with role-based menu items
- **Search & Filter**: Advanced search and filtering capabilities
- **Status Badges**: Color-coded status indicators

### 📁 Database
- **PostgreSQL Support**: Primary database with SQLite fallback
- **Optimized Models**: Efficient database schema with proper relationships
- **Dummy Data**: Pre-loaded test data for immediate use

## 🛠️ Tech Stack

- **Backend**: Django 4.x, Python 3.x
- **Database**: PostgreSQL (with SQLite fallback)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Icons**: Bootstrap Icons
- **Authentication**: Django's built-in authentication system

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite used as fallback)
- pip (Python package manager)

### Step 1: Extract and Navigate
\`\`\`bash
# Extract the ZIP file and navigate to the project directory
cd asset-management-system
\`\`\`

### Step 2: Create Virtual Environment
\`\`\`bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate
\`\`\`

### Step 3: Install Dependencies
\`\`\`bash
# Install required packages
pip install django psycopg2-binary
\`\`\`

### Step 4: Database Setup

#### Option A: PostgreSQL (Recommended)
1. Install PostgreSQL and create a database named \`asset_management_db\`
2. Update database credentials in \`asset_management/settings.py\` if needed
3. Run migrations:
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

#### Option B: SQLite (Development)
If PostgreSQL is not available, the system will automatically use SQLite:
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### Step 5: Load Dummy Data
\`\`\`bash
# Load demo users and assets
python load_dummy_data.py
\`\`\`

### Step 6: Run the Server
\`\`\`bash
python manage.py runserver
\`\`\`

Visit \`http://127.0.0.1:8000\` in your browser.

## 👥 Demo Accounts

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| Admin | admin | admin123 | Full system access |
| Asset Incharge | incharge | incharge123 | Asset management |
| User | user1 | user123 | Regular user access |
| User | user2 | user123 | Regular user access |
| User | user3 | user123 | Regular user access |

## 🎯 Usage Guide

### For Admins
1. **Dashboard**: View system-wide statistics
2. **Asset Management**: Create, edit, delete assets
3. **User Management**: Access Django admin for user management
4. **Assignment Control**: Assign/return assets to/from users

### For Asset Incharge
1. **Asset Assignment**: Assign available assets to users
2. **Asset Returns**: Process asset returns from users
3. **Asset Editing**: Update asset information and status
4. **Assignment Tracking**: Monitor assignment history

### For Users
1. **View Assets**: See only assigned assets
2. **Asset Details**: Click serial numbers for detailed information
3. **Assignment History**: View personal assignment history

## 📱 Key Features Walkthrough

### Asset List View
- **Search**: Find assets by serial number, name, or department
- **Filter**: Filter by status (Available, Assigned, Maintenance, Retired)
- **Category Filter**: Filter by asset category
- **Quick Actions**: View, edit, assign buttons based on role

### Asset Detail View
- **Complete Information**: All asset details in organized layout
- **Assignment History**: Full tracking of who had the asset when
- **Quick Actions**: Role-based action buttons
- **Status Updates**: Real-time status information

### Assignment Process
1. Navigate to available asset
2. Click "Assign" button
3. Select user from dropdown
4. Add optional notes
5. Confirm assignment
6. System automatically updates asset status and records timestamp

## 🔧 Customization

### Adding New Asset Categories
Edit \`assets/models.py\`:
\`\`\`python
CATEGORY_CHOICES = [
    ('laptop', 'Laptop'),
    ('desktop', 'Desktop'),
    # Add new categories here
    ('new_category', 'New Category'),
]
\`\`\`

### Modifying User Roles
Edit \`assets/models.py\`:
\`\`\`python
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('asset_incharge', 'Asset Incharge'),
    ('user', 'User'),
    # Add new roles here
]
\`\`\`

### Styling Customization
- Edit \`templates/base.html\` for global styles
- Modify CSS variables in the \`:root\` section
- Add custom Bootstrap classes as needed

## 🚀 Production Deployment

### Security Settings
1. Change \`SECRET_KEY\` in \`settings.py\`
2. Set \`DEBUG = False\`
3. Update \`ALLOWED_HOSTS\`
4. Configure proper database credentials
5. Set up static file serving

### Database Migration
\`\`\`bash
python manage.py collectstatic
python manage.py migrate
\`\`\`

## 📞 Support

For issues or questions:
1. Check the Django documentation
2. Review the code comments
3. Test with dummy data first
4. Ensure all dependencies are installed

## 🎉 Success Indicators

✅ **Login System**: All demo accounts work  
✅ **Role-based Access**: Different views for different roles  
✅ **Asset CRUD**: Create, read, update, delete operations  
✅ **Assignment System**: Assign and return assets  
✅ **Search & Filter**: Find assets quickly  
✅ **Responsive Design**: Works on all devices  
✅ **Database Integration**: PostgreSQL/SQLite support  
✅ **Dummy Data**: Ready-to-use test data  

## 📋 Project Structure

\`\`\`
asset-management-system/
├── asset_management/          # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Main configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── assets/                   # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── forms.py             # Django forms
│   ├── urls.py              # App URL patterns
│   └── admin.py             # Admin configuration
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── registration/        # Auth templates
│   └── assets/              # Asset templates
├── static/                  # Static files (CSS, JS, images)
├── manage.py               # Django management script
├── load_dummy_data.py      # Dummy data loader
└── README.md               # This file
\`\`\`

---

**🎯 Ready to use! The system is fully functional with all requested features implemented.**
\`\`\`

```python file="requirements.txt"
Django>=4.2.0
psycopg2-binary>=2.9.0
