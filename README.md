# police-data-geocoding
Script for ArcMap for geocoding police data locations as part of a project under UCLA professors [Felipe Goncalves](https://economics.ucla.edu/person/felipe-goncalves/) and [Emily Weisburst](https://luskin.ucla.edu/person/emily-weisburst).

## What does it do?
This script will take a spreadsheet containing **location data** in each row, and split out an identical spreadsheet, but with the [FIPS Code](https://en.wikipedia.org/wiki/FIPS_county_code) for for the county that contains the location listed. 



## Installation in ArcMap
0. Download this [USA Street Address Locator](https://drive.google.com/drive/folders/1UtU3mWGYVMxev5N6ALUmIOEcXHIpFl7d?usp=sharing) (~8 GB) from Google Drive. From what I understand, this is giant database that essentially contains the location of just about every address in the US. Make sure to place this folder **in the same directory as this script file**.
1. If you don't have the Catalog window open, go to **Windows** -> **Catalog** to open it, as it will be very useful for accessing the script.
2. In the Catalog window, navigate to **Toolboxes** -> **MyToolboxes**. If you don't already have a toolbox, right-click on MyToolboxes and navigate to **New** -> **Toolbox**, which will create al Toolbox.tbx file.  
![create a toolbox](images/CreateToolbox.png)
3. Right-click that new Toolbox.tbx file in, navigate to **Add** -> **Script...**  
![add a script](images/AddScript.png)
4. Set a name and description for this script, if you so desire, then click next.  
![Script Dialogue 1](images/SciptDialogue1.png)
5. On the next screen, click the little folder icon next to the **Script File** field to open a file selector dialogue where you should select this file ([ArcMap.py](ArcMap.py)). Then click next.  
![Script Dialogue 2](images/SciptDialogue2.png)
6. Now you will have to set the script parameters. I really wish there was an easy way for me to export this somehow so I don't have to update these instructions, but either way, this part is really important. You have to set these options exactly as I have them set, otherwise the script won't work.  
![setting parameters 1](images/ParameterSettings1.png)
![setting parameters 2](images/ParameterSettings2.png)  
The most important thing other than what's shown here that the parameters **Address or LatLon** and **Table** should be set to required (and the rest set to optional), and for the parameters **X Coord** and **Y Coord**, the property "Filter" should be set to **Value List** (essentially a dropdown menu).  
![setting filter for x,y coordinate](images/FilterSetting.png)
7. Once the parameters are set, head over to the **Validation** tab at the top. You should see some Python code in a big window. Click the **Edit...** button below that window, and a notepad with that code will open.
8. Copy the code from [Validator.py](Validator.py) into this notepad, and save. (Essentially, this script controls how the parameters get set, like as default settings and generating dropdown lists if you need to select certain spreadsheet columns.)
9. Close the notepad, and the code you just pasted should appear in that window.
10. Click OK at the bottom of the dialogue.

## Running the Script
In order to run an ArcMap script, simply navigate to where you imported it (if you followed the previous instructions, it will be in the Catalog window under Toolboxes -> My Toolboxes -> Toolbox.tbx -> *Script Name*).

Double click that script and you will see this menu: ![main script](images/MainScript.PNG)



## Contributing
Pull requests are welcome. Please, I really am new to all this GIS stuff.
