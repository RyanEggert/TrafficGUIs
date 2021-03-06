# zoomslider.py
from PyQt4 import QtGui


class ZoomSlider(QtGui.QSlider):
    """Slider used for zooming a HomographyView or a HomographyResultView.
    """
    def __init__(self, parent):
        super(ZoomSlider, self).__init__(parent)
        self.zoom_target = None  # QGraphicsView
        self.zoom_increment = .02
        self.valueChanged.connect(self.valueChanged_handler)
        self.prev_value = self.value()
        self.zoom_percentage = 1

    def valueChanged_handler(self):
        if self.zoom_target is None:
            self.setValue(100)  # If no target set, do not manipulate slider.
            return
        elif not self.zoom_target.image_loaded:
            self.setValue(100)
            return
        slider_val = self.value()
        desired_percentage = slider_val / 100.
        scale = desired_percentage / self.zoom_percentage
        self.zoom_percentage = desired_percentage
        self.zoom_target.scale(scale, scale)
