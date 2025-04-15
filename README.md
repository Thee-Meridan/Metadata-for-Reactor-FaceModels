# Metadata-for-Reactor-FaceModels
A hack to reactor "Load Face Model" and a standalone python script to add metadata to your facemodels
The purpose of which is to feed txt to prompt information for individual characters for consistancy in Renders, adding details such as body type, hair color, eye color, etc...things that the facemodel does not provide.  
Helps keep workflow nice and tidy and gives a one-stop soloution for likenesses.  
📸 ComfyUI Manual Patch: GB_LoadFaceModelWithMetadata
-------------------------------------------------------

This  is a manual patch.  I wanted to do a simple drop in custom node, but GPT wasn't having it, not understanding what to include from imports etc so I tried a billion restarts to get it to show up letalone work to no avail.  

Also, this way, your existing workflow will simply add the new features and you don't have to rewire a million things for  you noodle heads out there.

Make backups and follow instructions then for this to work.

This patch modifies the existing ReActor `LoadFaceModel` node so it outputs
not only the face tensor and filename — but also a third output: prompt metadata.

This lets you embed short prompt fragments (like tags or triggers) inside
your .safetensors face model files, then wire those directly into your prompts.

-----------------------------
🔧 What This Patch Does:
-----------------------------
• Adds a 3rd output: the string embedded in the "prompt" metadata field
• Filename is stripped of `.safetensors` and `-MD`
• Outputs:
    1. face_model tensor
    2. face_model name (string)
    3. prompt metadata (string)

-----------------------------
📂 How to Install Manually:
-----------------------------

1. Locate the following file in your ComfyUI install:
   📍 `ComfyUI/custom_nodes/comfyui-reactor-node/nodes.py`

2. Open that file in a text editor.

3. Search for the class named:
   ```python
   class LoadFaceModel:
Replace the entire class with the version provided in this patch: (Make sure to copy everything from class LoadFaceModel: down through return.)

Save the file.

Restart ComfyUI.

⚠️ Notes:
• This patch does NOT affect ReActor behavior — it only adds an extra output. • The prompt metadata must already be embedded inside your .safetensors files (see the provided Metadata Editor GUI tool for doing this). • If no metadata is present, the third output will be an empty string "".

✅ That’s it — your face models can now carry their own routing triggers!



Safetensor Metadata Editor
---------------------------
V1.0
gboycott@wowway.com

I created this utility with the help of ChatGPT to compliment the Metadata/Safetensor "prompt" embedding concept because it was not possible to efficiently change the Metadata within Comfyui due to the way it handles files/memory/etc.

You can run this alongside Comfy without issue, editing facemodels as you see fit.  Describe things that accompany your character/face swap so that things like hair, eyes, body shape etc are carried along to the image without having to put it in your scene/scenario description.  This is helpful for automation when you're loading characters randomly or incrementally etc.

In order to see changes in Comfy, you may have to switch away from the model in question, queue something else, then go back. 

A standalone graphical utility for browsing, editing, and saving metadata strings
embedded in .safetensors face models — fully compatible with ComfyUI and ReActor.

🚀 Features:
    - Simple two-panel interface
    - Browse a directory of .safetensors files
    - Edit prompt metadata per file
    - Multi-selection: apply the same prompt to multiple files at once
    - Saves directly back to the original file (no temp/overwrite weirdness)
    - ComfyUI-compatible: uses safe_open / save_file for proper file handling

🧠 What It Does:
    - Loads the "prompt" metadata string embedded in .safetensors files
    - Lets you edit it in a large, full-width text box
    - Press ENTER (or click Save) to commit the edit

🖱️ Usage:
    1. Launch the script (as .pyw or packaged .exe)
    2. Click "Select Directory" and browse to your face model folder
    3. Select a single file to view and edit its metadata
    4. Select multiple files to bulk-apply a prompt to all
    5. Press ENTER or click "Save" to embed the prompt

⌨️ Keyboard Tips:
    - Arrow keys / Scroll / Type first letter to navigate list
    - ENTER in metadata box will save (newlines disabled)
    - Ctrl-click or Shift-click to select multiple files

⚠️ Behavior Notes:
    - Existing metadata will be replaced when saving
    - If ComfyUI is open, saving still works (files are read into memory)
    - Only the "prompt" field is modified

📦 Optional:
    - Package as EXE using PyInstaller if desired
    - Designed for .pyw launch (no terminal window)

📁 Metadata location:
    - Embedded in the header of each .safetensors file
    - Used in ComfyUI by patched nodes.py or any node that accesses metadata

