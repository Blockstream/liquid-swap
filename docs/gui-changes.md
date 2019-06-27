# GUI Qt Designer

Liquid Swap Tool GUI was created using Qt5 Designer.
If changes to the layout are required (e.g. adding new windows, buttons, labels),
the following instructions will cover the process to convert designer files (`.ui`) to a python file (`.py`).

### Pre-requisites

Install the following tools:
```
# apt-get install qtcreator pyqt5-dev-tools
```

### Making changes to the Layout

Open the designer file with the Qt Designer program (`designer -qt=5`),
make the desired changes to the layout, and save the file in `.ui` format.

In order for Qt to make paths to images and other files portable, these need to be managed via Qt resources. 
The raw resource file for this project can be found at `/liquidswap/gui/ui/resource.qrc`.

Finally, graphical changes must be converted to python scripts, to do so run:
```
./tools/graphics_to_py.sh
```

If the resources have been modified, run:
```
RESOURCE=1 ./tools/graphics_to_py.sh
```
