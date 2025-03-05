from fastapi import FastAPI
from modules.project_processor import ProjectProcessor
from fastapi import UploadFile, File
import os
from fastapi.responses import FileResponse
import tempfile

app = FastAPI(title="Black Violet Reaper Setlist API",
              description="API for the Black Violet Reaper Setlist generator, based on REAPER projects.",
              version="0.1")


# Initialize the project processor
project_processor = ProjectProcessor()

@app.post("/load_project")
async def load_project(file: UploadFile = File(...)):
    if file.filename.endswith(".rpp") or file.filename.endswith(".RPP"):
        contents = await file.read()
        file_name = file.filename
        project_processor.load_project(contents,file_name)
        return {"message": "Project loaded successfully!"}
    else:
        return {"error": "Invalid file type. Please upload an .rpp file."}, 500
    
@app.get("/get_song_list")
def get_song_list():
    return project_processor.get_song_list()

@app.post("/set_setlist")
def set_setlist(setlist: list[str]):
    project_processor.set_setlist(setlist)
    return {"message": "Setlist set successfully!"}

@app.get("/get_setlist")
def get_setlist():
    return project_processor.get_setlist()

@app.get("/export_rpp_project")
def export_rpp_project():
    project_processor.create_markers_from_setlist()
    content, filename = project_processor.create_new_rpp_file()
    
    # Create a temporary file to store the content
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".rpp")
    temp_file.write(content.encode())
    temp_file.close()
    
    return FileResponse(temp_file.name, filename=filename)

