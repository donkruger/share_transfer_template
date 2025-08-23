# app/pdf_generator.py

import io
import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.utils import text_wrap

def make_pdf(payload: Dict[str, Any]) -> bytes:
    """Render all captured answers to a simple, printable PDF."""
    # Add error handling for unexpected payload types
    if not isinstance(payload, dict):
        # Try to import streamlit for error display, but don't fail if unavailable
        try:
            import streamlit as st
            st.error(f"PDF generation failed: Expected dictionary payload, got {type(payload).__name__}")
        except ImportError:
            pass
        
        # Return a simple error PDF instead of crashing
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        margin = 40
        y = h - margin
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, "Error: Invalid Data Format")
        y -= 2 * 14
        c.setFont("Helvetica", 10)
        c.drawString(margin, y, f"Received: {type(payload).__name__}")
        y -= 14
        c.drawString(margin, y, "Expected: Dictionary")
        y -= 14
        c.drawString(margin, y, "Payload content:")
        y -= 14
        c.drawString(margin, y, str(payload)[:100] + "..." if len(str(payload)) > 100 else str(payload))
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    line_height = 14
    margin = 40
    y = h - margin

    def check_page_break(y_pos):
        """Adds a new page if content gets too close to the bottom margin."""
        if y_pos < margin + 2 * line_height:
            c.showPage()
            return h - margin
        return y_pos

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Entity Onboarding – Response Summary")
    y -= 2 * line_height
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Submission Timestamp: {datetime.datetime.now():%Y-%m-%d %H:%M SAST}")
    y -= 1.5 * line_height

    for section, data in payload.items():
        y = check_page_break(y)
        c.setFont("Helvetica-Bold", 12)
        y -= line_height
        c.drawString(margin, y, str(section))
        y -= 0.5 * line_height
        c.line(margin, y, w - margin, y)
        y -= line_height
        c.setFont("Helvetica", 9)

        # Handle different data types more robustly
        if isinstance(data, list): # Handles repeating sections (Directors, UBOs, etc.)
            for i, item in enumerate(data):
                y = check_page_break(y)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(margin + 10, y, f"Item #{i+1}")
                y -= line_height
                c.setFont("Helvetica", 9)
                if isinstance(item, dict):
                    for q, a in item.items():
                        text = f"{q}: {a}"
                        for chunk in text_wrap(text, 95):
                            y = check_page_break(y)
                            c.drawString(margin + 20, y, chunk)
                            y -= line_height
                else:
                    # Handle non-dict items
                    text = f"Item: {item}"
                    for chunk in text_wrap(text, 95):
                        y = check_page_break(y)
                        c.drawString(margin + 20, y, chunk)
                        y -= line_height
                y -= 0.5 * line_height
        elif isinstance(data, dict): # Handles standard sections
            for q, a in data.items():
                text = f"{q}: {a}"
                for chunk in text_wrap(text, 100):
                    y = check_page_break(y)
                    c.drawString(margin + 10, y, chunk)
                    y -= line_height
                y -= 0.5 * line_height
        else: # Handle other data types (strings, numbers, etc.)
            text = f"{section}: {data}"
            for chunk in text_wrap(text, 100):
                y = check_page_break(y)
                c.drawString(margin + 10, y, chunk)
                y -= line_height
            y -= 0.5 * line_height

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read() 