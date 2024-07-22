import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import json

# Set up the app
st.title("NFT Generator")
st.markdown("# NFT Generator")

# Set up the canvas
canvas_width, canvas_height = 800, 600

# Set up the drawing tools
tools = {
    "marker": {"size": 5},
    "sharpie": {"size": 10},
    "pencil": {"size": 2},
}

# Set up the color palette
colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
color_names = ["Black", "Red", "Green", "Blue", "Yellow", "Magenta", "Cyan"]

# Set up the metadata
metadata = {}

# Set up the NFT collection
nft_collection = []

# UI Elements
selected_tool = st.sidebar.selectbox("Select Tool", list(tools.keys()))
selected_color = st.sidebar.selectbox("Select Color", color_names)
color = colors[color_names.index(selected_color)]
tool_size = tools[selected_tool]["size"]

st.sidebar.markdown("## Metadata")
name = st.sidebar.text_input("Name")
description = st.sidebar.text_area("Description")

if st.sidebar.button("Add Metadata"):
    metadata["name"] = name
    metadata["description"] = description
    nft_collection.append(metadata)

# Main app loop
st.markdown("## Drawing Canvas:")
canvas_result = st_canvas(
    stroke_width=tool_size,
    stroke_color=f"rgb{color}",
    background_color="#FFFFFF",
    width=canvas_width,
    height=canvas_height,
    drawing_mode="freedraw",
    key="canvas",
)

# Save the NFT collection
if st.button("Save NFT Collection"):
    with open("nft_collection.json", "w") as f:
        json.dump(nft_collection, f)
    st.success("NFT Collection saved successfully!")

# Display the NFT collection
st.markdown("## NFT Collection:")
for i, nft in enumerate(nft_collection):
    st.markdown(f"NFT {i+1}:")
    st.image(canvas_result.image_data)
    st.json(nft)
