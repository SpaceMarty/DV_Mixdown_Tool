#!/usr/bin/env python

from datetime import datetime
import os.path, json
# from python_get_resolve import GetResolve


# GET RESOLVE ITEMS
# ///////////////////////////////////////////////////////////////////////////////////////
# resolve             = GetResolve()
projectManager      = resolve.GetProjectManager()
media_storage       = resolve.GetMediaStorage()
project             = projectManager.GetCurrentProject()
timeline            = project.GetCurrentTimeline()
timeline_name       = timeline.GetName().replace(' ', '_')
fps                 = project.GetSetting('timelineFrameRate')
track_count         = timeline.GetTrackCount("video")
current_page        = resolve.GetCurrentPage()
media_pool          = project.GetMediaPool()
root_folder         = media_pool.GetRootFolder()
bin_list            = root_folder.GetSubFolderList()


# GET FILE NAME AND PATH VARIABLES
# ///////////////////////////////////////////////////////////////////////////////////////
now                 = datetime.now()
dt_string           = now.strftime("%d-%m-%Y_%H-%M-%S")
mixdown_name        = timeline_name + "_" + "MIXDOWN" + "_(" + dt_string + ")"
home                = os.path.expanduser('~')

# LOOK FOR PREVIOUSLY SAVED FOLDER PATH
# //////////////////////////////////////////////////////////////////////////////////////
try:    
    with open(home + "/Davinci_Script_Data.json", "r") as memory:
        settings = json.load(memory)
        selectedPath = settings["mixdown_path"]
except:
    settings = {}
    selectedPath = "Select a location..."


# USER INTERFACE
# /////////////////////////////////////////////////////////////////////////////////////

ui                  = fu.UIManager
disp                = bmd.UIDispatcher(ui)


# CREATE A WINDOW 
dlg = disp.AddWindow({ "WindowTitle": "Video Mixdown v1.0", 
                      "ID": "MyWin", 
                      "Geometry": [ 600, 400, 600, 80 ],},
                     
# ADD UI ELEMENTS HERE
    [
        ui.VGroup({"ID": "root", 
                   "Spacing": 10,
                   "Weight": 1}, # The spaces between each item
        [
            # Version Label
            # ui.Label({"ID": "Empty",
            #           "Text": "Video Mixdown v1.0",
            #           "Weight": 0}),
            
            # First Horizontal Row
            ui.HGroup({"ID": "H1",
                       "Spacing": 10,
                       "Weight": 1},
                      [
                        ui.Label({"ID": "FolderLabel",
                                  "Text": "Folder Path:",
                                  "Weight": 0.25}),
                        
                        ui.LineEdit({ "ID": "LineTxt", 
                                    "Text": selectedPath, 
                                    "Weight": 1}),                 
                      ]),
            # Second Horizontal Row
            ui.HGroup({"ID": "H2",
                       "Spacing": 10,
                       "Weight": 1},
                      [            
                        ui.Button({ "ID": "BrowseButton", 
                                "Text": "Browse", 
                                "Weight": 0}),
                        
                        ui.Button({ "ID": "CancelButton", 
                                "Text": "Cancel", 
                                "Weight": 0}),
                                    
                        ui.Button({ "ID": "GoButton",
                                "Text": "Go!", 
                                "Weight": 0,
                                "Checkable": True,}),
                        
                        ui.Label({"ID": "Processing",
                                  "Text": "Processing...",
                                  "Hidden": True,
                                  "Weight": 0.25}),                        
                        
                        ui.Label({"ID": "Empty",
                                "Weight": 1 }),
                        ])
        ]),
    ])

# GUI ELEMENT EVENT FUNCTIONS
# ///////////////////////////////////////////////////////////////////////////////////
 
itm = dlg.GetItems()

# THE WINDOW WAS CLOSED
def _func(ev):
    disp.ExitLoop()
dlg.On.MyWin.Close = _func
 
# CANCEL BUTTON IS CLICKED
def _func(ev):
    disp.ExitLoop()
dlg.On.CancelButton.Clicked = _func

# OK BUTTON IS CLICKED
def _func(ev):
    print("OK clicked")
    disp.ExitLoop()
    dlg.On.OKButton.Clicked = _func

# BROWSE BUTTON WAS CLICKED
def _func(ev):
    global selectedPath
    print('Browse Button Clicked')
    selectedPath = fu.RequestDir()
    if selectedPath != None:
        print("[Path]" + selectedPath)
        itm["LineTxt"].Text = selectedPath
        settings["mixdown_path"] = selectedPath
        try:
            with open(home + "/DaVinci_Script_Data.json", "w") as memory:
                json.dump(settings, memory, indent = 2)
        except:
            pass
dlg.On.BrowseButton.Clicked = _func

# GO BUTTON WAS CLICKED
def _func(ev):
    print("Go Button pressed")
    itm["BrowseButton"].Hidden = True
    itm["Processing"].Hidden = False
    itm["GoButton"].Hidden = True
    Go()
dlg.On.GoButton.Clicked = _func


# FUNCTION OF THE 'GO' BUTTON
# //////////////////////////////////////////////////////////////////////////////////////
def Go():
    global mixdown_file
    preset = project.LoadRenderPreset("Mixdown")
    # IF MIXDOWN PRESET EXITS, LAUNCHES RENDER FUNCTION
    if preset == True:
        print("Mixdown render preset found")
        render()
        itm["GoButton"].Text = "Go!"
    # IF MIXDOWN PRESET DOES NOT EXIST, PROMPTS USER TO MAKE ONE, THEN EXITS.
    else:
        print("Mixdown render preset NOT found")
        resolve.OpenPage("Edit") 
        disp.ExitLoop()
        dlg = disp.AddWindow({  "WindowTitle": "Warning!", 
                                "ID": "Warning",
                                "Geometry": [ 100, 100, 600, 100 ]}, 
                                [
                                ui.VGroup({ "ID": "root2", 
                                            "Spacing": 10,
                                            "Weight": 1}, 
                                            [
                                            ui.Label({  "ID": "WarningText",
                                                        "Text": "'Mixdown' preset not found! \nYour must create a preset called 'Mixdown' on the Deliver page.",
                                                        "Weight": 0.25}),
                                            
                                            ui.Button({ "ID": "OKButton", 
                                                        "Text": "OK", 
                                                        "Weight": 0}),
                                            ])
                                ])
        # OK Button Clicked
        def _func(ev):
            disp.ExitLoop()
        dlg.On.OKButton.Clicked = _func

            
        dlg.Show()
        disp.RunLoop()
        dlg.Hide()


# RENDER FUNCTION
# ////////////////////////////////////////////////////////////////////////////////////////////        
def render():
    print("Render process started")
    resolve.OpenPage("Deliver") 
    project.SetRenderSettings({"CustomName": mixdown_name, "TargetDir": selectedPath})
    project.DeleteAllRenderJobs()
    project.AddRenderJob()

    in_frame            = project.GetRenderJobList()[0]['MarkIn']
    out_frame           = project.GetRenderJobList()[0]['MarkOut']
    extention           = project.GetRenderJobList()[0]['OutputFilename'].rsplit(".", 1)[1]

    project.StartRendering()

    # Wait for Render to Finish
    rendering           = project.IsRenderingInProgress()
    while rendering:
        rendering       = project.IsRenderingInProgress()
    resolve.OpenPage("Edit")


    # IMPORT EXPORTED MIXDOWN
    # ///////////////////////////////////////////////////////////////////////////////////////
    mixdown_file        = selectedPath + "\\" + mixdown_name + '.' + extention



    # Look for Mixdowns bin and create one if it doesn't exist. Then imports the mixdown
    media_pool.SetCurrentFolder(root_folder)
    bins = []
    for bin in bin_list:
        bin_name = (bin.GetName()).lower()
        bins.append(bin_name.lower())
        if bin.GetName().lower() == "mixdowns":
            media_pool.SetCurrentFolder(bin)
    if "mixdowns" in bins:
        pass
    else:    
        media_pool.AddSubFolder(root_folder, "Mixdowns")
            
    mixdown_clip        = media_pool.ImportMedia([mixdown_file])
    
    disp.ExitLoop()

# LAUNCHES UI
# ///////////////////////////////////////////////////////////////////////////////////////////////    
dlg.Show()
disp.RunLoop()
dlg.Hide()


# TO DO LIST

# GENERATE MIXDOWN PRESET BASED ON USER INPUT
