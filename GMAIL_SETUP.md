# Gmail SMTP Setup for Password Reset Emails

## Current Status
The system is configured to use **console email backend** for development, which displays emails in the terminal instead of sending them. This prevents SMTP authentication errors during development.

## For Production: Gmail SMTP Setup

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to **Security** → **2-Step Verification**
3. Enable 2-Factor Authentication if not already enabled

### Step 2: Generate App Password
1. Go to **Security** → **2-Step Verification** → **App passwords**
2. Select **Mail** as the app
3. Select **Other (custom name)** as the device
4. Enter "Emergency Ambulance System" as the name
5. Click **Generate**
6. Copy the 16-character app password (format: xxxx xxxx xxxx xxxx)

### Step 3: Update Settings
In `emergency_ambulance/settings.py`, uncomment and update these lines:

```python
# Change from console backend to SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-gmail@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password'  # The 16-character app password
DEFAULT_FROM_EMAIL = 'Emergency Ambulance System <your-gmail@gmail.com>'
```

### Step 4: Test the Setup
1. Restart your Django server
2. Try the password reset functionality
3. Check that emails are sent successfully

## Development Mode
Currently using console backend - password reset emails will appear in your terminal window instead of being sent via email. This is perfect for development and testing.

## Security Notes
- Never commit your Gmail credentials to version control
- Use environment variables for production:
  ```python
  import os
  EMAIL_HOST_USER = os.environ.get('GMAIL_USER')
  EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
  ```
- App passwords are more secure than regular passwords
- Each app password is unique and can be revoked individually

## Troubleshooting
- **530 Authentication Required**: App password not set or incorrect
- **535 Username/Password not accepted**: Wrong credentials or 2FA not enabled
- **Less secure app access**: Not needed with app passwords
- **Blocked sign-in attempt**: Use app password instead of regular password
