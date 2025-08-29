# Emergency Ambulance Request System

A comprehensive Django-based emergency ambulance request system with role-based dashboards, REST API endpoints, and responsive Bootstrap UI.

## Features

### User Roles
- **Patient**: Request ambulance services and track request status
- **Paramedic**: Receive request notifications, accept/decline requests, update status
- **Admin**: Manage users, view system analytics, oversee all requests

### Core Functionality
- User authentication and role management
- Ambulance request handling with real-time status updates
- GPS-based location tracking
- Priority-based request management
- Comprehensive dashboard for each user role
- REST API endpoints for mobile/external integration
- Responsive Bootstrap-based UI

## Technology Stack

- **Backend**: Django 5.2, Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Authentication**: Django's built-in authentication system
- **API**: RESTful API with token authentication

## Project Structure

```
emergency_ambulance_request/
├── accounts/                 # User authentication and management
├── ambulance/               # Ambulance request handling
├── api/                     # REST API endpoints
├── emergency_ambulance/     # Main project settings
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Installation Steps

1. **Extract the project files**
   ```bash
   unzip emergency_ambulance_request.zip
   cd emergency_ambulance_request
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - API endpoints: http://127.0.0.1:8000/api/v1/

## User Accounts

### Default Admin Account
- Username: `admin`
- Password: `admin123`
- Role: Admin

### Creating Test Users
You can create test users through the registration page or Django admin panel.

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/profile/` - Get current user profile
- `PUT /api/v1/users/update_profile/` - Update user profile

### Ambulance Requests
- `GET /api/v1/requests/` - List requests (filtered by user role)
- `POST /api/v1/requests/` - Create new request
- `GET /api/v1/requests/{id}/` - Get request details
- `POST /api/v1/requests/{id}/assign_paramedic/` - Assign paramedic
- `POST /api/v1/requests/{id}/update_status/` - Update request status
- `POST /api/v1/requests/{id}/accept/` - Accept request (paramedic)

### Dashboard
- `GET /api/v1/dashboard/stats/` - Get dashboard statistics
- `GET /api/v1/dashboard/recent-requests/` - Get recent requests

## User Dashboards

### Patient Dashboard
- View request statistics
- Create new ambulance requests
- Track request status and history
- Quick access to emergency contacts

### Paramedic Dashboard
- View assigned requests
- Accept pending requests
- Update request status (en route, arrived, completed)
- Toggle availability status

### Admin Dashboard
- System-wide statistics and analytics
- Manage all users and requests
- View system performance metrics
- Ambulance fleet management

## Key Features

### Request Management
- **Priority Levels**: Critical, High, Medium, Low
- **Status Tracking**: Pending, Assigned, En Route, Arrived, Completed, Cancelled
- **Real-time Updates**: Status changes are tracked with timestamps
- **GPS Integration**: Location coordinates for pickup and destination

### Security Features
- Role-based access control
- CSRF protection
- User authentication required for all operations
- API token authentication

### Responsive Design
- Mobile-friendly Bootstrap UI
- Adaptive layouts for different screen sizes
- Touch-friendly interface elements
- Progressive enhancement

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files (Production)
```bash
python manage.py collectstatic
```

## Deployment

### Environment Variables
Set the following environment variables for production:

```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
ALLOWED_HOSTS=your-domain.com
```

### Production Settings
- Use PostgreSQL or MySQL for production database
- Configure proper static file serving
- Set up SSL/HTTPS
- Configure email backend for notifications
- Set up logging and monitoring

## API Documentation

The system provides comprehensive REST API endpoints for integration with mobile apps or external systems. All API endpoints require authentication and return JSON responses.

### Response Format
```json
{
    "status": "success|error",
    "data": {...},
    "message": "Response message"
}
```

### Error Handling
The API returns appropriate HTTP status codes and error messages for different scenarios.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@emergencyambulance.com
- Phone: (555) 123-4567
- Emergency: 911

## Changelog

### Version 1.0.0
- Initial release
- User authentication and role management
- Ambulance request system
- REST API implementation
- Bootstrap-based responsive UI
- Dashboard for all user roles

