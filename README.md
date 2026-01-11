# IntelliFace - Face Recognition Attendance System

🎯 **Automated attendance tracking using facial recognition technology for educational institutions.**

## 🚀 Features

### ✅ Core Features (Active)
- **Face Recognition Attendance**: Automatically mark attendance using facial recognition
- **Multi-Role System**: Admin, Teacher, and Student roles with appropriate permissions
- **Course Management**: Create and manage courses, classes, and lectures
- **Real-time Processing**: Background tasks capture and process attendance every 5 minutes
- **Camera Integration**: Support for multiple IP cameras per classroom via RTSP
- **JWT Authentication**: Secure API access with token-based authentication
- **RESTful API**: Complete REST API for all operations

### 🤖 ML/AI Features (Enabled)
- **Face Detection**: InsightFace-powered face detection and recognition
- **Facial Embeddings**: Generate and store mathematical face representations
- **Image Enhancement**: OpenCV-based image preprocessing for better accuracy
- **Similarity Matching**: Cosine similarity-based student identification
- **Automated Processing**: Celery-powered background attendance processing

### 🏗 Architecture
- **Backend**: Django 5.1.7 + Django REST Framework
- **Database**: PostgreSQL with UUID-based models
- **Task Queue**: Celery + Redis for background processing
- **ML Stack**: InsightFace + OpenCV + Scikit-learn
- **Deployment**: Docker containerized, Railway-ready

## 📡 API Endpoints

### Authentication
- `POST /api/login/` - JWT token generation
- `POST /api/refresh/` - Token refresh

### User Management
- `GET/POST /api/teacher/` - Teacher management
- `GET/POST /api/student/` - Student management
- `POST /api/student/{id}/upload-images/` - Upload student photos (auto-generates embeddings)

### Course & Attendance
- `GET/POST /api/course/` - Course management
- `GET/POST /api/class/` - Classroom management
- `POST /api/start-attendance/` - Begin lecture session
- `POST /api/stop-attendance/{lecture_id}/` - End session (auto-processes attendance)
- `POST /api/lecture/{lecture_id}/process-recognition/` - Manual attendance processing
- `GET /api/attendance/{lecture_id}/` - View attendance details

### System Status
- `GET /api/ml-status/` - Check ML features status
- `GET /health/` - System health check

## 🛠 Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis
- Docker (optional)

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd IntelliFace

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database and Redis URLs

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Redis (for Celery)
redis-server

# Start Celery worker (in separate terminal)
celery -A IntelliFace worker --loglevel=info

# Start Celery beat (in separate terminal)
celery -A IntelliFace beat --loglevel=info

# Start development server
python manage.py runserver
```

### Docker Deployment
```bash
# Build and run
docker build -t intelliface .
docker run -p 8000:8000 intelliface
```

### Test ML Features
```bash
python test_ml_features.py
```

## 📊 Usage Workflow

### 1. Initial Setup
1. Admin creates Teachers, Students, Courses, and Classes
2. Configure IP cameras for each classroom
3. Students upload profile photos (system generates face embeddings)

### 2. Lecture Session
1. Teacher starts attendance session via API
2. System begins capturing snapshots from classroom cameras
3. Background tasks process images every 5 minutes
4. Face recognition automatically marks attendance
5. Teacher ends session (final processing occurs)

### 3. Attendance Review
1. Teachers view attendance reports per lecture
2. Manual corrections can be made if needed
3. Attendance data available via API for integration

## 🔧 Configuration

### Face Recognition Settings
- **Similarity Threshold**: 0.50 (configurable)
- **Processing Interval**: 5 minutes
- **Detection Size**: 640x640 pixels
- **Execution**: CPU (GPU support available)

### Camera Configuration
- **Protocol**: RTSP
- **Format**: H.264/H.265 streams
- **Capture**: JPEG snapshots via FFmpeg
- **Storage**: Django media files

## 📈 Performance

### Specifications
- **Face Detection**: ~100-500ms per image (CPU)
- **Embedding Generation**: ~50-100ms per face
- **Similarity Comparison**: ~1ms per comparison
- **Memory Usage**: ~500MB for ML models

### Scalability
- Supports multiple concurrent lectures
- Background processing prevents API blocking
- Horizontal scaling with multiple Celery workers

## 🔒 Security

### Data Protection
- Face embeddings (mathematical representations) stored, not raw images
- JWT-based API authentication
- Role-based access control
- HTTPS recommended for production

### Privacy Compliance
- Embeddings can be deleted independently of images
- No biometric data stored in reversible format
- Audit trail for all attendance modifications

## 📚 Documentation

- [ML Features Guide](ML_FEATURES.md) - Detailed ML implementation
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [API Documentation](API.md) - Complete API reference

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check [ML_FEATURES.md](ML_FEATURES.md) for troubleshooting
- Review logs for error details

---

**IntelliFace** - Making attendance tracking intelligent and effortless! 🎓✨