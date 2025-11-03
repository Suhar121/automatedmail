# daily_scheduler.py
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import google.generativeai as genai
import schedule
import time
import threading
from datetime import datetime
import random

load_dotenv()

class DailyTopicGenerator:
    def __init__(self):
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.recipient_email = os.getenv('DAILY_TOPIC_RECIPIENT', 'suharyaseen36@gmail.com')
        
        # Initialize Gemini AI
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
    
    def generate_daily_topic(self):
        """Generate an interesting topic for the day"""
        if not self.model:
            return self._fallback_topic()
        
        try:
            prompt = """
            Generate an interesting, engaging topic for professional development or learning. 
            The topic should be:
            - Relevant for personal or professional growth
            - Suitable for research or exploration
            - Current and trending in 2024
            - Broad enough for deep exploration but specific enough to be actionable
            
            Return ONLY the topic name, nothing else.
            """
            
            response = self.model.generate_content(prompt)
            topic = response.text.strip()
            
            # Clean up the response
            topic = topic.replace('"', '').replace("'", "").strip()
            return topic
            
        except Exception as e:
            print(f"AI topic generation failed: {e}")
            return self._fallback_topic()
    
    def _fallback_topic(self):
        """Fallback topics if AI is not available"""
        topics = [
            "Artificial Intelligence in Healthcare",
            "Sustainable Technology Solutions",
            "Remote Work Best Practices in 2024",
            "Blockchain Beyond Cryptocurrency",
            "Cybersecurity Trends for Small Businesses",
            "The Future of Renewable Energy",
            "Mental Health in the Digital Age",
            "Space Technology and Commercialization",
            "Quantum Computing Applications",
            "Digital Marketing Strategies for 2024",
            "Climate Change and Technology Solutions",
            "The Metaverse and Virtual Reality",
            "Bioengineering and Medical Advancements",
            "5G and IoT Integration",
            "Sustainable Agriculture Technology"
        ]
        return random.choice(topics)
    
    def generate_topic_description(self, topic):
        """Generate a brief description for the topic"""
        if not self.model:
            return f"Explore the latest developments and insights about {topic}."
        
        try:
            prompt = f"""
            Write a brief, engaging description (2-3 sentences) about the topic: {topic}
            Make it inspiring and encourage research/learning.
            Keep it professional and informative.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception:
            return f"Explore the latest developments and insights about {topic}. This topic offers great opportunities for learning and professional growth."
    
    def send_daily_topic_email(self):
        """Send daily topic email"""
        try:
            # Generate topic and description
            topic = self.generate_daily_topic()
            description = self.generate_topic_description(topic)
            
            # Create email content
            subject = f"📚 Your Daily Learning Topic: {topic}"
            
            email_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .topic {{ font-size: 24px; font-weight: bold; color: #333; margin: 20px 0; }}
                    .description {{ font-size: 16px; color: #666; margin: 15px 0; }}
                    .cta {{ background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                    .footer {{ background: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎯 Daily Learning Topic</h1>
                    <p>Expand your knowledge every day</p>
                </div>
                
                <div class="content">
                    <div class="topic">✨ {topic}</div>
                    <div class="description">{description}</div>
                    
                    <p><strong>Why explore this topic today?</strong></p>
                    <ul>
                        <li>Stay updated with current trends</li>
                        <li>Enhance your professional skills</li>
                        <li>Discover new opportunities</li>
                        <li>Boost your creativity and innovation</li>
                    </ul>
                    
                    <p><strong>Suggested activities:</strong></p>
                    <ul>
                        <li>Research the latest developments</li>
                        <li>Read related articles or papers</li>
                        <li>Discuss with colleagues</li>
                        <li>Apply concepts to your work</li>
                    </ul>
                    
                    <p>Happy learning! 🚀</p>
                </div>
                
                <div class="footer">
                    <p>This daily topic was generated automatically by your AI Learning Assistant.</p>
                    <p>You're receiving this email because you subscribed to daily learning topics.</p>
                </div>
            </body>
            </html>
            """
            
            # Send email
            success = self._send_email(subject, email_content, is_html=True)
            
            if success:
                print(f"✅ Daily topic email sent at {datetime.now()}: {topic}")
                return True
            else:
                print(f"❌ Failed to send daily topic email")
                return False
                
        except Exception as e:
            print(f"❌ Error sending daily topic: {e}")
            return False
    
    def _send_email(self, subject, content, is_html=False):
        """Send email with the given content"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(content, 'html'))
            else:
                msg.attach(MIMEText(content, 'plain'))
            
            # Create server connection
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email error: {e}")
            return False

class Scheduler:
    def __init__(self):
        self.topic_generator = DailyTopicGenerator()
        self.running = False
    
    def schedule_daily_email(self):
        """Schedule the daily email for 1:00 PM"""
        # Schedule for 1:00 PM every day
        schedule.every().day.at("23:50:00").do(self._send_scheduled_email)
        
        print("🕐 Daily topic scheduler started...")
        print("📧 Emails scheduled for 1:00 PM daily")
        print("⏰ Next run:", schedule.next_run())
    
    def _send_scheduled_email(self):
        """Send the scheduled daily email"""
        print(f"🕐 Sending scheduled email at {datetime.now()}")
        self.topic_generator.send_daily_topic_email()
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        print("✅ Scheduler started successfully!")
        print("📧 Daily topics will be sent at 1:00 PM")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        print("🛑 Scheduler stopped")

# Utility functions
def send_test_email():
    """Send a test email immediately"""
    generator = DailyTopicGenerator()
    print("🧪 Sending test email...")
    success = generator.send_daily_topic_email()
    if success:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email")
    return success

def start_daily_scheduler():
    """Start the daily scheduler"""
    scheduler = Scheduler()
    scheduler.schedule_daily_email()
    scheduler.start_scheduler()
    return scheduler

if __name__ == "__main__":
    print("🚀 Starting Daily Topic Scheduler...")
    
    # Start the scheduler
    scheduler = start_daily_scheduler()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Stopping scheduler...")
        scheduler.stop_scheduler()