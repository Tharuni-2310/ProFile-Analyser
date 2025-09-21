import streamlit as st
import re
import random
import datetime
import spacy
import fitz  # PyMuPDF for better PDF extraction (fitz is the module name for PyMuPDF)
from difflib import SequenceMatcher
import docx  # For .docx support
from io import BytesIO  # For PDF generation
import base64

# --- Page config & theme ---
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# Global styling to modernize the look & feel
st.markdown(
    """
    <style>
      /* Background */
      .stApp { background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%); }
      .stApp:before { content: ""; position: fixed; inset: 0; pointer-events: none; opacity: .35;
        background-image: radial-gradient(#dbe8ff 1px, transparent 1px); background-size: 22px 22px; }

      /* Headings */
      h1, h2, h3 { font-family: 'Segoe UI', Roboto, Arial, sans-serif; }
      h1 { color: #0f67ff; letter-spacing: .3px; }
      h2, h3 { color: #0c2d57; }

      /* Hero - Modern Dark Theme */
      .hero { padding: 20px 24px; border-radius: 12px; margin: 4px 0 16px 0;
              background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
              border: 1px solid #667eea; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
      .hero .title { font-size: 26px; font-weight: 800; color:#ffffff; }
      .hero .subtitle { color:#e2e8f0; }

      /* Cards */
      .card {
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #e8eef7;
        background: #ffffff;
        box-shadow: 0 4px 14px rgba(15, 103, 255, 0.06);
        margin-bottom: 1rem;
      }
      .card:hover { box-shadow: 0 8px 22px rgba(15,103,255,.1); }

      /* Buttons - Modern Dark Theme */
      .stButton > button, button[data-testid="baseButton-secondary"] {
        background: #2d3748 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 1.25rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; font-weight: 600 !important; transition: all 0.3s ease !important;
        border-left: 4px solid #667eea !important;
      }
      .stDownloadButton > button, button[data-testid="baseButton-secondary"] {
        background: #4a5568 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 1.25rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; font-weight: 600 !important; transition: all 0.3s ease !important;
        border-left: 4px solid #805ad5 !important;
      }
      /* Primary CTA buttons */
      .cta {
        display:inline-block; padding: 12px 20px; border-radius: 8px; font-weight: 700;
        background: #667eea; color: #fff; border: none; transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102,126,234,0.3); border-left: 4px solid #553c9a;
      }
      .cta:hover { background: #5a67d8; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(102,126,234,0.4); }
      .cta:active { transform: translateY(0); }
      .stButton>button:hover { background: #4a5568; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.2); }
      .stButton>button:active { transform: translateY(0); }
      .stDownloadButton>button:hover { background: #718096 !important; transform: translateY(-2px) !important; box-shadow: 0 6px 16px rgba(0,0,0,0.2) !important; }
      .stDownloadButton>button:active { transform: translateY(0) !important; }
      
      /* Force override Streamlit button styles */
      .stButton > button:hover { background: #4a5568 !important; transform: translateY(-2px) !important; box-shadow: 0 6px 16px rgba(0,0,0,0.2) !important; }
      .stButton > button:active { transform: translateY(0) !important; }
      
      /* Additional button overrides */
      button[data-testid="baseButton-secondary"]:hover { background: #4a5568 !important; transform: translateY(-2px) !important; }
      button[data-testid="baseButton-secondary"]:active { transform: translateY(0) !important; }

      /* Metrics */
      [data-testid="stMetricValue"] { color: #0f67ff; }

      /* Links */
      a { color: #0f67ff; text-decoration: none; }
      a:hover { text-decoration: underline; }

      /* Pills / badges */
      .pill {
        display: inline-block; padding: 4px 10px; margin: 3px; border-radius: 999px;
        font-size: 12px; font-weight: 600; border: 1px solid #e8eef7; background: #f6f9ff; color: #0c2d57;
      }
      .pill.good { background: #eaf7ed; color: #1e7a3a; border-color: #cfead6; }
      .pill.warn { background: #fff7e6; color: #8a5a00; border-color: #ffe1a6; }
      .pill.bad { background: #ffefef; color: #a21919; border-color: #ffcaca; }

      /* KPI box */
      .kpi {
        padding: 12px 14px; border-radius: 12px; background: #ffffff; border: 1px solid #e8eef7;
        box-shadow: 0 4px 12px rgba(15, 103, 255, 0.04); margin-bottom: 10px;
      }
      .kpi .title { font-size: 12px; color: #6b7a90; text-transform: uppercase; letter-spacing: .08em; }
      .kpi .value { font-size: 20px; font-weight: 800; color: #0f67ff; }

      /* Score bar */
      .scorebar { height: 10px; background: #eef3ff; border-radius: 999px; overflow: hidden; }
      .scorebar > div { height: 10px; background: linear-gradient(90deg, #0f67ff, #5aa1ff); }
      .score-badge { position: relative; overflow: hidden; }
      .score-badge:after { content:""; position:absolute; top:0; left:-40%; width:40%; height:100%;
        background: linear-gradient(90deg, rgba(255,255,255,.0), rgba(255,255,255,.35), rgba(255,255,255,.0));
        transform: skewX(-20deg); animation: shine 2.6s infinite; }
      @keyframes shine { 0%{ left:-40%; } 60%{ left:120%; } 100%{ left:120%; } }

      /* Sidebar branding */
      .brand-banner { padding: 12px 16px; border-radius: 12px; margin: 4px 0 10px 0;
                      background: linear-gradient(135deg, #6a11cb 0%, #2575fc 50%, #00c6ff 100%);
                      color: #ffffff !important; font-weight: 900; font-size: 22px; text-align: center;
                      letter-spacing: 1px; text-transform: uppercase; box-shadow: 0 8px 24px rgba(0,0,0,0.25); }

      /* Sidebar card */
      .nav-card { padding: 16px 18px; border-radius: 12px; background: #2d3748 !important; border: 1px solid #4a5568 !important; box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important; }
      .nav-title { font-weight: 800; color: #ffffff !important; margin-bottom: 12px; letter-spacing: .3px; }
      .brand-title { font-size: 20px; font-weight: 900; color: #ffffff !important; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1px; }
      .nav-grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
      .nav-item { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-radius:8px; border:1px solid #4a5568; background:#4a5568; cursor:pointer; transition: all 0.3s ease; }
      .nav-item .label { display:flex; align-items:center; gap:10px; font-weight:600; color:#ffffff; }
      .nav-item .badge { font-size:11px; padding:4px 8px; border-radius:6px; background:#667eea; color:#ffffff; border:1px solid #553c9a; }
      .nav-item.active { background: #667eea !important; border-color:#553c9a !important; box-shadow: 0 4px 12px rgba(102,126,234,0.4) !important; }
      .nav-item:hover { background: #5a67d8 !important; transform: translateY(-1px) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# (Removed old Navigation links)

# Page anchors
st.markdown('<a name="top"></a>', unsafe_allow_html=True)

# Simple page switcher
PAGES = ["Start / Upload", "Edit & Build", "ATS Compatibility", "Resume Generator", "Job Matching", "Insights"]

# Initialize nav state
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = PAGES[0]

with st.sidebar:
    st.markdown("<div class='brand-banner'>ProFile Analyser</div>", unsafe_allow_html=True)
    st.markdown("<div class='nav-card'>", unsafe_allow_html=True)
    st.markdown("<div class='nav-title'>Go to</div>", unsafe_allow_html=True)
    # custom grid buttons that set the radio value
    for label in PAGES:
        is_active = (st.session_state.get("nav_page") == label)
        css_class = "nav-item active" if is_active else "nav-item"
        cols = st.columns([1,0.3])
        with cols[0]:
            if st.button(label, key=f"goto_{label}"):
                st.session_state["nav_page"] = label
                try:
                    st.rerun()
                except Exception:
                    pass
        with cols[1]:
            st.markdown(f"<div class='badge'>{'Now' if is_active else ''}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='{css_class}' style='display:none'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Removed Prev/Next buttons per request
    # radio defined above

def section_card(title):
    st.markdown(f"<div class='card'><h3>{title}</h3>", unsafe_allow_html=True)

def end_card():
    st.markdown("</div>", unsafe_allow_html=True)

# Section banners (placeholders until full refactor of content into blocks)
page = st.session_state.get("nav_page", PAGES[0])
if page == "Start / Upload":
    st.markdown('<a name="edit"></a>', unsafe_allow_html=True)
    st.markdown("## 🏁 Start / Upload")
elif page == "Edit & Build":
    st.markdown('<a name="edit"></a>', unsafe_allow_html=True)
    st.markdown("## ✏️ Edit & Build Resume")
elif page == "ATS Compatibility":
    st.markdown('<a name="ats"></a>', unsafe_allow_html=True)
    st.markdown("## 🎯 ATS Compatibility")
elif page == "Resume Generator":
    st.markdown('<a name="generator"></a>', unsafe_allow_html=True)
    st.markdown("## 📝 Resume Generator")
elif page == "Job Matching":
    st.markdown('<a name="jobs"></a>', unsafe_allow_html=True)
    st.markdown("## 🎯 Job Matching")
elif page == "Insights":
    st.markdown('<a name="insights"></a>', unsafe_allow_html=True)
    st.markdown("## 💡 Insights")

nlp = spacy.load("en_core_web_sm")

# --- Enhanced PDF Text Extraction ---
def extract_text_from_pdf(file_path):
    """Improved PDF text extraction using PyMuPDF"""
    try:
        doc = fitz.open(file_path)
        text = ""
        urls = set()
        for page in doc:
            text += page.get_text()
            try:
                for link in page.get_links():
                    uri = link.get('uri')
                    if uri and isinstance(uri, str) and uri.startswith(('http://', 'https://')):
                        urls.add(uri.strip())
            except Exception:
                pass
        doc.close()
        if urls:
            text += "\n\n" + "\n".join(sorted(urls))
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from .docx files"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        # Append embedded hyperlink targets (clickable links that may not appear in visible text)
        try:
            from docx.opc.constants import RELATIONSHIP_TYPE as DOCX_RT
            urls = set()
            for rel in doc.part.rels.values():
                if getattr(rel, 'reltype', None) == DOCX_RT.HYPERLINK:
                    target = getattr(rel, 'target_ref', None)
                    if target and isinstance(target, str) and target.startswith(('http://', 'https://')):
                        urls.add(target.strip())
            if urls:
                text += "\n" + "\n".join(sorted(urls))
        except Exception:
            pass
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_file(file_path, file_type):
    """Extract text based on file type"""
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    else:
        return ""

# --- Enhanced Skill Keywords with Synonyms and Abbreviations ---
SKILL_KEYWORDS = {
    "Data Science": [
        "python", "machine learning", "pandas", "numpy", "tensorflow", "data analysis",
        "scikit-learn", "sklearn", "jupyter", "matplotlib", "seaborn", "plotly",
        "sql", "postgresql", "mysql", "mongodb", "spark", "hadoop", "kafka",
        "powerbi", "tableau", "excel", "r", "statistics", "regression", "classification",
        "clustering", "nlp", "natural language processing", "deep learning", "neural networks"
    ],
    "Web Development": [
        "html", "css", "javascript", "js", "react", "vue", "angular", "node", "nodejs",
        "flask", "django", "express", "mongodb", "mysql", "postgresql", "rest api",
        "graphql", "typescript", "ts", "bootstrap", "tailwind", "sass", "less",
        "webpack", "babel", "npm", "yarn", "git", "github", "docker", "kubernetes"
    ],
    "Android Development": [
        "android", "kotlin", "java", "xml", "gradle", "android studio", "firebase",
        "room database", "retrofit", "okhttp", "glide", "picasso", "jetpack compose",
        "material design", "mvvm", "mvp", "dagger", "hilt", "coroutines", "flow"
    ],
    "UI/UX": [
        "figma", "adobe xd", "photoshop", "sketch", "invision", "protopie", "framer",
        "wireframing", "prototyping", "user research", "usability testing", "design systems",
        "responsive design", "accessibility", "wcag", "user personas", "journey mapping"
    ],
    "Artificial Intelligence": [
        "deep learning", "neural networks", "nlp", "bert", "transformers", "pytorch", "keras",
        "tensorflow", "opencv", "computer vision", "cnn", "rnn", "lstm", "gru", "gan",
        "reinforcement learning", "q-learning", "openai", "gpt", "chatgpt", "langchain"
    ],
    "Cybersecurity": [
        "network security", "penetration testing", "pen testing", "firewalls", "siem",
        "vulnerability assessment", "encryption", "ssl", "tls", "wireshark", "nmap",
        "metasploit", "burp suite", "owasp", "ethical hacking", "ceh", "comptia security+",
        "cryptography", "hash functions", "digital signatures", "vpn", "ids", "ips"
    ],
    "Cloud Computing": [
        "aws", "amazon web services", "azure", "gcp", "google cloud", "cloud", "devops",
        "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "gitlab", "github actions",
        "terraform", "ansible", "serverless", "lambda", "ec2", "s3", "rds", "vpc",
        "load balancer", "auto scaling", "cloudformation", "cloudwatch"
    ],
    "Software Development": [
        "c++", "cpp", "java", "python", "oop", "object oriented programming", "git",
        "algorithms", "data structures", "leetcode", "hackerrank", "design patterns",
        "microservices", "api", "rest", "graphql", "testing", "unit testing", "integration testing",
        "tdd", "bdd", "agile", "scrum", "kanban", "jira", "confluence"
    ],
    "Business Analyst": [
        "business analysis", "requirement gathering", "process modeling", "sql", "excel",
        "powerbi", "tableau", "jira", "confluence", "user stories", "use cases",
        "bpmn", "uml", "data modeling", "er diagrams", "stakeholder management",
        "gap analysis", "swot analysis", "root cause analysis"
    ],
    "Product Management": [
        "roadmap", "product strategy", "user stories", "agile", "scrum", "market research",
        "competitive analysis", "user personas", "journey mapping", "a/b testing",
        "analytics", "google analytics", "mixpanel", "amplitude", "jira", "confluence",
        "figma", "prototyping", "mvp", "minimum viable product"
    ],
    "Mobile App Development": [
        "android", "ios", "swift", "kotlin", "flutter", "react native", "xamarin",
        "mobile development", "app store", "google play", "firebase", "push notifications",
        "in-app purchases", "mobile ui", "responsive design", "cross platform"
    ],
    "Game Development": [
        "unity", "unreal", "c#", "game design", "3d modeling", "physics engine",
        "blender", "maya", "3ds max", "game mechanics", "level design", "character design",
        "animation", "rigging", "texturing", "shaders", "game physics", "ai in games"
    ],
    "Finance": [
        "accounting", "financial analysis", "excel", "valuation", "markets", "investment",
        "portfolio management", "risk management", "derivatives", "options", "futures",
        "bonds", "stocks", "mutual funds", "etf", "financial modeling", "dcf", "npv", "irr"
    ],
    "HR": [
        "recruitment", "onboarding", "payroll", "employee engagement", "hrms", "compliance",
        "performance management", "talent acquisition", "employee relations", "benefits",
        "compensation", "training", "development", "diversity", "inclusion", "workplace culture"
    ],
    "Digital Marketing": [
        "seo", "search engine optimization", "sem", "search engine marketing", "google analytics",
        "content marketing", "social media", "email marketing", "ppc", "google ads",
        "facebook ads", "instagram ads", "linkedin ads", "conversion optimization",
        "landing pages", "a/b testing", "marketing automation", "hubspot", "mailchimp"
    ],
    "Blockchain": [
        "blockchain", "bitcoin", "ethereum", "solidity", "smart contracts", "web3",
        "defi", "decentralized finance", "nft", "non-fungible tokens", "cryptocurrency",
        "hyperledger", "consensus algorithms", "proof of work", "proof of stake",
        "metamask", "ipfs", "interplanetary file system"
    ],
    "DevOps": [
        "devops", "ci/cd", "continuous integration", "continuous deployment", "jenkins",
        "gitlab ci", "github actions", "docker", "kubernetes", "terraform", "ansible",
        "prometheus", "grafana", "elk stack", "elasticsearch", "logstash", "kibana",
        "monitoring", "logging", "infrastructure as code", "iac"
    ],
    "UI/UX Design": [
        "ui design", "ux design", "user interface", "user experience", "figma", "sketch",
        "adobe xd", "invision", "prototyping", "wireframing", "user research",
        "usability testing", "design systems", "responsive design", "mobile design",
        "accessibility", "wcag", "user personas", "journey mapping"
    ],
    "AR/VR": [
        "augmented reality", "virtual reality", "ar", "vr", "unity", "unreal engine",
        "oculus", "htc vive", "hololens", "3d modeling", "blender", "maya",
        "spatial computing", "mixed reality", "mr", "computer vision", "tracking"
    ],
    "IoT": [
        "internet of things", "iot", "raspberry pi", "arduino", "sensors", "mqtt",
        "coap", "edge computing", "fog computing", "embedded systems", "microcontrollers",
        "wireless protocols", "bluetooth", "wifi", "zigbee", "lorawan", "nb-iot"
    ]
}

# --- Courses by Field ---
COURSES = {
    "Data Science": [
        "Data Science with Python – IBM (Coursera)",
        "Machine Learning A-Z – Udemy",
        "Python for Data Science – DataCamp",
        "SQL for Data Analysis – Mode Analytics",
        "Statistics for Data Science – Coursera",
        "Deep Learning Specialization – DeepLearning.AI (Coursera)"
    ],
    "Web Development": [
        "React for Beginners – Udemy",
        "Full Stack with Django – Udemy",
        "JavaScript Complete Guide – Udemy",
        "Node.js Bootcamp – Udemy",
        "MongoDB Complete Course – Udemy",
        "Git & GitHub Crash Course – Udemy"
    ],
    "Android Development": [
        "Android with Kotlin – Udemy",
        "Build Apps with Firebase – Udemy",
        "Android App Development – Coursera",
        "Kotlin for Android – Udemy",
        "Android Studio Masterclass – Udemy"
    ],
    "UI/UX": [
        "Figma UI Basics – Udemy",
        "UX Design Crash Course – Udemy",
        "Adobe XD Complete Course – Udemy",
        "User Research Methods – Coursera",
        "Prototyping with Figma – Udemy"
    ],
    "Artificial Intelligence": [
        "Deep Learning Specialization – DeepLearning.AI (Coursera)",
        "Natural Language Processing with BERT (Coursera)",
        "AI For Everyone (Coursera)",
        "Computer Vision with OpenCV – Udemy",
        "Machine Learning with Python – Coursera",
        "TensorFlow Developer Certificate – Google"
    ],
    "Cybersecurity": [
        "Introduction to Cyber Security (Coursera)",
        "Network Security (Udemy)",
        "Penetration Testing (NPTEL)",
        "Ethical Hacking Course – Udemy",
        "CompTIA Security+ Certification – Udemy",
        "CEH v12 Complete Course – Udemy"
    ],
    "Cloud Computing": [
        "AWS Cloud Practitioner Essentials (AWS)",
        "Azure Fundamentals (Microsoft)",
        "DevOps on AWS (Coursera)",
        "CI/CD with GitHub Actions (Coursera)",
        "Docker Complete Course – Udemy",
        "Kubernetes for Beginners – Udemy"
    ],
    "Software Development": [
        "Java Programming (Coursera)",
        "Data Structures & Algorithms (Coursera)",
        "Git & GitHub Bootcamp (Udemy)",
        "Python Complete Course – Udemy",
        "C++ Programming – Udemy",
        "System Design Interview Course – Udemy"
    ],
    "Business Analyst": [
        "Business Analysis Fundamentals (Udemy)",
        "Excel to MySQL: Analytics for Business (Coursera)",
        "SQL for Business Analysts – Udemy",
        "Power BI Complete Course – Udemy",
        "Tableau for Data Science – Udemy",
        "Business Process Modeling – Udemy"
    ],
    "Product Management": [
        "Digital Product Management (Coursera)",
        "Product Management by Pragmatic Institute",
        "Agile Project Management – Udemy",
        "User Story Mapping – Udemy",
        "Product Strategy Course – Udemy",
        "A/B Testing for Product Managers – Udemy"
    ],
    "Mobile App Development": [
        "iOS App Development with Swift (Coursera)",
        "Flutter & Dart (Udemy)",
        "React Native Complete Course – Udemy",
        "Mobile App Development – Udemy",
        "Cross-Platform Development – Udemy"
    ],
    "Game Development": [
        "Game Development with Unity (Coursera)",
        "Unreal Engine C++ Developer (Udemy)",
        "Unity 2D Game Development – Udemy",
        "3D Modeling with Blender – Udemy",
        "Game Design Principles – Udemy"
    ],
    "Finance": [
        "Financial Markets – Yale (Coursera)",
        "Accounting Fundamentals (Udemy)",
        "Investment Management – Coursera",
        "Financial Modeling – Udemy",
        "Risk Management – Coursera",
        "Portfolio Management – Udemy"
    ],
    "HR": [
        "Human Resource Management (Coursera)",
        "HR Analytics (Udemy)",
        "Recruitment and Selection – Udemy",
        "Employee Relations – Udemy",
        "HR Compliance – Udemy",
        "Performance Management – Udemy"
    ],
    "Digital Marketing": [
        "Digital Marketing Specialization (Coursera)",
        "SEO Training (Udemy)",
        "Google Analytics (Coursera)",
        "Social Media Marketing – Udemy",
        "Email Marketing – Udemy",
        "Content Marketing – Udemy"
    ],
    "Blockchain": [
        "Blockchain Basics – Coursera",
        "Ethereum Development – Udemy",
        "Solidity Programming – Udemy",
        "Web3 Development – Udemy",
        "Cryptocurrency Trading – Udemy",
        "DeFi Fundamentals – Udemy"
    ],
    "DevOps": [
        "DevOps Fundamentals – Udemy",
        "Docker and Kubernetes – Udemy",
        "CI/CD Pipeline – Udemy",
        "Terraform for Beginners – Udemy",
        "Ansible Automation – Udemy",
        "Monitoring and Logging – Udemy"
    ],
    "UI/UX Design": [
        "UI/UX Design Bootcamp – Udemy",
        "User Experience Design – Coursera",
        "Prototyping with Figma – Udemy",
        "Design Systems – Udemy",
        "User Research Methods – Udemy",
        "Accessibility Design – Udemy"
    ],
    "AR/VR": [
        "Unity AR Development – Udemy",
        "VR Development with Unity – Udemy",
        "3D Modeling for VR – Udemy",
        "Spatial Computing – Coursera",
        "Mixed Reality Development – Udemy"
    ],
    "IoT": [
        "IoT Fundamentals – Coursera",
        "Arduino Programming – Udemy",
        "Raspberry Pi Projects – Udemy",
        "IoT Security – Udemy",
        "Edge Computing – Udemy",
        "Sensor Networks – Udemy"
    ]
}

# --- Enhanced Section Headers with Fuzzy Matching ---
SECTION_HEADERS = {
    "experience": ["experience", "work experience", "employment", "work history", "professional experience", "career", "employment history"],
    "education": ["education", "academic", "academics", "qualifications", "academic background", "educational background"],
    "skills": ["skills", "technical skills", "competencies", "expertise", "technologies", "tools", "programming languages"],
    "projects": ["projects", "project work", "portfolio", "achievements", "key projects", "work samples"],
    "certifications": ["certifications", "certificates", "credentials", "accreditations", "professional certifications"],
    "contact": ["contact", "contact information", "personal information", "details", "contact details"],
    "objective": ["objective", "career objective", "summary", "profile", "personal statement", "career summary"],
    "declaration": ["declaration", "statement", "affirmation", "disclaimer"]
}

def normalize_section_heading(text):
    """Normalize section headings using fuzzy matching"""
    text_lower = text.lower().strip()
    for section, variations in SECTION_HEADERS.items():
        for variation in variations:
            if SequenceMatcher(None, text_lower, variation).ratio() > 0.8:
                return section
    return text_lower

# --- Enhanced Personal Info Extraction ---
def extract_personal_info(text):
    """Enhanced personal information extraction with improved name detection"""
    
    def is_valid_name(name_candidate):
        """Validate if a candidate string is likely a person's name"""
        if not name_candidate or len(name_candidate.strip()) < 2:
            return False
            
        # Clean the candidate
        cleaned = re.sub(r"[^A-Za-z\s\-'.]", "", name_candidate).strip()
        words = cleaned.split()
        
        # Must have 2-4 words
        if not (2 <= len(words) <= 4):
            return False
            
        # Each word should start with capital letter and be mostly alphabetic
        for word in words:
            if not word[0].isupper() or not word.replace("'", "").replace("-", "").isalpha():
                return False
                
        # Avoid common non-name patterns
        tech_words = {
            "java", "python", "html", "css", "sql", "react", "node", "django", "flask", 
            "aws", "azure", "javascript", "typescript", "angular", "vue", "spring",
            "developer", "engineer", "analyst", "manager", "director", "consultant",
            "software", "web", "mobile", "frontend", "backend", "fullstack", "data",
            "science", "machine", "learning", "artificial", "intelligence", "cloud",
            "devops", "database", "api", "rest", "graphql", "docker", "kubernetes"
        }
        
        # Check if any word is a tech term
        for word in words:
            if word.lower() in tech_words:
                return False
                
        # Avoid email-like patterns
        if "@" in name_candidate or "." in name_candidate.split()[-1]:
            return False
            
        # Avoid phone number patterns
        if re.search(r'\d{3,}', name_candidate):
            return False
            
        return True
    
    # Improved name extraction
    lines = [ln.strip() for ln in text.split("\n")[:20] if ln.strip()]
    name = "Not found"
    
    # 1) Look for explicit name labels first
    name_label_patterns = [
        r"(?i)^(?:name|full\s*name|applicant)\s*[:\-]\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
        r"(?i)^(?:name|full\s*name|applicant)\s*[:\-]\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})"
    ]
    
    for pattern in name_label_patterns:
        for line in lines[:10]:
            match = re.search(pattern, line)
            if match:
                candidate = match.group(1).strip()
                if is_valid_name(candidate):
                    name = candidate
                    break
        if name != "Not found":
            break
    
    # 2) Look for standalone names in first few lines (most common case)
    if name == "Not found":
        for i, line in enumerate(lines[:8]):  # Check first 8 lines
            # Skip lines that look like headers or contact info
            if any(keyword in line.lower() for keyword in ["email", "phone", "address", "linkedin", "github", "portfolio", "objective", "summary", "profile"]):
                continue
                
            # Clean the line and check if it's a valid name
            cleaned_line = re.sub(r"[^A-Za-z\s\-'.]", "", line).strip()
            if is_valid_name(cleaned_line):
                # Additional check: make sure it's not a job title or company name
                if not any(title in line.lower() for title in ["engineer", "developer", "analyst", "manager", "consultant", "specialist", "coordinator", "assistant", "associate", "senior", "junior", "lead", "principal", "architect", "director", "vice", "president", "ceo", "cto", "cfo"]):
                    name = cleaned_line
                    break
    
    # 3) Fallback: Use spaCy NER on top section
    if name == "Not found":
        try:
            # Use first 10 lines for NER
            top_text = "\n".join(lines[:10])
            doc = nlp(top_text)
            
            # Look for PERSON entities
            person_entities = []
            for ent in doc.ents:
                if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
                    if is_valid_name(ent.text):
                        person_entities.append(ent.text.strip())
            
            if person_entities:
                # Prefer entities that appear earlier in the text
                name = person_entities[0]
        except Exception:
            pass
    
    # 4) Final fallback: simple pattern matching
    if name == "Not found":
        simple_patterns = [
            r"^([A-Z][a-z]+\s[A-Z][a-z]+)$",  # First Last
            r"^([A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+)$",  # First Middle Last
            r"^([A-Z][a-z]+\s[A-Z]\.\s[A-Z][a-z]+)$"  # First M. Last
        ]
        
        for pattern in simple_patterns:
            for line in lines[:5]:
                match = re.match(pattern, line.strip())
                if match:
                    candidate = match.group(1).strip()
                    if is_valid_name(candidate):
                        name = candidate
                        break
            if name != "Not found":
                break
    
    # Enhanced email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else "Not found"
    
    # Enhanced phone extraction
    phone_patterns = [
        r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
        r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}',
        r'\+?[0-9]{10,15}'
    ]
    phone = "Not found"
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            if isinstance(phones[0], tuple):
                phone = ''.join(phones[0])
            else:
                phone = phones[0]
            break
    
    # Enhanced URL extraction
    def normalize_url(u: str) -> str:
        if not u:
            return u
        u = u.strip()
        if u.startswith("www."):
            return "https://" + u
        if u.startswith("linkedin.com"):
            return "https://www." + u
        if u and not u.startswith("http"):
            return "https://" + u
        return u

    # Accept URLs with or without protocol and across potential newlines after labels
    joined = text
    linkedin_pattern = r'(?:linkedin\s*[:\-]?\s*(?:\n|\r|\s)*)?(https?://(?:www\.)?linkedin\.com/[a-zA-Z0-9\-_/=?]+|www\.linkedin\.com/[a-zA-Z0-9\-_/=?]+|linkedin\.com/[a-zA-Z0-9\-_/=?]+)'
    linkedin_matches = re.findall(linkedin_pattern, joined, re.IGNORECASE)
    linkedin = normalize_url(linkedin_matches[0]) if linkedin_matches else "Not found"

    github_pattern = r'(?:github\s*[:\-]?\s*(?:\n|\r|\s)*)?(https?://(?:www\.)?github\.com/[a-zA-Z0-9\-_/=?]+|www\.github\.com/[a-zA-Z0-9\-_/=?]+|github\.com/[a-zA-Z0-9\-_/=?]+)'
    github_matches = re.findall(github_pattern, joined, re.IGNORECASE)
    github = normalize_url(github_matches[0]) if github_matches else "Not found"

    portfolio_pattern = r'(?:portfolio\s*[:\-]?\s*(?:\n|\r|\s)*)?(https?://[\w\.-]+\.[a-z]{2,}(?:/[a-zA-Z0-9\-_/=?#]+)?|www\.[\w\.-]+\.[a-z]{2,}(?:/[a-zA-Z0-9\-_/=?#]+)?)'
    portfolio_matches = re.findall(portfolio_pattern, joined, re.IGNORECASE)
    portfolio = normalize_url(portfolio_matches[0]) if portfolio_matches else "Not found"
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio
    }

# --- Enhanced Education Extraction ---
def extract_education_info(text):
    """Enhanced education information extraction (section-aware, robust patterns, deduped)"""
    degree_keywords = [
        "bachelor", "master", "phd", "m\.?tech", "b\.?tech", "b\.?e", "m\.?e",
        "b\.?sc", "m\.?sc", "mba", "bba", "associate", "diploma", "high school",
        "intermediate", "secondary", "senior secondary", "10th", "12th", "hsc", "ssc"
    ]
    inst_keywords = [
        "university", "college", "institute", "school", "academy", "polytechnic"
    ]
    year_pattern = r"(19|20)\d{2}"
    range_pattern = r"(19|20)\d{2}\s*[\-–—]\s*(19|20)?\d{2}|to\s*(19|20)\d{2}"

    found = []

    # 1) Section-aware parse: Education/Academics/Qualifications
    header_multi = re.compile(r"(?im)^(education|academics|academic qualifications|qualifications|educational background)\b[:\-]?(.*)$")
    for header in header_multi.finditer(text):
        start = header.end()
        nxt = re.search(r"(?im)^(experience|work|employment|projects|skills?|certifications?|licenses|summary|objective|contact|achievements?)\b", text[start:])
        end = start + nxt.start() if nxt else len(text)
        block = text[start:end]
        if header.group(2):
            block = header.group(2) + "\n" + block
        items = re.split(r"[\n\r;\u2022\u2023\u25E6\u2043\-\–\—\|/•·∙‣◦▪]+", block)
        for item in items:
            line = item.strip()
            low = line.lower()
            if len(line) < 4:
                continue
            if any(re.search(k, low) for k in degree_keywords) or any(k in low for k in inst_keywords) or re.search(year_pattern, low):
                # Keep typical education lines; avoid pure addresses/contacts
                if "@" in low or "http" in low:
                    continue
                found.append(line)

    # 2) Fallback patterns across full text
    degree_union = '(?:' + '|'.join(degree_keywords) + ')'
    inst_union = '(?:' + '|'.join(inst_keywords) + ')'
    patterns = [
        rf"(({degree_union})[^\n\r,;]*?(?:at|from|in)?\s*[A-Za-z .&'\-]*\s*(?:{year_pattern})?(?:\s*(?:{range_pattern}))?)",
        rf"([A-Za-z .&'\-]+(?:{inst_union})[^\n\r,;]*\s*(?:{year_pattern})?(?:\s*(?:{range_pattern}))?)"
    ]
    for pattern in patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
        except re.error:
            continue
        for match in matches:
            if isinstance(match, tuple):
                edu_text = ' '.join([m for m in match if isinstance(m, str) and m]).strip()
            else:
                edu_text = match.strip()
            if edu_text and len(edu_text) > 5:
                found.append(edu_text)

    # 3) Normalize and deduplicate
    normalized = []
    seen = set()
    for line in found:
        clean = re.sub(r"\s+", " ", line).strip(" .")
        # Collapse duplicated consecutive words: e.g., "Intermediate Intermediate" -> "Intermediate"
        clean = re.sub(r"\b(\w+)(?:\s+\1)+\b", r"\1", clean, flags=re.IGNORECASE)
        key = clean.lower()
        if key not in seen:
            seen.add(key)
            normalized.append(clean)

    # 4) Preferred formatting: B.Tech college, Intermediate college, 10th school
    def extract_institute(line_text: str) -> str:
        t = line_text
        # Remove degree keywords and years
        t = re.sub(r"(?i)\b(b\.?(e|tech)|btech|b\.e|b\.tech|m\.?(e|tech)|mtech|b\.sc|m\.sc|bsc|msc|phd|mba|bba|associate|diploma|intermediate|12th|hsc|senior secondary|10th|ssc|secondary|standard|grade)\b", " ", t)
        t = re.sub(r"(?i)\b(at|from|in|of)\b", " ", t)
        t = re.sub(r"\b(19|20)\d{2}\b", " ", t)
        t = re.sub(r"\s+[\-–—]\s+", " ", t)
        t = re.sub(r"\s+", " ", t).strip(" ,.-")
        return t

    btech_line = None
    inter_line = None
    ssc_line = None

    for ln in normalized:
        low = ln.lower()
        if btech_line is None and re.search(r"\b(b\.?(e|tech)|btech|b\.e|b\.tech)\b", low):
            btech_line = f"B.Tech - {extract_institute(ln)}".strip()
        if inter_line is None and re.search(r"\b(intermediate|12th|hsc|senior secondary)\b", low):
            inter_line = f"Intermediate - {extract_institute(ln)}".strip()
        if ssc_line is None and re.search(r"\b(10th|ssc|secondary)\b", low):
            ssc_line = f"SSC - {extract_institute(ln)}".strip()

    preferred = [x for x in [btech_line, inter_line, ssc_line] if x and len(x.split('-')[-1].strip()) > 0]
    if preferred:
        # Deduplicate preferred
        seenp = set()
        finalp = []
        for x in preferred:
            k = x.lower()
            if k not in seenp:
                seenp.add(k)
                finalp.append(x)
        return finalp

    return normalized if normalized else ["Not found"]

# --- Enhanced Skills Extraction with Preprocessing ---
def preprocess_text(text):
    """Preprocess text for better skill matching"""
    # Normalize case and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills_enhanced(text):
    """Enhanced skills extraction with preprocessing and soft skills detection"""
    processed_text = preprocess_text(text)
    doc = nlp(processed_text)
    
    # Section-aware extraction from explicit Skills sections (support multiple)
    section_skills_map = {}
    try:
        header_regex = re.compile(r"(?im)^(skills?|technical skills?)\b[:\-]?(.*)$")
        for m in header_regex.finditer(text):
            start = m.end()
            next_header = re.search(r"(?im)^(experience|work|employment|projects|education|certifications?|licenses|summary|objective|contact)\b", text[start:])
            end = start + next_header.start() if next_header else len(text)
            skills_block = text[start:end]
            if m.group(2):
                skills_block = m.group(2) + "\n" + skills_block
            raw_items = re.split(r"[\n\r,;\u2022\u2023\u25E6\u2043\-\–\—\|/•·∙‣◦▪]+", skills_block)
            for item in raw_items:
                original = item.strip()
                cleaned_norm = re.sub(r"[^a-zA-Z0-9\+\.#\s]", "", original).strip().lower()
                if 1 < len(cleaned_norm) <= 40:
                    section_skills_map.setdefault(cleaned_norm, original)
    except Exception:
        pass

    # Contextual spans like "proficient in", "experience with", etc.
    context_spans_text = []
    try:
        ctx_regex = re.compile(r"(?i)(skills?\s*[:\-]|proficient in|experience with|technologies\s*[:\-]|tools\s*[:\-]|stack\s*[:\-]|familiar with)\s*(.{0,200})")
        for ctx in ctx_regex.finditer(text):
            span = ctx.group(2)
            if span:
                context_spans_text.append(span)
    except Exception:
        pass
    context_terms = set()
    for span in context_spans_text:
        for token in re.split(r"[\n\r,;\u2022\u2023\u25E6\u2043\-\–\—\|/•·∙‣◦▪]+", span):
            cleaned = re.sub(r"[^a-zA-Z0-9\+\.#\s]", "", token).strip().lower()
            if 1 < len(cleaned) <= 40:
                context_terms.add(cleaned)

    # Technical skills from known keywords but limit to Skills sections or contextual spans
    technical_skills = set()
    for field, skills in SKILL_KEYWORDS.items():
        for skill in skills:
            k = skill.lower()
            if k in section_skills_map or k in context_terms:
                technical_skills.add(k)

    # Soft skills detection
    soft_skills = [
        "leadership", "communication", "teamwork", "problem solving", "critical thinking",
        "creativity", "adaptability", "time management", "organization", "attention to detail",
        "analytical", "strategic thinking", "project management", "customer service",
        "negotiation", "presentation", "research", "collaboration", "initiative",
        "flexibility", "multitasking", "decision making", "mentoring", "coaching"
    ]
    
    detected_soft_skills = set()
    for skill in soft_skills:
        if skill.lower() in processed_text:
            detected_soft_skills.add(skill.lower())
    
    # Named entity recognition for additional skills (only from skills blocks)
    ner_skills = set()
    try:
        skills_blocks_concat = "\n".join(section_skills_map.values()).lower()
        if skills_blocks_concat:
            doc_blocks = nlp(preprocess_text(skills_blocks_concat))
            for ent in doc_blocks.ents:
                if ent.label_ in ["ORG", "PRODUCT"] and len(ent.text) < 30:
                    ner_skills.add(ent.text.lower())
    except Exception:
        pass
    
    # Merge and normalize unique skills
    all_norm = set(section_skills_map.keys())
    all_norm |= technical_skills
    all_norm |= detected_soft_skills
    all_norm |= ner_skills
    
    # Filters to remove institutions/companies and noise from skills
    org_edu_blocklist = [
        "university", "college", "school", "institute", "academy", "junior college",
        "polytechnic", "campus"
    ]
    org_company_blocklist = [
        " private limited", " pvt", "pvt.", "limited", " ltd", "ltd.", " inc", "inc.", " llc", "llc.",
        "solutions", "technologies", "labs", "systems", "corporation", "corp", "company"
    ]
    def looks_like_org_or_edu(s: str) -> bool:
        low = s.lower()
        if any(k in low for k in org_edu_blocklist):
            return True
        if any(k in low for k in org_company_blocklist):
            return True
        if re.search(r"\b(19|20)\d{2}\b", low):
            return True
        if "@" in low or "http" in low:
            return True
        # Too many digits likely not a skill
        digits = sum(ch.isdigit() for ch in low)
        if digits / max(1, len(low)) > 0.3:
            return True
        return False

    # Prefer original casing from section items when available
    result = []
    for s in all_norm:
        if s in section_skills_map:
            val = re.sub(r"\s+", " ", section_skills_map[s]).strip(" .")
            if not looks_like_org_or_edu(val):
                result.append(val)
        else:
            if not looks_like_org_or_edu(s):
                result.append(s)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for it in result:
        key = it.lower()
        if key not in seen:
            seen.add(key)
            unique.append(it)

    # Final cleanup: remove noise, expand acronyms, allow only known short skills
    noise_terms = {
        "tstracking", "tracking id", "tracking", "na", "n/a"
    }
    alias_map = {
        "ar": "Augmented Reality",
        "vr": "Virtual Reality",
        "ai": "Artificial Intelligence",
        "ml": "Machine Learning",
        "nlp": "Natural Language Processing",
        "ux": "User Experience",
        "ui": "User Interface",
        "sem": "Search Engine Marketing",
        "seo": "Search Engine Optimization",
        "ips": "Intrusion Prevention System",
        "ids": "Intrusion Detection System",
    }
    allowed_short = {
        "ai", "ml", "dl", "nlp", "cv", "ux", "ui", "qa", "db", "ar", "vr", "sem", "seo", "ips", "ids"
    }
    cleaned = []
    seen2 = set()
    for item in unique:
        base = item.strip()
        low = base.lower()
        if low in noise_terms:
            continue
        # Drop very short tokens unless in allowlist
        if len(low) <= 2 and low not in allowed_short:
            continue
        if 2 < len(low) <= 3 and low not in allowed_short and not low.isupper():
            # three-letter lowercase randoms are likely noise unless allowed
            continue
        # Expand known acronyms to canonical names
        if low in alias_map:
            base = alias_map[low]
        # Normalize inner spaces
        base = re.sub(r"\s+", " ", base).strip()
        key2 = base.lower()
        if key2 not in seen2:
            seen2.add(key2)
            cleaned.append(base)

    return cleaned if cleaned else ["Not found"]

# --- Enhanced Certifications Extraction ---
def extract_certifications_enhanced(text):
    """Enhanced certifications extraction"""
    # Known certification providers and keywords
    cert_providers = [
        "coursera", "udemy", "edx", "udacity", "aws", "amazon", "google", "microsoft", "ibm",
        "oracle", "linkedin learning", "skillshare", "pluralsight", "datacamp",
        "deeplearning.ai", "fast.ai", "kaggle", "hackerrank", "leetcode"
    ]
    
    # Certification keywords and patterns
    cert_keywords = [
        "certified", "certification", "certificate", "accredited", "professional",
        "specialist", "expert", "master", "foundation", "associate"
    ]
    patterns = [
        r"\baws certified [a-zA-Z ][a-zA-Z \-+:/()0-9]+",
        r"\bgoogle (?:cloud )?professional [a-zA-Z \-+:/()0-9]+",
        r"\b(?:microsoft|azure) certified [a-zA-Z \-+:/()0-9]+",
        r"\bcertificate in [a-zA-Z \-+:/()0-9]+",
        r"\bcertification in [a-zA-Z \-+:/()0-9]+"
    ]

    found = set()
    # Common cert acronyms and codes
    cert_acronyms = [
        "pmp", "cissp", "ceh", "ccna", "csm", "psm", "pspo", "itil", "ocp", "oca",
        "security+", "network+", "a+", "aws saa", "aws sap", "gcp pca", "az-900", "dp-100",
        "pl-300", "sc-200", "ai-102", "ms-900"
    ]
    code_pattern = re.compile(r"\b[A-Z]{2,}-\d{2,3}\b")

    # 1) Section-aware parsing
    lower = text.lower()
    # Parse multiple certification-like sections
    header_multi = re.compile(r"(?im)^(certificates?|certifications?|licenses?(?:\s*&\s*certifications?)?|licenses|courses|training|professional development|credentials|badges|awards\s*&\s*certifications?)\b[:\-]?(.*)$")
    for header in header_multi.finditer(text):
        start = header.end()
        nxt = re.search(r"(?im)^(experience|work|employment|projects|education|skills?|summary|objective|contact|achievements?)\b", text[start:])
        end = start + nxt.start() if nxt else len(text)
        block = text[start:end]
        if header.group(2):
            block = header.group(2) + "\n" + block
        # Split by lines, bullets, commas, semicolons, pipes (avoid splitting on hyphens/dashes to keep titles intact)
        items = re.split(r"[\n\r,;\u2022\u2023\u25E6\u2043\|/•·∙‣◦▪]+", block)
        for item in items:
            clean = item.strip()
            low = clean.lower()
            if len(clean) < 3:
                continue
            # Within certification-like sections, accept reasonable certificate/course lines
            if any(ex in low for ex in ["university", "college", "school", "degree"]):
                continue
            # Keep if clear signals present
            titlecase_words = sum(1 for w in re.findall(r"\b[A-Za-z][a-z]+\b", clean) if w[:1].isupper())
            signals = (
                any(p in low for p in cert_providers) or
                any(k in low for k in cert_keywords) or
                any(a in low for a in cert_acronyms) or
                code_pattern.search(clean) or
                any(w in low for w in ["course", "training", "badge", "credential", "nanodegree", "bootcamp", "license", "academy", "forage"])
            )
            if signals or titlecase_words >= 2:
                # Collapse duplicated consecutive words inside item
                cleaned_item = re.sub(r"\b(\w+)(?:\s+\1)+\b", r"\1", clean, flags=re.IGNORECASE)
                found.add(cleaned_item)

    # 2) Line-by-line heuristics across entire document
    for raw in text.split("\n"):
        line = raw.strip()
        low = line.lower()
        if any(provider in low for provider in cert_providers) and len(line) > 3:
            found.add(line)
        elif (any(keyword in low for keyword in cert_keywords) or any(a in low for a in cert_acronyms) or code_pattern.search(line)) and len(line) > 3 and not any(ex in low for ex in ["university", "college", "school", "degree"]):
            found.add(line)
        else:
            for pat in patterns:
                m = re.search(pat, low)
                if m:
                    found.add(line)
                    break

    normalized = {re.sub(r"\s+", " ", c).strip(" .") for c in found}
    return list(normalized) if normalized else ["Not found"]

# --- Enhanced Projects Extraction ---
def extract_projects(text):
    """Extract project titles/lines from resume text (section-aware with fallbacks)."""
    projects = []

    def title_from_line(line: str) -> str:
        s = line.strip().strip("-–—|:;•·")
        # Take portion before comma if it looks like tags list
        if "," in s and len(s.split(",")[0].split()) <= 6:
            s = s.split(",")[0].strip()
        # Prefer text before separators
        for sep in [" - ", " – ", " — ", ":", " | ", " |", "| "]:
            if sep in s:
                left = s.split(sep)[0].strip()
                if len(left) >= 3:
                    s = left
                    break
        # Remove trailing parenthetical details
        s = re.sub(r"\s*\([^)]*\)$", "", s).strip()
        # If long sentence, try to capture leading Title Case chunk
        m = re.match(r"^([A-Z][A-Za-z0-9]+(?:[\s\-][A-Z][A-Za-z0-9]+){0,6})\b", s)
        if m and len(m.group(1)) >= 3:
            return m.group(1)
        # Otherwise limit to first 6 words
        return " ".join(s.split()[:6]).strip()

    def is_valid_title(title: str) -> bool:
        low = title.lower().strip()
        if len(low) < 3:
            return False
        stop_exact = {
            "technologies", "internships", "internship", "currently", "experience", "responsibilities",
            "built", "created", "developed"
        }
        if low in stop_exact:
            return False
        stop_sub = [" internship", "internship ", " responsibilities", " duties"]
        if any(ss in low for ss in stop_sub):
            return False
        # Allow CamelCase single tokens like ScholarHunt
        if " " not in title and re.search(r"[A-Z][a-z]+[A-Z][a-z]+", title):
            return True
        # Prefer 2-6 words for multi-word titles
        wc = len(title.split())
        if 2 <= wc <= 6:
            return True
        return False
    # 1) Section-aware: Projects/Personal Projects/Academic Projects
    try:
        header_multi = re.compile(r"(?im)^(projects?|personal projects?|academic projects?)\b[:\-]?(.*)$")
        for header in header_multi.finditer(text):
            start = header.end()
            nxt = re.search(r"(?im)^(experience|work|employment|education|skills?|certifications?|licenses|summary|objective|contact|achievements?)\b", text[start:])
            end = start + (nxt.start() if nxt else 0) if nxt else len(text)
            block = text[start:end]
            # If inline items on header line
            if header.group(2):
                block = header.group(2) + "\n" + block
            # Split primarily by newlines and bullets (avoid splitting on hyphens to keep names intact)
            items = re.split(r"[\n\r\u2022\u2023\u25E6\u2043•·∙‣◦▪]+", block)
            for raw in items:
                line = raw.strip().strip("-–—|:;")
                if len(line) < 5:
                    continue
                # Typical noise filters
                low = line.lower()
                if any(h in low for h in ["experience", "education", "skills", "certification", "contact"]):
                    continue
                t = title_from_line(line)
                if is_valid_title(t):
                    projects.append(t)
    except Exception:
        pass

    # 2) Fallback: scan for lines containing project-like cues
    if not projects:
        cues = ["project:", "capstone", "built", "developed", "implemented", "designed", "engineered"]
        lines = text.splitlines()
        for i, ln in enumerate(lines):
            low = ln.strip().lower()
            if any(c in low for c in cues):
                cleaned = ln.strip().strip("-–—|:;")
                if len(cleaned) > 5:
                    t = title_from_line(cleaned)
                    if is_valid_title(t):
                        projects.append(t)
                # Grab immediate next bullet/line as context
                if i + 1 < len(lines):
                    nxt = lines[i+1].strip().strip("-–—|:;")
                    if len(nxt) > 5:
                        t2 = title_from_line(nxt)
                        if is_valid_title(t2):
                            projects.append(t2)

    # Normalize and deduplicate
    normalized = []
    seen = set()
    for p in projects:
        clean = re.sub(r"\s+", " ", p).strip(" .")
        if len(clean) > 4:
            k = clean.lower()
            if k not in seen:
                seen.add(k)
                normalized.append(clean)
    return normalized if normalized else ["Not found"]

# --- Enhanced Info Extraction Function ---
def extract_info(text):
    """Enhanced information extraction with all improvements"""
    # Extract personal info
    personal_info = extract_personal_info(text)
    
    # Extract education
    education = extract_education_info(text)
    
    # Extract skills
    skills = extract_skills_enhanced(text)
    
    # Extract certifications
    certifications = extract_certifications_enhanced(text)
    
    # Extract projects
    projects = extract_projects(text)
    
    return {
        "name": personal_info["name"],
        "email": personal_info["email"],
        "phone": personal_info["phone"],
        "education": education,
        "skills": skills,
        "certifications": certifications,
        "projects": projects,
        "linkedin": personal_info["linkedin"],
        "github": personal_info["github"],
        "portfolio": personal_info["portfolio"]
    }

# --- Multi-Resume Comparison Functions ---
def create_comparison_table(resume_data):
    """Create a comparison table for multiple resumes"""
    st.markdown("### 📊 Resume Comparison Table")
    
    # Prepare data for the table
    comparison_data = {
        'Metric': ['Name', 'Field', 'ATS Score', 'Skills Count', 'Education', 'Projects', 'LinkedIn', 'GitHub']
    }
    
    # Add data for each resume
    for i, resume in enumerate(resume_data):
        col_name = f"Resume {i+1}"
        comparison_data[col_name] = [
            resume['name'],
            resume['field'],
            f"{resume['ats_score']}/100",
            len([s for s in resume['skills'] if s != 'Not found']),
            f"{len([e for e in resume['education'] if e != 'Not found'])} degrees" if resume['education'] and resume['education'][0] != 'Not found' else 'None',
            len([p for p in resume['projects'] if p != 'Not found']),
            '✅' if resume['linkedin'] != 'Not found' else '❌',
            '✅' if resume['github'] != 'Not found' else '❌'
        ]
    
    # Create DataFrame and display
    try:
        import pandas as pd
        df = pd.DataFrame(comparison_data)
    except ImportError:
        st.error("Pandas is required for comparison table. Please install it: pip install pandas")
        return
    
    # Style the table with highlights
    def highlight_ats_score(val):
        if 'ATS Score' in str(val):
            try:
                score = int(val.split('/')[0])
                if score >= 80:
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
                elif score >= 60:
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                else:
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            except:
                return ''
        return ''
    
    def highlight_skills(val):
        if 'Skills Count' in str(val):
            try:
                count = int(val)
                if count >= 15:
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
                elif count >= 10:
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                else:
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            except:
                return ''
        return ''
    
    # Apply styling
    try:
        styled_df = df.style.applymap(highlight_ats_score).applymap(highlight_skills)
        st.dataframe(styled_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error styling table: {e}")
        # Fallback to basic table
        st.dataframe(df, use_container_width=True)
    
    # Add skill comparison
    create_skill_comparison(resume_data)

def create_skill_comparison(resume_data):
    """Create skill comparison with highlights"""
    st.markdown("### 🔧 Skills Comparison")
    
    # Collect all skills from all resumes
    all_skills = set()
    resume_skills = {}
    
    for i, resume in enumerate(resume_data):
        skills = [s for s in resume['skills'] if s != 'Not found']
        resume_skills[f"Resume {i+1}"] = set(skills)
        all_skills.update(skills)
    
    # Find common and unique skills
    if len(resume_skills) > 1:
        common_skills = set.intersection(*resume_skills.values())
        unique_skills = {}
        for resume_name, skills in resume_skills.items():
            unique_skills[resume_name] = skills - common_skills
    
    # Define important skills for prioritization
    important_skills = {
        'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'sql', 'mongodb', 'postgresql',
        'machine learning', 'ai', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn',
        'html', 'css', 'bootstrap', 'typescript', 'php', 'c++', 'c#', 'go', 'rust',
        'devops', 'ci/cd', 'jenkins', 'terraform', 'ansible', 'linux', 'bash'
    }
    
    # Display common skills (show only important ones, max 8)
    if common_skills:
        important_common = [skill for skill in sorted(common_skills) if skill.lower() in important_skills][:8]
        if important_common:
            st.markdown(f"**🟢 Important Common Skills:** *{', '.join(important_common)}*")
        else:
            # If no important common skills, show first 5 common skills
            common_list = sorted(common_skills)[:5]
            st.markdown(f"**🟢 Common Skills:** *{', '.join(common_list)}*")
    
    # Display unique skills for each resume (prioritize important ones, max 4 per resume)
    for resume_name, skills in unique_skills.items():
        if skills:
            # Prioritize important skills first
            important_unique = [skill for skill in sorted(skills) if skill.lower() in important_skills][:4]
            if important_unique:
                st.markdown(f"**🔵 {resume_name} Key Skills:** *{', '.join(important_unique)}*")
            else:
                # If no important unique skills, show first 3 unique skills
                skills_list = sorted(skills)[:3]
                st.markdown(f"**🔵 {resume_name} Unique:** *{', '.join(skills_list)}*")
    
    # Display missing important skills only
    if len(resume_skills) > 1:
        st.markdown("**🔴 Important Missing Skills:**")
        for resume_name, skills in resume_skills.items():
            other_skills = set()
            for other_name, other_skill_set in resume_skills.items():
                if other_name != resume_name:
                    other_skills.update(other_skill_set)
            
            missing_skills = other_skills - skills
            # Only show important missing skills
            important_missing = [skill for skill in sorted(missing_skills) if skill.lower() in important_skills][:4]
            if important_missing:
                st.markdown(f"**{resume_name}:** *{', '.join(important_missing)}*")


def create_summary_analysis(resume_data):
    """Create summary analysis of resume strengths"""
    st.markdown("### 📈 Summary Analysis")
    
    # Find the strongest resume
    best_resume_idx = max(range(len(resume_data)), key=lambda i: resume_data[i]['ats_score'])
    best_resume = resume_data[best_resume_idx]
    
    # Calculate statistics
    scores = [r['ats_score'] for r in resume_data]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # Create summary cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average ATS Score", f"{avg_score:.1f}/100")
    
    with col2:
        st.metric("Highest Score", f"{max_score}/100", f"Resume {best_resume_idx + 1}")
    
    with col3:
        st.metric("Score Range", f"{max_score - min_score}", f"{min_score} - {max_score}")
    
    # Detailed analysis
    st.markdown("#### 🏆 **Strongest Resume: Resume " + str(best_resume_idx + 1))
    st.markdown(f"**Name:** {best_resume['name']}")
    st.markdown(f"**Field:** {best_resume['field']}")
    st.markdown(f"**ATS Score:** {best_resume['ats_score']}/100 ⭐")
    
    # Reasons why this resume is strongest
    reasons = []
    if best_resume['ats_score'] >= 80:
        reasons.append("High ATS compatibility score")
    
    skill_count = len([s for s in best_resume['skills'] if s != 'Not found'])
    if skill_count >= 15:
        reasons.append("Comprehensive skill set")
    
    cert_count = len([c for c in best_resume['certifications'] if c != 'Not found'])
    if cert_count >= 3:
        reasons.append("Strong certification portfolio")
    
    project_count = len([p for p in best_resume['projects'] if p != 'Not found'])
    if project_count >= 3:
        reasons.append("Diverse project experience")
    
    if best_resume['linkedin'] != 'Not found' and best_resume['github'] != 'Not found':
        reasons.append("Complete professional presence")
    
    if reasons:
        st.markdown("**Why this resume is strongest:**")
        for reason in reasons:
            st.markdown(f"• {reason}")
    
    # Recommendations for improvement
    st.markdown("#### 💡 **Recommendations for Other Resumes:**")
    
    for i, resume in enumerate(resume_data):
        if i != best_resume_idx:
            st.markdown(f"**Resume {i+1} improvements:**")
            improvements = []
            
            if resume['ats_score'] < best_resume['ats_score'] - 10:
                improvements.append("Improve ATS compatibility and formatting")
            
            skill_count = len([s for s in resume['skills'] if s != 'Not found'])
            if skill_count < 10:
                improvements.append("Add more relevant skills")
            
            if resume['linkedin'] == 'Not found':
                improvements.append("Add LinkedIn profile")
            
            if resume['github'] == 'Not found':
                improvements.append("Add GitHub profile")
            
            cert_count = len([c for c in resume['certifications'] if c != 'Not found'])
            if cert_count < 2:
                improvements.append("Consider adding relevant certifications")
            
            if improvements:
                for improvement in improvements:
                    st.markdown(f"• {improvement}")
            else:
                st.markdown("• Resume is already well-optimized!")

# --- Resume Format Validation ---
def validate_resume_format(text):
    """Validate resume format and warn about potential issues"""
    warnings = []
    
    # Check for very short content (might be scanned)
    if len(text.strip()) < 500:
        warnings.append("⚠ Very short content detected. This might be a scanned PDF or image-based resume.")
    
    # Check for weird symbols (OCR artifacts)
    weird_symbols = re.findall(r'[^\w\s\.\,\-\+\@\#\$\%\(\)\[\]\{\}\:\;\?\!]', text)
    if len(weird_symbols) > len(text) * 0.1:  # More than 10% weird symbols
        warnings.append("⚠ Many unusual symbols detected. This might be a scanned PDF with poor OCR.")
    
    # Check for multi-column indicators
    multi_column_indicators = ["|", "  ", "\t\t"]
    if any(indicator in text for indicator in multi_column_indicators):
        warnings.append("⚠ Multi-column layout detected. Consider using a single-column format for better ATS compatibility.")
    
    # Check for image-heavy indicators (very few words)
    words = text.split()
    if len(words) < 100:
        warnings.append("⚠ Very few words detected. This might be an image-heavy resume.")
    
    return warnings

# --- Pre-upload Guidelines ---
PRE_UPLOAD_GUIDELINES = """
📋 *Before Uploading Your Resume:*

✅ *Format Requirements:*
• Use single-column layout (avoid multi-column formats)
• Use clear, readable fonts (Arial, Calibri, Times New Roman)
• Keep file size under 5MB
• Use PDF or DOCX format

✅ *Content Guidelines:*
• Include clear section headings (EXPERIENCE, EDUCATION, SKILLS, etc.)
• Use bullet points for descriptions
• Include contact information (email, phone, LinkedIn)
• Add quantifiable achievements (e.g., "Increased sales by 25%")
• List relevant skills and certifications

❌ *Avoid:*
• Image-heavy resumes (logos, graphics)
• Scanned documents
• Multi-column layouts
• Very small fonts
• Overly creative designs

💡 *Tips for Better Results:*
• Use consistent formatting throughout
• Include keywords relevant to your target role
• Keep descriptions concise and impactful
• Proofread for spelling and grammar errors
"""

# --- Project Suggestions by Field ---
PROJECT_IDEAS = {
    "Data Science": [
        "Movie Recommendation System (ML)",
        "E-commerce Sales Dashboard (Tableau/Excel)",
        "Customer Churn Prediction",
        "Stock Price Predictor"
    ],
    "Web Development": [
        "Portfolio Website (HTML/CSS/JS)",
        "Blog Platform (Django/Flask)",
        "E-commerce Store (React/Node)"
    ],
    "Android Development": [
        "Expense Tracker App (Kotlin)",
        "Weather App (Java)",
        "Chat App (Firebase)"
    ],
    "UI/UX": [
        "Mobile App Redesign (Figma)",
        "Landing Page UI (Adobe XD)",
        "User Flow Mapping"
    ],
    "Artificial Intelligence": ["Fake News Detection using BERT", "Image Captioning with CNN+RNN", "Speech Recognition System (Deep Learning)", "Chatbot with Transformers"],
    "Cybersecurity": ["Network Vulnerability Scanner", "Phishing Detection System", "Firewall Rule Automation", "SIEM Log Analyzer"],
    "Cloud Computing": ["Deploy a CI/CD pipeline with GitHub Actions and AWS", "Serverless Web App (AWS Lambda)", "Multi-cloud Monitoring Dashboard"],
    "Software Development": ["Library Management System (Java)", "Task Manager App (Python)", "REST API with Flask/Django"],
    "Business Analyst": ["Sales Data Dashboard (PowerBI)", "Process Optimization Case Study", "Customer Segmentation Analysis"],
    "Product Management": ["Go-to-Market Strategy Plan", "User Feedback Analysis Tool", "Product Roadmap Dashboard"],
    "Mobile App Development": ["Fitness Tracker App (Flutter)", "Recipe App (iOS/Swift)", "Event Planner App (React Native)"],
    "Game Development": ["2D Platformer Game (Unity)", "Multiplayer Card Game (Unreal)", "VR Puzzle Game"],
    "Finance": ["Stock Portfolio Tracker (Excel/Python)", "Loan Default Prediction (ML)", "Financial Statement Analyzer"],
    "HR": ["Employee Onboarding Portal", "HR Analytics Dashboard", "Leave Management System"],
    "Digital Marketing": ["SEO Audit & Digital Campaign (Google Analytics)", "Social Media Sentiment Analysis", "Email Campaign Automation"]
}

CERTIFICATIONS = {
    "Data Science": ["Google Data Analytics", "IBM Data Science", "Microsoft Data Analyst Associate","CISCO","EDUSKILLS"],
    "Web Development": ["Meta Front-End Certificate", "FreeCodeCamp Responsive Web Design"],
    "Artificial Intelligence": ["DeepLearning.AI Specialization", "Google AI Professional Certificate"],
    "Cybersecurity": ["CompTIA Security+", "Certified Ethical Hacker (CEH)", "Cisco CCNA Security"],
    "Cloud Computing": ["AWS Cloud Practitioner", "Azure Fundamentals", "Google Associate Cloud Engineer"],
    "Software Development": ["Oracle Certified Java Programmer", "Microsoft Certified: Azure Developer Associate"],
    "Business Analyst": ["IIBA ECBA", "CBAP Certification"],
    "Product Management": ["Pragmatic Institute Product Management", "Certified Scrum Product Owner (CSPO)"],
    "Mobile App Development": ["Google Associate Android Developer", "Apple Certified iOS Developer"],
    "Game Development": ["Unity Certified Developer", "Unreal Engine Certification"],
    "Finance": ["CFA Level 1", "CPA", "Financial Risk Manager (FRM)"],
    "HR": ["SHRM-CP", "HRCI PHR"],
    "Digital Marketing": ["Google Analytics Individual Qualification", "HubSpot Content Marketing"],
    "UI/UX": ["NN/g UX Certification", "Adobe Certified Expert"]
}

TOOLS_LIST = ["VS Code", "Jupyter", "GitHub", "Excel", "Tableau"]

# Expanded known skills and certifications
KNOWN_SKILLS = set([
    "python", "machine learning", "pandas", "numpy", "tensorflow", "data analysis", "html", "css", "javascript", "react", "node", "flask", "django",
    "android", "kotlin", "java", "xml", "figma", "adobe xd", "photoshop", "sketch", "sql", "powerbi", "tableau", "c++", "c#", "aws", "azure", "gcp", "docker", "kubernetes"
])
CERT_PROVIDERS = ["coursera", "udemy", "aws", "google", "microsoft", "edx", "udacity", "ibm", "oracle", "linkedin learning"]


# --- Detect Field ---
def detect_field(text_or_skills):
    # Build a searchable lowercase corpus from either raw text or extracted skills
    if isinstance(text_or_skills, str):
        corpus = text_or_skills.lower()
    else:
        corpus = " ".join([s for s in text_or_skills if isinstance(s, str)]).lower()
    max_matches = 0
    best_field = "General"
    for field, keywords in SKILL_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if kw.lower() in corpus)
        if match_count > max_matches:
            max_matches = match_count
            best_field = field
    return best_field


# --- Ideal Resume Template ---
IDEAL_SECTIONS = ["objective", "projects", "skills", "education", "experience", "certifications", "contact", "declaration"]
IDEAL_SKILLS = set([kw for kws in SKILL_KEYWORDS.values() for kw in kws])
IDEAL_CERTS = set([prov.title() for prov in CERT_PROVIDERS])

# --- Scoring without Job Description ---
def template_score(text, info):
    # Section completeness
    section_score = int(40 * sum(1 for s in IDEAL_SECTIONS if s in text.lower()) / len(IDEAL_SECTIONS))
    # Skill diversity
    skill_score = int(30 * len([s for s in info['skills'] if s in IDEAL_SKILLS]) / len(IDEAL_SKILLS))
    # Certification diversity
    cert_score = int(15 * len([c for c in info['certifications'] if any(p.lower() in c.lower() for p in CERT_PROVIDERS)]) / len(CERT_PROVIDERS))
    # Education presence
    edu_score = 15 if info['education'] and info['education'][0] != 'Not found' else 0
    return section_score + skill_score + cert_score + edu_score

# --- Resume Clarity Helper ---
def clarity_score(text):
    # Metrics: presence of numbers/percentages, bullet points, concise sentences
    metrics = 0
    if any(x in text for x in ["%", "percent", "improved", "reduced", "increased", "decreased"]):
        metrics += 1
    if "•" in text or "- " in text:
        metrics += 1
    if len([s for s in text.split(". ") if len(s) < 120]) > 3:
        metrics += 1
    return int((metrics / 3) * 15)  # up to 15 points for clarity

# --- Professional Resume Scoring System (Enhancv-inspired) ---
def dynamic_resume_score(text, info, field="General"):
    """
    Comprehensive resume scoring based on industry standards and ATS optimization.
    Scoring criteria inspired by professional resume analyzers like Enhancv.
    """
    score = 0
    breakdown = {}
    
    # === 1. CONTENT COMPLETENESS (20 points) ===
    content_score = 0
    
    # Essential sections (12 points)
    essential_sections = ["experience", "education", "skills"]
    present_essential = sum(1 for section in essential_sections if section in text.lower())
    content_score += (present_essential / len(essential_sections)) * 12
    
    # Optional sections (8 points)
    optional_sections = ["objective", "summary", "projects", "certifications", "achievements", "volunteer"]
    present_optional = sum(1 for section in optional_sections if section in text.lower())
    content_score += min((present_optional / len(optional_sections)) * 8, 8)
    
    score += content_score
    breakdown["Content Completeness"] = round(content_score, 1)
    
    # === 2. SKILLS ASSESSMENT (25 points) ===
    skills_score = 0
    
    # Skills quantity and relevance (15 points)
    valid_skills = [s for s in info['skills'] if s != 'Not found' and len(s.strip()) > 0]
    skills_count = len(valid_skills)
    
    if skills_count >= 8:
        skills_score += 10
    elif skills_count >= 5:
        skills_score += 7
    elif skills_count >= 3:
        skills_score += 5
    elif skills_count >= 1:
        skills_score += 3
    
    # Field-specific skills (10 points)
    field_skills = SKILL_KEYWORDS.get(field, [])
    if field_skills:
        relevant_skills = [s for s in valid_skills if s.lower() in [sk.lower() for sk in field_skills]]
        relevance_ratio = len(relevant_skills) / max(1, len(valid_skills))
        skills_score += relevance_ratio * 10
    
    score += skills_score
    breakdown["Skills Assessment"] = round(skills_score, 1)
    
    # === 3. EXPERIENCE & IMPACT (20 points) ===
    experience_score = 0
    
    # Action verbs and metrics (15 points)
    action_verbs = ["achieved", "developed", "implemented", "managed", "led", "created", "designed", 
                   "improved", "increased", "reduced", "optimized", "launched", "coordinated", "analyzed"]
    metrics_indicators = ["%", "percent", "improved", "reduced", "increased", "decreased", "by", "from", "to"]
    
    action_verb_count = sum(1 for verb in action_verbs if verb in text.lower())
    metrics_count = sum(1 for metric in metrics_indicators if metric in text.lower())
    
    if action_verb_count >= 5 and metrics_count >= 3:
        experience_score += 15
    elif action_verb_count >= 3 and metrics_count >= 1:
        experience_score += 10
    elif action_verb_count >= 2:
        experience_score += 7
    elif action_verb_count >= 1:
        experience_score += 3
    
    # Experience length and depth (5 points)
    if len(text) > 2000:  # Substantial content
        experience_score += 5
    elif len(text) > 1000:
        experience_score += 3
    elif len(text) > 500:
        experience_score += 1
    
    score += experience_score
    breakdown["Experience & Impact"] = round(experience_score, 1)
    
    # === 4. PROFESSIONAL PRESENTATION (15 points) ===
    presentation_score = 0
    
    # Contact information (5 points)
    contact_info = 0
    if info['email'] != 'Not found':
        contact_info += 2
    if info['phone'] != 'Not found':
        contact_info += 2
    if info['linkedin'] != 'Not found':
        contact_info += 1
    presentation_score += min(contact_info, 5)
    
    # Professional formatting (5 points)
    formatting_indicators = 0
    if "•" in text or "- " in text:  # Bullet points
        formatting_indicators += 2
    if any(char in text for char in ["|", "•", "-"]):  # Consistent formatting
        formatting_indicators += 2
    if len([s for s in text.split(". ") if len(s) < 150]) > 5:  # Concise sentences
        formatting_indicators += 1
    presentation_score += min(formatting_indicators, 5)
    
    # Certifications and credentials (5 points)
    valid_certs = [c for c in info['certifications'] if c != 'Not found' and len(c.strip()) > 0]
    if len(valid_certs) >= 3:
        presentation_score += 5
    elif len(valid_certs) >= 1:
        presentation_score += 3
    
    score += presentation_score
    breakdown["Professional Presentation"] = round(presentation_score, 1)
    
    # === 5. ATS OPTIMIZATION (20 points) ===
    ats_score = 0
    ats_breakdown = {}
    
    # === ATS Keyword Optimization (8 points) ===
    field_keywords = SKILL_KEYWORDS.get(field, [])
    if field_keywords:
        keyword_matches = sum(1 for keyword in field_keywords if keyword.lower() in text.lower())
        keyword_ratio = keyword_matches / max(1, len(field_keywords))
        keyword_score = keyword_ratio * 8
        ats_score += keyword_score
        ats_breakdown["Keyword Match"] = round(keyword_score, 1)
    else:
        ats_breakdown["Keyword Match"] = 0
    
    # === ATS Section Headers (4 points) ===
    standard_headers = ["experience", "education", "skills", "certifications", "projects", "summary", "objective"]
    header_matches = sum(1 for header in standard_headers if header in text.lower())
    header_score = (header_matches / len(standard_headers)) * 4
    ats_score += header_score
    ats_breakdown["Section Headers"] = round(header_score, 1)
    
    # === ATS Format Compatibility (3 points) ===
    format_score = 0
    # Check for common ATS-friendly formatting
    if "•" in text or "- " in text:  # Bullet points
        format_score += 1
    if not any(char in text for char in ["[", "]", "{", "}", "|", "~", "^"]):  # No special characters
        format_score += 1
    if len(text) > 500 and len(text) < 3000:  # Optimal length
        format_score += 1
    ats_score += format_score
    ats_breakdown["Format Compatibility"] = format_score
    
    # === ATS Contact Information (2 points) ===
    contact_score = 0
    if info['email'] != 'Not found':
        contact_score += 1
    if info['phone'] != 'Not found':
        contact_score += 1
    ats_score += contact_score
    ats_breakdown["Contact Info"] = contact_score
    
    # === ATS Experience Details (3 points) ===
    experience_score = 0
    # Check for job titles, company names, dates
    if any(word in text.lower() for word in ["experience", "work", "employment", "job"]):
        experience_score += 1
    if any(word in text.lower() for word in ["2024", "2023", "2022", "2021", "2020"]):
        experience_score += 1
    if any(word in text.lower() for word in ["company", "corporation", "inc", "ltd", "llc"]):
        experience_score += 1
    ats_score += experience_score
    ats_breakdown["Experience Details"] = experience_score
    
    score += ats_score
    breakdown["ATS Optimization"] = round(ats_score, 1)
    breakdown["ATS Details"] = ats_breakdown
    
    # === BONUS POINTS (up to 10 points) ===
    bonus_points = 0
    
    # Projects section
    if 'projects' in text.lower():
        bonus_points += 3
    
    # GitHub/Portfolio links
    if any(url in text.lower() for url in ['github.com', 'portfolio', 'behance.net']):
        bonus_points += 2
    
    # Education details
    if info['education'] and info['education'][0] != 'Not found':
        bonus_points += 2
    
    # Professional summary/objective
    if any(section in text.lower() for section in ['summary', 'objective', 'profile']):
        bonus_points += 2
    
    # Recent experience (if mentioned)
    if any(year in text for year in ['2024', '2023', '2022']):
        bonus_points += 1
    
    score += bonus_points
    breakdown["Bonus Points"] = round(bonus_points, 1)
    
    # === FINAL SCORE CALCULATION ===
    final_score = min(100, round(score))
    
    # Adjust score based on field-specific requirements
    if field in ["Cybersecurity", "Cloud Computing"] and len(valid_certs) < 1:
        final_score = max(0, final_score - 10)  # Certifications are crucial for these fields
    
    if field in ["Data Science", "Artificial Intelligence"] and skills_count < 5:
        final_score = max(0, final_score - 8)  # Technical skills are essential
    
    if field in ["Product Management", "Business Analyst"] and action_verb_count < 3:
        final_score = max(0, final_score - 5)  # Leadership/management skills important
    
    breakdown["Total Score"] = final_score
    
    return final_score, breakdown

# --- Enhanced Dynamic Strengths/Weaknesses Analysis ---
def get_strengths_weaknesses(text, info):
    """
    Comprehensive analysis of resume strengths and weaknesses based on industry standards.
    """
    strengths = []
    weaknesses = []
    
    # === STRENGTHS ANALYSIS ===
    
    # Contact Information
    if info['email'] != 'Not found' and info['phone'] != 'Not found':
        strengths.append("Complete contact information provided")
    elif info['email'] != 'Not found':
        strengths.append("Email address included")
    
    # Professional Presence
    if info['linkedin'] != 'Not found':
        strengths.append("LinkedIn profile linked for professional networking")
    
    # Content Structure
    if 'projects' in text.lower():
        strengths.append("Projects section demonstrates practical experience")
    if 'summary' in text.lower() or 'objective' in text.lower():
        strengths.append("Professional summary/objective provides clear direction")
    if 'certifications' in text.lower():
        strengths.append("Certifications section shows continuous learning")
    
    # Skills Assessment
    valid_skills = [s for s in info['skills'] if s != 'Not found' and len(s.strip()) > 0]
    if len(valid_skills) >= 8:
        strengths.append("Comprehensive skill set with 8+ technical skills")
    elif len(valid_skills) >= 5:
        strengths.append("Good range of technical skills (5+ skills listed)")
    
    # Impact and Metrics
    action_verbs = ["achieved", "developed", "implemented", "managed", "led", "created", "designed", 
                   "improved", "increased", "reduced", "optimized", "launched", "coordinated", "analyzed"]
    action_verb_count = sum(1 for verb in action_verbs if verb in text.lower())
    if action_verb_count >= 5:
        strengths.append("Strong use of action verbs demonstrates leadership")
    elif action_verb_count >= 3:
        strengths.append("Good use of action verbs shows initiative")
    
    # Quantifiable Results
    metrics_indicators = ["%", "percent", "improved", "reduced", "increased", "decreased", "by", "from", "to"]
    metrics_count = sum(1 for metric in metrics_indicators if metric in text.lower())
    if metrics_count >= 3:
        strengths.append("Quantifiable achievements with measurable impact")
    elif metrics_count >= 1:
        strengths.append("Some quantifiable results included")
    
    # Formatting and Presentation
    if "•" in text or "- " in text:
        strengths.append("Professional bullet-point formatting")
    if len([s for s in text.split(". ") if len(s) < 150]) > 5:
        strengths.append("Concise, readable writing style")
    
    # === WEAKNESSES ANALYSIS ===
    
    # Contact Information Issues
    if info['email'] == 'Not found':
        weaknesses.append("Missing email address - essential for contact")
    if info['phone'] == 'Not found':
        weaknesses.append("Missing phone number - limits communication options")
    if info['linkedin'] == 'Not found':
        weaknesses.append("No LinkedIn profile - missing professional networking opportunity")
    
    # Content Gaps
    if 'projects' not in text.lower():
        weaknesses.append("No projects section - missing practical experience demonstration")
    if 'summary' not in text.lower() and 'objective' not in text.lower():
        weaknesses.append("No professional summary/objective - unclear career direction")
    if 'certifications' not in text.lower():
        weaknesses.append("No certifications section - missing credential validation")
    
    # Skills Issues
    if len(valid_skills) < 3:
        weaknesses.append("Limited technical skills (less than 3 skills listed)")
    elif len(valid_skills) < 5:
        weaknesses.append("Moderate skill set - consider adding more relevant skills")
    
    # Impact and Results Issues
    if action_verb_count < 2:
        weaknesses.append("Limited use of action verbs - weakens impact statements")
    if metrics_count == 0:
        weaknesses.append("No quantifiable results - missing measurable achievements")
    
    # Formatting Issues
    if "•" not in text and "- " not in text:
        weaknesses.append("No bullet points - reduces readability and scannability")
    if len([s for s in text.split(". ") if len(s) > 200]) > 3:
        weaknesses.append("Some sentences too long - affects readability")
    
    # Content Quality
    if len(text) < 500:
        weaknesses.append("Resume too brief - may lack sufficient detail")
    elif len(text) > 3000:
        weaknesses.append("Resume too lengthy - may lose reader attention")
    
    # Professional Development
    if not info['certifications'] or info['certifications'][0] == 'Not found':
        weaknesses.append("No certifications - missing professional development evidence")
    
    # Recent Experience
    if not any(year in text for year in ['2024', '2023', '2022']):
        weaknesses.append("No recent experience mentioned - may appear outdated")
    
    # Remove duplicates and ensure quality
    strengths = list(set([s for s in strengths if s and len(s.strip()) > 0]))
    weaknesses = list(set([w for w in weaknesses if w and len(w.strip()) > 0]))
    
    # Limit to top 5 most important items
    return strengths[:5], weaknesses[:5]

# --- ATS Feature Extraction and Analysis ---
def extract_ats_features(text, info, field):
    """
    Comprehensive ATS feature extraction and analysis.
    Returns detailed breakdown of ATS compatibility factors.
    """
    features = {}
    
    # === KEYWORD ANALYSIS ===
    field_keywords = SKILL_KEYWORDS.get(field, [])
    if field_keywords:
        keyword_matches = [kw for kw in field_keywords if kw.lower() in text.lower()]
        features["Keywords Found"] = keyword_matches[:10]  # Top 10 matches
        features["Keyword Match Rate"] = f"{len(keyword_matches)}/{len(field_keywords)} ({len(keyword_matches)/len(field_keywords)*100:.1f}%)"
    else:
        features["Keywords Found"] = []
        features["Keyword Match Rate"] = "N/A"
    
    # === SECTION HEADERS ===
    standard_headers = ["experience", "education", "skills", "certifications", "projects", "summary", "objective", "work history", "employment"]
    found_headers = [h for h in standard_headers if h in text.lower()]
    features["Standard Headers Found"] = found_headers
    features["Header Compliance"] = f"{len(found_headers)}/{len(standard_headers)} ({len(found_headers)/len(standard_headers)*100:.1f}%)"
    
    # === CONTACT INFORMATION ===
    contact_info = {}
    contact_info["Email"] = "Present" if info['email'] != 'Not found' else "Missing"
    contact_info["Phone"] = "Present" if info['phone'] != 'Not found' else "Missing"
    contact_info["LinkedIn"] = "Present" if info['linkedin'] != 'Not found' else "Missing"
    features["Contact Information"] = contact_info
    
    # === FORMATTING ANALYSIS ===
    formatting = {}
    formatting["Bullet Points"] = "Present" if "•" in text or "- " in text else "Missing"
    formatting["Special Characters"] = "Clean" if not any(char in text for char in ["[", "]", "{", "}", "|", "~", "^"]) else "Contains Special Chars"
    formatting["Content Length"] = f"{len(text)} characters ({'Optimal' if 500 <= len(text) <= 3000 else 'Too Short' if len(text) < 500 else 'Too Long'})"
    features["Formatting"] = formatting
    
    # === EXPERIENCE DETAILS ===
    experience = {}
    experience["Experience Section"] = "Present" if any(word in text.lower() for word in ["experience", "work", "employment"]) else "Missing"
    experience["Recent Dates"] = "Present" if any(year in text for year in ["2024", "2023", "2022"]) else "Missing"
    experience["Company Names"] = "Present" if any(word in text.lower() for word in ["company", "corporation", "inc", "ltd", "llc"]) else "Missing"
    features["Experience Details"] = experience
    
    # === SKILLS ANALYSIS ===
    skills = {}
    valid_skills = [s for s in info['skills'] if s != 'Not found' and len(s.strip()) > 0]
    skills["Skills Count"] = len(valid_skills)
    skills["Skills Quality"] = "Strong" if len(valid_skills) >= 5 else "Moderate" if len(valid_skills) >= 3 else "Weak"
    features["Skills Analysis"] = skills
    
    # === ATS COMPATIBILITY SCORE ===
    compatibility_score = 0
    max_score = 20
    
    # Keywords (8 points)
    if field_keywords:
        keyword_ratio = len([kw for kw in field_keywords if kw.lower() in text.lower()]) / len(field_keywords)
        compatibility_score += keyword_ratio * 8
    
    # Headers (4 points)
    header_ratio = len(found_headers) / len(standard_headers)
    compatibility_score += header_ratio * 4
    
    # Formatting (3 points)
    if "•" in text or "- " in text:
        compatibility_score += 1
    if not any(char in text for char in ["[", "]", "{", "}", "|", "~", "^"]):
        compatibility_score += 1
    if 500 <= len(text) <= 3000:
        compatibility_score += 1
    
    # Contact (2 points)
    if info['email'] != 'Not found':
        compatibility_score += 1
    if info['phone'] != 'Not found':
        compatibility_score += 1
    
    # Experience (3 points)
    if any(word in text.lower() for word in ["experience", "work", "employment"]):
        compatibility_score += 1
    if any(year in text for year in ["2024", "2023", "2022"]):
        compatibility_score += 1
    if any(word in text.lower() for word in ["company", "corporation", "inc", "ltd", "llc"]):
        compatibility_score += 1
    
    features["ATS Compatibility Score"] = f"{compatibility_score:.1f}/{max_score} ({compatibility_score/max_score*100:.1f}%)"
    
    return features

# --- Enhanced Personalized Tips ---
def get_personalized_tips(text, info):
    """
    Generate personalized, actionable tips based on resume analysis.
    """
    tips = []
    
    # Contact Information Tips
    if info['linkedin'] == 'Not found':
        tips.append("🔗 *Add LinkedIn Profile*: Include your LinkedIn URL to enhance professional credibility and networking opportunities.")
    
    if info['email'] == 'Not found':
        tips.append("📧 *Add Email Address*: Include a professional email address for direct communication.")
    
    if info['phone'] == 'Not found':
        tips.append("📱 *Add Phone Number*: Include your phone number for immediate contact options.")
    
    # Content Structure Tips
    if 'projects' not in text.lower():
        tips.append("💼 *Add Projects Section*: Include 2-3 relevant projects with technologies used and outcomes achieved.")
    
    if 'summary' not in text.lower() and 'objective' not in text.lower():
        tips.append("📝 *Add Professional Summary*: Include a 2-3 sentence summary highlighting your key strengths and career goals.")
    
    if 'certifications' not in text.lower():
        tips.append("🏆 *Add Certifications*: Include relevant certifications to demonstrate continuous learning and expertise.")
    
    # Skills Enhancement Tips
    valid_skills = [s for s in info['skills'] if s != 'Not found' and len(s.strip()) > 0]
    if len(valid_skills) < 5:
        tips.append("🛠 *Expand Skills Section*: List at least 5-8 relevant technical skills for your target role.")
    
    # Impact and Results Tips
    action_verbs = ["achieved", "developed", "implemented", "managed", "led", "created", "designed", 
                   "improved", "increased", "reduced", "optimized", "launched", "coordinated", "analyzed"]
    action_verb_count = sum(1 for verb in action_verbs if verb in text.lower())
    if action_verb_count < 3:
        tips.append("🚀 *Use Action Verbs*: Start bullet points with strong action verbs like 'Developed', 'Implemented', 'Led'.")
    
    metrics_indicators = ["%", "percent", "improved", "reduced", "increased", "decreased", "by", "from", "to"]
    metrics_count = sum(1 for metric in metrics_indicators if metric in text.lower())
    if metrics_count < 2:
        tips.append("📊 *Add Quantifiable Results*: Include specific metrics like 'Increased efficiency by 25%' or 'Reduced costs by $10K'.")
    
    # Formatting Tips
    if "•" not in text and "- " not in text:
        tips.append("📋 *Use Bullet Points*: Format experience and skills with bullet points for better readability.")
    
    # Content Quality Tips
    if len(text) < 800:
        tips.append("📄 *Expand Content*: Add more detail to experience descriptions and achievements.")
    
    if len(text) > 2500:
        tips.append("✂ *Condense Content*: Keep resume concise and focused on most relevant information.")
    
    # Professional Development Tips
    if not info['certifications'] or info['certifications'][0] == 'Not found':
        tips.append("🎓 *Pursue Certifications*: Consider industry-relevant certifications to strengthen your profile.")
    
    # Recent Experience Tips
    if not any(year in text for year in ['2024', '2023', '2022']):
        tips.append("🕒 *Update Recent Experience*: Ensure your most recent work experience is prominently featured.")
    
    # ATS Optimization Tips
    if not any(section in text.lower() for section in ['experience', 'education', 'skills']):
        tips.append("🔍 *Use Standard Headers*: Include standard section headers like 'Experience', 'Education', 'Skills' for ATS compatibility.")
    
    # Limit to most important tips
    return tips[:6]

# --- PDF Resume Generator ---
def generate_pdf_resume(name, email, phone, linkedin, summary, skills, experience, education, projects, certifications, field):
    """Generate a professional PDF resume with ATS-optimized formatting"""
    # Lazy-import reportlab so the app can run even if reportlab is not installed
    try:
        import importlib
        _pagesizes = importlib.import_module("reportlab.lib.pagesizes")
        letter, A4 = _pagesizes.letter, _pagesizes.A4
        _platypus = importlib.import_module("reportlab.platypus")
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle = (
            _platypus.SimpleDocTemplate,
            _platypus.Paragraph,
            _platypus.Spacer,
            _platypus.Table,
            _platypus.TableStyle,
        )
        _styles = importlib.import_module("reportlab.lib.styles")
        getSampleStyleSheet, ParagraphStyle = _styles.getSampleStyleSheet, _styles.ParagraphStyle
        _units = importlib.import_module("reportlab.lib.units")
        inch = _units.inch
        colors = importlib.import_module("reportlab.lib.colors")
        _enums = importlib.import_module("reportlab.lib.enums")
        TA_CENTER, TA_LEFT, TA_JUSTIFY = _enums.TA_CENTER, _enums.TA_LEFT, _enums.TA_JUSTIFY
    except Exception:
        st.error("PDF generation requires the 'reportlab' package. Please install it: pip install reportlab")
        return None
    
    # Create a buffer to store the PDF
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=6,
        spaceBefore=12,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.darkblue,
        borderPadding=3
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=3,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Build the story (content)
    story = []
    
    # Title
    story.append(Paragraph(name.upper(), title_style))
    story.append(Spacer(1, 6))
    
    # Contact Information
    contact_info = f"{email} | {phone} | {linkedin}"
    story.append(Paragraph(contact_info, normal_style))
    story.append(Spacer(1, 12))
    
    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    story.append(Paragraph(summary, normal_style))
    story.append(Spacer(1, 6))
    
    # Technical Skills
    story.append(Paragraph("TECHNICAL SKILLS", heading_style))
    story.append(Paragraph(skills, normal_style))
    story.append(Spacer(1, 6))
    
    # Professional Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
    experience_lines = experience.split('\n')
    for line in experience_lines:
        if line.strip():
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
            else:
                story.append(Paragraph(line.strip(), normal_style))
    story.append(Spacer(1, 6))
    
    # Education
    story.append(Paragraph("EDUCATION", heading_style))
    education_lines = education.split('\n')
    for line in education_lines:
        if line.strip():
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
            else:
                story.append(Paragraph(line.strip(), normal_style))
    story.append(Spacer(1, 6))
    
    # Projects
    story.append(Paragraph("PROJECTS", heading_style))
    project_lines = projects.split('\n')
    for line in project_lines:
        if line.strip():
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
            else:
                story.append(Paragraph(line.strip(), normal_style))
    story.append(Spacer(1, 6))
    
    # Certifications
    story.append(Paragraph("CERTIFICATIONS & TRAINING", heading_style))
    cert_lines = certifications.split('\n')
    for line in cert_lines:
        if line.strip():
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
            else:
                story.append(Paragraph(line.strip(), normal_style))
    story.append(Spacer(1, 6))
    
    # Additional Information
    story.append(Paragraph("ADDITIONAL INFORMATION", heading_style))
    additional_info = [
        "• Proficient in Agile methodologies and project management tools",
        "• Strong problem-solving skills with analytical mindset", 
        "• Excellent communication and collaboration abilities",
        "• Committed to continuous professional development"
    ]
    for info in additional_info:
        story.append(Paragraph(info, bullet_style))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

# --- YouTube Video Recommendation ---
YOUTUBE_VIDEO = {
    "title": "How to Make a Resume Stand Out in 2024 (5 Tips)",
    "summary": "A concise guide to making your resume stand out with actionable tips and real examples.",
    "url": "https://youtu.be/IIGWpw1FXhk?si=eaG2uk0OCHGvm7Tw"
}

# --- Relevant/Irrelevant Courses/Certs ---
def classify_courses_certs(info, field):
    relevant_courses = [c for c in COURSES.get(field, []) if any(kw in c.lower() for kw in info['skills'])]
    irrelevant_courses = [c for c in COURSES.get(field, []) if c not in relevant_courses]
    relevant_certs = [c for c in info['certifications'] if any(p in c.lower() for p in CERT_PROVIDERS if p in field.lower() or p in ' '.join(info['skills']).lower())]
    irrelevant_certs = [c for c in info['certifications'] if c not in relevant_certs]
    return relevant_courses, irrelevant_courses, relevant_certs, irrelevant_certs

# --- Suggest Missing from Template ---
def suggest_missing(info, text):
    missing_sections = [s for s in IDEAL_SECTIONS if s not in text.lower()]
    missing_skills = [s for s in IDEAL_SKILLS if s not in [sk.lower() for sk in info['skills']]]
    missing_certs = [p.title() for p in CERT_PROVIDERS if not any(p in c.lower() for c in info['certifications'])]
    return missing_sections, missing_skills, missing_certs


# Recommend missing skills for the predicted field

def recommend_skills(extracted_skills, field):
    if field in SKILL_KEYWORDS:
        missing = [kw for kw in SKILL_KEYWORDS[field] if kw not in [s.lower() for s in extracted_skills]]
        return missing
    return []


# --- NLP-based keyword extraction ---
def extract_keywords(text):
    doc = nlp(text)
    # Use noun chunks and named entities as keywords
    keywords = set()
    for chunk in doc.noun_chunks:
        if len(chunk.text) > 2:
            keywords.add(chunk.text.strip().lower())
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE", "PERSON", "SKILL", "WORK_OF_ART", "EVENT"]:
            keywords.add(ent.text.strip().lower())
    # Add unique words longer than 4 chars (excluding stopwords)
    for token in doc:
        if not token.is_stop and not token.is_punct and len(token.text) > 4:
            keywords.add(token.text.strip().lower())
    return keywords


# --- Course Relevance Helper ---
def course_relevance(course, missing_skills):
    for skill in missing_skills:
        if skill.lower() in course.lower():
            return "✅ Strongly Recommended"
    if any(word in course.lower() for word in ["crash", "introduction", "beginner"]):
        return "✅ Add after completion"
    return "✅ Must Have"


# (Removed duplicate set_page_config; configured earlier)

# --- Custom CSS for Neatness ---
st.markdown(
    """
    <style>
    .stAlert-success {
        color: #222 !important;
    }
    body, .main {
        background: linear-gradient(120deg, #e0e7ff 0%, #c9e4ff 40%, #f8fafc 100%) !important;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    .st-bb {border-bottom: 2px solid #e0e0e0; margin: 1.5em 0 1em 0;}
    .st-section {
        padding: 1.2em 1.5em;
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 8px 32px 0 rgba(80,120,200,0.18), 0 2px 8px 0 rgba(80,120,200,0.12);
        margin-bottom: 1.2em;
        transition: box-shadow 0.2s;
    }
    .st-section:hover {
        box-shadow: 0 12px 40px 0 rgba(80,120,200,0.22), 0 4px 16px 0 rgba(80,120,200,0.16);
    }
    .st-emoji {font-size: 1.3em; margin-right: 0.3em;}
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI Semibold', 'Roboto', 'Arial', sans-serif;
        color: #2d3a4a;
        letter-spacing: 0.5px;
    }
    .section-title {
        font-size: 1.3em;
        font-weight: 700;
        margin-bottom: 0.5em;
        padding: 0.2em 0.8em;
        border-radius: 8px;
        display: inline-block;
    }
    .section-title-blue { background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%); color: #fff; }
    .section-title-green { background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); color: #222; }
    .section-title-orange { background: linear-gradient(90deg, #f7971e 0%, #ffd200 100%); color: #222; }
    .section-title-red { background: linear-gradient(90deg, #f9536b 0%, #b91d73 100%); color: #fff; }
    .section-title-purple { background: linear-gradient(90deg, #a18cd1 0%, #fbc2eb 100%); color: #222; }
    .score-badge {
        font-size: 2.2em;
        font-weight: 800;
        color: #fff;
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        border-radius: 16px;
        padding: 0.2em 0.7em;
        margin-bottom: 0.5em;
        display: inline-block;
        box-shadow: 0 2px 8px 0 rgba(80,120,200,0.18);
    }
    .suggestion-card {
        background: linear-gradient(120deg, #f8fafc 60%, #e0e7ff 100%);
        border-radius: 12px;
        box-shadow: 0 2px 8px 0 rgba(80,120,200,0.10);
        padding: 1em 1.2em;
        margin-bottom: 0.7em;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(120deg, #e0e7ff 0%, #c9e4ff 100%) !important;
        border-right: 2px solid #bfc9d9;
    }
    
    /* Comparison table styling */
    .comparison-table {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        overflow: hidden;
        margin: 1em 0;
    }
    
    .comparison-metric {
        font-weight: 600;
        color: #2d3a4a;
        padding: 0.5em;
        background: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
    }
    
    .comparison-value {
        padding: 0.5em;
        border-bottom: 1px solid #e9ecef;
    }
    
    .highlight-green {
        background-color: #d4edda !important;
        color: #155724 !important;
        font-weight: bold;
    }
    
    .highlight-yellow {
        background-color: #fff3cd !important;
        color: #856404 !important;
        font-weight: bold;
    }
    
    .highlight-red {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        font-weight: bold;
    }
    
    .highlight-blue {
        background-color: #d1ecf1 !important;
        color: #0c5460 !important;
        font-weight: bold;
    }
    
    .skill-comparison {
        background: linear-gradient(120deg, #f8fafc 60%, #e0e7ff 100%);
        border-radius: 12px;
        padding: 1.5em;
        margin: 1em 0;
        border-left: 4px solid #2575fc;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5em;
        margin: 1em 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Icon URLs ---
ICON_RESUME = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
ICON_SKILLS = "https://cdn-icons-png.flaticon.com/512/1055/1055687.png"
ICON_CERT = "https://cdn-icons-png.flaticon.com/512/190/190411.png"
ICON_PROJECT = "https://cdn-icons-png.flaticon.com/512/906/906175.png"
ICON_VIDEO = "https://cdn-icons-png.flaticon.com/512/1384/1384060.png"
ICON_SUGGEST = "https://cdn-icons-png.flaticon.com/512/1828/1828884.png"
ICON_FEEDBACK = "https://cdn-icons-png.flaticon.com/512/1828/1828919.png"

files = st.session_state.get('uploaded_files_cache', [])

if page == "Start / Upload":
    # --- User Greeting and Title ---
    st.markdown("""
    <div style='margin-bottom: 1.5em;'>
      <h2 style='margin-bottom:0.2em;'>🤖 Welcome to <span style='color:#2575fc;'>ProFile Analyzer</span>!</h2>
      <span style='font-size:1.1em; color:#4a5a6a;'>Upload your resume(s) and get instant, actionable feedback.</span>
    </div>
    """, unsafe_allow_html=True)

    st.title("🤖 ProFile Analyzer")

    # --- Pre-upload Guidelines ---
    with st.expander("📋 Upload Guidelines", expanded=False):
        st.markdown(PRE_UPLOAD_GUIDELINES)

    # --- Uploader ---
    uploaded_files = st.file_uploader("📤 Upload Resume(s) (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)
    st.markdown("<div class='st-bb'></div>", unsafe_allow_html=True)
    if uploaded_files:
        # Persist safe copies (name, ext, bytes) because UploadedFile streams may not persist across pages
        cached = []
        for uf in uploaded_files:
            try:
                data = uf.read()
            except Exception:
                data = b""
            cached.append({
                'name': uf.name,
                'ext': uf.name.split('.')[-1].lower(),
                'bytes': data,
            })
        st.session_state['uploaded_files_cache'] = cached
        files = cached

# Add file management controls
if files:
    # File management section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Resume Management")
    
    # Show current files
    st.sidebar.markdown(f"**Currently loaded:** {len(files)} resume(s)")
    for i, file in enumerate(files):
        file_name = file.get('name', f'Resume {i+1}') if isinstance(file, dict) else file.name
        st.sidebar.markdown(f"• {file_name}")
    
    # Add more files button
    if st.sidebar.button("➕ Add More Resumes", help="Upload additional resumes for comparison"):
        st.session_state['show_uploader'] = True
    
    # Clear all files button
    if st.sidebar.button("🗑️ Clear All Resumes", help="Remove all uploaded resumes"):
        st.session_state['uploaded_files_cache'] = []
        st.session_state['show_uploader'] = False
        st.rerun()
    
    # Show uploader if requested
    if st.session_state.get('show_uploader', False):
        st.markdown("### 📤 Upload Additional Resumes")
        additional_files = st.file_uploader("Select additional resume files", type=["pdf", "docx"], accept_multiple_files=True, key="additional_uploader")
        
        if additional_files:
            # Add new files to existing cache
            current_files = st.session_state.get('uploaded_files_cache', [])
            for uf in additional_files:
                try:
                    data = uf.read()
                except Exception:
                    data = b""
                current_files.append({
                    'name': uf.name,
                    'ext': uf.name.split('.')[-1].lower(),
                    'bytes': data,
                })
            st.session_state['uploaded_files_cache'] = current_files
            st.session_state['show_uploader'] = False
            st.rerun()
        
        if st.button("❌ Cancel"):
            st.session_state['show_uploader'] = False
            st.rerun()
    
    # Check if multiple resumes are uploaded
    if len(files) > 1:
        # Show comparison view for multiple resumes
        st.markdown("""
        <div class='summary-card'>
            <h2 style='color: white; margin-bottom: 0.5em;'>📊 Multi-Resume Analysis</h2>
            <p style='color: white; margin: 0; font-size: 1.1em;'>Compare {num_resumes} resumes side by side to identify strengths and areas for improvement.</p>
        </div>
        """.format(num_resumes=len(files)), unsafe_allow_html=True)
        
        # Debug info
        st.info(f"Processing {len(files)} resumes for comparison...")
        
        # Extract data from all resumes
        all_resume_data = []
        for idx, uploaded in enumerate(files):
            # Build temp file from cached bytes
            if isinstance(uploaded, dict):
                file_extension = uploaded.get('ext', 'pdf')
                data_bytes = uploaded.get('bytes', b"")
            else:
                file_extension = uploaded.name.split('.')[-1].lower()
                try:
                    data_bytes = uploaded.read()
                except Exception:
                    data_bytes = b""
            
            temp_file_path = f"temp_resume_{idx}.{file_extension}"
            with open(temp_file_path, "wb") as f:
                f.write(data_bytes)
            
            # Extract text based on file type
            if file_extension == "pdf":
                text = extract_text_from_pdf(temp_file_path)
            elif file_extension == "docx":
                text = extract_text_from_docx(temp_file_path)
            else:
                text = ""
            
            # Extract information
            info = extract_info(text)
            field = detect_field(text)
            resume_score, score_breakdown = dynamic_resume_score(text, info, field)
            
            all_resume_data.append({
                'name': info['name'],
                'field': field,
                'ats_score': resume_score,
                'skills': info['skills'],
                'certifications': info['certifications'],
                'education': info['education'],
                'projects': info['projects'],
                'linkedin': info['linkedin'],
                'github': info['github'],
                'file_name': uploaded.get('name', f'Resume {idx+1}') if isinstance(uploaded, dict) else uploaded.name
            })
        
        # Create comparison table
        try:
            create_comparison_table(all_resume_data)
        except Exception as e:
            st.error(f"Error creating comparison table: {e}")
            st.exception(e)
        
        # Add summary analysis
        try:
            create_summary_analysis(all_resume_data)
        except Exception as e:
            st.error(f"Error creating summary analysis: {e}")
            st.exception(e)
        
        # Individual resume tabs
        st.markdown("### 📄 Individual Resume Analysis")
        tab_labels = [f"Resume {i+1}" for i in range(len(files))]
        tabs = st.tabs(tab_labels)
    else:
        # Single resume - show individual tabs with option to add more
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📄 Resume Analysis")
        with col2:
            if st.button("➕ Add More Resumes", help="Upload additional resumes for comparison", type="primary"):
                st.session_state['show_uploader'] = True
                st.rerun()
        
        # Show info about comparison feature
        st.info("💡 **Tip:** Upload multiple resumes to compare them side-by-side and identify the strongest version!")
        
        tab_labels = [f"Resume {i+1}" for i in range(len(files))]
        tabs = st.tabs(tab_labels)
    
    for idx, uploaded in enumerate(files):
        with tabs[idx]:
            st.markdown(f"<div class='st-section'>", unsafe_allow_html=True)
            st.image(ICON_RESUME, width=48)
            st.markdown(f"### 📄 <span class='st-emoji'>Resume {idx+1}</span>", unsafe_allow_html=True)
            # After first upload, auto-switch to Edit & Build so users see the main workflow
            if st.session_state.get("nav_page") == PAGES[0]:
                st.session_state["nav_page"] = "Edit & Build"
                try:
                    st.rerun()
                except Exception:
                    pass

            # Build temp file from cached bytes or live upload
            if isinstance(uploaded, dict):
                file_extension = uploaded.get('ext', 'pdf')
                data_bytes = uploaded.get('bytes', b"")
            else:
                file_extension = uploaded.name.split('.')[-1].lower()
                try:
                    data_bytes = uploaded.read()
                except Exception:
                    data_bytes = b""
            temp_file_path = f"temp_resume_{idx}.{file_extension}"
            with open(temp_file_path, "wb") as f:
                f.write(data_bytes)
            
            # Extract text based on file type
            if file_extension == "pdf":
                text = extract_text_from_pdf(temp_file_path)
            elif file_extension == "docx":
                text = extract_text_from_docx(temp_file_path)
            else:
                text = ""
            
            # Validate resume format
            format_warnings = validate_resume_format(text)
            if format_warnings:
                st.warning("*Resume Format Issues Detected:*")
                for warning in format_warnings:
                    st.markdown(f"• {warning}")
            
            info = extract_info(text)
            field = detect_field(text)

            # --- Fixed counts for display (removed sliders) ---
            skill_count = 10
            cert_count = 10
            proj_count = 10

            # --- Extracted/Edit panels (mutually exclusive) ---
            if page == "Edit & Build":
                panel_opts = ["Extracted Info", "Edit Info"]
                panel_key = f"edit_active_panel_{idx}"
                if panel_key not in st.session_state:
                    st.session_state[panel_key] = panel_opts[0]
                st.session_state[panel_key] = st.radio(
                    "Edit Panels",
                    panel_opts,
                    index=panel_opts.index(st.session_state[panel_key]),
                    horizontal=True,
                    key=f"edit_panel_radio_{idx}"
                )

            # --- Extracted Info Block (Edit & Build page) ---
            if page == "Edit & Build":
                with st.expander("🔍 Extracted Info", expanded=(st.session_state.get(panel_key)=="Extracted Info")):
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.image(ICON_FEEDBACK, width=32)
                    st.write(f"👤 Name: {info['name']}")
                    st.write(f"✉ Email: {info['email']}")
                    st.write(f"📞 Phone: {info['phone']}")
                    st.write(f"🎓 Education: {', '.join(info['education'])}")
                    st.write(f"🛠 Skills: {', '.join(info['skills'][:skill_count])}")
                    st.write(f"📄 Certifications: {', '.join(info['certifications'][:cert_count])}")
                    st.write(f"📦 Projects: {', '.join(info.get('projects', [])[:proj_count])}")
                    st.write(f"🔗 LinkedIn: {info['linkedin']}")
                    st.write(f"🐙 GitHub: {info['github']}")
                    st.write(f"🌐 Portfolio: {info['portfolio']}")
                    st.write(f"💼 Predicted Field: {field}")
                    st.markdown("</div>", unsafe_allow_html=True)
            

            # --- ATS Score Display (Before Editing) ---
            if page == "Edit & Build":
                st.markdown("### 📊 **Current ATS Score**")
                current_score, current_breakdown = dynamic_resume_score(text, info, field)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f'<div class="score-badge">{current_score}/100</div>', unsafe_allow_html=True)
                    st.progress(current_score / 100)
                    
                    # Score interpretation
                    if current_score >= 85:
                        st.success("🎯 *Excellent!* Your resume meets professional standards.")
                    elif current_score >= 75:
                        st.success("✅ *Strong Resume!* Minor improvements can make it outstanding.")
                    elif current_score >= 65:
                        st.info("📈 *Good Foundation!* Focus on the areas below for better results.")
                    elif current_score >= 50:
                        st.warning("⚠ *Needs Improvement.* Consider the suggestions below.")
                    else:
                        st.error("🔴 *Requires Major Updates.* Follow the recommendations below.")
                
                # Store original score for comparison
                st.session_state[f'original_score_{idx}'] = current_score
                st.session_state[f'original_breakdown_{idx}'] = current_breakdown
            
            # --- Manual Edit Section (Edit & Build page) ---
            if page == "Edit & Build":
                with st.expander("✏ Edit Extracted Information", expanded=(st.session_state.get(panel_key)=="Edit Info")):
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.markdown("*Edit any incorrectly extracted information:*")
                    
                    # Create session state for edited info
                    if f'edited_info_{idx}' not in st.session_state:
                        st.session_state[f'edited_info_{idx}'] = info.copy()
                    
                    edited_info = st.session_state[f'edited_info_{idx}']
                    
                    # Editable fields
                    edited_info['name'] = st.text_input("Name:", value=edited_info['name'], key=f"name_{idx}")
                    edited_info['email'] = st.text_input("Email:", value=edited_info['email'], key=f"email_{idx}")
                    edited_info['phone'] = st.text_input("Phone:", value=edited_info['phone'], key=f"phone_{idx}")
                    edited_info['linkedin'] = st.text_input("LinkedIn:", value=edited_info['linkedin'], key=f"linkedin_{idx}")
                    edited_info['github'] = st.text_input("GitHub:", value=edited_info['github'], key=f"github_{idx}")
                    edited_info['portfolio'] = st.text_input("Portfolio:", value=edited_info['portfolio'], key=f"portfolio_{idx}")
                    
                    # Skills editing with suggestions
                    st.markdown("*Skills (one per line):*")
                    
                    # Get current skills text first
                    current_skills_text = st.session_state.get(f"skills_text_{idx}", "\n".join(edited_info['skills'] if edited_info['skills'] != ["Not found"] else []))
                    
                    # Show suggested skills for the field
                    field_skills = SKILL_KEYWORDS.get(field, [])
                    if field_skills:
                        st.markdown(f"**💡 Suggested skills for {field}:**")
                        current_skills_list = [s.strip() for s in current_skills_text.split('\n') if s.strip()]
                        suggested_skills = [skill for skill in field_skills[:10] if skill.lower() not in [s.lower() for s in current_skills_list]]
                        if suggested_skills:
                            cols = st.columns(3)
                            for i, skill in enumerate(suggested_skills[:9]):
                                with cols[i % 3]:
                                    if st.button(f"+ {skill}", key=f"suggest_skill_{skill}_{idx}", help=f"Add {skill} to your skills"):
                                        if skill not in current_skills_list:
                                            current_skills_list.append(skill)
                                            st.session_state[f"skills_text_{idx}"] = "\n".join(current_skills_list)
                                            st.rerun()
                    
                    skills_text = st.text_area("Skills:", value=current_skills_text, key=f"skills_{idx}")
                    edited_info['skills'] = [s.strip() for s in skills_text.split('\n') if s.strip()]
                    
                    # Certifications editing with suggestions
                    st.markdown("*Certifications (one per line):*")
                    
                    # Get current certifications text first
                    current_certs_text = st.session_state.get(f"certs_text_{idx}", "\n".join(edited_info['certifications'] if edited_info['certifications'] != ["Not found"] else []))
                    
                    # Show suggested certifications for the field
                    field_certs = CERTIFICATIONS.get(field, [])
                    if field_certs:
                        st.markdown(f"**🏆 Suggested certifications for {field}:**")
                        current_certs_list = [c.strip() for c in current_certs_text.split('\n') if c.strip()]
                        suggested_certs = [cert for cert in field_certs[:6] if cert.lower() not in [c.lower() for c in current_certs_list]]
                        if suggested_certs:
                            cols = st.columns(2)
                            for i, cert in enumerate(suggested_certs[:6]):
                                with cols[i % 2]:
                                    if st.button(f"+ {cert}", key=f"suggest_cert_{cert}_{idx}", help=f"Add {cert} to your certifications"):
                                        if cert not in current_certs_list:
                                            current_certs_list.append(cert)
                                            st.session_state[f"certs_text_{idx}"] = "\n".join(current_certs_list)
                                            st.rerun()
                    
                    certs_text = st.text_area("Certifications:", value=current_certs_text, key=f"certs_{idx}")
                    edited_info['certifications'] = [c.strip() for c in certs_text.split('\n') if c.strip()]
                    
                    # Education editing
                    st.markdown("*Education (one per line):*")
                    edu_text = st.text_area("Education:", value="\n".join(edited_info['education'] if edited_info['education'] != ["Not found"] else []), key=f"edu_{idx}")
                    edited_info['education'] = [e.strip() for e in edu_text.split('\n') if e.strip()]
                    
                    # Update session state
                    st.session_state[f'edited_info_{idx}'] = edited_info
                    
                    # Use edited info for scoring if user has made changes
                    if st.button("🔄 Update Analysis with Edited Info", key=f"update_{idx}"):
                        info = edited_info
                        field = detect_field(" ".join(edited_info['skills']))
                        # Set flag to show updated score
                        st.session_state[f'score_updated_{idx}'] = True
                        st.success("✅ Analysis updated with your changes!")
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)

            # --- Updated ATS Score Display (After Editing) ---
            # Only show updated score if user has clicked "Update Analysis" button
            if page == "Edit & Build" and f'edited_info_{idx}' in st.session_state and st.session_state.get(f'score_updated_{idx}', False):
                st.markdown("### 📈 **Updated ATS Score**")
                
                # Calculate updated score with edited info
                updated_info = st.session_state[f'edited_info_{idx}']
                updated_field = detect_field(" ".join(updated_info['skills']))
                updated_score, updated_breakdown = dynamic_resume_score(text, updated_info, updated_field)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f'<div class="score-badge">{updated_score}/100</div>', unsafe_allow_html=True)
                    st.progress(updated_score / 100)
                    
                    # Show improvement
                    original_score = st.session_state.get(f'original_score_{idx}', 0)
                    improvement = updated_score - original_score
                    
                    if improvement > 0:
                        st.success(f"🎉 **+{improvement} points improvement!** Your edits made the resume stronger.")
                    elif improvement < 0:
                        st.warning(f"⚠️ **{improvement} points decrease.** Consider reviewing your changes.")
                    else:
                        st.info("📊 **No change in score.** Your edits maintained the current quality.")
                    
                    # Score interpretation
                    if updated_score >= 85:
                        st.success("🎯 *Excellent!* Your resume meets professional standards.")
                    elif updated_score >= 75:
                        st.success("✅ *Strong Resume!* Minor improvements can make it outstanding.")
                    elif updated_score >= 65:
                        st.info("📈 *Good Foundation!* Focus on the areas below for better results.")
                    elif updated_score >= 50:
                        st.warning("⚠ *Needs Improvement.* Consider the suggestions below.")
                    else:
                        st.error("🔴 *Requires Major Updates.* Follow the recommendations below.")
                
                # Detailed comparison
                with st.expander("📊 **Score Comparison Breakdown**", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Original Score:**")
                        original_breakdown = st.session_state.get(f'original_breakdown_{idx}', {})
                        for category, points in original_breakdown.items():
                            if category != "Total Score":
                                # Ensure points is a number, not a dict
                                if isinstance(points, (int, float)):
                                    points_value = points
                                else:
                                    points_value = 0
                                st.metric(category, f"{points_value} pts")
                    
                    with col2:
                        st.markdown("**Updated Score:**")
                        for category, points in updated_breakdown.items():
                            if category != "Total Score":
                                # Ensure points is a number, not a dict
                                if isinstance(points, (int, float)):
                                    points_value = points
                                else:
                                    points_value = 0
                                
                                # Ensure original points is also a number
                                original_points = original_breakdown.get(category, 0)
                                if isinstance(original_points, (int, float)):
                                    original_value = original_points
                                else:
                                    original_value = 0
                                
                                change = points_value - original_value
                                delta_color = "normal" if change == 0 else "inverse" if change < 0 else "normal"
                                st.metric(category, f"{points_value} pts", delta=f"{change:+.1f}" if change != 0 else None)

            # --- Resume Score Block (ATS Compatibility page) ---
            if page == "ATS Compatibility":
                with st.container():
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    
                    # Use updated info if available, otherwise use original
                    if f'edited_info_{idx}' in st.session_state and st.session_state.get(f'score_updated_{idx}', False):
                        # Use updated information for scoring
                        updated_info = st.session_state[f'edited_info_{idx}']
                        updated_field = detect_field(" ".join(updated_info['skills']))
                        resume_score, score_breakdown = dynamic_resume_score(text, updated_info, updated_field)
                        st.info("📊 **Analysis based on your updated resume information**")
                    else:
                        # Use original information for scoring
                        resume_score, score_breakdown = dynamic_resume_score(text, info, field)
                        st.info("📊 **Analysis based on original resume information**")
                    
                    st.markdown(f'<div class="score-badge">{resume_score}/100</div>', unsafe_allow_html=True)
                    st.image(ICON_FEEDBACK, width=32)
                    st.progress(resume_score / 100)

                    # Mutual-exclusive panel selector
                    panel_options = [
                        "Score Breakdown",
                        "ATS Feature Analysis",
                        "Enhancement Guide",
                    ]
                    if "ats_active_panel" not in st.session_state:
                        st.session_state["ats_active_panel"] = panel_options[0]
                    st.session_state["ats_active_panel"] = st.radio(
                        "Panels",
                        panel_options,
                        index=panel_options.index(st.session_state["ats_active_panel"]),
                        horizontal=True,
                        key=f"ats_panel_{idx}",
                    )
                
                # Score interpretation
                if resume_score >= 85:
                    st.success("🎯 *Excellent!* Your resume meets professional standards.")
                elif resume_score >= 75:
                    st.success("✅ *Strong Resume!* Minor improvements can make it outstanding.")
                elif resume_score >= 65:
                    st.info("📈 *Good Foundation!* Focus on the areas below for better results.")
                elif resume_score >= 50:
                    st.warning("⚠ *Needs Improvement.* Consider the suggestions below.")
                else:
                    st.error("🔴 *Requires Major Updates.* Follow the recommendations below.")
                
                # Detailed Score Breakdown
                with st.expander("📊 **Detailed Score Breakdown**", expanded=(st.session_state.get("ats_active_panel") == "Score Breakdown")):
                    # Define maximum points for each category
                    max_points = {
                        "Content Completeness": 20,
                        "Skills Assessment": 25,
                        "Experience & Impact": 20,
                        "Professional Presentation": 15,
                        "ATS Optimization": 20,
                        "Bonus Points": 10,
                        "Total Score": 100
                    }
                    
                    # Show scoring structure overview
                    st.markdown("**📋 Scoring Structure Overview:**")
                    st.markdown("Our comprehensive 100-point scoring system evaluates your resume across key areas:")
                    
                    scoring_overview = [
                        "🎯 **Content Completeness** (20 pts): Essential & optional sections",
                        "🛠️ **Skills Assessment** (25 pts): Quantity & field relevance", 
                        "💼 **Experience & Impact** (20 pts): Action verbs & measurable results",
                        "✨ **Professional Presentation** (15 pts): Contact info, formatting & credentials",
                        "🔍 **ATS Optimization** (20 pts): Keyword matching & ATS compatibility",
                        "🎁 **Bonus Points** (10 pts): Projects, portfolio links & recent experience"
                    ]
                    
                    for item in scoring_overview:
                        st.markdown(f"• {item}")
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        for category, points in list(score_breakdown.items())[:3]:
                            if category != "ATS Details":
                                max_pts = max_points.get(category, 100)
                                # Color coding based on performance
                                if points >= max_pts * 0.8:  # 80% or higher
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Excellent", delta_color="normal")
                                elif points >= max_pts * 0.6:  # 60-79%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Good", delta_color="normal")
                                elif points >= max_pts * 0.4:  # 40-59%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Needs Work", delta_color="inverse")
                                else:  # Below 40%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Poor", delta_color="inverse")
                    with col2:
                        for category, points in list(score_breakdown.items())[3:]:
                            if category != "ATS Details":
                                max_pts = max_points.get(category, 100)
                                # Color coding based on performance
                                if points >= max_pts * 0.8:  # 80% or higher
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Excellent", delta_color="normal")
                                elif points >= max_pts * 0.6:  # 60-79%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Good", delta_color="normal")
                                elif points >= max_pts * 0.4:  # 40-59%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Needs Work", delta_color="inverse")
                                else:  # Below 40%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Poor", delta_color="inverse")
                
                # ATS Detailed Breakdown (ATS Compatibility page)
                if "ATS Details" in score_breakdown:
                    with st.expander("🎯 **ATS Optimization Details**", expanded=False):
                        st.markdown("**Applicant Tracking System (ATS) Compatibility Analysis:**")
                        ats_details = score_breakdown["ATS Details"]
                        
                        # Define maximum points for ATS categories
                        ats_max_points = {
                            "Keyword Match": 8,
                            "Section Headers": 4,
                            "Format Compatibility": 3,
                            "Contact Info": 2,
                            "Experience Details": 3
                        }
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            for category, points in list(ats_details.items())[:3]:
                                max_pts = ats_max_points.get(category, 10)
                                # Color coding based on ATS performance
                                if points >= max_pts * 0.8:  # 80% or higher
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Excellent", delta_color="normal")
                                elif points >= max_pts * 0.6:  # 60-79%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Good", delta_color="normal")
                                elif points >= max_pts * 0.4:  # 40-59%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Needs Work", delta_color="inverse")
                                else:  # Below 40%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Poor", delta_color="inverse")
                        with col2:
                            for category, points in list(ats_details.items())[3:]:
                                max_pts = ats_max_points.get(category, 10)
                                # Color coding based on ATS performance
                                if points >= max_pts * 0.8:  # 80% or higher
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Excellent", delta_color="normal")
                                elif points >= max_pts * 0.6:  # 60-79%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Good", delta_color="normal")
                                elif points >= max_pts * 0.4:  # 40-59%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Needs Work", delta_color="inverse")
                                else:  # Below 40%
                                    st.metric(category, f"{points}/{max_pts} pts", delta="Poor", delta_color="inverse")
                        
                        # ATS Recommendations
                        st.markdown("**ATS Optimization Tips:**")
                        ats_tips = []
                        if ats_details.get("Keyword Match", 0) < 4:
                            ats_tips.append("🔍 **Add more field-specific keywords** to improve ATS matching")
                        if ats_details.get("Section Headers", 0) < 2:
                            ats_tips.append("📋 **Use standard section headers** like 'Experience', 'Education', 'Skills'")
                        if ats_details.get("Format Compatibility", 0) < 2:
                            ats_tips.append("📄 **Use simple formatting** - avoid special characters and complex layouts")
                        if ats_details.get("Contact Info", 0) < 2:
                            ats_tips.append("📞 **Include complete contact information** for ATS parsing")
                        if ats_details.get("Experience Details", 0) < 2:
                            ats_tips.append("💼 **Add detailed work experience** with dates and company names")
                        
                        for tip in ats_tips:
                            st.markdown(f"• {tip}")
                
                # Comprehensive ATS Feature Analysis (compact, two-column layout)
                ats_features = extract_ats_features(text, info, field)
                with st.expander("🔍 **Comprehensive ATS Feature Analysis**", expanded=(st.session_state.get("ats_active_panel") == "ATS Feature Analysis")):
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    col1, col2 = st.columns([1,1])

                    # Left column: Keywords + Headers + Contact
                    with col1:
                        # Keyword Analysis (compact)
                        keywords_found = ats_features.get("Keywords Found", [])
                        match_rate = ats_features.get('Keyword Match Rate', '0/0')
                        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
                        st.markdown("<div class='title'>Keyword Match</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='value'>{match_rate}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                        if keywords_found:
                            top_kw = "".join([f"<span class='pill'>{kw}</span>" for kw in keywords_found[:6]])
                            st.markdown(f"**Top Keywords:** {top_kw}", unsafe_allow_html=True)
                        else:
                            st.markdown("<span class='pill bad'>No field keywords</span>", unsafe_allow_html=True)

                        # Section headers (compact)
                        st.markdown(f"**📋 Headers:** {ats_features.get('Header Compliance', 'Unknown')}")
                        headers = ats_features.get("Standard Headers Found", [])
                        if headers:
                            pills = "".join([f"<span class='pill good'>{h.title()}</span>" for h in headers])
                            st.markdown("**Found:** " + pills, unsafe_allow_html=True)

                        # Contact info (inline)
                        contact_info = ats_features.get("Contact Information", {})
                        if contact_info:
                            items = [f"<span class='pill {'good' if v=='Present' else 'bad'}'>{k}</span>" for k, v in contact_info.items()]
                            st.markdown("**📞 Contact:** " + " ".join(items), unsafe_allow_html=True)

                    # Right column: Formatting + Experience + Skills + Score
                    with col2:
                        # Formatting (inline)
                        formatting = ats_features.get("Formatting", {})
                        if formatting:
                            pills = []
                            for k, v in formatting.items():
                                status_class = 'good' if any(word in v for word in ['Present', 'Clean', 'Optimal']) else 'warn'
                                pills.append(f"<span class='pill {status_class}'>{k}: {v}</span>")
                            st.markdown("**📄 Formatting:** " + " ".join(pills), unsafe_allow_html=True)

                        # Experience (inline)
                        experience = ats_features.get("Experience Details", {})
                        if experience:
                            items = [f"<span class='pill {'good' if v=='Present' else 'bad'}'>{k}</span>" for k, v in experience.items()]
                            st.markdown("**💼 Experience:** " + " ".join(items), unsafe_allow_html=True)

                        # Skills summary
                        skills = ats_features.get("Skills Analysis", {})
                        st.markdown(f"**🛠️ Skills:** <span class='pill'>{skills.get('Skills Count', 0)} total</span> <span class='pill'>{skills.get('Skills Quality', 'Unknown')}</span>", unsafe_allow_html=True)

                        # Overall score
                        score_text = ats_features.get('ATS Compatibility Score', '0/20')
                        st.markdown(f"**🎯 ATS Score:** {score_text}")
                        try:
                            ats_score_value = float(score_text.split('/')[0])
                        except Exception:
                            ats_score_value = 0.0
                        pct = min(100, max(0, int((ats_score_value/20)*100)))
                        st.markdown(f"<div class='scorebar'><div style='width:{pct}%;'></div></div>", unsafe_allow_html=True)
                    if ats_score_value >= 16:
                            st.markdown("<span class='pill good'>Excellent</span>", unsafe_allow_html=True)
                    elif ats_score_value >= 12:
                            st.markdown("<span class='pill'>Good</span>", unsafe_allow_html=True)
                    elif ats_score_value >= 8:
                            st.markdown("<span class='pill warn'>Moderate</span>", unsafe_allow_html=True)
                    else:
                            st.markdown("<span class='pill bad'>Low</span>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Strengths and Weaknesses
                strengths, weaknesses = get_strengths_weaknesses(text, info)
                if strengths:
                    st.markdown('<span class="section-title section-title-green">✅ Strengths</span>', unsafe_allow_html=True)
                    for s in strengths:
                        st.markdown(f'<div class="suggestion-card">✓ {s}</div>', unsafe_allow_html=True)
                
                if weaknesses:
                    st.markdown('<span class="section-title section-title-red">⚠ Areas for Improvement</span>', unsafe_allow_html=True)
                    for w in weaknesses:
                        st.markdown(f'<div class="suggestion-card">• {w}</div>', unsafe_allow_html=True)
                
                # Personalized Tips
                tips = get_personalized_tips(text, info)
                if tips:
                    st.markdown('<span class="section-title section-title-purple">💡 Personalized Tips</span>', unsafe_allow_html=True)
                    for tip in tips:
                        st.markdown(f'<div class="suggestion-card">💡 {tip}</div>', unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Strengths & Areas for Improvement Block (Insights page) ---
            if page == "Insights":
                with st.container():
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.markdown("<span class='st-emoji'>👍</span> <b>Strengths:</b>", unsafe_allow_html=True)
                    st.image(ICON_SUGGEST, width=28)
                    strengths = []
                    if 'contact' in text.lower(): strengths.append("Clean layout, contact info present")
                    if any(s in [sk.lower() for sk in info['skills']] for s in ["python", "ml", "machine learning"]): strengths.append("Technical terms like 'Python', 'ML' appear")
                    if 'projects' in text.lower(): strengths.append("Projects section included")
                    for s in strengths:
                        st.markdown(f"• {s}")
                    st.markdown("<span class='st-emoji'>👎</span> <b>Areas for Improvement:</b>", unsafe_allow_html=True)
                    st.markdown("• Did You Know? Adding actionable metrics (e.g. 'Improved X by 20%') increases readability")
                    st.markdown("• Tip: Add a 'Projects' section with 2–3 real-world examples")
                    if info['linkedin'] == 'Not found':
                        st.markdown("• Tip: Add your LinkedIn URL")
                    if 'certifications' not in text.lower():
                        st.markdown("• Tip: Include a 'Certifications' section")
                    st.markdown("</div>", unsafe_allow_html=True)

            # --- Missing Skills & Recommended Courses Block (Insights page) ---
            if page == "Insights":
                with st.expander("✅ Missing Skills & Recommended Courses", expanded=False):
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.image(ICON_SKILLS, width=32)
                    # Determine current field and skills
                    current_skills = [s.lower() for s in info['skills'] if s != 'Not found']
                    current_field = detect_field(current_skills)
                    field_skills = [s.lower() for s in SKILL_KEYWORDS.get(current_field, [])]
                    # Compute missing skills relative to field
                    missing = [s for s in field_skills if s not in current_skills]
                    if missing:
                        st.markdown("**❌ Missing Field Skills:** " + ", ".join(ms.title() for ms in missing[:8]))
                    else:
                        st.markdown("**✅ You cover the key field skills.**")
                    # Recommended courses based on field
                    field_courses = COURSES.get(current_field, [])
                    if field_courses:
                        st.markdown("**📚 Recommended Courses:**")
                        for i, course in enumerate(field_courses[:5], 1):
                            provider = course.split(' – ')[-1] if ' – ' in course else 'Various'
                            st.markdown(f"{i}. {course} — <span class='pill'>{provider}</span>", unsafe_allow_html=True)
                    # Recommended certifications
                    field_certs = CERTIFICATIONS.get(current_field, [])
                    if field_certs:
                        st.markdown("**🏆 Relevant Certifications:** " + ", ".join(field_certs[:5]))

            # --- Comprehensive Resume Enhancement Recommendations (slides via tabs) ---
            if page == "ATS Compatibility":
                with st.expander("🚀 **Comprehensive Resume Enhancement Guide**", expanded=(st.session_state.get("ats_active_panel") == "Enhancement Guide")):
                    t1, t2, t3, t4, t5, t6 = st.tabs([
                        "Skills",
                        "Projects",
                        "Courses & Certs",
                        "Structure",
                        "ATS Checklist",
                        "Action Plan"
                    ])

                    # Precompute shared data - use updated info if available
                    if f'edited_info_{idx}' in st.session_state and st.session_state.get(f'score_updated_{idx}', False):
                        analysis_info = st.session_state[f'edited_info_{idx}']
                        analysis_field = detect_field(" ".join(analysis_info['skills']))
                    else:
                        analysis_info = info
                        analysis_field = field
                    
                    current_skills = [s.lower() for s in analysis_info['skills'] if s != 'Not found']
                    field_skills = SKILL_KEYWORDS.get(analysis_field, [])
                
                    with t1:
                        st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                        st.subheader("🛠️ Skills Analysis & Recommendations")
                        if current_skills:
                            st.markdown("**✅ Skills You Have:** " + ", ".join(s.title() for s in current_skills[:5]))
                        missing_skills = [skill for skill in field_skills if skill.lower() not in current_skills]
                        if missing_skills:
                            st.markdown("**❌ Critical Missing Skills:** " + ", ".join(s.title() for s in missing_skills[:5]))
                        st.markdown("**📈 Skills Enhancement Strategy:**")
                        st.markdown("• 🎯 Prioritize field-specific skills  • 📚 Learn complementary skills  • 🔄 Stay current  • 📊 Quantify proficiency")
                        st.markdown("</div>", unsafe_allow_html=True)

                    with t2:
                        st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                        st.subheader("💼 Project Recommendations")
                        field_projects = PROJECT_IDEAS.get(field, [])
                    if field_projects:
                        for i, project in enumerate(field_projects[:3], 1):
                            st.markdown(f"**{i}. {project}** — <span class='pill'>Tech: {', '.join(field_skills[:3])}</span>", unsafe_allow_html=True)
                    st.markdown("**🚀 Tips:** Document, Demo, Metrics, Deploy, Responsive")
                    st.markdown("</div>", unsafe_allow_html=True)

                with t3:
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.subheader("📚 Course & Certification Recommendations")
                    field_courses = COURSES.get(field, [])
                    if field_courses:
                        for i, course in enumerate(field_courses[:3], 1):
                            provider = course.split(' – ')[-1] if ' – ' in course else 'Various'
                            priority = 'High' if i == 1 else 'Medium' if i == 2 else 'Good to have'
                            st.markdown(f"**{i}. {course}** — <span class='pill'>{provider}</span> <span class='pill'>{priority}</span>", unsafe_allow_html=True)
                    field_certs = CERTIFICATIONS.get(field, [])
                    if field_certs:
                        st.markdown("**🏆 Certifications:** " + ", ".join(field_certs[:3]))
                    st.markdown("</div>", unsafe_allow_html=True)

                with t4:
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.subheader("📋 Resume Structure Enhancement")
                    section_checklist = [
                        ("Professional Summary", "summary" in text.lower() or "objective" in text.lower()),
                        ("Contact Information", analysis_info['email'] != 'Not found' and analysis_info['phone'] != 'Not found'),
                        ("Skills Section", len(current_skills) > 0),
                        ("Experience Section", "experience" in text.lower()),
                        ("Education Section", "education" in text.lower()),
                        ("Projects Section", "projects" in text.lower()),
                        ("Certifications Section", "certifications" in text.lower()),
                        ("LinkedIn Profile", analysis_info['linkedin'] != 'Not found')
                    ]
                    pills = " ".join([f"<span class='pill {'good' if present else 'warn'}'>{section}</span>" for section, present in section_checklist])
                    st.markdown(pills, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with t5:
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.subheader("🔍 ATS Optimization Checklist")
                    ats_checklist = [
                        ("Standard Section Headers", any(h in text.lower() for h in ["experience", "education", "skills"])),
                        ("Keyword Optimization", len([kw for kw in field_skills if kw.lower() in text.lower()]) >= 3),
                        ("Bullet Point Formatting", "•" in text or "- " in text),
                        ("Clean Formatting", not any(char in text for char in ["[", "]", "{", "}", "|"])),
                        ("Optimal Length", 500 <= len(text) <= 3000),
                        ("Contact Information", analysis_info['email'] != 'Not found' and analysis_info['phone'] != 'Not found'),
                        ("Recent Experience", any(year in text for year in ["2024", "2023", "2022"])),
                        ("Quantifiable Results", any(word in text for word in ["%", "improved", "increased", "reduced"]))
                    ]
                    pills = " ".join([f"<span class='pill {'good' if present else 'warn'}'>{item}</span>" for item, present in ats_checklist])
                    st.markdown(pills, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with t6:
                    st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                    st.subheader("🎯 30-Day Action Plan")
                    action_plan = [
                        "Week 1: Complete 1-2 recommended courses",
                        "Week 2: Start building a recommended project",
                        "Week 3: Update resume with new skills and projects",
                        "Week 4: Optimize for ATS and get feedback"
                    ]
                    st.markdown(" ".join([f"<span class='pill'>{step}</span>" for step in action_plan]), unsafe_allow_html=True)
                    st.markdown("**Pro Tips:** Focus on quality, track progress, network, measure improvements, iterate.")
                    st.markdown("</div>", unsafe_allow_html=True)
                # End of Comprehensive Resume Enhancement Guide section

            # --- Resume Improvement & Template Generator ---
            # This section has been moved to the "Resume Generator" page

            # --- Resume Generator Page Content ---
            if page == "Resume Generator":
                # --- Resume Improvement & Template Generator ---
                st.markdown("<div class='hero'>", unsafe_allow_html=True)
                st.markdown("<div class='title'>📝 Resume Generator</div>", unsafe_allow_html=True)
                st.markdown("<div class='subtitle'>Create an enhanced, ATS-optimized resume with AI-powered suggestions</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                st.image(ICON_FEEDBACK, width=32)
                
                # === 1. SUMMARY OF CHANGES NEEDED ===
                st.markdown("### 📋 **Summary of Changes Needed**")
                
                # Collect all improvement suggestions
                improvement_suggestions = []
                
                # Skills improvements
                current_skills = [s.lower() for s in info['skills'] if s != 'Not found']
                field_skills = SKILL_KEYWORDS.get(field, [])
                missing_skills = [skill for skill in field_skills if skill.lower() not in current_skills]
                if missing_skills:
                    improvement_suggestions.append(f"**Add {len(missing_skills)} missing skills:** {', '.join(missing_skills[:3])}")
                
                # Section improvements
                if 'summary' not in text.lower() and 'objective' not in text.lower():
                    improvement_suggestions.append("**Add Professional Summary section**")
                if 'projects' not in text.lower():
                    improvement_suggestions.append("**Add Projects section**")
                if 'certifications' not in text.lower():
                    improvement_suggestions.append("**Add Certifications section**")
                if info['linkedin'] == 'Not found':
                    improvement_suggestions.append("**Add LinkedIn profile URL**")
                
                # Formatting improvements
                if "•" not in text and "- " not in text:
                    improvement_suggestions.append("**Use bullet points for better formatting**")
                if not any(word in text for word in ["%", "improved", "increased", "reduced"]):
                    improvement_suggestions.append("**Add quantifiable achievements with metrics**")
                
                # Display improvements
                if improvement_suggestions:
                    st.markdown("**🔧 Required Improvements:**")
                    for i, suggestion in enumerate(improvement_suggestions, 1):
                        st.markdown(f"{i}. {suggestion}")
                else:
                    st.success("🎉 **Great job!** Your resume meets most professional standards.")
                
                st.markdown("---")
                
                # === 2. EDITABLE RESUME DETAILS ===
                st.markdown("### ✏️ **Edit Resume Details**")
                st.markdown("**Update your information for the improved resume:**")
                
                # Create editable fields
                col1, col2 = st.columns(2)
                
                with col1:
                    edited_name = st.text_input("Full Name", value=info['name'] if info['name'] != 'Not found' else "", key=f"improve_name_{idx}")
                    edited_email = st.text_input("Email", value=info['email'] if info['email'] != 'Not found' else "", key=f"improve_email_{idx}")
                    edited_phone = st.text_input("Phone", value=info['phone'] if info['phone'] != 'Not found' else "", key=f"improve_phone_{idx}")
                    edited_linkedin = st.text_input("LinkedIn URL", value=info['linkedin'] if info['linkedin'] != 'Not found' else "", key=f"improve_linkedin_{idx}")
                
                with col2:
                    edited_education = st.text_area("Education", value="\n".join(info['education']) if info['education'] and info['education'][0] != 'Not found' else "", key=f"improve_education_{idx}")
                    edited_skills = st.text_area("Skills (one per line)", value="\n".join(info['skills']) if info['skills'] and info['skills'][0] != 'Not found' else "", key=f"improve_skills_{idx}")
                    edited_certifications = st.text_area("Certifications", value="\n".join(info['certifications']) if info['certifications'] and info['certifications'][0] != 'Not found' else "", key=f"improve_certifications_{idx}")
                
                # Job-focused tailoring
                st.markdown("**Job Target (optional):**")
                target_role = st.text_input("Target Role / Title", value="", key=f"target_role_{idx}")
                job_description = st.text_area("Paste Job Description (JD)", value="", height=150, key=f"job_desc_{idx}")
                
                # Simple keyword extraction from JD
                def extract_keywords(text_block):
                    words = re.findall(r"[A-Za-z]{3,}", text_block.lower())
                    stop = set(["and","with","for","you","your","the","this","that","from","will","have","are","our","not","but","per","who","job","role","work","team","ability","skills","experience","years","strong","good","excellent","required","preferred","plus","using","use"])    
                    freq = {}
                    for w in words:
                        if w in stop:
                            continue
                        freq[w] = freq.get(w, 0) + 1
                    return [w for w,_ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:12]]
                jd_keywords = extract_keywords(job_description) if job_description else []
                # Tailored skills: prioritize overlap between JD keywords and provided skills/field skills
                provided_skills = [s.strip().lower() for s in (edited_skills.split("\n") if edited_skills else []) if s.strip()]
                tailored_priority = [kw for kw in jd_keywords if kw in provided_skills or kw in [fs.lower() for fs in SKILL_KEYWORDS.get(field, [])]]
                
                # Professional Summary
                st.markdown("**Professional Summary:**")
                professional_summary = st.text_area(
                    "Write a compelling 2-3 sentence professional summary",
                    value="",
                    placeholder="e.g., Experienced [field] professional with expertise in [key skills]. Passionate about [relevant interests] and committed to delivering innovative solutions.",
                    key=f"improve_summary_{idx}"
                )
                
                # Experience Section
                st.markdown("**Work Experience:**")
                experience_text = st.text_area(
                    "Add your work experience with bullet points",
                    value="",
                    placeholder="e.g., • Developed and maintained web applications using React and Node.js\n• Improved application performance by 25% through optimization\n• Collaborated with cross-functional teams to deliver projects on time",
                    key=f"improve_experience_{idx}"
                )
                
                # Projects Section
                st.markdown("**Projects:**")
                projects_text = st.text_area(
                    "Add 2-3 relevant projects with technologies used",
                    value="",
                    placeholder="e.g., • E-commerce Platform - Built using React, Node.js, MongoDB\n• Machine Learning Model - Developed predictive analytics using Python, scikit-learn\n• Portfolio Website - Created responsive design with HTML, CSS, JavaScript",
                    key=f"improve_projects_{idx}"
                )
                
                st.markdown("---")
                
                # === 3. ATS-OPTIMIZED RESUME TEMPLATE ===
                st.markdown("### 📄 **ATS-Optimized Resume Template**")
                
                # Generate improved resume content
                if st.button("🔄 Generate Improved Resume", key=f"improve_generate_{idx}"):
                    # Create ATS-optimized professional resume content
                    # Precompute default sections to avoid backslashes in f-string expressions
                    default_summary = (
                        professional_summary
                        if professional_summary
                        else (
                            f"Results-driven {field} professional with {len(field_skills[:3])}+ years of experience in {', '.join(field_skills[:3])}. "
                            f"Proven track record of delivering innovative solutions and driving measurable business outcomes. "
                            f"Passionate about continuous learning and staying current with industry trends."
                        )
                    )

                    default_skills = (
                        (', '.join([s.title() for s in tailored_priority[:8]]))
                        if tailored_priority
                        else (edited_skills if edited_skills else ', '.join(field_skills[:8]))
                    )

                    default_experience = (
                        experience_text
                        if experience_text
                        else (
                            f"• Developed and implemented {field.lower()} solutions resulting in 25% improvement in efficiency\n"
                            f"• Collaborated with cross-functional teams to deliver projects on time and within budget\n"
                            f"• Utilized {', '.join(field_skills[:3])} to optimize processes and enhance user experience\n"
                            f"• Analyzed data and provided actionable insights leading to informed decision-making"
                        )
                    )

                    default_education = (
                        edited_education
                        if edited_education
                        else (
                            "• Bachelor's Degree in Computer Science/Related Field\n"
                            "• Relevant coursework: Data Structures, Algorithms, Database Management\n"
                            "• GPA: 3.5+ (if applicable)"
                        )
                    )

                    default_projects = (
                        projects_text
                        if projects_text
                        else (
                            f"• {field} Application - Built using {', '.join(field_skills[:3])}, deployed on cloud platform\n"
                            "• Data Analysis Project - Developed predictive models achieving 85% accuracy\n"
                            "• Portfolio Website - Responsive design with modern UI/UX principles"
                        )
                    )

                    default_certifications = (
                        edited_certifications
                        if edited_certifications
                        else (
                            f"• {field} Certification - Industry-recognized credential\n"
                            "• Professional Development Courses - Continuous learning initiatives\n"
                            "• Technical Training - Hands-on workshops and bootcamps"
                        )
                    )

                    improved_resume = f"""
{edited_name.upper()}
{edited_email} | {edited_phone} | {edited_linkedin}

TARGET ROLE
{target_role if target_role else field}

PROFESSIONAL SUMMARY
{default_summary}

TECHNICAL SKILLS
{default_skills}

PROFESSIONAL EXPERIENCE
{default_experience}

EDUCATION
{default_education}

PROJECTS
{default_projects}

CERTIFICATIONS & TRAINING
{default_certifications}

ADDITIONAL INFORMATION
• Proficient in Agile methodologies and project management tools
• Strong problem-solving skills with analytical mindset
• Excellent communication and collaboration abilities
• Committed to continuous professional development
"""
                    
                    # Store the improved resume in session state
                    st.session_state[f'improved_resume_{idx}'] = improved_resume
                    
                    st.success("✅ **Improved Resume Generated!** Scroll down to preview and download.")
                
                # === 4. RESUME PREVIEW ===
                if f'improved_resume_{idx}' in st.session_state:
                    st.markdown("### 👀 **Resume Preview**")
                    
                    # Display the improved resume
                    st.text_area(
                        "Preview of Your Improved Resume",
                        value=st.session_state[f'improved_resume_{idx}'],
                        height=400,
                        key=f"improve_preview_{idx}"
                    )
                    
                    # === 5. DOWNLOAD OPTIONS ===
                    st.markdown("### 💾 **Download Options**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Download as TXT
                        st.download_button(
                            label="📄 Download as Text",
                            data=st.session_state[f'improved_resume_{idx}'],
                            file_name=f"{edited_name.replace(' ', '_')}_Improved_Resume.txt",
                            mime="text/plain",
                            key=f"improve_download_txt_{idx}"
                        )
                    
                    with col2:
                        # Download as HTML (formatted, academic single-column)
                        # Precompute HTML sections to avoid backslashes in f-string expressions
                        html_target_role = f'<div class="muted">Target Role: {target_role}</div>' if target_role else ''
                        
                        html_summary = (
                            professional_summary
                            if professional_summary
                            else f'Experienced {field} professional with expertise in {", ".join(field_skills[:3])}. Passionate about technology and committed to delivering innovative solutions.'
                        )
                        
                        html_skills_chips = (
                            ''.join([f'<span>{s.title()}</span>' for s in tailored_priority[:10]])
                            if tailored_priority
                            else (edited_skills if edited_skills else ', '.join(field_skills[:8]))
                        )
                        
                        html_experience = (
                            experience_text.replace(chr(10), '<br>')
                            if experience_text
                            else f'• Developed and implemented {field.lower()} solutions resulting in 25% improvement in efficiency<br>• Collaborated with cross-functional teams to deliver projects on time and within budget<br>• Utilized {", ".join(field_skills[:3])} to optimize processes and enhance user experience'
                        )
                        
                        html_education = (
                            edited_education.replace(chr(10), '<br>')
                            if edited_education
                            else '• Bachelor\'s Degree in Computer Science/Related Field<br>• Relevant coursework: Data Structures, Algorithms, Database Management'
                        )
                        
                        html_projects = (
                            projects_text.replace(chr(10), '<br>')
                            if projects_text
                            else f'• {field} Application - Built using {", ".join(field_skills[:3])}, deployed on cloud platform<br>• Data Analysis Project - Developed predictive models achieving 85% accuracy'
                        )
                        
                        html_certifications = (
                            edited_certifications.replace(chr(10), '<br>')
                            if edited_certifications
                            else f'• {field} Certification - Industry-recognized credential<br>• Professional Development Courses - Continuous learning initiatives'
                        )
                        
                        html_resume = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{edited_name} - Resume</title>
    <style>
        body {{ margin: 36px; line-height: 1.55; color:#213047; font-family: 'Segoe UI', Arial, sans-serif; }}
        h1 {{ font-family: Georgia, 'Times New Roman', serif; font-weight: 800; color: #0c2d57; margin: 0 0 6px 0; }}
        .accent {{ height: 4px; width: 72px; background: linear-gradient(90deg,#0f67ff,#5aa1ff); border-radius: 999px; margin-bottom: 18px; }}
        h2 {{ font-family: Georgia, 'Times New Roman', serif; color: #0c2d57; margin-top: 22px; margin-bottom: 8px; font-size: 18px; }}
        .contact {{ margin-bottom: 14px; color:#37506b; }}
        .section {{ margin-bottom: 16px; }}
        .chips span {{ display:inline-block; background:#eef3ff; color:#0f67ff; padding:4px 8px; border-radius:999px; margin:2px; font-size:12px; }}
        .muted {{ color:#5c708a; }}
    </style>
</head>
<body>
    <h1>{edited_name}</h1>
    <div class="accent"></div>
    <div class="contact">{edited_email} | {edited_phone} | {edited_linkedin}</div>
    {html_target_role}
    
    <div class="section">
        <h2>Professional Summary</h2>
        <p>{html_summary}</p>
    </div>
    
    <div class="section">
        <h2>Technical Skills</h2>
        <div class="chips">{html_skills_chips}</div>
    </div>
    
    <div class="section">
        <h2>Experience</h2>
        <p>{html_experience}</p>
    </div>
    
    <div class="section">
        <h2>Education</h2>
        <p>{html_education}</p>
    </div>
    
    <div class="section">
        <h2>Projects / Coursework</h2>
        <p>{html_projects}</p>
    </div>
    
    <div class="section">
        <h2>Certifications & Training</h2>
        <p>{html_certifications}</p>
    </div>
</body>
</html>
"""
                        
                        st.download_button(
                            label="🌐 Download as HTML",
                            data=html_resume,
                            file_name=f"{edited_name.replace(' ', '_')}_Improved_Resume.html",
                            mime="text/html",
                            key=f"improve_download_html_{idx}"
                        )
                    
                    with col3:
                        # Generate and download PDF
                        if st.button("📋 Generate PDF Resume", key=f"generate_pdf_{idx}"):
                            # Prepare content for PDF
                            pdf_summary = professional_summary if professional_summary else f"Results-driven {field} professional with {len(field_skills[:3])}+ years of experience in {', '.join(field_skills[:3])}. Proven track record of delivering innovative solutions and driving measurable business outcomes."
                            
                            pdf_skills = edited_skills if edited_skills else ', '.join(field_skills[:8])
                            
                            pdf_experience = experience_text if experience_text else f"• Developed and implemented {field.lower()} solutions resulting in 25% improvement in efficiency\n• Collaborated with cross-functional teams to deliver projects on time and within budget\n• Utilized {', '.join(field_skills[:3])} to optimize processes and enhance user experience"
                            
                            pdf_education = edited_education if edited_education else "• Bachelor's Degree in Computer Science/Related Field\n• Relevant coursework: Data Structures, Algorithms, Database Management"
                            
                            pdf_projects = projects_text if projects_text else f"• {field} Application - Built using {', '.join(field_skills[:3])}, deployed on cloud platform\n• Data Analysis Project - Developed predictive models achieving 85% accuracy"
                            
                            pdf_certifications = edited_certifications if edited_certifications else f"• {field} Certification - Industry-recognized credential\n• Professional Development Courses - Continuous learning initiatives"
                            
                            # Generate PDF
                            pdf_content = generate_pdf_resume(
                                edited_name, edited_email, edited_phone, edited_linkedin,
                                pdf_summary, pdf_skills, pdf_experience, pdf_education,
                                pdf_projects, pdf_certifications, field
                            )
                            
                            # Store PDF in session state only if valid bytes were returned
                            if pdf_content:
                                st.session_state[f'pdf_resume_{idx}'] = pdf_content
                                st.success("✅ PDF generated successfully! Click download below.")
                            else:
                                st.warning("PDF generation failed or is unavailable. Please ensure 'reportlab' is installed.")
                        
                        # Download PDF if available
                        if f'pdf_resume_{idx}' in st.session_state and st.session_state[f'pdf_resume_{idx}']:
                            st.download_button(
                                label="📄 Download PDF",
                                data=st.session_state[f'pdf_resume_{idx}'],
                                file_name=f"{edited_name.replace(' ', '_')}_Professional_Resume.pdf",
                                mime="application/pdf",
                                key=f"improve_download_pdf_{idx}"
                            )
                    
                    # ATS Score for improved resume
                    st.markdown("### 🎯 **Improved Resume ATS Score**")
                    
                    # Calculate ATS score for improved resume
                    improved_info = {
                        'name': edited_name,
                        'email': edited_email,
                        'phone': edited_phone,
                        'linkedin': edited_linkedin,
                        'education': edited_education.split('\n') if edited_education else [],
                        'skills': edited_skills.split('\n') if edited_skills else [],
                        'certifications': edited_certifications.split('\n') if edited_certifications else []
                    }
                    
                    improved_score, improved_breakdown = dynamic_resume_score(st.session_state[f'improved_resume_{idx}'], improved_info, field)
                    
                    st.metric("Improved ATS Score", f"{improved_score}/100")
                    st.progress(improved_score / 100)
                    
                    if improved_score >= 85:
                        st.success("🎉 **Excellent!** Your improved resume should pass most ATS systems.")
                    elif improved_score >= 75:
                        st.info("✅ **Great improvement!** Your resume is now ATS-optimized.")
                    else:
                        st.warning("⚠️ **Good progress!** Continue refining for better results.")
                
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Job Matching Page Content ---
            if page == "Job Matching":
                st.markdown("<div class='hero'>", unsafe_allow_html=True)
                st.markdown("<div class='title'>🎯 Job Matching</div>", unsafe_allow_html=True)
                st.markdown("<div class='subtitle'>Find companies hiring for roles that match your resume</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='st-section'>", unsafe_allow_html=True)
                
                # Check if user has uploaded a resume
                if files:
                    # Analyze the first resume to determine the role
                    if len(files) > 0:
                        # Use the first uploaded file
                        uploaded = files[0]
                        if isinstance(uploaded, dict):
                            file_extension = uploaded.get('ext', 'pdf')
                            data_bytes = uploaded.get('bytes', b"")
                        else:
                            file_extension = uploaded.name.split('.')[-1].lower()
                            try:
                                data_bytes = uploaded.read()
                            except Exception:
                                data_bytes = b""
                        
                        temp_file_path = f"temp_resume_job_matching.{file_extension}"
                        with open(temp_file_path, "wb") as f:
                            f.write(data_bytes)
                        
                        # Extract text and analyze
                        if file_extension == "pdf":
                            text = extract_text_from_pdf(temp_file_path)
                        elif file_extension == "docx":
                            text = extract_text_from_docx(temp_file_path)
                        else:
                            text = ""
                        
                        # Analyze resume to determine role
                        info = extract_info(text)
                        field = detect_field(text)
                        
                        st.markdown("### 📋 **Your Resume Analysis**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Name:** {info['name']}")
                            st.write(f"**Email:** {info['email']}")
                            st.write(f"**Phone:** {info['phone']}")
                        
                        with col2:
                            st.write(f"**Detected Field:** {field}")
                            st.write(f"**Skills Found:** {len([s for s in info['skills'] if s != 'Not found'])} skills")
                            st.write(f"**Experience Level:** {'Senior' if len(text) > 2000 else 'Mid-level' if len(text) > 1000 else 'Entry-level'}")
                        
                        # Job matching based on detected field
                        st.markdown("### 🎯 **Matching Job Opportunities**")
                        
                        # Define job opportunities by field
                        job_opportunities = {
                            "Data Science": [
                                {"company": "Google", "role": "Data Scientist", "location": "Mountain View, CA", "salary": "$130k-180k", "match": "95%", "skills": ["Python", "Machine Learning", "SQL"]},
                                {"company": "Microsoft", "role": "Senior Data Analyst", "location": "Seattle, WA", "salary": "$120k-160k", "match": "92%", "skills": ["Python", "PowerBI", "Statistics"]},
                                {"company": "Amazon", "role": "Data Engineer", "location": "Austin, TX", "salary": "$125k-170k", "match": "88%", "skills": ["Python", "AWS", "Spark"]},
                                {"company": "Meta", "role": "Research Scientist", "location": "Menlo Park, CA", "salary": "$140k-200k", "match": "90%", "skills": ["Python", "Deep Learning", "Research"]},
                                {"company": "Netflix", "role": "Data Scientist", "location": "Los Gatos, CA", "salary": "$135k-185k", "match": "87%", "skills": ["Python", "A/B Testing", "Statistics"]}
                            ],
                            "Web Development": [
                                {"company": "Google", "role": "Frontend Engineer", "location": "Mountain View, CA", "salary": "$120k-170k", "match": "93%", "skills": ["React", "JavaScript", "CSS"]},
                                {"company": "Facebook", "role": "Full Stack Developer", "location": "Menlo Park, CA", "salary": "$125k-175k", "match": "91%", "skills": ["React", "Node.js", "GraphQL"]},
                                {"company": "Airbnb", "role": "Software Engineer", "location": "San Francisco, CA", "salary": "$130k-180k", "match": "89%", "skills": ["React", "Python", "Django"]},
                                {"company": "Uber", "role": "Frontend Engineer", "location": "San Francisco, CA", "salary": "$115k-165k", "match": "86%", "skills": ["React", "TypeScript", "Webpack"]},
                                {"company": "Stripe", "role": "Full Stack Engineer", "location": "San Francisco, CA", "salary": "$140k-190k", "match": "94%", "skills": ["React", "Ruby", "PostgreSQL"]}
                            ],
                            "Artificial Intelligence": [
                                {"company": "OpenAI", "role": "AI Research Engineer", "location": "San Francisco, CA", "salary": "$150k-220k", "match": "96%", "skills": ["Python", "TensorFlow", "NLP"]},
                                {"company": "Tesla", "role": "Machine Learning Engineer", "location": "Palo Alto, CA", "salary": "$140k-200k", "match": "92%", "skills": ["Python", "PyTorch", "Computer Vision"]},
                                {"company": "NVIDIA", "role": "AI Software Engineer", "location": "Santa Clara, CA", "salary": "$135k-185k", "match": "89%", "skills": ["Python", "CUDA", "Deep Learning"]},
                                {"company": "DeepMind", "role": "Research Scientist", "location": "London, UK", "salary": "$130k-180k", "match": "95%", "skills": ["Python", "Reinforcement Learning", "Research"]},
                                {"company": "Anthropic", "role": "AI Safety Researcher", "location": "San Francisco, CA", "salary": "$145k-210k", "match": "91%", "skills": ["Python", "AI Safety", "Research"]}
                            ],
                            "Cybersecurity": [
                                {"company": "CrowdStrike", "role": "Security Engineer", "location": "Austin, TX", "salary": "$120k-170k", "match": "94%", "skills": ["Python", "SIEM", "Threat Analysis"]},
                                {"company": "Palo Alto Networks", "role": "Cybersecurity Analyst", "location": "Santa Clara, CA", "salary": "$115k-160k", "match": "91%", "skills": ["Network Security", "Firewalls", "Incident Response"]},
                                {"company": "FireEye", "role": "Security Consultant", "location": "Milpitas, CA", "salary": "$125k-175k", "match": "88%", "skills": ["Penetration Testing", "Vulnerability Assessment", "Security"]},
                                {"company": "Rapid7", "role": "Security Researcher", "location": "Boston, MA", "salary": "$130k-180k", "match": "92%", "skills": ["Python", "Malware Analysis", "Research"]},
                                {"company": "Zscaler", "role": "Cloud Security Engineer", "location": "San Jose, CA", "salary": "$135k-185k", "match": "90%", "skills": ["Cloud Security", "AWS", "Zero Trust"]}
                            ]
                        }
                        
                        # Get opportunities for the detected field
                        opportunities = job_opportunities.get(field, job_opportunities["Data Science"])  # Default to Data Science
                        
                        # Display job opportunities
                        for i, job in enumerate(opportunities):
                            with st.expander(f"🏢 {job['company']} - {job['role']} ({job['match']} Match)", expanded=(i==0)):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.markdown(f"**📍 Location:** {job['location']}")
                                    st.markdown(f"**💰 Salary:** {job['salary']}")
                                
                                with col2:
                                    st.markdown(f"**🎯 Match Score:** {job['match']}")
                                    st.markdown(f"**🏢 Company:** {job['company']}")
                                
                                with col3:
                                    st.markdown("**🛠 Required Skills:**")
                                    for skill in job['skills']:
                                        # Check if user has this skill
                                        user_skills = [s.lower() for s in info['skills'] if s != 'Not found']
                                        if skill.lower() in user_skills:
                                            st.markdown(f"✅ {skill}")
                                        else:
                                            st.markdown(f"❌ {skill}")
                                
                                # Application tips
                                st.markdown("**💡 Application Tips:**")
                                tips = [
                                    f"Highlight your {field.lower()} experience in your cover letter",
                                    f"Emphasize projects that demonstrate {', '.join(job['skills'][:2])} skills",
                                    f"Research {job['company']}'s recent initiatives and mention them",
                                    "Quantify your achievements with specific metrics",
                                    "Tailor your resume to include keywords from the job description"
                                ]
                                
                                for tip in tips:
                                    st.write(f"• {tip}")
                                
                                # Apply button (placeholder)
                                # Create a truly unique key using multiple job attributes
                                company_clean = job['company'].replace(' ', '_').replace('.', '').replace(',', '')
                                role_clean = job['role'].replace(' ', '_').replace('.', '').replace(',', '')
                                location_clean = job.get('location', 'Unknown').replace(' ', '_').replace('.', '').replace(',', '')
                                salary_clean = job.get('salary', 'Unknown').replace('$', '').replace(',', '').replace('-', '_')
                                
                                unique_key = f"apply_{company_clean}_{i}_{role_clean}_{location_clean}_{salary_clean}"
                                if st.button(f"📝 Apply at {job['company']}", key=unique_key):
                                    st.info(f"💡 This would redirect to {job['company']}'s career page in a real application!")
                        
                        # Summary statistics
                        st.markdown("### 📊 **Job Market Summary**")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Opportunities", len(opportunities))
                        with col2:
                            avg_salary = sum([int(job['salary'].split('-')[0].replace('$', '').replace('k', '')) for job in opportunities]) // len(opportunities)
                            st.metric("Avg. Salary", f"${avg_salary}k")
                        with col3:
                            high_match = len([j for j in opportunities if int(j['match'].replace('%', '')) >= 90])
                            st.metric("High Match Jobs", high_match)
                        with col4:
                            st.metric("Your Skills Match", f"{len([s for s in info['skills'] if s != 'Not found'])} skills")
                        
                        # Download job opportunities
                        job_summary = f"""
JOB OPPORTUNITIES FOR: {info['name'].upper()}
DETECTED FIELD: {field}

OPPORTUNITIES FOUND: {len(opportunities)}

"""
                        for i, job in enumerate(opportunities, 1):
                            job_summary += f"""
{i}. {job['company']} - {job['role']}
   Location: {job['location']}
   Salary: {job['salary']}
   Match Score: {job['match']}
   Required Skills: {', '.join(job['skills'])}
   
"""
                        
                        st.download_button(
                            label="📄 Download Job Opportunities",
                            data=job_summary,
                            file_name=f"{info['name'].replace(' ', '_')}_Job_Opportunities.txt",
                            mime="text/plain",
                            key="download_job_opportunities"
                        )
                
                else:
                    st.info("👆 Please upload your resume first to get personalized job recommendations!")
                    st.markdown("""
                    **🎯 What Job Matching Provides:**
                    
                    • **Role Detection** - Analyzes your resume to identify your target role
                    • **Company Matching** - Finds companies actively hiring for your skills
                    • **Salary Insights** - Shows market rates for your position
                    • **Skill Gap Analysis** - Identifies missing skills for target roles
                    • **Application Tips** - Personalized advice for each opportunity
                    • **Match Scoring** - Shows how well you fit each position
                    • **Location Options** - Remote and on-site opportunities
                    """)
                
                st.markdown("</div>", unsafe_allow_html=True)

    # --- Resume Length Checker (Outside tabs loop) ---
    if page == "Edit & Build" and files:
        st.markdown("### 📏 **Resume Length Analysis**")
        
        # Get the first resume's text for analysis
        if len(files) > 0:
            # Build temp file from cached bytes or live upload
            if isinstance(files[0], dict):
                file_extension = files[0].get('ext', 'pdf')
                data_bytes = files[0].get('bytes', b"")
            else:
                file_extension = files[0].name.split('.')[-1].lower()
                try:
                    data_bytes = files[0].read()
                except Exception:
                    data_bytes = b""
            temp_file_path = f"temp_resume_length_check.{file_extension}"
            with open(temp_file_path, "wb") as f:
                f.write(data_bytes)
            
            # Extract text based on file type
            if file_extension == "pdf":
                text = extract_text_from_pdf(temp_file_path)
            elif file_extension == "docx":
                text = extract_text_from_docx(temp_file_path)
            else:
                text = ""
            
            # Calculate resume length metrics
            word_count = len(text.split())
            char_count = len(text)
            line_count = len(text.split('\n'))
            
            # Determine experience level based on content length
            if word_count < 300:
                experience_level = "Entry-level"
                recommended_length = "300-500 words"
                length_status = "Too Short"
                length_color = "warning"
            elif word_count < 500:
                experience_level = "Entry to Mid-level"
                recommended_length = "400-600 words"
                length_status = "Good"
                length_color = "success"
            elif word_count < 800:
                experience_level = "Mid-level"
                recommended_length = "500-800 words"
                length_status = "Optimal"
                length_color = "success"
            elif word_count < 1200:
                experience_level = "Senior-level"
                recommended_length = "700-1000 words"
                length_status = "Good"
                length_color = "success"
            else:
                experience_level = "Executive-level"
                recommended_length = "800-1200 words"
                length_status = "Too Long"
                length_color = "warning"
            
            # Display length metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Word Count", word_count)
            with col2:
                st.metric("Character Count", f"{char_count:,}")
            with col3:
                st.metric("Lines", line_count)
            with col4:
                if length_color == "success":
                    st.success(f"✅ {length_status}")
                else:
                    st.warning(f"⚠️ {length_status}")
            
            # Length recommendations
            st.markdown("**📋 Length Recommendations:**")
            st.write(f"• **Experience Level:** {experience_level}")
            st.write(f"• **Recommended Length:** {recommended_length}")
            st.write(f"• **Current Status:** {length_status}")
            
            # Specific recommendations based on length
            if word_count < 300:
                st.warning("**⚠️ Your resume is too short!** Consider adding:")
                st.write("• More detailed job descriptions with achievements")
                st.write("• Additional skills and certifications")
                st.write("• Projects and volunteer experience")
                st.write("• Quantifiable results and metrics")
            elif word_count > 1200:
                st.warning("**⚠️ Your resume is too long!** Consider:")
                st.write("• Removing outdated or irrelevant experience")
                st.write("• Condensing job descriptions to key achievements")
                st.write("• Removing redundant skills")
                st.write("• Focusing on most recent and relevant experience")
            else:
                st.success("**✅ Your resume length is optimal!**")
                st.write("• Good balance of detail and conciseness")
                st.write("• Appropriate for your experience level")
                st.write("• ATS-friendly length")
            
            st.markdown("---")

