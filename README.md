# 🤖 ProFile Analyzer

A comprehensive resume analysis tool that provides intelligent feedback, scoring, and personalized recommendations for job seekers.

## ✨ Features

### 📄 **Enhanced File Support**
- **PDF Processing**: Improved text extraction using PyMuPDF for better accuracy
- **DOCX Support**: Native support for Microsoft Word documents
- **Format Validation**: Automatic detection of scanned documents, multi-column layouts, and image-heavy resumes

### 🔍 **Intelligent Information Extraction**
- **Enhanced Personal Info**: Improved name, email, phone, and URL extraction with better regex patterns
- **Smart Skills Detection**: Comprehensive skill matching with synonyms, abbreviations, and soft skills
- **Section Normalization**: Fuzzy matching for section headers (e.g., "Work History" → "Experience")
- **Education Parsing**: Advanced degree and institution extraction

### 🎯 **Field-Specific Analysis**
- **15+ Professional Fields**: Data Science, Web Development, AI/ML, Cybersecurity, Cloud Computing, DevOps, UI/UX, Blockchain, AR/VR, IoT, and more
- **Domain-Specific Skills**: Tailored skill recommendations for each field
- **Field-Relevant Projects**: Curated project ideas specific to your industry
- **Certification Guidance**: Industry-specific certification recommendations

### 📊 **Advanced Scoring System**
- **Field-Weighted Scoring**: Different criteria weights based on your professional field
- **Multi-Dimensional Analysis**: Structure (30%), Skills (30%), Certifications (15%), Clarity (15%), Projects (10%)
- **Clarity Detection**: Evaluates action verbs, metrics, bullet points, and concise writing
- **Real-time Updates**: Score updates as you edit extracted information

### 🛠 **Interactive Features**
- **Manual Editing**: Edit any incorrectly extracted information
- **Dynamic Sliders**: Control how many skills, certifications, and project ideas to display
- **Real-time Analysis**: Instant feedback as you make changes
- **Multiple Resume Comparison**: Side-by-side analysis of multiple resumes

### 📋 **Comprehensive Feedback**
- **Personalized Strengths/Weaknesses**: Dynamic analysis based on your resume content
- **Actionable Recommendations**: Specific courses, certifications, and project suggestions
- **Missing Information Detection**: Identifies gaps in your resume
- **Format Guidelines**: Pre-upload checklist for optimal results

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd resume_analyzer_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 📁 File Structure

```
resume_analyzer_app/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── venv/                 # Virtual environment (if used)
```

## 🎨 Usage

1. **Upload Your Resume**: Support for PDF and DOCX formats
2. **Review Guidelines**: Check the upload guidelines for optimal results
3. **Analyze Content**: Automatic extraction of personal info, skills, education, and certifications
4. **Edit if Needed**: Manually correct any extraction errors
5. **Get Feedback**: Receive personalized recommendations and scoring
6. **Compare Multiple**: Upload multiple resumes for side-by-side comparison

## 🔧 Technical Features

### **Enhanced Text Extraction**
- **PyMuPDF**: Superior PDF text extraction compared to pdfminer
- **python-docx**: Native DOCX file support
- **Error Handling**: Graceful handling of corrupted or unreadable files

### **Smart Information Processing**
- **Fuzzy Matching**: Handles variations in section headers and skill names
- **NLP Integration**: spaCy for named entity recognition and keyword extraction
- **Regex Optimization**: Improved patterns for contact information and URLs

### **Field-Specific Intelligence**
- **15+ Professional Domains**: Comprehensive coverage of modern career fields
- **Dynamic Weighting**: Scoring algorithms tailored to each field's requirements
- **Relevant Recommendations**: Skills, courses, and projects specific to your industry

### **User Experience**
- **Modern UI**: Clean, responsive design with gradient backgrounds
- **Interactive Elements**: Sliders, expanders, and real-time updates
- **Visual Feedback**: Progress bars, badges, and color-coded sections
- **Mobile-Friendly**: Responsive design that works on all devices

## 📈 Scoring Breakdown

### **Structure (30%)**
- Section completeness (Objective, Experience, Education, Skills, etc.)
- Formatting consistency
- Contact information presence

### **Skills (30%)**
- Technical skill relevance to field
- Skill diversity and depth
- Soft skills detection

### **Certifications (15%)**
- Industry-relevant certifications
- Provider recognition (AWS, Google, Microsoft, etc.)
- Certification diversity

### **Clarity (15%)**
- Action verbs and metrics usage
- Bullet point formatting
- Concise sentence structure

### **Projects (10%)**
- Project section presence
- Real-world examples
- Technical complexity

## 🎯 Supported Fields

- **Data Science**: Python, ML, SQL, Statistics, Visualization
- **Web Development**: Frontend/Backend, Frameworks, Databases
- **Artificial Intelligence**: Deep Learning, NLP, Computer Vision
- **Cybersecurity**: Network Security, Penetration Testing, Certifications
- **Cloud Computing**: AWS, Azure, GCP, DevOps, Infrastructure
- **Software Development**: Programming Languages, Algorithms, Testing
- **Business Analyst**: Requirements, Process Modeling, Analytics
- **Product Management**: Strategy, User Research, Analytics
- **UI/UX Design**: Design Tools, User Research, Prototyping
- **Digital Marketing**: SEO, Analytics, Social Media, Campaigns
- **Blockchain**: Smart Contracts, Web3, Cryptocurrency
- **DevOps**: CI/CD, Containers, Infrastructure as Code
- **AR/VR**: Unity, Unreal Engine, Spatial Computing
- **IoT**: Embedded Systems, Sensors, Wireless Protocols

## 🔄 Recent Updates

### **v2.0 - Comprehensive Enhancement**
- ✅ **PyMuPDF Integration**: Better PDF text extraction
- ✅ **DOCX Support**: Native Word document processing
- ✅ **Enhanced Extraction**: Improved personal info, skills, and education detection
- ✅ **Field-Specific Scoring**: Tailored algorithms for different professions
- ✅ **Manual Editing**: Interactive correction of extracted information
- ✅ **Format Validation**: Automatic detection of problematic resume formats
- ✅ **Pre-upload Guidelines**: Comprehensive checklist for optimal results
- ✅ **15+ Professional Fields**: Expanded domain coverage
- ✅ **Advanced NLP**: Better keyword extraction and entity recognition

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have suggestions for improvements, please:
1. Check the upload guidelines
2. Ensure your resume is in a supported format
3. Try editing extracted information if needed
4. Open an issue with detailed information

---

**Built with ❤️ for job seekers worldwide** 
