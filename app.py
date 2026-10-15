# ─────────────────────────────────────────────────────
# app.py — Universal Job Application Agent
# Streamlit Web App — runs in any browser
# ─────────────────────────────────────────────────────

import streamlit as st
import anthropic
import json
import time
import base64
import os

# ── Page config ───────────────────────────────────────
st.set_page_config(
    page_title="Job Application Agent",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 720px; margin: auto; }
    .stButton > button {
        width: 100%;
        background: #534AB7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 15px;
        font-weight: 500;
    }
    .stButton > button:hover { background: #3C3489; }
    .job-card {
        background: #f8f7ff;
        border: 1px solid #AFA9EC;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
    }
    .job-card h4 { color: #3C3489; margin: 0 0 6px 0; }
    .job-card p  { margin: 3px 0; font-size: 14px; color: #444; }
    .badge-a { background:#EAF3DE; color:#27500A; padding:2px 8px;
               border-radius:8px; font-size:12px; font-weight:500; }
    .badge-b { background:#E6F1FB; color:#0C447C; padding:2px 8px;
               border-radius:8px; font-size:12px; font-weight:500; }
    .badge-c { background:#FAEEDA; color:#633806; padding:2px 8px;
               border-radius:8px; font-size:12px; font-weight:500; }
    .success-box {
        background:#EAF3DE; border:1px solid #C0DD97;
        border-radius:8px; padding:12px 16px; margin:8px 0;
    }
    .warn-box {
        background:#FAEEDA; border:1px solid #DDB87A;
        border-radius:8px; padding:12px 16px; margin:8px 0;
    }
    .info-box {
        background:#EEEDFE; border:1px solid #AFA9EC;
        border-radius:8px; padding:12px 16px; margin:8px 0;
    }
    .step-label {
        background:#534AB7; color:white; border-radius:50%;
        width:26px; height:26px; display:inline-flex;
        align-items:center; justify-content:center;
        font-size:12px; font-weight:600; margin-right:8px;
    }
    .log-entry-applied { color:#27500A; font-weight:500; }
    .log-entry-skipped { color:#633806; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────
for key, default in {
    "page":          "home",
    "profile":       None,
    "api_key":       "",
    "log":           [],
    "applied":       0,
    "skipped":       0,
    "current_job":   None,
    "agent_running": False,
    "messages":      [],
    "jobs_queue":    [],
    "status":        "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ───────────────────────────────────────────
def go(page): st.session_state.page = page; st.rerun()

def tier(score):
    if score >= 80: return "A", "badge-a"
    if score >= 65: return "B", "badge-b"
    return "C", "badge-c"

def add_log(decision, title, company):
    st.session_state.log.append({
        "decision": decision,
        "title":    title,
        "company":  company,
        "time":     time.strftime("%H:%M")
    })
    if decision == "APPLIED":  st.session_state.applied  += 1
    if decision == "SKIPPED":  st.session_state.skipped  += 1

def call_ai(prompt, system=""):
    key = st.session_state.api_key
    if not key:
        return "ERROR: No API key provided."
    try:
        client = anthropic.Anthropic(api_key=key)
        kwargs = {"model":"claude-sonnet-4-6","max_tokens":1000,
                  "messages":[{"role":"user","content":prompt}]}
        if system: kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        return resp.content[0].text
    except Exception as e:
        return f"API Error: {str(e)}"

def profile_summary(p):
    return f"""
CANDIDATE: {p['name']}
Email: {p['email']} | Phone: {p['phone']}
Domain: {p['domain']} | Role: {p['target_role']}
Experience: {p['experience']} | Location: {p['location']}
CTC: {p['expected_ctc']} | Notice: {p['notice_period']}
Skills: {', '.join(p['skills'])}
Achievements: {'; '.join(p['achievements'])}
Education: {p.get('education','')}
"""

# ════════════════════════════════════════════════════════
#  PAGE: HOME
# ════════════════════════════════════════════════════════
if st.session_state.page == "home":
    st.markdown("## 🚀 Universal Job Application Agent")
    st.markdown("**Apply to jobs on any portal — for any person, any domain**")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🌐 Any Portal")
        st.caption("Naukri, LinkedIn, Indeed, Shine, Foundit")
    with col2:
        st.markdown("#### 🏢 Any Domain")
        st.caption("HR, IT, Finance, Marketing, Sales & more")
    with col3:
        st.markdown("#### ✅ You're in Control")
        st.caption("Y/N confirmation before every application")

    st.markdown("---")

    st.markdown("""
<div class="info-box">
<b>How it works:</b><br>
1️⃣ Enter your Anthropic API key<br>
2️⃣ Fill candidate profile (name, email, role, skills)<br>
3️⃣ Paste job descriptions from Naukri / LinkedIn<br>
4️⃣ Agent generates tailored cover letter + resume bullets<br>
5️⃣ You approve each application with one click<br>
6️⃣ Copy everything and apply in under 3 minutes per job
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
<div class="warn-box">
⚠️ <b>Note on Computer Use:</b> Fully automated browser control requires 
Claude Computer Use running on a local machine. This web app gives you 
AI-generated cover letters, resume bullets, and recruiter messages — 
you paste and submit on the portal yourself. Fastest safe approach.
</div>
""", unsafe_allow_html=True)

    st.markdown("")
    if st.button("Get Started →"):
        go("setup")

# ════════════════════════════════════════════════════════
#  PAGE: SETUP — API KEY + PROFILE
# ════════════════════════════════════════════════════════
elif st.session_state.page == "setup":
    st.markdown("## ⚙️ Setup")
    st.markdown("---")

    # ── API Key ───────────────────────────────────────
    st.markdown("#### 🔑 Step 1 — Anthropic API Key")
    st.caption("Get yours free at console.anthropic.com (add $5 credit)")
    api_key = st.text_input("Paste your API key here",
                             value=st.session_state.api_key,
                             type="password",
                             placeholder="sk-ant-...")
    if api_key: st.session_state.api_key = api_key

    if st.button("Test API Key"):
        if not api_key:
            st.error("Please enter an API key first.")
        else:
            with st.spinner("Testing..."):
                result = call_ai("Say: API key works!")
            if "Error" in result:
                st.error(f"❌ {result}")
            else:
                st.success("✅ API key is valid and working!")

    st.markdown("---")

    # ── Profile form ──────────────────────────────────
    st.markdown("#### 👤 Step 2 — Candidate Profile")

    with st.form("profile_form"):
        st.markdown("**Personal Details**")
        c1, c2 = st.columns(2)
        name    = c1.text_input("Full Name *", placeholder="e.g. Rahul Sharma")
        email   = c2.text_input("Email ID *",  placeholder="rahul@email.com")
        c3, c4  = st.columns(2)
        phone   = c3.text_input("Phone *",     placeholder="9876543210")
        password = c4.text_input("Portal Password *", type="password",
                                  help="Used to auto-login to the job portal")

        st.markdown("**Job Preferences**")
        c5, c6  = st.columns(2)
        domain  = c5.text_input("Job Domain *",
                                 placeholder="e.g. HR, IT, Finance, Marketing")
        role    = c6.text_input("Target Role *",
                                 placeholder="e.g. HRBP, Software Engineer")
        c7, c8  = st.columns(2)
        location = c7.text_input("Preferred Location *",
                                   placeholder="e.g. Noida, Remote, Mumbai")
        experience = c8.text_input("Years of Experience *",
                                    placeholder="e.g. 5 years")
        c9, c10 = st.columns(2)
        ctc     = c9.text_input("Expected CTC",  placeholder="e.g. 15-20 LPA")
        notice  = c10.text_input("Notice Period", placeholder="e.g. 30 days")
        education = st.text_input("Education",
                                   placeholder="e.g. MBA HRM – XYZ University (2020)")

        st.markdown("**Portal**")
        portal_choice = st.selectbox("Job Portal",
            ["Naukri.com", "LinkedIn.com", "Indeed.co.in",
             "Shine.com", "Foundit.in", "Other (enter below)"])
        portal_custom = st.text_input("Custom Portal URL (if Other selected)",
                                       placeholder="https://www.example.com")

        st.markdown("**Skills & Achievements**")
        skills_raw = st.text_area("Top Skills (comma separated) *",
            placeholder="HR Business Partnering, Keka HRMS, PMS, Power BI, Talent Acquisition",
            height=80)
        achievements_raw = st.text_area("Key Achievements (one per line) *",
            placeholder="Reduced attrition from 30% to 15%\nRecruited 2000+ employees\nImplemented Keka HRMS end-to-end",
            height=100)
        max_applies = st.slider("Max applications per session", 1, 20, 5)

        submitted = st.form_submit_button("Save Profile & Continue →")

    if submitted:
        errors = []
        if not name:     errors.append("Full Name")
        if not email:    errors.append("Email ID")
        if not phone:    errors.append("Phone")
        if not password: errors.append("Portal Password")
        if not domain:   errors.append("Job Domain")
        if not role:     errors.append("Target Role")
        if not location: errors.append("Preferred Location")
        if not experience: errors.append("Years of Experience")
        if not skills_raw: errors.append("Skills")
        if not achievements_raw: errors.append("Achievements")

        if errors:
            st.error(f"Please fill: {', '.join(errors)}")
        else:
            portals = {
                "Naukri.com":   "https://www.naukri.com",
                "LinkedIn.com": "https://www.linkedin.com",
                "Indeed.co.in": "https://www.indeed.co.in",
                "Shine.com":    "https://www.shine.com",
                "Foundit.in":   "https://www.foundit.in",
            }
            purl = portals.get(portal_choice, portal_custom)
            pname = portal_choice.split(".")[0] if portal_choice != "Other (enter below)" else "Custom"

            st.session_state.profile = {
                "name":         name,
                "email":        email,
                "password":     password,
                "phone":        phone,
                "domain":       domain,
                "target_role":  role,
                "location":     location,
                "experience":   experience,
                "expected_ctc": ctc,
                "notice_period": notice,
                "education":    education,
                "portal_url":   purl,
                "portal_name":  pname,
                "skills":       [s.strip() for s in skills_raw.split(",") if s.strip()],
                "achievements": [a.strip() for a in achievements_raw.splitlines() if a.strip()],
                "max_applies":  max_applies,
            }
            st.success("✅ Profile saved!")
            time.sleep(0.8)
            go("agent")

# ════════════════════════════════════════════════════════
#  PAGE: AGENT — PASTE JD + GENERATE + APPLY
# ════════════════════════════════════════════════════════
elif st.session_state.page == "agent":
    p = st.session_state.profile
    if not p:
        st.warning("Please complete setup first.")
        if st.button("Go to Setup"): go("setup")
        st.stop()

    # ── Top bar ───────────────────────────────────────
    st.markdown(f"## 🤖 Agent — {p['name']}")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Applied",  st.session_state.applied)
    c2.metric("Skipped",  st.session_state.skipped)
    c3.metric("In Log",   len(st.session_state.log))
    c4.metric("Limit",    p["max_applies"])

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Paste JD", "✍️ Cover Letter", "📊 Resume Bullets", "📁 Log"])

    # ════════════ TAB 1: PASTE JD ════════════
    with tab1:
        st.markdown("#### Paste any job description")
        st.caption("From Naukri, LinkedIn, Indeed or any portal")

        jd_company  = st.text_input("Company Name", placeholder="e.g. Infosys BPM")
        jd_role     = st.text_input("Role Title",   placeholder="e.g. HR Business Partner")
        jd_url      = st.text_input("Job URL (optional — paste from portal)",
                                     placeholder="https://www.naukri.com/...")
        jd_text     = st.text_area("Paste Full Job Description *",
                                    height=200,
                                    placeholder="Paste the complete JD here...")

        if st.button("🔍 Analyze JD & Generate All"):
            if not jd_text.strip():
                st.error("Please paste the job description.")
            elif not st.session_state.api_key:
                st.error("API key missing. Go to Setup.")
            else:
                with st.spinner("AI is analyzing the JD and generating everything..."):
                    prompt = f"""
Analyze this job description for {p['name']} and produce THREE sections.
Use EXACTLY these headings on their own lines:
MATCH ANALYSIS
COVER LETTER
LINKEDIN MESSAGE

Company: {jd_company or 'the company'}
Role: {jd_role or 'this role'}

JD:
{jd_text}

{profile_summary(p)}

MATCH ANALYSIS: Match score /100, top 3 strengths, top 2 gaps (3 lines total)
COVER LETTER: Under 260 words. Start "Dear Hiring Manager,". End with {p['email']} | {p['phone']}
LINKEDIN MESSAGE: Under 110 words. Friendly, specific to candidate's real achievements.
"""
                    result = call_ai(prompt)

                def extract(text, start, end):
                    s = text.find(start)
                    if s == -1: return text
                    s += len(start)
                    e = text.find(end, s) if end else -1
                    return text[s:e].strip() if e != -1 else text[s:].strip()

                ma = extract(result, "MATCH ANALYSIS", "COVER LETTER")
                cl = extract(result, "COVER LETTER",   "LINKEDIN MESSAGE")
                lm = extract(result, "LINKEDIN MESSAGE", "")

                st.session_state["last_ma"] = ma
                st.session_state["last_cl"] = cl
                st.session_state["last_lm"] = lm
                st.session_state["last_jd_company"] = jd_company
                st.session_state["last_jd_role"]    = jd_role
                st.session_state["last_jd_url"]     = jd_url

                st.markdown("---")

                # Match Analysis
                st.markdown("##### 📊 Match Analysis")
                st.info(ma)

                # Cover Letter
                st.markdown("##### ✉️ Cover Letter")
                st.text_area("Copy this cover letter:", value=cl, height=280,
                              key="cl_display")

                # LinkedIn Message
                st.markdown("##### 💼 LinkedIn Recruiter Message")
                st.text_area("Copy this message:", value=lm, height=140,
                              key="lm_display")

                # Job URL
                if jd_url:
                    st.markdown("##### 🔗 Apply Here")
                    st.markdown(f"[Open Job Portal → {jd_url}]({jd_url})")

                st.markdown("---")
                col_a, col_b = st.columns(2)
                if col_a.button("✅ Mark as Applied"):
                    add_log("APPLIED", jd_role or "Role", jd_company or "Company")
                    st.success(f"✓ Marked as Applied! Total: {st.session_state.applied}")
                if col_b.button("⏭ Skip this job"):
                    add_log("SKIPPED", jd_role or "Role", jd_company or "Company")
                    st.info("Skipped.")

    # ════════════ TAB 2: COVER LETTER ════════════
    with tab2:
        st.markdown("#### Generate a standalone cover letter")
        st.caption("For any role — without pasting the full JD")

        cl_company  = st.text_input("Company", key="cl_co",
                                     placeholder="e.g. Wipro")
        cl_role     = st.text_input("Role",    key="cl_rl",
                                     placeholder="e.g. Senior HRBP")
        cl_skills   = st.text_input("Key skills required (from JD)",
                                     key="cl_sk",
                                     placeholder="e.g. HRBP, OKR, PMS, Engagement")
        cl_tone     = st.selectbox("Tone", ["Professional", "Warm & Friendly",
                                             "Confident", "Concise"])

        if st.button("✍️ Generate Cover Letter"):
            if not cl_company or not cl_role:
                st.error("Enter company and role.")
            else:
                with st.spinner("Writing your cover letter..."):
                    prompt = f"""
Write a tailored cover letter for {p['name']} applying for "{cl_role}" at {cl_company}.
Required skills: {cl_skills}
Tone: {cl_tone}
{profile_summary(p)}
- Under 260 words
- Start: "Dear Hiring Manager,"
- Mention 2-3 specific achievements
- End with: {p['email']} | {p['phone']}
- No generic openers
"""
                    result = call_ai(prompt)
                st.text_area("Your Cover Letter:", value=result, height=320,
                              key="cl_result")

    # ════════════ TAB 3: RESUME BULLETS ════════════
    with tab3:
        st.markdown("#### ATS-Optimized Resume Bullets")
        st.caption("Rewrite your bullets to match any JD's keywords")

        rb_company = st.text_input("Company",  key="rb_co",
                                    placeholder="e.g. HCL Technologies")
        rb_role    = st.text_input("Role",     key="rb_rl",
                                    placeholder="e.g. HR Manager Operations")
        rb_skills  = st.text_input("Target keywords from JD",
                                    key="rb_sk",
                                    placeholder="e.g. HR Ops, Payroll, HRIS, Compliance")
        rb_count   = st.slider("Number of bullets", 3, 8, 5)

        if st.button("📊 Generate Resume Bullets"):
            if not rb_role:
                st.error("Enter the role name.")
            else:
                with st.spinner("Optimizing your resume bullets..."):
                    prompt = f"""
Write {rb_count} ATS-optimized resume bullet points for {p['name']}
applying for "{rb_role}" at {rb_company or 'the company'}.
Target keywords: {rb_skills}
{profile_summary(p)}
- Strong action verbs
- Real quantified achievements from candidate profile
- Each bullet starts with •
- ATS-friendly keywords woven naturally
- Each bullet 1-2 lines max
"""
                    result = call_ai(prompt)
                st.text_area("Your Resume Bullets:", value=result, height=280,
                              key="rb_result")

    # ════════════ TAB 4: LOG ════════════
    with tab4:
        st.markdown("#### Application Log")

        if not st.session_state.log:
            st.info("No applications logged yet. Use Paste JD tab to get started.")
        else:
            # Summary
            col1, col2 = st.columns(2)
            col1.success(f"✅ Applied: {st.session_state.applied}")
            col2.warning(f"⏭ Skipped: {st.session_state.skipped}")

            st.markdown("---")
            for i, entry in enumerate(reversed(st.session_state.log), 1):
                icon = "✅" if entry["decision"] == "APPLIED" else "⏭"
                css  = "log-entry-applied" if entry["decision"] == "APPLIED" else "log-entry-skipped"
                st.markdown(
                    f'<p class="{css}">{icon} <b>{entry["title"]}</b> @ {entry["company"]} — {entry["time"]}</p>',
                    unsafe_allow_html=True)

            # Download log
            st.markdown("---")
            log_text = f"JOB APPLICATION LOG — {p['name']}\n"
            log_text += f"Applied: {st.session_state.applied} | Skipped: {st.session_state.skipped}\n"
            log_text += "="*40 + "\n"
            for e in st.session_state.log:
                log_text += f"[{e['decision']}] {e['title']} @ {e['company']} ({e['time']})\n"

            st.download_button(
                label="⬇️ Download Log as .txt",
                data=log_text,
                file_name=f"job_log_{p['name'].replace(' ','_')}.txt",
                mime="text/plain"
            )

            if st.button("🗑 Clear Log"):
                st.session_state.log      = []
                st.session_state.applied  = 0
                st.session_state.skipped  = 0
                st.rerun()

    st.markdown("---")
    col_s, col_p = st.columns(2)
    if col_s.button("⚙️ Edit Profile"):  go("setup")
    if col_p.button("🏠 Home"):          go("home")

# ════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════
st.markdown("---")
st.caption("Universal Job Application Agent · Built with Claude AI · For personal/testing use only")
