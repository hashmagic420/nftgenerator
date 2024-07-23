import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import io
import base64
import json

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

# Set up the drawing tools
tools = {
    "marker": {"size": 5},
    "sharpie": {"size": 10},
    "pencil": {"size": 2},
}

# Initialize session state for layers, saved data, and pixel art
if 'layers' not in st.session_state:
    st.session_state.layers = []

if 'saved_data' not in st.session_state:
    st.session_state.saved_data = {}

if 'pixel_art' not in st.session_state:
    st.session_state.pixel_art = None

if 'pixel_art_dimensions' not in st.session_state:
    st.session_state.pixel_art_dimensions = (32, 32)

if 'mode' not in st.session_state:
    st.session_state.mode = "Free Draw"

# Handle the mode selection
mode = st.sidebar.radio("Select Mode", ("Free Draw", "Pixel Art"))

# Update the session state mode before creating widgets
if mode != st.session_state.mode:
    st.session_state.mode = mode

# UI Elements
selected_tool = st.sidebar.selectbox("Select Tool", list(tools.keys()), key="selected_tool")
selected_color = st.sidebar.color_picker("Select Color", "#000000", key="selected_color")
tool_size = tools[selected_tool]["size"]

st.sidebar.markdown("## Metadata")
name = st.sidebar.text_input("Name", key="name")
description = st.sidebar.text_area("Description", key="description")

if st.sidebar.button("Add Metadata", key="add_metadata"):
    metadata = {"name": name, "description": description}
    st.session_state.saved_data["metadata"] = metadata

# Layer management
st.sidebar.markdown("## Layers")
new_layer = st.sidebar.text_input("New Layer Name", key="new_layer")
if st.sidebar.button("Add Layer", key="add_layer") and new_layer:
    st.session_state.layers.append({"name": new_layer, "visible": True, "data": None})
    new_layer = ""

for idx, layer in enumerate(st.session_state.layers):
    layer['visible'] = st.sidebar.checkbox(layer['name'], value=layer['visible'], key=f"layer_{idx}")

# Import image
uploaded_image = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="uploaded_image")
if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGBA")
    image = ImageOps.contain(image, (canvas_width, canvas_height))
    image_data = io.BytesIO()
    image.save(image_data, format='PNG')
    image_data.seek(0)
    st.session_state.layers.append({"name": "Uploaded Image", "visible": True, "data": image_data.getvalue()})
    st.image(image, caption='Uploaded Image', use_column_width=True)

if st.session_state.mode == "Free Draw":
    # Display the drawing canvas
    st.markdown("## Drawing Canvas")
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",
        stroke_width=tool_size,
        stroke_color=selected_color,
        background_color="#FFFFFF",
        width=canvas_width,
        height=canvas_height,
        drawing_mode="freedraw",
        key="canvas",
    )

    # Combine layers into the canvas
    if canvas_result.image_data is not None:
        canvas_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        for layer in st.session_state.layers:
            if layer['visible'] and layer['data'] is not None:
                image = Image.open(io.BytesIO(layer['data'])).convert("RGBA")
                image = image.resize((canvas_width, canvas_height))
                canvas_image = Image.alpha_composite(canvas_image, image)
        canvas_result.image_data = np.array(canvas_image)

    # Save the drawn canvas to the layers
    if canvas_result.image_data is not None:
        for layer in st.session_state.layers:
            if layer['visible']:
                image_data = io.BytesIO()
                Image.fromarray(canvas_result.image_data.astype('uint8')).save(image_data, format='PNG')
                image_data.seek(0)
                layer['data'] = image_data.getvalue()

elif st.session_state.mode == "Pixel Art":
    st.markdown("## Pixel Art Canvas")
    pixel_size = st.sidebar.slider("Pixel Size", 5, 50, 20, key="pixel_size")
    rows = st.sidebar.number_input("Rows", min_value=5, max_value=100, value=st.session_state.pixel_art_dimensions[0], key="rows")
    cols = st.sidebar.number_input("Columns", min_value=5, max_value=100, value=st.session_state.pixel_art_dimensions[1], key="cols")

    if st.session_state.pixel_art is None or st.session_state.pixel_art_dimensions != (rows, cols):
        st.session_state.pixel_art_dimensions = (rows, cols)
        st.session_state.pixel_art = np.zeros((rows, cols, 3), dtype=np.uint8) + 255

    def draw_pixel_art(pixel_art, pixel_size):
        img = Image.new("RGB", (cols * pixel_size, rows * pixel_size), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        for row in range(rows):
            for col in range(cols):
                color = tuple(pixel_art[row, col])
                draw.rectangle([col * pixel_size, row * pixel_size, (col + 1) * pixel_size, (row + 1) * pixel_size], fill=color, outline=(0, 0, 0))
        return img

    pixel_art_img = draw_pixel_art(st.session_state.pixel_art, pixel_size)
    buf = io.BytesIO()
    pixel_art_img.save(buf, format="PNG")
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    img_html = f'<img src="data:image/png;base64,{data}" usemap="#imagemap">'
    st.markdown(img_html, unsafe_allow_html=True)

    # Capture click events on the image
    st.markdown(f"""
        <map name="imagemap">
        {"".join([f'<area shape="rect" coords="{col * pixel_size},{row * pixel_size},{(col + 1) * pixel_size},{(row + 1) * pixel_size}" href="?row={row}&col={col}&color={selected_color[1:]}" alt="pixel">' for row in range(rows) for col in range(cols)])}
        </map>
    """, unsafe_allow_html=True)

    query_params = st.experimental_get_query_params()
    if 'row' in query_params and 'col' in query_params and 'color' in query_params:
        row = int(query_params['row'][0])
        col = int(query_params['col'][0])
        color = query_params['color'][0]
        st.session_state.pixel_art[row, col] = np.array([int(color[i:i+2], 16) for i in (0, 2, 4)])
        # Instead of reloading the entire page, clear the query parameters to stay in pixel art mode
        st.experimental_set_query_params()

    pixel_art_img = draw_pixel_art(st.session_state.pixel_art, pixel_size)
    buf = io.BytesIO()
    pixel_art_img.save(buf, format="PNG")
    st.image(pixel_art_img, use_column_width=True)

# Save the NFT collection
if st.button("Save NFT Collection", key="save_collection"):
    st.session_state.saved_data["layers"] = st.session_state.layers
    st.session_state.saved_data["pixel_art"] = st.session_state.pixel_art
    st.session_state.saved_data["pixel_art_dimensions"] = st.session_state.pixel_art_dimensions
    with open("nft_collection.json", "w") as f:
        json.dump(st.session_state.saved_data, f)
    st.success("NFT Collection and state saved successfully!")

# Load saved state
if st.button("Load Saved State", key="load_collection"):
    try:
        with open("nft_collection.json", "r") as f:
            st.session_state.saved_data = json.load(f)
        st.session_state.layers = st.session_state.saved_data.get("layers", [])
        metadata = st.session_state.saved_data.get("metadata", {})
        st.session_state.pixel_art = st.session_state.saved_data.get("pixel_art", None)
        st.session_state.pixel_art_dimensions = st.session_state.saved_data.get("pixel_art_dimensions", (32, 32))
        st.success("Saved state loaded successfully!")
    except FileNotFoundError:
        st.warning("No saved state found!")

# Display the NFT collection
st.markdown("## NFT Collection:")
for i, nft in enumerate(st.session_state.saved_data.get("nft_collection", [])):
    st.markdown(f"NFT {i+1}:")
    for layer in st.session_state.layers:
        if layer['data'] is not None:
            st.image(layer['data'])
    st.json(nft)

# Footer
st.markdown("<footer>brought to you by: hash.magic🧝‍♂️</footer>", unsafe_allow_html=True)
