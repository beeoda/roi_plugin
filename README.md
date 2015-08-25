# ROI Explorer
QGIS Plugin for exploring the spectral signatures of ROIs

<img src="./docs/ROITool_demo.png" width="400">

## TODO
- [x] Implement zonal stats code
- [x] Implement plot save dialog
- [ ] Add help
    * Include demo as a GIF
- [ ] Add "ROI Explorer" menu with items that restores/opens plugin window and shows a help/about page
- [ ] Rebrand plugin
    * Rename everything from "ROI Tool" to "ROI Explorer"
- [x] Icon
- [ ] Upload to QGIS repository
- [ ] Implement stats export dialog
- [ ] Enable dynamic UI layout changes from "portrait" to "landscape"
    + Monitor `QDockWidget.dockLocationChanged`
    + If position is left/right, keep portrait
    + If position is top/bottom, switch to landscape
    + Accomplish by switching `QDialog` between vertical and horizontal layouts
    + Blockers:
        * Make layout changes with splitter
        * Ensure certain UI elements can't be squashed (e.g., only plot or table can collapse) 
