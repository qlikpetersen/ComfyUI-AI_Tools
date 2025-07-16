# Prerequisites

## Windows
1. Git - Download from: https://git-scm.com/downloads
2. pyenv - Run the following in PowerShell: `Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"`
 
## Mac
1. Git - Download from: https://git-scm.com/downloads
2. brew - Instructions on the homebrew website: https://brew.sh/

# Installation
Note: we will be installing python version 3.12.9 through pyenv. If you have issues installing, first check if you are getting the correct python version.
1. Make sure you have the appropriate prerequisites installed.
2. Download the installer for Mac or GitBash(Windows). They are located in the repo, under the extraStuff folder. 
3. Open a Terminal or git-bash window, depending on your system type, and run the installer
    Hint: if you are in the directory it is at, you need to run it like the following example: `./install-mac.sh`
4. If the install completes correctly, you can use the run.sh or run.bat in the ComfyUI directory which is located in the users home directory.
5. If using the normal workflow, manually install the `anynode` package. Instructions for this are below.

# Getting unknown nodes
If you load a workflow and some of the nodes are not found. Use the following procedure and information to help solve the issue.

1. Click on the Manager button in the top bar
2. Click on `Install Missing Custom Nodes`
3. Install the listed nodes, then the Restart button at the bottom of the panel.

If that does not solve it, you can look at the installed packages, and install other packages in the manager GUI under `Custom Nodes Manager`

Re-open the workflow
.env
