import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageOps
import json
import io

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

# Set up the metadata
metadata = {}

# Set up the NFT collection
nft_collection = []

# Initialize session state for layers and saved data
if 'layers' not in st.session_state:
    st.session_state.layers = []

if 'saved_data' not in st.session_state:
    st.session_state.saved_data = {}

# UI Elements
selected_tool = st.sidebar.selectbox("Select Tool", list(tools.keys()))
selected_color = st.sidebar.color_picker("Select Color", "#000000")
tool_size = tools[selected_tool]["size"]

st.sidebar.markdown("## Metadata")
name = st.sidebar.text_input("Name")
description = st.sidebar.text_area("Description")

if st.sidebar.button("Add Metadata"):
    metadata["name"] = name
    metadata["description"] = description
    nft_collection.append(metadata)

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

# Save the NFT collection
if st.button("Save NFT Collection"):
    with open("nft_collection.json", "w") as f:
        json.dump(nft_collection, f)
    st.session_state.saved_data = {
        "layers": st.session_state.layers,
        "metadata": metadata,
        "nft_collection": nft_collection
    }
    st.success("NFT Collection and state saved successfully!")

# Load saved state
if st.button("Load Saved State"):
    if st.session_state.saved_data:
        st.session_state.layers = st.session_state.saved_data.get("layers", [])
        metadata = st.session_state.saved_data.get("metadata", {})
        nft_collection = st.session_state.saved_data.get("nft_collection", [])
        st.success("Saved state loaded successfully!")
    else:
        st.warning("No saved state found!")

# Display the NFT collection
st.markdown("## NFT Collection:")
for i, nft in enumerate(nft_collection):
    st.markdown(f"NFT {i+1}:")
    for layer in st.session_state.layers:
        if layer['data'] is not None:
            st.image(layer['data'])
    st.json(nft)
