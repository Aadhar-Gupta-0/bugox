"""Streamlit frontend. All analysis runs offline, with no cloud tokens."""
import streamlit as st
from bugox import diagnose

st.set_page_config(page_title="bugox · Debugging Lab", page_icon="🐞", layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#0c1729,#0f2534);color:#eaf6f3}
.block-container{max-width:1100px;padding-top:3rem}
h1{letter-spacing:-.05em}
div[data-testid="stMetric"]{background:#193446;border-radius:14px;padding:16px}
</style>
""", unsafe_allow_html=True)
st.caption("BUGOX / LOCAL DEBUGGING LAB")
st.title("Make error messages understandable.")
st.write("Paste a Python traceback or a JavaScript error. Get a clear, evidence-based next step without sending your code to a third party.")

col, result = st.columns([1, 1], gap="large")
sample = """Traceback (most recent call last):
  File "example.py", line 4, in <module>
    print(total)
NameError: name 'total' is not defined"""
with col:
    st.subheader("Your error")
    raw = st.text_area("Paste traceback", value=sample, height=240, max_chars=32768)
    st.caption("No code execution, telemetry, accounts, or paid API required.")
    analyze = st.button("Analyze locally", type="primary", use_container_width=True)
with result:
    st.subheader("Diagnostic")
    if analyze:
        try:
            output = diagnose(raw)
            st.success(output.title)
            st.write(output.explanation)
            st.code(output.matched_line, language="text")
            if output.line_number:
                st.caption(f"Reported stack line: {output.line_number}")
            st.caption("Heuristic guidance; confirm against your actual code and environment.")
            with st.expander("Machine-readable details"):
                st.json(output.to_dict())
        except ValueError as error:
            st.error(str(error))
    else:
        st.info("Choose Analyze locally to see a diagnosis.")
