# LinkedIn Scheduler

A professional LinkedIn post scheduling application built with Python Flask. Schedule posts with images, manage your content pipeline, and track your posting analytics - all with a beautiful, modern interface.

## 🚀 Features

- **LinkedIn OAuth Integration** - Secure connection to your LinkedIn account
- **Post Scheduling** - Schedule posts for specific dates and times
- **Image Support** - Upload and attach images to your posts
- **Draft Management** - Save posts as drafts and publish later
- **Analytics Dashboard** - Track success rates and post performance
- **Auto-Retry** - Automatic retry mechanism for failed posts
- **Real-time Status Updates** - Live updates on post status
- **Responsive Design** - Works perfectly on desktop and mobile

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Scheduling**: APScheduler
- **Authentication**: LinkedIn OAuth 2.0
- **Image Processing**: Pillow (PIL)

## 📋 Prerequisites

- Python 3.8 or higher
- LinkedIn Developer Account
- Git

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/linkedin-scheduler.git
cd linkedin-scheduler
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. LinkedIn App Setup

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create a new app
3. Add the following redirect URI: `http://localhost:5000/auth/linkedin/callback`
4. Request access to the following scopes:
   - `r_liteprofile`
   - `w_member_social`

### 5. Environment Configuration

Create a `.env` file in the root directory:

```env
# LinkedIn OAuth Credentials
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:5000/auth/linkedin/callback

# Flask Secret Key
SECRET_KEY=your_super_secret_key_here

# Database URL (optional - defaults to SQLite)
DATABASE_URL=sqlite:///linkedin_scheduler.db
```

### 6. Initialize Database

```bash
python -c "from app import app; from database import init_db; init_db(app)"
```

### 7. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🎯 Usage

### 1. Connect LinkedIn Account
- Visit the landing page
- Click "Connect LinkedIn Account"
- Complete the OAuth authorization

### 2. Create Posts
- Navigate to "Create Post"
- Write your content (up to 3000 characters)
- Optionally attach an image
- Choose to save as draft or schedule for later

### 3. Manage Posts
- View all posts in the Dashboard
- Edit scheduled posts
- Publish drafts immediately
- Delete unwanted posts

### 4. Analytics
- Track success rates
- View posting history
- Monitor failed posts
- Get insights and recommendations

## 📁 Project Structure

```
linkedin-scheduler/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── database.py           # Database models
├── linkedin_api.py       # LinkedIn API integration
├── scheduler.py          # Post scheduling logic
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── uploads/         # Image uploads
├── templates/           # HTML templates
└── README.md
```

## 🔐 Security Features

- **OAuth 2.0** - Secure LinkedIn authentication
- **CSRF Protection** - Built-in Flask security
- **Input Validation** - Comprehensive data validation
- **File Upload Security** - Safe image handling
- **Session Management** - Secure user sessions

## 🚀 Deployment

### Heroku Deployment

1. Install Heroku CLI
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Set environment variables:
   ```bash
   heroku config:set LINKEDIN_CLIENT_ID=your_client_id
   heroku config:set LINKEDIN_CLIENT_SECRET=your_client_secret
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set LINKEDIN_REDIRECT_URI=https://your-app-name.herokuapp.com/auth/linkedin/callback
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

## 🧪 Testing

Run the application locally and test:

1. **OAuth Flow** - Connect LinkedIn account
2. **Post Creation** - Create posts with and without images
3. **Scheduling** - Schedule posts for future dates
4. **Publishing** - Verify posts appear on LinkedIn
5. **Analytics** - Check dashboard statistics

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/auth/linkedin` | Initiate LinkedIn OAuth |
| GET | `/auth/linkedin/callback` | OAuth callback |
| GET | `/dashboard` | Main dashboard |
| GET | `/create-post` | Create post page |
| POST | `/api/posts` | Create new post |
| DELETE | `/api/posts/<id>` | Delete post |
| POST | `/api/posts/<id>/publish` | Publish post immediately |
| POST | `/api/posts/<id>/reschedule` | Reschedule post |
| GET | `/analytics` | Analytics page |

## 🔧 Configuration Options

### Environment Variables

- `LINKEDIN_CLIENT_ID` - LinkedIn app client ID
- `LINKEDIN_CLIENT_SECRET` - LinkedIn app client secret
- `LINKEDIN_REDIRECT_URI` - OAuth redirect URI
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string

### App Configuration

- **Max File Size**: 16MB for images
- **Supported Formats**: PNG, JPG, JPEG, GIF
- **Character Limit**: 3000 characters per post
- **Retry Attempts**: 3 attempts for failed posts

## 🐛 Troubleshooting

### Common Issues

1. **LinkedIn OAuth Error**
   - Verify client ID and secret
   - Check redirect URI matches exactly
   - Ensure app has required permissions

2. **Posts Not Publishing**
   - Check LinkedIn access token validity
   - Verify user permissions
   - Check scheduler logs

3. **Image Upload Issues**
   - Ensure file size is under 16MB
   - Check supported file formats
   - Verify upload directory permissions

### Debug Mode

Run with debug enabled:
```bash
FLASK_DEBUG=1 python app.py
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LinkedIn API for social media integration
- Flask community for the excellent framework
- Font Awesome for icons
- Google Fonts for typography

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section
2. Search existing GitHub issues
3. Create a new issue with detailed information

---

**Happy Scheduling! 🎉**

Made with ❤️ for the LinkedIn community
