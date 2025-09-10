# app/styling.py
"""
Smart Instrument Finder - Styling and CSS
Professional styling with gradient text, animations, and modern UI elements.
Color Palette: #ed1847 (primary red) with complementary shades and tints.
"""

# Color Palette based on #ed1847 with orange secondary
RED_PALETTE = {
    'primary': '#ed1847',        # Main brand color
    'dark': '#b91540',          # Darker shade for hover states
    'darker': '#7f1d1d',        # Darkest shade for active states
    'light': '#f87171',         # Light shade for accents
    'lighter': '#fef2f2',       # Very light for backgrounds
    'ultra_light': '#fefefe',   # Ultra light for subtle backgrounds
    'text_dark': '#4a4a4a',     # Dark text on light backgrounds (consistent with user requirement)
    'text_medium': '#4a4a4a',   # Medium text color (consistent with user requirement)
    'border': '#fca5a5',        # Light border color
    'shadow': 'rgba(237, 24, 71, 0.25)'  # Shadow color with transparency
}

# Orange Secondary Color Palette
ORANGE_PALETTE = {
    'primary': '#f4942a',        # Secondary orange color
    'light': '#fed7aa',          # Light orange for backgrounds
    'lighter': '#fef3e2',        # Very light orange for subtle backgrounds
    'ultra_light': '#fffbf5',    # Ultra light orange
    'text': '#4a4a4a',           # Text color (changed to consistent gray)
    'border': '#fdba74',         # Light orange border
    'shadow': 'rgba(244, 148, 42, 0.25)'  # Orange shadow with transparency
}

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
  0% { color: #4a4a4a; }
  25% { color: #5a5a5a; }
  50% { color: #6a6a6a; }
  75% { color: #5a5a5a; }
  100% { color: #4a4a4a; }
}

.gradient-title {
  font-family: 'Questrial', sans-serif !important;
  font-size: 2.2rem !important;
  font-weight: 400 !important;
  text-align: left !important;
  margin-top: 0.5rem !important;
  margin-bottom: 1.5rem !important;
  color: #4a4a4a !important;
  animation: color-shift 4s ease-in-out infinite !important;
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

/* Custom progress bar styling with brand color */
.stProgress > div > div > div > div {
    background-color: #ed1847 !important;
}

/* Progress bar track styling */
.stProgress > div > div > div {
    background-color: #fef2f2 !important;
}

/* Custom info message styling with light orange background */
.element-container .stAlert {
    background-color: rgba(244, 148, 42, 0.08) !important;
    border-left-color: #f4942a !important;
    border-radius: 8px !important;
}

/* Specific styling for info messages (progress updates) */
.element-container .stAlert[data-baseweb="notification"] {
    background-color: rgba(244, 148, 42, 0.08) !important;
    border-left-color: #f4942a !important;
    color: #4a4a4a !important;
    border-radius: 8px !important;
}

/* Custom button styling with red theme colors */
.stButton > button[kind="primary"] {
    background-color: #ed1847 !important;
    border-color: #ed1847 !important;
    color: white !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #b91540 !important;
    border-color: #b91540 !important;
    color: white !important;
}

.stButton > button[kind="primary"]:active,
.stButton > button[kind="primary"]:focus {
    background-color: #7f1d1d !important;
    border-color: #7f1d1d !important;
    color: white !important;
    box-shadow: 0 0 0 3px rgba(237, 24, 71, 0.25) !important;
}

/* Download button styling */
.stDownloadButton > button {
    background-color: #ed1847 !important;
    border-color: #ed1847 !important;
    color: white !important;
}

.stDownloadButton > button:hover {
    background-color: #b91540 !important;
    border-color: #b91540 !important;
    color: white !important;
}

/* Comprehensive top spacing removal - following working example pattern */
.main .block-container {
    padding-top: 0.25rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* Remove Streamlit header completely */
.stApp > header {
    height: 0 !important;
    display: none !important;
}

/* Remove all top margins from first elements */
.element-container:first-child,
.element-container:first-child > div,
.element-container:first-child > div > div {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Remove all top margins from gradient titles */
.gradient-title {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Remove top spacing from main content area */
[data-testid="stMain"] {
    padding-top: 0 !important;
}

[data-testid="stMain"] > div {
    padding-top: 0 !important;
}

/* Remove top spacing from the main container */
.main {
    padding-top: 0 !important;
}

/* Ensure the first element in main has no top spacing */
.main .block-container > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Target app view container */
[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
}

/* Getting Started Card Hover Effects */
.getting-started-card {
    transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    cursor: default !important;
}

.getting-started-card:hover {
    transform: translateY(-3px) !important;
    box-shadow: 
        0 8px 25px rgba(237, 24, 71, 0.2),
        0 0 20px rgba(237, 24, 71, 0.3),
        0 0 40px rgba(237, 24, 71, 0.1),
        0 2px 10px rgba(237, 24, 71, 0.1) !important;
}

/* Nested warning card hover effect with subtle orange glow */
.getting-started-card:hover .progress-warning {
    box-shadow: 
        0 3px 12px rgba(255, 152, 0, 0.2),
        0 0 15px rgba(255, 152, 0, 0.15) !important;
}

/* Smooth transitions for all interactive elements */
.getting-started-card * {
    transition: color 0.3s ease !important;
}

/* Reusable callouts aligned with Getting Started warning */
.callout-warning {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%) !important;
    padding: 1rem !important;
    border-radius: 10px !important;
    border-left: 3px solid #ff9800 !important;
    margin: 0.5rem 0 1rem 0 !important;
    box-shadow: 0 1px 5px rgba(255, 152, 0, 0.1) !important;
}

.callout-warning h4,
.callout-warning p,
.callout-warning li {
    color: #4a4a4a !important;
}

.callout-warning:hover {
    box-shadow: 0 3px 12px rgba(255, 152, 0, 0.15) !important;
}

.callout-info {
    background: linear-gradient(135deg, #fefefe 0%, #fef2f2 100%) !important;
    padding: 1rem !important;
    border-radius: 10px !important;
    border-left: 3px solid #ed1847 !important;
    margin: 0.5rem 0 1rem 0 !important;
    box-shadow: 0 1px 5px rgba(237, 24, 71, 0.1) !important;
}

.callout-info h4,
.callout-info p,
.callout-info li {
    color: #4a4a4a !important;
}

/* Enhanced transition timing for nested warning card */
.progress-warning {
    transition: box-shadow 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}

/* Banner styling */
.banner-container {
    margin-bottom: 2rem !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(237, 24, 71, 0.1) !important;
}

.banner-image {
    width: 100% !important;
    height: auto !important;
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Enhanced UI/UX Improvements */

/* Improved button interactions with subtle animations */
.stButton > button {
    transition: all 0.2s ease-in-out !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(237, 24, 71, 0.15) !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(237, 24, 71, 0.15) !important;
}

/* Enhanced input focus states for better accessibility */
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div:focus-within {
    outline: none !important;
    border-color: #ed1847 !important;
    box-shadow: 0 0 0 3px rgba(237, 24, 71, 0.1) !important;
    transition: all 0.2s ease-in-out !important;
}

/* Improved card styling for better visual hierarchy */
.stContainer {
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

/* Enhanced metric cards */
.stMetric {
    background: linear-gradient(135deg, #fefefe 0%, #fef2f2 100%) !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    border: 1px solid rgba(237, 24, 71, 0.1) !important;
    transition: all 0.2s ease-in-out !important;
}

.stMetric:hover {
    box-shadow: 0 4px 12px rgba(237, 24, 71, 0.1) !important;
    transform: translateY(-1px) !important;
}

/* Improved expander styling */
.streamlit-expanderHeader {
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s ease-in-out !important;
}

.streamlit-expanderHeader:hover {
    background-color: rgba(237, 24, 71, 0.05) !important;
}

/* Better spacing for columns */
.element-container .stColumn {
    transition: all 0.2s ease-in-out !important;
}

.element-container .stColumn:hover {
    box-shadow: 0 2px 8px rgba(237, 24, 71, 0.08) !important;
    transform: translateY(-1px) !important;
}

/* Enhanced loading states */
.stSpinner > div {
    border-color: #ed1847 #fef2f2 #fef2f2 #ed1847 !important;
}

/* Improved table styling */
.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden !important;
    border: 1px solid rgba(237, 24, 71, 0.1) !important;
}

/* Better alert styling hierarchy */
.stAlert {
    border-radius: 8px !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
}

/* Enhanced selection controls */
.stRadio > div {
    background: rgba(254, 242, 242, 0.3) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}

.stCheckbox {
    transition: all 0.2s ease-in-out !important;
}

.stCheckbox:hover {
    transform: scale(1.02) !important;
}

/* Improved visual feedback for interactive elements */
.stSelectbox:hover,
.stTextInput:hover,
.stTextArea:hover {
    transform: translateY(-1px) !important;
    transition: all 0.2s ease-in-out !important;
}

/* Enhanced sidebar interactions */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    margin-bottom: 0.5rem !important;
}

/* Better visual hierarchy for headers */
h1, h2, h3 {
    letter-spacing: -0.5px !important;
    line-height: 1.2 !important;
}

/* Improved code blocks */
.stCode {
    border-radius: 6px !important;
    border: 1px solid rgba(237, 24, 71, 0.1) !important;
}

/* Enhanced accessibility focus indicators */
*:focus {
    outline: 2px solid #ed1847 !important;
    outline-offset: 2px !important;
}

/* Remove focus outline for mouse users, keep for keyboard users */
.js-focus-visible *:focus:not(.focus-visible) {
    outline: none !important;
}

/* Consistent spacing and alignment */
.main .block-container > div:first-child {
    padding-top: 1rem !important;
}

/* Improved responsive design elements */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .stButton > button,
    .stDownloadButton > button {
        width: 100% !important;
    }
}

/* Feedback Component - Simple dropdown styling integrated with project theme */
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

# Enhanced styling for user onboarding sections
ONBOARDING_SECTION_CSS = """
<style>
.onboarding-step {
    background: linear-gradient(135deg, #fefefe 0%, #fef2f2 100%);
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid #ed1847;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(237, 24, 71, 0.1);
}

.step-header {
    color: #4a4a4a;
    font-family: 'Questrial', sans-serif;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.step-description {
    color: #4a4a4a;
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 1rem;
}

.wallet-context-info {
    background: rgba(237, 24, 71, 0.05);
    border: 1px solid rgba(237, 24, 71, 0.2);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}

/* Streamlit Sidebar Styling - Let config.toml handle most theming */
[data-testid="stSidebar"] {
    background-color: #f5f6f8 !important;
}

[data-testid="stSidebar"] > div {
    background-color: #f5f6f8 !important;
}

/* Sidebar content styling - simplified */
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2 {
    color: #4a4a4a !important;
}

/* Keep ALL h3 headings white in sidebar (Search Stats, Your Portfolio) */
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .element-container .stMarkdown h3 {
    color: white !important;
}

/* Keep "Recent Selections:" bold text white - Higher specificity */
[data-testid="stSidebar"] .element-container .stMarkdown strong,
[data-testid="stSidebar"] .stMarkdown strong,
[data-testid="stSidebar"] .element-container .stMarkdown b,
[data-testid="stSidebar"] .stMarkdown b {
    color: white !important;
}

/* Fix white text visibility issues in sidebar */
/* Metric labels and values */
[data-testid="stSidebar"] .stMetric label,
[data-testid="stSidebar"] .stMetric div,
[data-testid="stSidebar"] .stMetric p,
[data-testid="stSidebar"] .stMetric span {
    color: #4a4a4a !important;
}

/* Metric value styling specifically */
[data-testid="stSidebar"] [data-testid="metric-value"] {
    color: #4a4a4a !important;
}

/* Metric label styling specifically */
[data-testid="stSidebar"] [data-testid="metric-label"] {
    color: #4a4a4a !important;
}

/* Caption text in sidebar */
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] .caption,
[data-testid="stSidebar"] small {
    color: #4a4a4a !important;
}

/* Button text in sidebar */
[data-testid="stSidebar"] .stButton > button {
    color: #4a4a4a !important;
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
}

/* Secondary button styling in sidebar */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    color: #4a4a4a !important;
    background-color: #f8f9fa !important;
    border-color: #dee2e6 !important;
}

/* All text elements in sidebar */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #4a4a4a !important;
}

/* Comprehensive metric styling for sidebar */
[data-testid="stSidebar"] [data-testid="stMetricValue"] > div,
[data-testid="stSidebar"] [data-testid="stMetricLabel"] > div,
[data-testid="stSidebar"] .metric-container,
[data-testid="stSidebar"] .metric-container * {
    color: #4a4a4a !important;
}

/* Add top padding to metrics in columns (Search Stats section) */
[data-testid="stSidebar"] .stColumn .stMetric {
    padding-top: 0.5rem !important;
}

/* Remove extra padding from single metrics (Portfolio section) */
[data-testid="stSidebar"] .element-container:not(.stColumn) .stMetric {
    padding-top: 0rem !important;
}

/* Target Streamlit's internal metric structure */
[data-testid="stSidebar"] .stMetric > div > div,
[data-testid="stSidebar"] .stMetric > div > div > div {
    color: #4a4a4a !important;
}

/* Ensure remove buttons are visible */
[data-testid="stSidebar"] button[kind="secondary"],
[data-testid="stSidebar"] .stButton > button[data-baseweb="button"][kind="secondary"] {
    color: #4a4a4a !important;
    background-color: #ffffff !important;
    border: 1px solid #dee2e6 !important;
}

/* Hover states for sidebar buttons */
[data-testid="stSidebar"] .stButton > button:hover {
    color: #2d3748 !important;
    background-color: #f7fafc !important;
    border-color: #cbd5e0 !important;
}

/* Force text color for specific sidebar text elements - but exclude headings, metrics, and alerts */
[data-testid="stSidebar"] .element-container p:not(.stMetric *):not(.stAlert *),
[data-testid="stSidebar"] .element-container div:not(.stMetric):not(.stMetric *):not(.stAlert):not(.stAlert *):not(h1):not(h2):not(h3):not(strong):not(b),
[data-testid="stSidebar"] .element-container span:not(.stMetric *):not(.stAlert *):not(strong):not(b) {
    color: #4a4a4a !important;
}

/* Ensure headings and bold text stay white - final override */
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .element-container h3,
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] .stMarkdown strong,
[data-testid="stSidebar"] .element-container strong,
[data-testid="stSidebar"] b,
[data-testid="stSidebar"] .stMarkdown b,
[data-testid="stSidebar"] .element-container b {
    color: white !important;
}

/* AGGRESSIVE: Force white text for info messages in sidebar */
[data-testid="stSidebar"] [data-baseweb="notification"],
[data-testid="stSidebar"] [data-baseweb="notification"] *,
[data-testid="stSidebar"] div[data-baseweb="notification"],
[data-testid="stSidebar"] div[data-baseweb="notification"] *,
[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] .stAlert *,
[data-testid="stSidebar"] .element-container .stAlert,
[data-testid="stSidebar"] .element-container .stAlert * {
    color: white !important;
}

/* AGGRESSIVE: Force white text for ALL metrics in sidebar */
[data-testid="stSidebar"] div[data-testid="metric-container"],
[data-testid="stSidebar"] div[data-testid="metric-container"] *,
[data-testid="stSidebar"] div[data-testid="stMetricValue"],
[data-testid="stSidebar"] div[data-testid="stMetricValue"] *,
[data-testid="stSidebar"] div[data-testid="stMetricLabel"],
[data-testid="stSidebar"] div[data-testid="stMetricLabel"] *,
[data-testid="stSidebar"] .stMetric,
[data-testid="stSidebar"] .stMetric *,
[data-testid="stSidebar"] .stMetric > div,
[data-testid="stSidebar"] .stMetric > div *,
[data-testid="stSidebar"] .stMetric > div > div,
[data-testid="stSidebar"] .stMetric > div > div *,
[data-testid="stSidebar"] .element-container .stMetric,
[data-testid="stSidebar"] .element-container .stMetric *,
[data-testid="stSidebar"] .element-container .stMetric > div,
[data-testid="stSidebar"] .element-container .stMetric > div *,
[data-testid="stSidebar"] .element-container .stMetric > div > div,
[data-testid="stSidebar"] .element-container .stMetric > div > div * {
    color: white !important;
}

/* CLEAN APPROACH: Make ALL sidebar text white for consistency */

/* All metrics - white text, no background */
[data-testid="stSidebar"] .stMetric,
[data-testid="stSidebar"] .stMetric *,
[data-testid="stSidebar"] .stMetric div,
[data-testid="stSidebar"] .stMetric span,
[data-testid="stSidebar"] .stMetric label,
[data-testid="stSidebar"] [data-testid="stMetricValue"],
[data-testid="stSidebar"] [data-testid="stMetricValue"] *,
[data-testid="stSidebar"] [data-testid="stMetricLabel"],
[data-testid="stSidebar"] [data-testid="stMetricLabel"] * {
    color: white !important;
    background: transparent !important;
}

/* All info messages - white text */
[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] .stAlert *,
[data-testid="stSidebar"] [data-baseweb="notification"],
[data-testid="stSidebar"] [data-baseweb="notification"] * {
    color: white !important;
    background: transparent !important;
}

/* All caption text - white */
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: white !important;
    background: transparent !important;
}

/* All paragraph text - white */
[data-testid="stSidebar"] p {
    color: white !important;
    background: transparent !important;
}

/* All buttons - keep white background but make them more subtle */
[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 6px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.3) !important;
    color: white !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
}

/* Form styling with lighter theme */
.stForm {
    border: 1px solid #fecaca !important;
    background-color: #fefbfb !important;
}

/* Text input styling */
.stTextInput > div > div > input {
    border-color: #fecaca !important;
}

.stTextInput > div > div > input:focus {
    border-color: #ed1847 !important;
    box-shadow: 0 0 0 2px rgba(237, 24, 71, 0.1) !important;
}

/* Selectbox styling */
.stSelectbox > div > div {
    border-color: #fecaca !important;
}

.stSelectbox > div > div:focus-within {
    border-color: #ed1847 !important;
    box-shadow: 0 0 0 2px rgba(237, 24, 71, 0.1) !important;
}

/* Slider styling */
.stSlider > div > div > div > div {
    background-color: #ed1847 !important;
}

.stSlider > div > div > div {
    background-color: #fef7f7 !important;
}

/* Checkbox styling */
.stCheckbox > label > div {
    border-color: #fca5a5 !important;
}

.stCheckbox > label > div[data-checked="true"] {
    background-color: #ed1847 !important;
    border-color: #ed1847 !important;
}

/* Success message styling */
.stSuccess {
    background-color: rgba(237, 24, 71, 0.1) !important;
    border-color: #ed1847 !important;
    color: #4a4a4a !important;
}

/* Warning message styling */
.stWarning {
    background-color: rgba(255, 152, 0, 0.1) !important;
    border-color: #ff9800 !important;
}

/* Error message styling */
.stError {
    background-color: rgba(220, 38, 127, 0.1) !important;
    border-color: #dc2626 !important;
}

/* Info message styling - using light orange theme throughout */
.stInfo {
    background-color: rgba(244, 148, 42, 0.08) !important;
    border-left-color: #f4942a !important;
    color: #4a4a4a !important;
    border-radius: 8px !important;
}

/* Additional info elements that use secondaryBackgroundColor */
.element-container .stAlert[data-baseweb="notification"][kind="info"] {
    background-color: rgba(244, 148, 42, 0.08) !important;
    border-left-color: #f4942a !important;
    color: #4a4a4a !important;
    border-radius: 8px !important;
}

/* Ensure info boxes use light orange theme */
div[data-testid="stNotification"] {
    background-color: rgba(244, 148, 42, 0.08) !important;
    border-left-color: #f4942a !important;
    color: #4a4a4a !important;
    border-radius: 8px !important;
}

/* Override any blue info backgrounds and text */
.info, .st-info, [data-baseweb="notification"][kind="info"] {
    background-color: rgba(244, 148, 42, 0.08) !important;
    border-left-color: #f4942a !important;
    color: #4a4a4a !important;
    border-radius: 8px !important;
}

/* Comprehensive info box targeting */
div[data-baseweb="notification"],
div[data-baseweb="notification"][kind="info"],
.stAlert[kind="info"],
.element-container .stAlert,
.stNotification {
    background-color: rgba(244, 148, 42, 0.08) !important;
    border-left-color: #f4942a !important;
    border-radius: 8px !important;
}

/* Target specific info message text elements */
.stInfo p, .stInfo div, .stInfo span,
div[data-testid="stNotification"] p,
div[data-testid="stNotification"] div,
div[data-testid="stNotification"] span,
.element-container .stAlert p,
.element-container .stAlert div,
.element-container .stAlert span,
.element-container .stAlert strong,
.element-container .stAlert em {
    color: #4a4a4a !important;
}

/* Override any default blue link colors in info sections */
.stInfo a, div[data-testid="stNotification"] a {
    color: #f4942a !important;
    text-decoration: underline !important;
}

/* Success message styling with light orange theme */
.stSuccess {
    background-color: rgba(244, 148, 42, 0.12) !important;
    border-left-color: #f4942a !important;
    color: #4a4a4a !important;
    border-radius: 8px !important;
}

/* Progress indicators and other elements */
.stProgress > div > div > div > div {
    background-color: #f4942a !important;
}

.stProgress > div > div > div {
    background-color: rgba(244, 148, 42, 0.15) !important;
}

/* Expander styling */
.streamlit-expanderHeader {
    background-color: #fef2f2 !important;
    border-color: #fca5a5 !important;
}

.streamlit-expanderContent {
    background-color: #fefefe !important;
    border-color: #fca5a5 !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: #fef2f2 !important;
}

.stTabs [data-baseweb="tab"] {
    color: #4a4a4a !important;
}

.stTabs [aria-selected="true"] {
    background-color: #ed1847 !important;
    color: white !important;
}

/* Metric styling */
.metric-container {
    background-color: rgba(237, 24, 71, 0.05) !important;
    border: 1px solid rgba(237, 24, 71, 0.1) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}

/* Column styling for better visual separation */
.element-container .stColumn {
    background-color: rgba(253, 242, 248, 0.3) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
    margin: 0.25rem !important;
}

/* Custom Badge Components - Vertically Centered with Orange Theme */
.custom-success-badge,
.custom-wallet-badge,
.custom-warning-badge {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0.5rem 0.75rem !important;
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-align: center !important;
    min-height: 2.5rem !important;
    box-sizing: border-box !important;
    margin: 0.25rem 0 !important;
    transition: all 0.2s ease-in-out !important;
}

/* Success badge styling - subtle orange theme */
.custom-success-badge {
    background: linear-gradient(135deg, rgba(244, 148, 42, 0.12) 0%, rgba(244, 148, 42, 0.08) 100%) !important;
    border: 1px solid rgba(244, 148, 42, 0.3) !important;
    color: #4a4a4a !important;
    border-left: 3px solid #f4942a !important;
}

.custom-success-badge:hover {
    background: linear-gradient(135deg, rgba(244, 148, 42, 0.18) 0%, rgba(244, 148, 42, 0.12) 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px rgba(244, 148, 42, 0.15) !important;
}

/* Wallet availability badge styling - subtle orange theme */
.custom-wallet-badge {
    background: linear-gradient(135deg, rgba(244, 148, 42, 0.1) 0%, rgba(244, 148, 42, 0.06) 100%) !important;
    border: 1px solid rgba(244, 148, 42, 0.25) !important;
    color: #4a4a4a !important;
    border-left: 3px solid #f4942a !important;
}

.custom-wallet-badge:hover {
    background: linear-gradient(135deg, rgba(244, 148, 42, 0.15) 0%, rgba(244, 148, 42, 0.1) 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px rgba(244, 148, 42, 0.12) !important;
}

/* Warning badge styling - muted orange theme */
.custom-warning-badge {
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, rgba(255, 152, 0, 0.05) 100%) !important;
    border: 1px solid rgba(255, 152, 0, 0.2) !important;
    color: #4a4a4a !important;
    border-left: 3px solid #ff9800 !important;
}

.custom-warning-badge:hover {
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.12) 0%, rgba(255, 152, 0, 0.08) 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1) !important;
}
</style>
"""

# Sidebar Gradient CSS - Applied consistently across all pages
SIDEBAR_GRADIENT_CSS = """
<style>
/* Sidebar animated gradient background matching header */
[data-testid="stSidebar"] {
    background: linear-gradient(120deg, #f4942a, #ff6b35, #e8530f, #d4410a, #f4942a) !important;
    background-size: 300% 300% !important;
    animation: gradient-move 6s infinite ease-in-out !important;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.15) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
}

[data-testid="stSidebar"] > div {
    background: transparent !important;
}

/* Ensure sidebar expand button is visible when collapsed */
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 0.5rem !important;
    left: 0.5rem !important;
    z-index: 999999 !important;
    background-color: rgba(244, 148, 42, 0.9) !important;
    border-radius: 4px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
}

/* Sidebar collapse button styling */
[data-testid="baseButton-header"] {
    background-color: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 4px !important;
}

[data-testid="baseButton-header"]:hover {
    background-color: rgba(255, 255, 255, 0.3) !important;
}

/* Fix the page name in sidebar navigation - applied to all pages */
[data-testid="stSidebarNav"] ul li:first-child a span {
    display: none;
}

[data-testid="stSidebarNav"] ul li:first-child a::after {
    content: "Find Instruments";
    font-weight: 400;
}

/* Comprehensive sidebar content styling for white text */
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown *,
[data-testid="stSidebar"] .stInfo,
[data-testid="stSidebar"] .stInfo *,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stButton,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] span,
[data-testid="stSidebar"] .element-container,
[data-testid="stSidebar"] .element-container *,
[data-testid="stSidebar"] .block-container,
[data-testid="stSidebar"] .block-container *,
[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] .stAlert *,
[data-testid="stSidebar"] .stSuccess,
[data-testid="stSidebar"] .stSuccess *,
[data-testid="stSidebar"] .stWarning,
[data-testid="stSidebar"] .stWarning *,
[data-testid="stSidebar"] .stError,
[data-testid="stSidebar"] .stError *,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: white !important;
}

/* Sidebar input styling for better visibility */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: rgba(255, 255, 255, 0.9) !important;
    color: #333 !important;
}

[data-testid="stSidebar"] .stTextInput > div > div > input {
    background-color: rgba(255, 255, 255, 0.9) !important;
    color: #333 !important;
}

/* Sidebar button styling */
[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.3) !important;
}

/* Sidebar info box styling with aggressive white text */
[data-testid="stSidebar"] .stInfo {
    background-color: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

/* Force white text in sidebar info boxes and alerts */
[data-testid="stSidebar"] .stInfo,
[data-testid="stSidebar"] .stInfo *,
[data-testid="stSidebar"] .stInfo div,
[data-testid="stSidebar"] .stInfo p,
[data-testid="stSidebar"] .stInfo span,
[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] .stAlert *,
[data-testid="stSidebar"] .stAlert div,
[data-testid="stSidebar"] .stAlert p,
[data-testid="stSidebar"] .stAlert span,
[data-testid="stSidebar"] div[data-testid="stNotification"],
[data-testid="stSidebar"] div[data-testid="stNotification"] *,
[data-testid="stSidebar"] div[data-testid="stNotification"] div,
[data-testid="stSidebar"] div[data-testid="stNotification"] p,
[data-testid="stSidebar"] div[data-testid="stNotification"] span {
    color: white !important;
}

/* Override any specific Streamlit alert styling in sidebar */
section[data-testid="stSidebar"] div[data-baseweb="notification"],
section[data-testid="stSidebar"] div[data-baseweb="notification"] *,
section[data-testid="stSidebar"] div[data-baseweb="notification"] div,
section[data-testid="stSidebar"] div[data-baseweb="notification"] p,
section[data-testid="stSidebar"] div[data-baseweb="notification"] span {
    color: white !important;
}

/* Logo styling on gradient background */
[data-testid="stSidebarNav"]::before {
    filter: brightness(0) invert(1) !important;
}

/* Navigation links styling */
[data-testid="stSidebarNav"] ul li a,
[data-testid="stSidebarNav"] ul li a span {
    color: white !important;
}

[data-testid="stSidebarNav"] ul li a:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
}

@keyframes gradient-move {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
"""

SIDEBAR_FINAL_ENFORCEMENT_CSS = """
<style>
/* FINAL ENFORCEMENT: Sidebar metric labels and values must be white */
[data-testid="stSidebar"] [data-testid="stMetricValue"],
[data-testid="stSidebar"] [data-testid="stMetricValue"] *,
[data-testid="stSidebar"] [data-testid="metric-value"],
[data-testid="stSidebar"] [data-testid="metric-value"] *,
[data-testid="stSidebar"] [data-testid="stMetricLabel"],
[data-testid="stSidebar"] [data-testid="stMetricLabel"] *,
[data-testid="stSidebar"] [data-testid="metric-label"],
[data-testid="stSidebar"] [data-testid="metric-label"] *,
[data-testid="stSidebar"] .stMetric [data-testid],
[data-testid="stSidebar"] .stMetric [data-testid] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

/* Ensure expander content text inside sidebar is white as well */
[data-testid="stSidebar"] .streamlit-expanderContent,
[data-testid="stSidebar"] .streamlit-expanderContent * {
    color: #ffffff !important;
}

/* Dynamic portfolio selections and search results - force white text */
[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stSelectbox *,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSelectbox span,
[data-testid="stSidebar"] .stSelectbox p,
[data-testid="stSidebar"] .stSelectbox div:not([data-baseweb="select"]) {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Target dynamic text content in sidebar (search results, selections) */
[data-testid="stSidebar"] .element-container .stMarkdown p,
[data-testid="stSidebar"] .element-container .stMarkdown span,
[data-testid="stSidebar"] .element-container .stMarkdown div,
[data-testid="stSidebar"] .element-container .stText,
[data-testid="stSidebar"] .element-container .stText *,
[data-testid="stSidebar"] .stText,
[data-testid="stSidebar"] .stText * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Target bullet points and list items in Recent Selections */
[data-testid="stSidebar"] ul,
[data-testid="stSidebar"] ul *,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] li *,
[data-testid="stSidebar"] .element-container ul,
[data-testid="stSidebar"] .element-container ul *,
[data-testid="stSidebar"] .element-container li,
[data-testid="stSidebar"] .element-container li * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Comprehensive targeting for any dynamic content */
[data-testid="stSidebar"] .stMarkdown:not(h1):not(h2):not(h3):not(strong):not(b),
[data-testid="stSidebar"] .stMarkdown:not(h1):not(h2):not(h3):not(strong):not(b) *,
[data-testid="stSidebar"] .element-container:not(.stMetric) .stMarkdown,
[data-testid="stSidebar"] .element-container:not(.stMetric) .stMarkdown * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Make sidebar HR separator lines white - precise targeting */
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid #ffffff !important;
    background: transparent !important;
    height: 1px !important;
    margin: 25.92px 0 !important;
    opacity: 0.7 !important;
}

/* Alternative targeting for Streamlit's markdown HR elements */
[data-testid="stSidebar"] .stMarkdown hr {
    border: none !important;
    border-top: 1px solid #ffffff !important;
    background: transparent !important;
    height: 1px !important;
    opacity: 0.7 !important;
}

/* AGGRESSIVE REMOVAL: Remove all red outlines completely */
* {
    outline: none !important;
}

/* Restore subtle accessibility outlines only for keyboard navigation */
*:focus-visible {
    outline: 2px solid rgba(244, 148, 42, 0.6) !important;
    outline-offset: 2px !important;
}

/* Remove any box-shadow that might be creating red outlines */
*:focus,
*:active,
*[aria-selected="true"],
*[data-selected="true"] {
    box-shadow: none !important;
}

/* Specifically target Streamlit's internal CSS classes that might have red outlines */
[class*="css-"]:focus,
[class*="css-"]:active,
[class*="css-"][aria-selected="true"] {
    outline: none !important;
    box-shadow: none !important;
}

/* Remove any border that might appear as red outline */
*:focus,
*:active {
    border-color: transparent !important;
}

/* NUCLEAR APPROACH: Override any possible red color sources */
* {
    --primary-color: #f4942a !important;
    --focus-color: #f4942a !important;
    --active-color: #f4942a !important;
}

/* Target specific Streamlit elements that might have hardcoded red */
button[data-testid],
[data-testid] button,
[data-testid] a,
[data-testid] [role="button"],
[class*="streamlit"],
[class*="st-"] {
    outline: none !important;
    box-shadow: none !important;
    border: none !important;
}

/* Override any CSS custom properties that might control red outlines */
:root {
    --primary-color: #f4942a !important;
    --focus-ring-color: rgba(244, 148, 42, 0.5) !important;
    --outline-color: rgba(244, 148, 42, 0.5) !important;
}

/* Force override any inline styles or computed styles */
*[style*="outline"],
*[style*="border"],
*[style*="box-shadow"] {
    outline: none !important;
    border-color: transparent !important;
    box-shadow: none !important;
}

/* RESTORE: Proper expander styling without aggressive red outlines */
/* Expander container styling */
[data-testid="stExpander"] {
    border: 1px solid rgba(244, 148, 42, 0.2) !important;
    border-radius: 8px !important;
    background-color: rgba(244, 148, 42, 0.02) !important;
    margin: 0.5rem 0 !important;
    box-shadow: 0 1px 3px rgba(244, 148, 42, 0.1) !important;
    overflow: hidden !important;
}

/* Expander header styling */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, rgba(244, 148, 42, 0.08) 0%, rgba(244, 148, 42, 0.04) 100%) !important;
    border: none !important;
    border-bottom: 1px solid rgba(244, 148, 42, 0.15) !important;
    padding: 1rem !important;
    color: #4a4a4a !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
}

/* Expander header hover state */
.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, rgba(244, 148, 42, 0.12) 0%, rgba(244, 148, 42, 0.06) 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px rgba(244, 148, 42, 0.15) !important;
}

/* Expander content styling */
.streamlit-expanderContent {
    background-color: #ffffff !important;
    border: none !important;
    padding: 1rem !important;
    color: #4a4a4a !important;
}

/* Remove focus outline from expander but keep visual feedback */
.streamlit-expanderHeader:focus {
    outline: none !important;
    background: linear-gradient(135deg, rgba(244, 148, 42, 0.15) 0%, rgba(244, 148, 42, 0.08) 100%) !important;
    box-shadow: 0 0 0 2px rgba(244, 148, 42, 0.3) !important;
}

/* Expander toggle icon styling */
[data-testid="stExpanderToggleIcon"] {
    color: #f4942a !important;
}

/* RESTORE: Checkbox visibility and styling - ENHANCED */
/* Make checkboxes ALWAYS visible with strong styling */
input[type="checkbox"] {
    appearance: auto !important;
    -webkit-appearance: checkbox !important;
    -moz-appearance: checkbox !important;
    width: 20px !important;
    height: 20px !important;
    border: 3px solid #f4942a !important;
    border-radius: 4px !important;
    background-color: #ffffff !important;
    cursor: pointer !important;
    margin: 4px !important;
    padding: 0 !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: block !important;
    box-shadow: 0 2px 4px rgba(244, 148, 42, 0.3) !important;
}

/* Checkbox checked state - more prominent */
input[type="checkbox"]:checked {
    background-color: #f4942a !important;
    border-color: #f4942a !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(244, 148, 42, 0.5) !important;
}

/* Checkbox hover state - enhanced visibility */
input[type="checkbox"]:hover {
    border-color: #e8530f !important;
    border-width: 3px !important;
    box-shadow: 0 0 0 3px rgba(244, 148, 42, 0.3) !important;
    transform: scale(1.1) !important;
}

/* Checkbox focus state - subtle orange instead of aggressive red */
input[type="checkbox"]:focus {
    outline: 3px solid rgba(244, 148, 42, 0.6) !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 0 4px rgba(244, 148, 42, 0.2) !important;
}

/* Streamlit checkbox container styling - enhanced */
.stCheckbox > label {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    cursor: pointer !important;
    padding: 8px !important;
    border-radius: 6px !important;
    transition: all 0.2s ease-in-out !important;
}

/* Make entire checkbox area clickable and hoverable */
.stCheckbox > label:hover {
    background-color: rgba(244, 148, 42, 0.05) !important;
    transform: translateY(-1px) !important;
}

/* Checkbox label text - enhanced */
.stCheckbox > label > span {
    color: #4a4a4a !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

/* Ensure checkbox container is visible in result display */
.stCheckbox > label > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: 28px !important;
    min-height: 28px !important;
}

/* CLICKABLE ROWS: Make entire result row interactive */
/* Target the container that holds each search result */
.element-container:has(.stCheckbox) {
    cursor: pointer !important;
    border-radius: 8px !important;
    transition: all 0.2s ease-in-out !important;
    padding: 8px !important;
    margin: 4px 0 !important;
}

/* Row hover effect */
.element-container:has(.stCheckbox):hover {
    background-color: rgba(244, 148, 42, 0.03) !important;
    box-shadow: 0 2px 8px rgba(244, 148, 42, 0.1) !important;
    transform: translateY(-1px) !important;
}

/* Alternative approach for browsers that don't support :has() */
.stContainer > div:hover {
    background-color: rgba(244, 148, 42, 0.02) !important;
    border-radius: 6px !important;
}

/* FIX: Button styling and alignment issues */
/* Primary buttons - restore proper orange theme */
.stButton > button[kind="primary"],
button[kind="primary"],
.stFormSubmitButton > button {
    background-color: #f4942a !important;
    border: 2px solid #f4942a !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 2px 4px rgba(244, 148, 42, 0.2) !important;
}

/* Primary button hover state */
.stButton > button[kind="primary"]:hover,
button[kind="primary"]:hover,
.stFormSubmitButton > button:hover {
    background-color: #e8530f !important;
    border-color: #e8530f !important;
    color: white !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(244, 148, 42, 0.3) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"],
button[kind="secondary"] {
    background-color: #ffffff !important;
    border: 2px solid #f4942a !important;
    color: #f4942a !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease-in-out !important;
}

/* Secondary button hover state */
.stButton > button[kind="secondary"]:hover,
button[kind="secondary"]:hover {
    background-color: #f4942a !important;
    border-color: #f4942a !important;
    color: white !important;
    transform: translateY(-1px) !important;
}

/* FIX: Search input and button alignment */
/* Ensure search form elements are properly aligned */
.stForm {
    margin-bottom: 1rem !important;
}

/* Search form columns alignment */
.stForm .stColumns {
    align-items: flex-end !important;
}

/* Search input container alignment */
.stForm .stTextInput {
    margin-bottom: 0 !important;
}

/* Search button alignment - match input height */
.stForm .stFormSubmitButton {
    margin-bottom: 0 !important;
    display: flex !important;
    align-items: flex-end !important;
}

.stForm .stFormSubmitButton > button {
    height: 2.75rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-bottom: 0 !important;
}

/* Text input height consistency */
.stTextInput > div > div > input {
    height: 2.75rem !important;
    padding: 0.5rem 0.75rem !important;
    box-sizing: border-box !important;
}

/* Remove any conflicting button overrides */
button:not(.stButton button):not([data-testid="baseButton-header"]) {
    background-color: initial !important;
    border-color: initial !important;
    color: initial !important;
}

/* Ensure form submit buttons maintain orange theme */
.stForm button[type="submit"] {
    background-color: #f4942a !important;
    border: 2px solid #f4942a !important;
    color: white !important;
}

/* SPECIFIC FIX: Target the Smart Search form submit button */
.stFormSubmitButton > button,
.stForm .stFormSubmitButton > button,
[data-testid="stFormSubmitButton"] > button,
button[data-testid="baseButton-primary"] {
    background-color: #f4942a !important;
    border: 2px solid #f4942a !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    height: 2.75rem !important;
    box-shadow: 0 2px 4px rgba(244, 148, 42, 0.2) !important;
    transition: all 0.2s ease-in-out !important;
}

/* Smart Search button hover state */
.stFormSubmitButton > button:hover,
.stForm .stFormSubmitButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
button[data-testid="baseButton-primary"]:hover {
    background-color: #e8530f !important;
    border-color: #e8530f !important;
    color: white !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(244, 148, 42, 0.3) !important;
}

/* Override any Streamlit default primary button styling */
button[kind="primary"],
button[data-baseweb="button"][kind="primary"] {
    background: #f4942a !important;
    background-color: #f4942a !important;
    border-color: #f4942a !important;
    color: white !important;
}
</style>
"""