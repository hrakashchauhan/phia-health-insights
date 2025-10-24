# 📚 PHIA Platform Documentation

## 🏗 **System Architecture**

### **Core Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    PHIA Health Platform                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer (Streamlit)                                │
│  ├── User Interface Components                             │
│  ├── Interactive Dashboards                               │
│  ├── Data Visualization (Plotly)                          │
│  └── Authentication System                                 │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                       │
│  ├── Health Data Management                               │
│  ├── User Session Management                              │
│  ├── Analytics Engine                                     │
│  └── AI Integration Layer                                 │
├─────────────────────────────────────────────────────────────┤
│  AI & Analytics Layer                                       │
│  ├── Google Gemini Integration                            │
│  ├── Health Pattern Analysis                              │
│  ├── Correlation Detection                                │
│  └── Predictive Insights                                  │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── SQLite Database                                      │
│  ├── User Data Storage                                    │
│  ├── Health Metrics Storage                               │
│  └── Session Management                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ **Database Schema**

### **Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- SHA256 hashed
    email TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

### **Health Data Table**
```sql
CREATE TABLE health_data (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    sleep_hours REAL,
    steps INTEGER,
    heart_rate INTEGER,
    stress_score INTEGER,  -- 0-100 scale
    weight REAL,
    mood INTEGER,  -- 1-10 scale
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🤖 **AI Integration Details**

### **Google Gemini Configuration**
```python
import google.generativeai as genai

# Configure API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Health analysis prompt structure
prompt = f"""
You are PHIA, an advanced AI health analyst.
Analyze this health data: {health_summary}
User question: {user_question}
Provide evidence-based insights and recommendations.
"""
```

### **Health Analysis Engine**

The AI system performs comprehensive analysis including:

1. **Pattern Recognition**
   - Sleep consistency analysis
   - Activity trend detection
   - Stress pattern identification
   - Mood correlation analysis

2. **Correlation Analysis**
   - Sleep-mood relationships
   - Activity-stress connections
   - Heart rate-fitness correlations
   - Multi-metric trend analysis

3. **Predictive Insights**
   - Health risk assessment
   - Trend projection
   - Optimization recommendations
   - Preventive care suggestions

## 📊 **Data Flow Architecture**

```
User Input → Data Validation → Database Storage → Analysis Engine → AI Processing → Insights Generation → User Interface
```

### **Data Processing Pipeline**

1. **Input Validation**
   ```python
   def validate_health_data(data):
       # Range validation
       sleep_hours: 0.0 - 12.0
       steps: 0 - 30,000
       heart_rate: 40 - 120
       stress_score: 0 - 100
       weight: 30.0 - 200.0
       mood: 1 - 10
   ```

2. **Data Storage**
   ```python
   def save_health_data(user_id, date, metrics):
       # Insert or update daily health record
       # Maintain data integrity
       # Handle duplicate dates
   ```

3. **Analysis Processing**
   ```python
   def analyze_health_patterns(user_data):
       # Calculate trends (7-day vs 30-day)
       # Identify correlations
       # Generate insights
       # Prepare AI context
   ```

## 🔐 **Security Implementation**

### **Authentication System**
```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    hashed = hash_password(password)
    # Verify against database
```

### **Data Privacy**
- Local SQLite database storage
- No external data transmission (except AI queries)
- User data isolation
- Session-based authentication

## 🎨 **UI/UX Design Principles**

### **Design Philosophy**
- **Minimalist Interface:** Clean, focused design
- **Data-Driven Insights:** Information hierarchy based on importance
- **Accessibility:** Clear typography, intuitive navigation
- **Responsive Design:** Works across devices

### **Color Scheme**
```css
Primary: #667eea (Blue gradient)
Secondary: #764ba2 (Purple gradient)
Success: #28a745 (Green)
Warning: #ffc107 (Yellow)
Error: #dc3545 (Red)
Background: #f8f9fa (Light gray)
```

## 🚀 **Deployment Architecture**

### **Streamlit Cloud Deployment**
```yaml
# streamlit configuration
[server]
port = 8501
address = "0.0.0.0"

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

### **Environment Configuration**
```bash
# Production environment variables
GOOGLE_API_KEY=<gemini_api_key>
DATABASE_URL=sqlite:///phia_mvp.db
DEBUG=False
```

## 📈 **Performance Optimization**

### **Database Optimization**
- Indexed queries on user_id and date
- Efficient data retrieval patterns
- Minimal database connections

### **AI Query Optimization**
- Contextual data summarization
- Efficient prompt engineering
- Response caching strategies

### **Frontend Optimization**
- Streamlit caching for data operations
- Optimized chart rendering
- Minimal re-renders

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
def test_health_data_validation():
    # Test input validation
    # Test edge cases
    # Test error handling

def test_ai_integration():
    # Test API connectivity
    # Test response parsing
    # Test fallback mechanisms
```

### **Integration Tests**
- Database operations
- AI API integration
- User authentication flow
- End-to-end user journeys

## 📊 **Analytics & Monitoring**

### **Health Metrics Tracking**
- User engagement patterns
- Feature usage statistics
- AI query performance
- System health monitoring

### **Error Handling**
```python
try:
    # AI API call
    response = model.generate_content(prompt)
    return response.text
except Exception as e:
    # Fallback to rule-based responses
    return generate_fallback_response(user_data, question)
```

## 🔄 **Data Migration & Backup**

### **Database Backup Strategy**
```bash
# Automated backup script
sqlite3 phia_mvp.db ".backup backup_$(date +%Y%m%d).db"
```

### **Data Export Functionality**
```python
def export_user_data(user_id, format='csv'):
    # Export health data
    # Generate insights report
    # Create downloadable file
```

## 🛠 **Development Workflow**

### **Local Development Setup**
```bash
# Clone repository
git clone https://github.com/hrakashchauhan/phia-health-insights.git

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add API keys

# Run development server
streamlit run streamlit_app.py
```

### **Code Quality Standards**
- PEP 8 compliance
- Type hints where applicable
- Comprehensive documentation
- Error handling best practices

## 🔮 **Future Enhancements**

### **Phase 2: Advanced Features**
- Wearable device integration
- Machine learning models
- Predictive health analytics
- Social features

### **Phase 3: Healthcare Integration**
- HIPAA compliance
- EHR integration
- Clinical decision support
- Telemedicine features

### **Phase 4: Enterprise Features**
- Multi-tenant architecture
- Advanced analytics dashboard
- API for third-party integration
- Enterprise security features

## 📞 **Support & Maintenance**

### **Monitoring**
- Application performance monitoring
- Error tracking and alerting
- User feedback collection
- System health checks

### **Maintenance Schedule**
- Weekly dependency updates
- Monthly security reviews
- Quarterly feature releases
- Annual architecture reviews

---

**This documentation is maintained alongside the codebase and updated with each release.**
