import os
import streamlit as st
from datetime import datetime
import google.generativeai as genai
from googleapiclient.discovery import build
from dotenv import load_dotenv
import time

# Set page config
st.set_page_config(
    page_title="MediAI Assistant | Smart Emergency & Medical Information",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Configure API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not all([GEMINI_API_KEY, YOUTUBE_API_KEY]):
    st.error("Required API keys not found. Please check your .env file.")
    st.stop()

# Initialize APIs
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

class MediAIAssistant:
    def __init__(self):
        self.create_custom_css()
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
        if 'show_first_aid_kit' not in st.session_state:
            st.session_state.show_first_aid_kit = False

    def create_custom_css(self):
        """Add custom CSS styling for medical interface."""
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
            
            .stApp {
                background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
                font-family: 'Poppins', sans-serif;
            }
            
            .hero-section {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                padding: 4rem 2rem;
                border-radius: 24px;
                color: white;
                text-align: center;
                margin-bottom: 3rem;
                animation: fadeIn 1s ease-out;
            }
            
            .hero-title {
                font-size: 3.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                color: white;
            }
            
            .hero-subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                max-width: 700px;
                margin: 0 auto;
            }
            
            .navigation-card {
                background: white;
                padding: 2rem;
                border-radius: 16px;
                margin: 1rem 0;
                transition: all 0.3s ease;
                cursor: pointer;
                border-left: 6px solid #3b82f6;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            
            .navigation-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }
            
            .medical-container {
                background: white;
                padding: 2rem;
                border-radius: 16px;
                border-left: 6px solid #3b82f6;
                margin: 1.5rem 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                animation: slideIn 0.5s ease-out;
            }
            
            .emergency-warning {
                background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
                color: white;
                padding: 1.25rem;
                border-radius: 12px;
                margin: 1.5rem 0;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);
                animation: pulse 2s infinite;
            }
            
            .remedy-card {
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                margin: 1rem 0;
                border-left: 6px solid #10b981;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            
            .remedy-title {
                color: #10b981;
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            
            .video-section {
                margin-top: 2rem;
                padding: 2rem;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            
            .video-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-top: 1rem;
            }
            
            .video-card {
                background: #f8fafc;
                border-radius: 12px;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .video-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }
            
            .video-title {
                padding: 1rem;
                font-weight: 500;
                color: #1e40af;
            }
            
            .first-aid-kit {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: white;
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                z-index: 1000;
                max-width: 300px;
                border-left: 6px solid #dc2626;
                animation: slideIn 0.3s ease-out;
            }
            
            .first-aid-kit-toggle {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #dc2626;
                color: white;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
                transition: all 0.3s ease;
                z-index: 999;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(20px); }
                to { opacity: 1; transform: translateX(0); }
            }
            
            @keyframes pulse {
                0% { opacity: 0.6; }
                50% { opacity: 1; }
                100% { opacity: 0.6; }
            }
            </style>
        """, unsafe_allow_html=True)

    def analyze_medicine(self, medicine_name):
        """Generate detailed medicine analysis using AI."""
        prompt = f"""
        Provide a detailed analysis of the medicine '{medicine_name}' in the following format:
        
        **Generic Name:**
        [Generic name of the medicine]
        
        **Drug Class:**
        [The class/category of the medicine]
        
        **Primary Uses:**
        - [Main use 1]
        - [Main use 2]
        - [Main use 3]
        
        **Common Side Effects:**
        - [Side effect 1]
        - [Side effect 2]
        - [Side effect 3]
        
        **Precautions:**
        - [Important precaution 1]
        - [Important precaution 2]
        
        **Typical Dosage:**
        [Standard dosage information]
        
        **Storage Requirements:**
        [How to properly store the medicine]
        
        **Important Notes:**
        - [Additional important information]
        - [Interactions with other medications if any]
        """
        return self.safe_generate_content(prompt)

    def analyze_symptoms(self, symptoms):
        """Generate natural remedy recommendations using AI."""
        prompt = f"""
        As a professional naturopathic doctor, provide a detailed natural remedy recommendation for the following symptoms: {symptoms}
        
        Format the response as:
        
        **Condition Assessment:**
        [Brief assessment of the described symptoms]
        
        **Top Natural Remedies:**
        1. [Remedy 1 Name]
           - Key Ingredients: [List main ingredients]
           - Benefits: [How it helps]
           - Simple Preparation Method
        
        2. [Remedy 2 Name]
           - Key Ingredients: [List main ingredients]
           - Benefits: [How it helps]
           - Simple Preparation Method
        
        3. [Remedy 3 Name]
           - Key Ingredients: [List main ingredients]
           - Benefits: [How it helps]
           - Simple Preparation Method
        
        **Lifestyle Recommendations:**
        - [Recommendation 1]
        - [Recommendation 2]
        - [Recommendation 3]
        
        **Important Notes:**
        - [Safety precaution 1]
        - [Safety precaution 2]
        
        **When to See a Doctor:**
        [List specific symptoms or conditions that require professional medical attention]
        """
        return self.safe_generate_content(prompt)

    def analyze_emergency(self, emergency_type):
        """Generate emergency response guidance using AI."""
        prompt = f"""
        As a professional emergency doctor, provide exactly 5 precise, clear steps for immediate first aid treatment for {emergency_type}.
        Format the response as:
        
        **Immediate Steps to Take:**
        1. [First immediate action]
        2. [Second immediate action]
        3. [Third immediate action]
        4. [Fourth immediate action]
        5. [Fifth immediate action]

        **Warning Signs to Watch For:**
        - [Critical warning sign 1]
        - [Critical warning sign 2]
        - [Critical warning sign 3]
        
        **Additional Notes:**
        [Important information about when to seek immediate medical attention]
        """
        return self.safe_generate_content(prompt)

    def get_emergency_videos(self, emergency_type):
        """Fetch relevant emergency first aid videos from YouTube."""
        try:
            search_query = f"first aid {emergency_type} emergency treatment tutorial medical"
            request = youtube.search().list(
                part="snippet",
                q=search_query,
                type="video",
                videoEmbeddable="true",
                maxResults=3,
                relevanceLanguage="en",
                safeSearch="strict"
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                video = {
                    'title': item['snippet']['title'],
                    'video_id': item['id']['videoId'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'description': item['snippet']['description']
                }
                videos.append(video)
            return videos
        except Exception as e:
            st.error(f"Error fetching videos: {e}")
            return []

    def get_remedy_videos(self, remedy_name):
        """Fetch relevant natural remedy preparation videos from YouTube."""
        try:
            search_query = f"how to prepare {remedy_name} natural remedy home remedies tutorial"
            request = youtube.search().list(
                part="snippet",
                q=search_query,
                type="video",
                videoEmbeddable="true",
                maxResults=3,
                relevanceLanguage="en",
                safeSearch="strict"
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                video = {
                    'title': item['snippet']['title'],
                    'video_id': item['id']['videoId'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'description': item['snippet']['description']
                }
                videos.append(video)
            return videos
        except Exception as e:
            st.error(f"Error fetching videos: {e}")
            return []

    def safe_generate_content(self, prompt):
        """Generate AI content safely with loading animation."""
        try:
            with st.spinner(''):
                st.markdown("""
                    <div class="loading-animation">
                        <span>🧬</span>
                        <span>Processing with MediAI...</span>
                    </div>
                """, unsafe_allow_html=True)
                response = model.generate_content(prompt)
                time.sleep(0.8)  # Smooth transition
                return response.text
        except Exception as e:
            st.error(f"Error generating content: {e}")
            return None

    def extract_remedies(self, text):
        """Extract remedy names from the AI response."""
        import re
        remedies = []
        pattern = r'\d\.\s+([^-\n]+)'
        matches = re.finditer(pattern, text)
        for match in matches:
            remedies.append(match.group(1).strip())
        return remedies

    def render_homepage(self):
        """Render the homepage with hero section and navigation cards."""
        st.markdown("""
            <div class="hero-section">
                <h1 class="hero-title"> AI HEAL Assistant</h1>
                <p class="hero-subtitle">
                    Your intelligent medical companion for emergency guidance, medication analysis, and natural remedies
                </p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
                <div class="navigation-card">
                    <h3>🚨 Emergency Response</h3>
                    <p>Get instant AI-powered guidance for medical emergencies and first aid procedures</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Access Emergency Response", key="home_emergency"):
                st.session_state.page = 'emergency'
                st.rerun()

        with col2:
            st.markdown("""
                <div class="navigation-card">
                    <h3>💊 Medicine Analysis</h3>
                    <p>Get comprehensive information about medications, their effects, and proper usage</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Access Medicine Analysis", key="home_medicine"):
                st.session_state.page = 'medicine'
                st.rerun()

        with col3:
            st.markdown("""
                <div class="navigation-card">
                    <h3>🌿 Natural Remedies</h3>
                    <p>Discover natural and holistic solutions for common health issues</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Access Natural Remedies", key="home_remedies"):
                st.session_state.page = 'remedies'
                st.rerun()

    def render_emergency_page(self):
        """Render the emergency response page."""
        st.markdown("""
            <div class="emergency-warning">
                ⚠️ For life-threatening emergencies, immediately call emergency services (911/112)
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="medical-container">
                <h2>🚨 Emergency Response AI</h2>
                <p>Describe the emergency situation for immediate AI-generated first aid guidance.</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            emergency_input = st.text_input(
                "Emergency Situation Description",
                placeholder="e.g., cardiac arrest, severe burn, fracture, allergic reaction",
                key="emergency_input"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_button = st.button("Generate Emergency Response", type="primary", key="emergency_generate")

        if generate_button and emergency_input:
            emergency_response = self.analyze_emergency(emergency_input)
            if emergency_response:
                st.markdown('<div class="medical-container">', unsafe_allow_html=True)
                st.markdown(emergency_response)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("""
                    <div class="video-section">
                        <h3>📹 First Aid Instruction Videos</h3>
                        <p>Watch these AI-curated first aid instruction videos for additional guidance.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                videos = self.get_emergency_videos(emergency_input)
                if videos:
                    cols = st.columns(3)
                    for idx, video in enumerate(videos):
                        with cols[idx]:
                            st.markdown(f"""
                                <div class="video-card">
                                    <iframe 
                                        class="video-frame"
                                        src="https://www.youtube.com/embed/{video['video_id']}"
                                        style="width: 100%; aspect-ratio: 16/9; border: none;"
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                        allowfullscreen>
                                    </iframe>
                                    <div class="video-title">{video['title'][:50]}...</div>
                                </div>
                            """, unsafe_allow_html=True)

    def render_medicine_page(self):
        """Render the medicine analysis page."""
        st.markdown("""
            <div class="medical-container">
                <h2>💊 Medicine Analysis AI</h2>
                <p>Enter any medication name for comprehensive AI-powered analysis of its properties, uses, and precautions.</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            medicine_name = st.text_input(
                "Medication Name",
                placeholder="e.g., Paracetamol, Amoxicillin, Aspirin",
                key="medicine_input"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_button = st.button("Analyze Medication", type="primary", key="medicine_analyze")

        if analyze_button and medicine_name:
            medicine_info = self.analyze_medicine(medicine_name)
            if medicine_info:
                st.markdown("""
                    <div class="medical-container">
                        <h3>💊 Comprehensive Medication Analysis</h3>
                """, unsafe_allow_html=True)
                st.markdown(medicine_info)
                st.markdown("</div>", unsafe_allow_html=True)

    def render_remedies_page(self):
        """Render the enhanced natural remedies page."""
        st.markdown("""
            <div class="medical-container">
                <h2>🌿 Natural Remedies AI</h2>
                <p>Describe your symptoms for personalized natural remedy recommendations and video guides.</p>
            </div>
        """, unsafe_allow_html=True)

        symptoms = st.text_area(
            "Describe Your Symptoms",
            placeholder="e.g., recurring headache with neck tension, difficulty sleeping, occasional nausea",
            height=100,
            key="remedies_input"
        )

        analyze_symptoms_button = st.button("Get Natural Remedies", type="primary", key="remedies_analyze")

        if analyze_symptoms_button and symptoms:
            remedy_info = self.analyze_symptoms(symptoms)
            if remedy_info:
                st.markdown("""
                    <div class="remedy-card">
                        <h3>🌿 Natural Remedy Recommendations</h3>
                """, unsafe_allow_html=True)
                st.markdown(remedy_info)
                st.markdown("</div>", unsafe_allow_html=True)

                # Extract remedy names and fetch videos
                remedies = self.extract_remedies(remedy_info)
                if remedies:
                    st.markdown("""
                        <div class="video-section">
                            <h3>📹 How to Prepare These Remedies</h3>
                            <p>Watch these curated video guides for step-by-step preparation instructions.</p>
                        </div>
                    """, unsafe_allow_html=True)

                    for remedy in remedies:
                        videos = self.get_remedy_videos(remedy)
                        if videos:
                            st.markdown(f"""
                                <div class="remedy-card">
                                    <h4 class="remedy-title">🎥 {remedy} Preparation Guides</h4>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            video_cols = st.columns(3)
                            for idx, video in enumerate(videos):
                                with video_cols[idx]:
                                    st.markdown(f"""
                                        <div class="video-card">
                                            <iframe 
                                                class="video-frame"
                                                src="https://www.youtube.com/embed/{video['video_id']}"
                                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                                allowfullscreen>
                                            </iframe>
                                            <div class="video-title">{video['title'][:50]}...</div>
                                        </div>
                                    """, unsafe_allow_html=True)

    def render_first_aid_kit(self):
        """Render the first aid kit popup."""
        if not st.session_state.show_first_aid_kit:
            st.markdown("""
                <div class="first-aid-kit-toggle" onclick="document.getElementById('firstAidKit').style.display='block';">
                    🧰
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div id="firstAidKit" class="first-aid-kit" style="display: {'block' if st.session_state.show_first_aid_kit else 'none'}">
                <h3>🧰  First Aid Kit </h3>
                <ul>
                    <li>📌 Adhesive bandages (various sizes)</li>
                    <li>🩹 Sterile gauze pads</li>
                    <li>📍 Adhesive tape</li>
                    <li>🎗️ Elastic bandage</li>
                    <li>🔺 Triangular bandage</li>
                    <li>🧼 Antiseptic wipes</li>
                    <li>🧴 Antibiotic ointment</li>
                    <li>💊 Pain relief medication</li>
                    <li>✂️ Scissors</li>
                    <li>🔍 Tweezers</li>
                    <li>🧤 Disposable gloves</li>
                    <li>🛡️ Emergency blanket</li>
                    <li>📖 First aid manual</li>
                    <li>🧪 Saline solution</li>
                    <li>🌡️ Digital thermometer</li>
                </ul>
                <button onclick="this.parentElement.style.display='none';">Close</button>
            </div>
        """, unsafe_allow_html=True)

    def render_navigation(self):
        """Render the navigation menu."""
        st.sidebar.markdown("## 📍 Navigation")
        
        nav_options = {
            "🏠 Home": ("home", "sidebar_home"),
            "🚨 Emergency Response": ("emergency", "sidebar_emergency"),
            "💊 Medicine Analysis": ("medicine", "sidebar_medicine"),
            "🌿 Natural Remedies": ("remedies", "sidebar_remedies")
        }
        
        for label, (page, key) in nav_options.items():
            if st.sidebar.button(label, key=key):
                st.session_state.page = page
                st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🧰 First Aid Kit")
        if st.sidebar.button("Show First Aid Kit Contents", key="sidebar_firstaid"):
            st.session_state.show_first_aid_kit = not st.session_state.show_first_aid_kit
            st.rerun()

    def render_footer(self):
        """Render the application footer."""
        st.markdown("""
            <div class="app-footer">
                <div class="footer-text">
                    <p>🏥 MediAI Assistant is designed to provide preliminary medical information and emergency guidance.</p>
                    <p>For accurate diagnosis and treatment, always consult qualified healthcare professionals.</p>
                </div>
                <div style="height: 1px; background: #e2e8f0; margin: 1rem 0;"></div>
                <div class="footer-copyright">
                    <p>© 2025 MediAI Assistant | Version 2.1.0</p>
                    <p style="font-size: 0.8rem; color: #a0aec0; margin-top: 0.5rem;">
                        Powered by Advanced Medical AI Technology
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    def run(self):
        """Main application logic."""
        self.render_navigation()
        
        if st.session_state.page == 'home':
            self.render_homepage()
        elif st.session_state.page == 'emergency':
            self.render_emergency_page()
        elif st.session_state.page == 'medicine':
            self.render_medicine_page()
        elif st.session_state.page == 'remedies':
            self.render_remedies_page()

        self.render_first_aid_kit()
        self.render_footer()

if __name__ == "__main__":
    system = MediAIAssistant()
    system.run()