═══════════════════════════════════════════════════════
  UNIVERSAL JOB APPLICATION AGENT — WEB APP
  Deploy once, use from any laptop, any device
═══════════════════════════════════════════════════════

OPTION A: RUN LOCALLY (your own laptop)
─────────────────────────────────────────
Works instantly on any laptop with Python.

1. Install Python from python.org

2. Open Command Prompt in this folder and run:
   pip install streamlit anthropic python-dotenv

3. Run the app:
   streamlit run app.py

4. Browser opens automatically at:
   http://localhost:8501

Share with friends on same network:
   http://YOUR_IP:8501
   (find your IP: run  ipconfig  in Command Prompt)

─────────────────────────────────────────────────────

OPTION B: DEPLOY FREE ON STREAMLIT CLOUD
──────────────────────────────────────────
Anyone in the world can use it via a link.
No installation needed on their device.

Step 1: Create free GitHub account
  → github.com → Sign up

Step 2: Create new repository
  → Click "New" → Name it "job-agent"
  → Upload all files from this folder

Step 3: Deploy on Streamlit Cloud
  → Go to share.streamlit.io
  → Sign in with GitHub
  → Click "New app"
  → Select your repository
  → Set main file: app.py
  → Click Deploy

Step 4: Share the link!
  You get a URL like:
  https://yourname-job-agent.streamlit.app
  
  Anyone opens this link → fills their details
  → agent works → no installation needed

─────────────────────────────────────────────────────

OPTION C: DEPLOY ON RENDER (free, always online)
──────────────────────────────────────────────────
Step 1: Push code to GitHub (same as Option B Step 1-2)

Step 2: Go to render.com → New Web Service
  → Connect GitHub repo
  → Build command: pip install -r requirements.txt
  → Start command: streamlit run app.py --server.port $PORT
  → Deploy

─────────────────────────────────────────────────────

WHAT USERS NEED
────────────────
Just a browser and an Anthropic API key.
They enter their own API key in the app.
No installation. No Python. No setup.

HOW TO GET API KEY
───────────────────
console.anthropic.com → Sign up → Billing → Add $5
API Keys → Create → Copy → Paste in app

═══════════════════════════════════════════════════════
