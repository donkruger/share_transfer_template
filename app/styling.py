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
@keyframes gradient-animation {
  0%   {background-position: 0% 50%;}
  50%  {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}
.gradient-title {
  font-family: 'Questrial', sans-serif;
  font-size: 2.2rem;
  font-weight: 400;
  text-align: left;
  background: linear-gradient(270deg, #3c66a4, #0fbce3);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-animation 7s ease-in-out infinite;
  margin-top: 0.5rem;
  margin-bottom: 1.5rem;
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