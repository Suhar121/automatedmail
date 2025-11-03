# scheduler_frontend.py
import streamlit as st
import os
from daily_scheduler import DailyTopicGenerator, start_daily_scheduler, send_test_email
import threading
import time
from datetime import datetime

if 'RENDER' in os.environ:
    st.set_page_config(
        page_title="AI LinkedIn Poster",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )


# Page configuration
st.set_page_config(
    page_title="Daily Topic Scheduler",
    page_icon="📅",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .status-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    .status-active {
        background: #d4edda;
        border: 2px solid #c3e6cb;
        color: #155724;
    }
    .status-inactive {
        background: #f8d7da;
        border: 2px solid #f5c6cb;
        color: #721c24;
    }
    .topic-box {
        background: #e7f3ff;
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'scheduler_running' not in st.session_state:
        st.session_state.scheduler_running = False
    if 'last_sent' not in st.session_state:
        st.session_state.last_sent = None
    if 'scheduler_thread' not in st.session_state:
        st.session_state.scheduler_thread = None

def main():
    st.markdown('<h1 class="main-header">📅 Daily Topic Scheduler</h1>', unsafe_allow_html=True)
    
    initialize_session_state()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Daily Learning Topics")
        st.markdown("""
        Get AI-generated learning topics delivered to your email every day at 1:00 PM.
        
        **Features:**
        - 🤖 AI-powered topic generation
        - 📧 Daily email delivery
        - 🕐 Automatic scheduling (1:00 PM daily)
        - 📚 Professional development focus
        - 🎯 Curated for continuous learning
        """)
        
        # Current status
        st.subheader("📊 System Status")
        
        status_class = "status-active" if st.session_state.scheduler_running else "status-inactive"
        status_text = "🟢 ACTIVE" if st.session_state.scheduler_running else "🔴 INACTIVE"
        
        st.markdown(f"""
        <div class="status-box {status_class}">
            <h3>System Status: {status_text}</h3>
            <p>Scheduled: Daily at 1:00 PM</p>
            <p>Recipient: suharyaseen36@gmail.com</p>
            {f'<p>Last sent: {st.session_state.last_sent}</p>' if st.session_state.last_sent else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Control buttons
        st.subheader("⚙️ Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not st.session_state.scheduler_running:
                if st.button("🚀 Start Scheduler", type="primary", use_container_width=True):
                    # Start scheduler in background thread
                    def start_scheduler():
                        st.session_state.scheduler_running = True
                        start_daily_scheduler()
                    
                    thread = threading.Thread(target=start_scheduler)
                    thread.daemon = True
                    thread.start()
                    st.session_state.scheduler_thread = thread
                    st.success("✅ Scheduler started! Emails will be sent daily at 1:00 PM")
                    st.rerun()
            else:
                if st.button("🛑 Stop Scheduler", type="secondary", use_container_width=True):
                    st.session_state.scheduler_running = False
                    st.success("🛑 Scheduler stopped")
                    st.rerun()
        
        with col2:
            if st.button("🧪 Send Test Email", use_container_width=True):
                with st.spinner("Sending test email..."):
                    success = send_test_email()
                if success:
                    st.session_state.last_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success("✅ Test email sent successfully!")
                else:
                    st.error("❌ Failed to send test email")
        
        with col3:
            if st.button("🔄 Generate Preview", use_container_width=True):
                with st.spinner("Generating topic preview..."):
                    generator = DailyTopicGenerator()
                    topic = generator.generate_daily_topic()
                    description = generator.generate_topic_description(topic)
                    
                    st.session_state.preview_topic = topic
                    st.session_state.preview_description = description
                
                st.success("✅ Topic preview generated!")
    
    with col2:
        st.header("📧 Configuration")
        
        # Email settings
        st.subheader("Recipient Settings")
        current_recipient = os.getenv('DAILY_TOPIC_RECIPIENT', 'suharyaseen36@gmail.com')
        st.info(f"**Current recipient:** {current_recipient}")
        
        # Schedule settings
        st.subheader("Schedule Settings")
        st.info("**Current schedule:** Daily at 1:00 PM")
        
        # Manual topic generation preview
        if hasattr(st.session_state, 'preview_topic'):
            st.subheader("📝 Topic Preview")
            st.markdown(f"""
            <div class="topic-box">
                <h4>✨ {st.session_state.preview_topic}</h4>
                <p>{st.session_state.preview_description}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # System requirements
        st.subheader("🔧 Requirements")
        st.markdown("""
        **Required Environment Variables:**
        - `EMAIL_SENDER`: Your Gmail address
        - `EMAIL_PASSWORD`: Gmail app password
        - `GEMINI_API_KEY`: Google Gemini API key
        - `DAILY_TOPIC_RECIPIENT`: Recipient email
        """)
        
        # Check configuration
        st.subheader("✅ Configuration Check")
        env_vars = {
            "EMAIL_SENDER": os.getenv('EMAIL_SENDER'),
            "EMAIL_PASSWORD": os.getenv('EMAIL_PASSWORD'),
            "GEMINI_API_KEY": os.getenv('GEMINI_API_KEY'),
            "DAILY_TOPIC_RECIPIENT": os.getenv('DAILY_TOPIC_RECIPIENT')
        }
        
        for var, value in env_vars.items():
            if value:
                st.success(f"✅ {var}")
            else:
                st.error(f"❌ {var}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **How it works:**
    1. AI generates a new professional topic daily
    2. System sends formatted email at 1:00 PM
    3. You receive curated learning suggestions
    4. Continuous learning made automatic!
    """)

if __name__ == "__main__":
    main()