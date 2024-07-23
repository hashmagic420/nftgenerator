import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageOps
import json
import io
import numpy as np

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

# Initialize session state for layers and saved data
if 'layers' not in st.session_state:
    st.session_state.layers = []

if 'saved_data' not in st.session_state:
    st.session_state.saved_data = {}

if 'pixel_art' not in st.session_state:
    st.session_state.pixel_art = None

if 'pixel_art_dimensions' not in st.session_state:
    st.session_state.pixel_art_dimensions = (32, 32)

# UI Elements
selected_tool = st.sidebar.selectbox("Select Tool", list(tools.keys()))
selected_color = st.sidebar.color_picker("Select Color", "#000000")
tool_size = tools[selected_tool]["size"]

st.sidebar.markdown("## Metadata")
name = st.sidebar.text_input("Name")
description = st.sidebar.text_area("Description")

if st.sidebar.button("Add Metadata"):
    metadata = {"name": name, "description": description}
    st.session_state.saved_data["metadata"] = metadata

# Layer management
st.sidebar.markdown("## Layers")
new_layer = st.sidebar.text_input("New Layer Name")
if st.sidebar.button("Add Layer") and new_layer:
    st.session_state.layers.append({"name": new_layer, "visible": True, "data": None})
    new_layer = ""

for layer in st.session_state.layers:
    layer['visible'] = st.sidebar.checkbox(layer['name'], value=layer['visible'])

# Import image
uploaded_image = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
if uploaded_image is not None:
    image = Image.open(uploaded_image)
    image = ImageOps.contain(image, (canvas_width, canvas_height))
    image_data = io.BytesIO()
    image.save(image_data, format='PNG')
    image_data.seek(0)
    st.session_state.layers.append({"name": "Uploaded Image", "visible": True, "data": image_data.getvalue()})
    st.image(image, caption='Uploaded Image', use_column_width=True)

# Mode selection
mode = st.sidebar.radio("Select Mode", ("Free Draw", "Pixel Art"))

if mode == "Free Draw":
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
        for layer in st.session_state.layers:
            if layer['visible'] and layer['data'] is not None:
                image = Image.open(io.BytesIO(layer['data']))
                image = image.resize((canvas_width, canvas_height))
                canvas_image = Image.alpha_composite(Image.fromarray(canvas_result.image_data), image)
                canvas_result.image_data = canvas_image

    # Save the drawn canvas to the layers
    if canvas_result.image_data is not None:
        for layer in st.session_state.layers:
            if layer['visible']:
                layer['data'] = canvas_result.image_data

elif mode == "Pixel Art":
    st.markdown("## Pixel Art Canvas")
    pixel_size = st.sidebar.slider("Pixel Size", 5, 50, 20)
    rows = st.sidebar.number_input("Rows", min_value=5, max_value=100, value=st.session_state.pixel_art_dimensions[0])
    cols = st.sidebar.number_input("Columns", min_value=5, max_value=100, value=st.session_state.pixel_art_dimensions[1])

    if st.session_state.pixel_art is None or st.session_state.pixel_art_dimensions != (rows, cols):
        st.session_state.pixel_art_dimensions = (rows, cols)
        st.session_state.pixel_art = [[(255, 255, 255) for _ in range(cols)] for _ in range(rows)]

    canvas = Image.new("RGB", (cols * pixel_size, rows * pixel_size), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for row in range(rows):
        for col in range(cols):
            color = st.session_state.pixel_art[row][col]
            draw.rectangle([col * pixel_size, row * pixel_size, (col + 1) * pixel_size, (row + 1) * pixel_size], fill=color, outline=(200, 200, 200))

    st.image(canvas, width=canvas_width)

    # Handle clicks
    click_data = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",
        stroke_width=0,
        stroke_color=selected_color,
        background_image=canvas,
        width=cols * pixel_size,
        height=rows * pixel_size,
        drawing_mode="none",
        key="pixel_canvas",
    )

    if click_data.json_data and click_data.json_data["objects"]:
        for obj in click_data.json_data["objects"]:
            x = int(obj["left"] // pixel_size)
            y = int(obj["top"] // pixel_size)
            st.session_state.pixel_art[y][x] = selected_color

        # Redraw the canvas with the updated pixel art
        for row in range(rows):
            for col in range(cols):
                color = st.session_state.pixel_art[row][col]
                draw.rectangle([col * pixel_size, row * pixel_size, (col + 1) * pixel_size, (row + 1) * pixel_size], fill=color, outline=(200, 200, 200))
        st.image(canvas, width=canvas_width)

# Save the NFT collection
if st.button("Save NFT Collection"):
    with open("nft_collection.json", "w") as f:
        json.dump(st.session_state.saved_data, f)
    st.success("NFT Collection and state saved successfully!")

# Load saved state
if st.button("Load Saved State"):
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
