# im_alignement_tool

Small tool to superimpose two images.
The images realignement is based on the fact that both images match at least at 60%. The smallest image is set as template to match in the other one.
Based on template matching implemented in OpenCV.
This tool is runnable from interface.py or directly in differentiel.py script.

A small GUI is developped using PySide2 (Qt free bundle) and Qt Designer (realign.ui)

An executable could be create using pyinstaller:
  pyinstaller --add-data "realign.ui";. --hidden-import PySide.QtXml differentiel.py
  
