# app/styling.py

GOOGLE_FONTS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Questrial&family=Open+Sans&display=swap');
html, body, textarea, input, button, select, label {
    font-family: 'Open Sans', sans-serif !important;
    font-size: 0.9rem;
}
h1, h2, h3, h4, h5, h6 {font-family: 'Questrial', sans-serif !important; font-weight: 400;}
</style>
"""

GRADIENT_TITLE_CSS = """
<style>
@keyframes color-shift {
  0% { color: #3c66a4; }
  50% { color: #0fbce3; }
  100% { color: #3c66a4; }
}

.gradient-title {
  font-family: 'Questrial', sans-serif !important;
  font-size: 2.2rem !important;
  font-weight: 400 !important;
  text-align: left !important;
  margin-top: 0.5rem !important;
  margin-bottom: 1.5rem !important;
  color: #3c66a4 !important;
  animation: color-shift 3s ease-in-out infinite !important;
  display: block !important;
  visibility: visible !important;
}
</style>
"""

FADE_IN_CSS = """
<style>
/* Defines the fade-in animation. It animates opacity from 0 to 1
and optionally adds a slight upward translation for effect.
*/
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Targets the main content container in Streamlit's DOM 
and applies the half-second fade-in animation.
*/
.main .block-container {
    animation: fadeIn 0.5s ease-in-out;
}

/* Custom progress bar styling with EasyETFs brand color */
.stProgress > div > div > div > div {
    background-color: #ed1847 !important;
}

/* Progress bar track styling */
.stProgress > div > div > div {
    background-color: #f0f2f6 !important;
}

/* Custom info message styling with high-opacity red background */
.element-container .stAlert {
    background-color: rgba(237, 24, 71, 0.1) !important;
    border-left-color: #ed1847 !important;
}

/* Specific styling for info messages (progress updates) */
.element-container .stAlert[data-baseweb="notification"] {
    background-color: rgba(237, 24, 71, 0.1) !important;
    border-left-color: #ed1847 !important;
    color: #991b1b !important;
}

/* Custom button styling to ensure blue theme colors */
.stButton > button[kind="primary"] {
    background-color: #0fbce3 !important;
    border-color: #0fbce3 !important;
    color: white !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #3c66a4 !important;
    border-color: #3c66a4 !important;
    color: white !important;
}

.stButton > button[kind="primary"]:active,
.stButton > button[kind="primary"]:focus {
    background-color: #2a4a75 !important;
    border-color: #2a4a75 !important;
    color: white !important;
    box-shadow: 0 0 0 3px rgba(15, 188, 227, 0.25) !important;
}

/* Download button styling */
.stDownloadButton > button {
    background-color: #0fbce3 !important;
    border-color: #0fbce3 !important;
    color: white !important;
}

.stDownloadButton > button:hover {
    background-color: #3c66a4 !important;
    border-color: #3c66a4 !important;
    color: white !important;
}

/* Reduce top spacing/padding on all pages */
.main .block-container {
    padding-top: 1rem !important;
    max-width: 100% !important;
}

/* Reduce spacing around headers */
.stApp > header {
    height: 0 !important;
}

/* Minimize top margin on main content */
.element-container:first-child {
    margin-top: 0 !important;
}

/* Reduce margin on gradient titles */
.gradient-title {
    margin-top: 0 !important;
}
</style>
"""

FAVICON_INJECTION_CSS = """
<style>
/* Hidden container for favicon injection */
.favicon-injection {
    position: absolute;
    top: 0;
    left: 0;
    width: 0;
    height: 0;
    overflow: hidden;
    z-index: -1;
}
</style>
""" 