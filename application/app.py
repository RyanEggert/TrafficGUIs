#!/usr/bin/env python
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from safety_main import Ui_TransportationSafety


class Organizer(object):
    def __init__(self):
        super(Organizer, self).__init__()


class DisplayImage(object):
    def __init__(self, image, pixmap):
        self._image = None
        self.image = image
        self.pixmap = pixmap
        self.scale_factor = 0  # If 512x512 img and 256x256 pixmap, this is 0.5
        self.compute_scale_factor()

    # @property
    # def image(self):
    #     return self._image

    # @image.setter
    # def image(self, new_image):
    #     try:
    #         self.image_size = (new_image.height(), new_image.width())
    #     except TypeError, e:
    #         print("ERR: Invalid image passed to DisplayImage. Must be QImage.")
    #     else:
    #         self._image = image

    # @image.deleter
    # def image(self):
    #     self._image = None
    #     self.image_size = (None, None)

    def compute_scale_factor(self):
        pix_width = float(self.pixmap.width())
        pix_height = float(self.pixmap.height())
        img_width = float(self.image.width())
        img_height = float(self.image.height())
        print(img_width / pix_width)
        print(img_height / pix_height)
        self.scale_factor = img_width / pix_width

    def tf_pixmap_to_image(self, x_coord, y_coord):
        """
        MapsTransforms pixmap coordinates to unscaled image coordinates. Rounds
        to nearest integer value using Python's built-in round() function.

        EX: If scale_factor = 0.5 and input (44, 21), returns (88, 42)
        """
        sf = float(self.scale_factor)
        x_scaled = round(x_coord / sf)
        y_scaled = round(y_coord / sf)
        return x_scaled, y_scaled

    def tf_image_to_pixmap(self, x_coord, y_coord):
        """
        Transforms image coordinates to scaled pixmap coordinates.

        EX: If scale_factor = 0.5 and input (44, 21), returns (22, 11)
        """
        x_scaled = round(x_coord * self.scale_factor)
        y_scaled = round(y_coord * self.scale_factor)
        return x_scaled, y_scaled

class ImageLabel(QWidget):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)

        # self.zoomSpinBox = QSlider()

        self.filename = None
        self.image = QImage()
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(200, 200)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.currentPoint = QPoint(300,300)
        self.allPoints = []

    @property
    def zoomSpinBox(self):
        return self._zoomSpinBox
    @zoomSpinBox.setter
    def zoomSpinBox(self, new_zsb):
        self._zoomSpinBox = new_zsb
        self._zoomSpinBox.setMinimum(10)
        self._zoomSpinBox.setMaximum(400)
        self._zoomSpinBox.setValue(50)
        self._zoomSpinBox.valueChanged.connect(self.showImage)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.currentPoint = event.pos()
            self.allPoints.append(self.currentPoint)
            self.update()

    def paintEvent(self, event, percent=None):
        painter = QPainter(self)
        pen = QPen(Qt.blue, 7, Qt.SolidLine, Qt.RoundCap)
        painter.drawImage(event.rect(), self.image)
        print "Event", event.rect().width(), event.rect().height()
        print "Image", self.image.width(), self.image.height()
        print "Label", self.imageLabel.width(), self.imageLabel.height()

        # if self.image.isNull():
        #     return
        # if percent is None:
        #     percent = self.zoomSpinBox.value()

        # width = self.image.width() * factor
        # height = self.image.height() * factor
        # image = self.image.scaled(width, height, Qt.KeepAspectRatio)

        # painter.drawImage(event.rect(), self.image)
        # self.showImage()
        painter.setPen(pen)
        for point in self.allPoints:
            painter.drawPoint(point)

    def showImage(self, percent=None):
        pass
        # if self.image.isNull():
        #     return
        # if percent is None:
        #     percent = self.zoomSpinBox.value()
        # factor = percent / 100.0
        # width = self.image.width() * factor
        # height = self.image.height() * factor
        # self.image.scaled(width, height, Qt.KeepAspectRatio)
        # self.imageLabel.setPixmap(QPixmap.fromImage(self.image))

    def loadInitialFile(self):
        settings = QSettings()
        fname = unicode(settings.value("LastFile").toString())
        if fname and QFile.exists(fname):
            self.loadFile(fname)

    def loadFile(self, fname=None):
        if fname is None:
            action = self.sender()
            if isinstance(action, QAction):
                fname = unicode(action.data().toString())
                # if not self.okToContinue():
                #   return
            else:
                return
        if fname:
            self.filename = None
            image = QImage(fname)
            if image.isNull():
                message = "Failed to read %s" % fname
            else:
                # self.addRecentFile(fname)
                self.image = QImage()
                # for action, check in self.resetableActions:
                #   action.setChecked(check)
                self.image = image
                self.filename = fname
                self.showImage()
                self.dirty = False
                message = "Loaded %s" % os.path.basename(fname)

    def fileOpen(self):
        # if not self.okToContinue():
        #   return
        dir = os.path.dirname(self.filename) \
            if self.filename is not None else "."
        formats = ["*.%s" % unicode(format).lower() \
                for format in QImageReader.supportedImageFormats()]
        fname = unicode(QFileDialog.getOpenFileName(self,
                            "Image Changer - Choose Image", dir,
                            "Image files (%s)" % " ".join(formats)))
        if fname:
            self.loadFile(fname)


class MainGUI(QMainWindow):

    def __init__(self):
        super(MainGUI, self).__init__()
        self.ui = Ui_TransportationSafety()
        self.ui.setupUi(self)

        # Experimenting with organizational objects
        self.homography = Organizer()
        self.feature_tracking = Organizer()

        self.aerialImage = ImageLabel()
        self.screenshot = ImageLabel()

        self.aerialImage.zoomSpinBox = self.ui.homography_hslider_zoom_aerial_image
        self.screenshot.zoomSpinBox = self.ui.homography_hslider_zoom_camera_image

        # self.ui.homography_camera_scroll_area.layout().addWidget(self.screenshot)
        # self.ui.homography_aerial_scroll_area.layout().addWidget(self.aerialImage)

        self.ui.scrollArea.setWidget(self.aerialImage)
        self.ui.scrollArea_2.setWidget(self.screenshot)

        # Connect Menu actions
        self.ui.actionOpen_Project.triggered.connect(self.open_project)
        # self.ui.actionLoad_Image.triggered.connect(self.open_image)
        self.ui.actionAdd_Replace_Aerial_Image.triggered.connect(self.homography_open_image_aerial)
        self.ui.actionAdd_Replace_Aerial_Image.triggered.connect(self.homography_open_image_camera)
        self.ui.main_tab_widget.setCurrentIndex(0)  # Start on the first tab

        # Connect button actionst
        self.ui.homography_button_open_aerial_image.clicked.connect(self.aerialImage.fileOpen)  # TODO: New method. Check which tab is open. Move to homography tab if not already there. Then call open_image_aerial.
        self.ui.homography_button_open_camera_image.clicked.connect(self.screenshot.fileOpen)

        # Connect back + continue buttons
        self.ui.homography_continue_button.clicked.connect(self.show_next_tab)
        self.ui.feature_tracking_continue_button.clicked.connect(self.show_next_tab)
        self.ui.feature_tracking_back_button.clicked.connect(self.show_prev_tab)

        # self.ui.track_image.mousePressEvent = self.get_image_position
        self.show()

        

    def show_next_tab(self):
        curr_i = self.ui.main_tab_widget.currentIndex()
        self.ui.main_tab_widget.setCurrentIndex(curr_i + 1)

    def show_prev_tab(self):
        curr_i = self.ui.main_tab_widget.currentIndex()
        self.ui.main_tab_widget.setCurrentIndex(curr_i - 1)

    def open_project(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Open Project', '/home')
        print(fname)

    def homography_open_image_camera(self):
        """Opens a file dialog, allowing user to select an camera image file.

        Creates a QImage object and QPixmap from the filename of an camera image
        selected by the user in a popup file dialog menu.
        """
        qi = self.open_image_fd(dialog_text="Select camera image...")
        self.homography.image_aerial = qi
        self.homography.pixmap_aerial = QPixmap.fromImage(qi)
        # Do other stuff
        # self.homography_show_image('aerial'), etc. ?

    def homography_open_image_aerial(self):
        """Opens a file dialog, allowing user to select an aerial image file.

        Creates a QImage object and QPixmap from the filename of an aerial image
        selected by the user in a popup file dialog menu.
        """
        qi = self.open_image_fd(dialog_text="Select aerial image...")
        self.homography.image_aerial = qi
        self.homography.pixmap_aerial = QPixmap.fromImage(qi)
        # Do other stuff
        # self.homography_show_image('aerial'), etc. ?

    def open_image_fd(self, dialog_text="Open Image", default_dir=""):
        """Opens a file dialog, allowing user to select an image file.

        Creates a QImage object from the filename selected by the user in the
        popup file dialog menu.

        Args:
            dialog_text [Optional(str.)]: Text to prompt user with in open file
                dialog. Defaults to "Open Image".
            default_dir [Optional(str.)]: Path of the default directory to open
                the file dialog box to. Defaults to "".

        Returns:
            QImage: Image object created from selected image file.
        """
        fname = QFileDialog.getOpenFileName(self, dialog_text, default_dir)  # TODO: Filter to show only image files
        image = QImage(fname)
        return image

    # def open_image(self):
    #     fname = QFileDialog.getOpenFileName(self, 'Open Project', '')
    #     print(fname)
    #     tracking_image = QImage(fname)
    #     pixmap = QPixmap.fromImage(tracking_image)
    #     pixmap = pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
    #     self._tracking_image = DisplayImage(tracking_image, pixmap)
    #     self.ui.track_image.setPixmap(pixmap)

    def get_image_position(self, event):
        print(event.pos())
        print(self._tracking_image.image.pixel(event.x(), event.y()))


def main():
    app = QApplication(sys.argv)
    ex = MainGUI()
    # print(dir(ex.ui))  # Uncomment to show structure of ui object
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
