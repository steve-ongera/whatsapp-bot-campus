# WhatsApp Bot Application

**Developer:** Steve Ongera  
**Framework:** Django  
**Purpose:** Intelligent WhatsApp group message classification and automated response system

## Overview

This Django application provides an intelligent WhatsApp bot system designed to monitor group messages, classify their importance, and provide automated responses. The bot is particularly useful for educational institutions, study groups, and organizational communication where important messages need to be highlighted and managed effectively.

## Features

### Core Functionality
- **Message Classification**: Automatically classifies messages as important or non-important using keyword detection, machine learning, and sender role-based prioritization
- **Smart Broadcasting**: Automatically broadcasts important messages to relevant recipients
- **Multi-Group Support**: Manages multiple WhatsApp groups with individual configurations
- **Performance Tracking**: Comprehensive metrics and analytics for bot performance
- **User Interaction Tracking**: Monitors user engagement and satisfaction

### Key Capabilities
- Keyword-based importance detection
- Sender role prioritization (teachers, admins, class reps)
- Automated message summaries (daily/weekly)
- Configurable response thresholds
- Rate limiting and spam protection
- Performance metrics and analytics

## Database Models

### Core Models

#### WhatsAppGroup
Represents individual WhatsApp groups managed by the bot.
- **Fields**: `group_id`, `group_name`, `group_type`, `created_at`, `is_active`
- **Group Types**: Class Group, Study Group, General Group

#### GroupMember
Manages members within WhatsApp groups.
- **Fields**: `whatsapp_group`, `phone_number`, `name`, `role`, `joined_at`, `is_active`
- **Roles**: Student, Class Representative, Teacher, Admin

#### Message
Stores all WhatsApp messages for processing.
- **Fields**: `message_id`, `whatsapp_group`, `sender`, `content`, `message_type`, `timestamp`
- **Message Types**: Text, Image, Document, Audio, Video, Sticker

### Classification System

#### ImportantKeyword
Defines keywords that indicate message importance.
- **Categories**: Schedule, Assignment, Exam, Deadline, Meeting, Announcement, Task, Report
- **Weight System**: 1-10 importance scaling

#### MessageClassification
Stores classification results for each message.
- **Classification Methods**: Keyword Based, Machine Learning, Manual Classification, Sender Role Based
- **Metrics**: Importance score, confidence level, detected keywords

### Bot Management

#### BotConfiguration
Per-group configuration settings for bot behavior.
- **Settings**: Auto-broadcast, minimum importance score, escalation threshold
- **Rate Limiting**: Maximum messages per hour, notification delays

#### BotResponse
Tracks bot actions and responses.
- **Response Types**: Broadcast, Direct Message, Escalate, Ignore, Auto Reply
- **Tracking**: Recipients, send status, timestamps

### Analytics & Reporting

#### MessageSummary
Generates periodic summaries of group activity.
- **Summary Types**: Daily, Weekly, Custom Period
- **Content**: Message counts, key topics, important message highlights

#### UserInteraction
Tracks user engagement with the bot.
- **Interaction Types**: Commands, Queries, Feedback, Summary Requests, Issue Reports

#### BotPerformanceMetrics
Comprehensive performance tracking.
- **Metrics**: Accuracy scores, response times, user satisfaction, false positive/negative rates

## Installation

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL/MySQL (recommended for production)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp-bot-application
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

4. **Configure database**
   ```python
   # settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'whatsapp_bot_db',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Initial Setup

1. **Create WhatsApp Groups**
   - Add groups through Django admin or API
   - Configure group types and settings

2. **Add Group Members**
   - Import member lists with roles
   - Set up proper role hierarchies

3. **Configure Keywords**
   - Define important keywords for each category
   - Set appropriate weights (1-10 scale)

4. **Bot Configuration**
   ```python
   # Example configuration
   BotConfiguration.objects.create(
       whatsapp_group=group,
       auto_broadcast_important=True,
       minimum_importance_score=0.7,
       escalation_threshold=0.5,
       max_messages_per_hour=50
   )
   ```

### Environment Variables

Create a `.env` file with the following variables:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_API_URL=https://api.whatsapp.com/v1/
```

## Usage

### Message Processing Flow

1. **Message Reception**: Messages are received via WhatsApp API webhook
2. **Classification**: Bot analyzes message importance using:
   - Keyword detection
   - Sender role priority
   - Machine learning models (if configured)
3. **Action Decision**: Based on classification, bot decides to:
   - Broadcast to group
   - Send direct messages
   - Escalate to human moderator
   - Ignore message
4. **Response Execution**: Bot performs the determined action
5. **Metrics Recording**: Performance data is logged for analysis

### Admin Interface

Access the Django admin interface at `/admin/` to:
- Manage groups and members
- Configure keywords and weights
- Monitor bot performance
- Review message classifications
- Generate reports and summaries

### API Endpoints (if implemented)

```
GET /api/groups/ - List all groups
POST /api/groups/ - Create new group
GET /api/messages/<group_id>/ - Get group messages
POST /api/classify/ - Classify message manually
GET /api/metrics/<group_id>/ - Get performance metrics
```

## Monitoring & Analytics

### Performance Metrics
- **Accuracy Score**: Percentage of correctly classified messages
- **Response Time**: Average time to process and respond to messages
- **User Satisfaction**: Based on user feedback and interactions
- **False Positive/Negative Rates**: Classification error tracking

### Reports Available
- Daily/Weekly message summaries
- Keyword effectiveness analysis
- User engagement statistics
- Bot performance trends

## Customization

### Adding New Classification Methods

1. Create new classification method in `MessageClassification.classification_method` choices
2. Implement classification logic in your message processing service
3. Update bot configuration to enable new method

### Custom Keywords

Keywords can be customized per group or globally:
```python
# Add custom keyword
ImportantKeyword.objects.create(
    keyword="urgent assignment",
    category="assignment",
    weight=9
)
```

### Response Templates

Customize bot responses by modifying the response generation logic in your message processing service.

## Security Considerations

- **API Security**: Implement proper authentication for WhatsApp API webhooks
- **Data Privacy**: Ensure compliance with data protection regulations
- **Rate Limiting**: Configure appropriate message limits to prevent spam
- **Access Control**: Implement proper user permissions for admin functions

## Troubleshooting

### Common Issues

1. **Messages Not Being Classified**
   - Check keyword configuration
   - Verify bot configuration settings
   - Review classification thresholds

2. **High False Positive Rate**
   - Adjust minimum importance score
   - Review and refine keywords
   - Update keyword weights

3. **Performance Issues**
   - Monitor database query optimization
   - Check message processing queue
   - Review rate limiting settings

### Logging

Enable detailed logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'whatsapp_bot.log',
        },
    },
    'loggers': {
        'whatsapp_bot': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- **Developer**: Steve Ongera
- **Email**: [your-email@domain.com]
- **GitHub Issues**: [repository-url]/issues

## Changelog

### Version 1.0.0
- Initial release with core functionality
- Message classification system
- Basic bot responses
- Performance metrics tracking

---

**Note**: This application is designed for educational and organizational use. Ensure compliance with WhatsApp's Terms of Service and applicable data protection regulations when deploying in production.