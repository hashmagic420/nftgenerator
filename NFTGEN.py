import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import base64

# Custom CSS for neuromorphic design
st.markdown("""
    <style>
    body {
        background-color: #E64A19;
        color: #FFFFFF;
    }
    .main {
        background-color: #E64A19;
    }
    .stButton > button {
        background-color: #000000;
        color: #FFFFFF;
        border-radius: 12px;
        box-shadow: 5px 5px 15px 5px rgba(0,0,0,0.3), -5px -5px 15px 5px rgba(255,152,0,0.3);
    }
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stFileUploader > div > div > div > button,
    .stSelectbox > div > div > select,
    .stSlider > div > div > div > div,
    .stRadio > div > label > div,
    .stSidebar > div > div {
        background-color: #FFFFFF;
        color: #000000;
        border-radius: 12px;
        box-shadow: 5px 5px 15px 5px rgba(0,0,0,0.3), -5px -5px 15px 5px rgba(255,152,0,0.3);
    }
    footer {
        font-size: 18px;
        color: #FFFFFF;
        text-align: center;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Set up the app
st.title("NFT Generator")
st.markdown("# NFT Generator")

# Set up the canvas dimensions
canvas_width, canvas_height = 800, 600

# Initialize session state for layers, saved data, and pixel art
if 'layers' not in st.session_state:
    st.session_state.layers = []

if 'saved_data' not in st.session_state:
    st.session_state.saved_data = {}

if 'pixel_art' not in st.session_state:
    st.session_state.pixel_art = None

if 'pixel_art_dimensions' not in st.session_state:
    st.session_state.pixel_art_dimensions = (32, 32)

# Mode selection
mode = st.sidebar.radio("Select Mode", ("Free Draw", "Pixel Art"))

if mode == "Pixel Art":
    st.markdown("## Pixel Art Canvas")
    pixel_size = st.sidebar.slider("Pixel Size", 5, 50, 20)
    rows = st.sidebar.number_input("Rows", min_value=5, max_value=100, value=st.session_state.pixel_art_dimensions[0])
    cols = st.sidebar.number_input("Columns", min_value=5, max_value=100, value=st.session_state.pixel_art_dimensions[1])
    selected_color = st.sidebar.color_picker("Select Color", "#000000")

    if st.session_state.pixel_art is None or st.session_state.pixel_art_dimensions != (rows, cols):
        st.session_state.pixel_art_dimensions = (rows, cols)
        st.session_state.pixel_art = np.zeros((rows, cols, 3), dtype=np.uint8) + 255

    def draw_pixel_art(pixel_art, pixel_size):
        img = Image.new("RGB", (cols * pixel_size, rows * pixel_size), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        for row in range(rows):
            for col in range(cols):
                color = tuple(pixel_art[row, col])
                draw.rectangle([col * pixel_size, row * pixel_size, (col + 1) * pixel_size, (row + 1) * pixel_size], fill=color)
        return img

    pixel_art_img = draw_pixel_art(st.session_state.pixel_art, pixel_size)
    buf = io.BytesIO()
    pixel_art_img.save(buf, format="PNG")
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    img_html = f'<img src="data:image/png;base64,{data}" usemap="#imagemap">'
    st.markdown(img_html, unsafe_allow_html=True)

    st.markdown("""
        <map name="imagemap">
        </map>
    """, unsafe_allow_html=True)

    # Capture click events on the image
    click = st.sidebar.radio("Click to Add Pixel", ("", "Add Pixel"))

    if click == "Add Pixel":
        x = st.sidebar.number_input("X Coordinate", min_value=0, max_value=cols-1, value=0)
        y = st.sidebar.number_input("Y Coordinate", min_value=0, max_value=rows-1, value=0)
        st.session_state.pixel_art[y, x] = tuple(int(selected_color[i:i+2], 16) for i in (1, 3, 5))
        st.experimental_rerun()

# Footer
st.markdown("<footer>brought to you by: hash.magic🧝‍♂️</footer>", unsafe_allow_html=True)
