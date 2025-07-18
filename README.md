# Prerequisites

## Windows
1. Git - Download from: https://git-scm.com/downloads
2. pyenv - Run the following in PowerShell: `Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"`
 
## Mac
1. brew - Instructions on the homebrew website: https://brew.sh/
2. Git - Download from: https://git-scm.com/downloads

# Installation
Note: we will be installing python version 3.12.9 through pyenv. If you have issues installing, first check if you are getting the correct python version.
1. Make sure you have the appropriate prerequisites installed.
2. Download just the installer for Mac or GitBash(Windows). They are located in the repo, under the extraStuff folder. 
3. Use Explorer or Finder depending on your system type to run the installer script
  Note: On Windows, if asked what graphics card you have, select the amd option
4. If the install completes correctly, you can use the run.sh or run.bat in the ComfyUI directory which is located in the users home directory.
5. Open the workflow (.json) file you are going to use by selecting the Open option under the Workflow dropdown menu
6. If it gives an error popup saying it is missing nodes, "X" out of the popup
7. Click on the Manager button in the top bar
8. Click on `Install Missing Custom Nodes`
9. Install the listed nodes, then hit the Restart button at the bottom of the panel.
10. Once the service has restarted and you have reloaded the webpage, if there are still errors, close the workflow tab (not the browser tab) and re-open the workflow file.
11. To put your OpenAI key in, create a text file named `.env` in the ComfyUI main directory. Add a line (no spaces) that matches the example below:
```
OPENAI_API_KEY="INSERT YOUR KEY HERE"
```


If you are still having issues, try to kill the python process and restart the server.


.env
