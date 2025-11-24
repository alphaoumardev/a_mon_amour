import random
import datetime
import streamlit as st

st.set_page_config(
    page_title="AIR Platform Prototype",
    page_icon="🧭",
    layout="wide",
)

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "intake_data" not in st.session_state:
    st.session_state.intake_data = {}
if "prescription" not in st.session_state:
    st.session_state.prescription = {}
if "step" not in st.session_state:
    st.session_state.step = "Onboarding"

st.title("Allies in Recovery – AIR Platform Prototype")
st.caption(
    "This prototype walks through onboarding, a tailored prescription, and service experiences based on the design report."
)

sidebar_steps = ["Onboarding", "Prescription", "Services"]
st.session_state.step = st.sidebar.radio("Navigate", sidebar_steps, index=sidebar_steps.index(st.session_state.step))

# -------------------- Onboarding --------------------
if st.session_state.step == "Onboarding":
    st.header("1) Onboarding")
    st.subheader("Account creation")
    with st.form("register"):
        email = st.text_input("Email", placeholder="family@example.com")
        password = st.text_input("Password", type="password")
        relationship = st.selectbox(
            "Relationship to loved one",
            ["Parent", "Spouse/Partner", "Sibling", "Friend", "Other"],
        )
        consent = st.checkbox("I consent to HIPAA-compliant data use for tailoring.")
        submitted = st.form_submit_button("Create account")
    if submitted and consent and email and password:
        st.session_state.user_profile = {
            "email": email,
            "relationship": relationship,
            "consent": consent,
            "created_at": datetime.datetime.now().isoformat(),
        }
        st.success("Account created. Continue to intake.")
        st.session_state.step = "Onboarding"
    elif submitted:
        st.error("Please complete all fields and consent to continue.")

    st.divider()
    st.subheader("Family–patient intake")
    with st.form("intake"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Your age", min_value=16, max_value=120, value=35)
            gender = st.selectbox("Gender identity", ["Woman", "Man", "Non-binary", "Prefer not to say"])
            household = st.text_input("Household composition", placeholder="You, partner, two children")
            availability = st.slider("Availability (hours/week)", 1, 20, 5)
            digital = st.select_slider("Digital literacy", options=["Low", "Medium", "High"], value="Medium")
        with col2:
            substances = st.multiselect(
                "Substance(s) used",
                ["Alcohol", "Opioids", "Stimulants", "Cannabis", "Other"],
                default=["Alcohol"],
            )
            stage = st.select_slider(
                "Stage of change",
                options=["Pre-contemplation", "Contemplation", "Preparation", "Action", "Maintenance"],
                value="Contemplation",
            )
            conflicts = st.slider("Conflict frequency (0=rare, 10=often)", 0, 10, 4)
            stress = st.slider("Stress level (0=low, 10=high)", 0, 10, 6)
            safety = st.selectbox(
                "Safety concerns",
                ["None", "Mental health concerns", "Legal issues", "Overdose history", "Violence"],
                index=0,
            )
        notes = st.text_area("Describe recent challenges", height=100)
        intake_submit = st.form_submit_button("Save intake")

    if intake_submit:
        st.session_state.intake_data = {
            "age": age,
            "gender": gender,
            "household": household,
            "availability": availability,
            "digital": digital,
            "substances": substances,
            "stage": stage,
            "conflicts": conflicts,
            "stress": stress,
            "safety": safety,
            "notes": notes,
        }
        st.success("Intake saved. Continue to confirmation.")

    if st.session_state.intake_data:
        st.divider()
        st.subheader("Confirmation & baseline assessment")
        st.write(st.session_state.intake_data)
        baseline = 100 - (st.session_state.intake_data.get("stress", 0) * 4 + st.session_state.intake_data.get("conflicts", 0) * 2)
        baseline = max(10, min(95, baseline))
        st.metric("Baseline Family Support Score", f"{baseline}/100")
        st.info("This score tracks stress and readiness. Proceed to Prescription for tailored guidance.")
        st.session_state.step = "Prescription"

# -------------------- Prescription --------------------
elif st.session_state.step == "Prescription":
    st.header("2) Prescription")
    if not st.session_state.intake_data:
        st.warning("Complete onboarding first.")
    else:
        intake = st.session_state.intake_data
        st.write("Using intake data to recommend a tailored path.")

        def compute_risk(intake_data):
            base = intake_data.get("stress", 0) + intake_data.get("conflicts", 0)
            if "Opioids" in intake_data.get("substances", []):
                base += 4
            if intake_data.get("safety") in {"Overdose history", "Violence"}:
                base += 5
            return min(10, max(0, int(base / 2)))

        risk_score = compute_risk(intake)
        module_pool = [
            "Understanding Addiction",
            "Communication Skills",
            "Self-care & Stress Management",
            "Positive Reinforcement",
            "Setting Boundaries",
            "Engagement & Treatment Entry",
        ]
        prioritized = sorted(
            module_pool,
            key=lambda m: (
                0 if m == "Communication Skills" and intake.get("conflicts", 0) > 5 else 1,
                0 if m == "Self-care & Stress Management" and intake.get("stress", 0) > 5 else 1,
                random.random(),
            ),
        )
        services = [
            "Weekly live group (America/Toronto)",
            "Virtual room role-play twice per month",
            "Mindfulness podcast series",
            "Chatbot check-ins aligned to your modules",
            "Resource library bookmarks"
        ]

        st.metric("Risk score (0-10)", risk_score)
        st.progress(risk_score / 10, text="Higher values show more frequent alerts.")

        st.subheader("Personalised module sequence")
        for i, module in enumerate(prioritized, start=1):
            st.markdown(f"**{i}. {module}** – est. 20–30 minutes")

        st.subheader("Service plan")
        st.write("Tailored recommendations emphasize stress relief and communication practice.")
        st.write(services)

        st.subheader("Explainability")
        st.write(
            "High stress and conflict prioritized communication and self-care modules. Safety concerns trigger human review before finalizing the plan."
        )

        st.session_state.prescription = {
            "risk": risk_score,
            "modules": prioritized,
            "services": services,
        }
        st.session_state.step = "Services"

# -------------------- Services --------------------
elif st.session_state.step == "Services":
    st.header("3) Services")
    if not st.session_state.prescription:
        st.warning("Generate a prescription first.")
    else:
        modules = st.session_state.prescription.get("modules", [])
        services = st.session_state.prescription.get("services", [])

        tabs = st.tabs(["Virtual room", "Chatbot", "CRAFT modules", "Podcasts & blogs", "Live groups"])

        with tabs[0]:
            st.subheader("Virtual room scenario")
            scenario = st.selectbox(
                "Choose a scenario",
                [
                    "Dealing with denial",
                    "Encouraging treatment entry",
                    "Practicing positive reinforcement",
                ],
            )
            st.write("Clinician agent coaching cue:")
            st.info("Use reflective listening and reward healthy behavior.")
            user_input = st.text_input("Your response to the patient agent")
            if st.button("Get feedback", key="vr_feedback"):
                st.success(
                    "Great use of empathy! Try adding a small reward when your loved one engages in healthy activities."
                )

        with tabs[1]:
            st.subheader("Always-available chatbot")
            question = st.text_input("Ask a question")
            if st.button("Send", key="chatbot"):
                st.write(
                    "Reminder: acknowledge small wins, keep boundaries clear, and follow your next module: "
                    f"{modules[1] if len(modules) > 1 else modules[0]}"
                )
            st.warning("Safety: messages about self-harm or violence trigger a human follow-up.")

        with tabs[2]:
            st.subheader("CRAFT modules")
            for module in modules:
                st.markdown(f"- {module} – interactive lesson with exercises and knowledge checks")
            st.progress(0.35, text="2 of 6 modules complete")

        with tabs[3]:
            st.subheader("Podcasts & blogs")
            st.write("Curated picks based on your profile:")
            st.markdown("- Mindfulness moments (podcast)\n- Setting healthy boundaries (blog)\n- Reinforcing recovery behaviors (blog)")

        with tabs[4]:
            st.subheader("Live groups")
            st.write("Join weekly sessions guided by clinicians.")
            slot = st.selectbox("Choose a time (America/Toronto)", ["Tuesday 6 PM", "Thursday 12 PM", "Saturday 10 AM"])
            st.button("Reserve spot", key="reserve")
            st.info(f"Current plan: {services[0] if services else 'One live group per week'}")
