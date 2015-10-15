import ScreenCloud
from PythonQt.QtCore import QFile, QSettings
from PythonQt.QtGui import QDesktopServices, QMessageBox
from PythonQt.QtUiTools import QUiLoader
import time, requests

class UguuUploader():
    def __init__(self):
        self.uil = QUiLoader()
        self.loadSettings()

    def isConfigured(self):
        return True

    def loadSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("uguu.se")
        
        self.nameFormat = settings.value("name-format", "screenshot-%H-%M-%S")
        self.copyLink = settings.value("copy-link", "true") in ["true", True]

        settings.endGroup()
        settings.endGroup()

    def saveSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("uguu.se")
        
        settings.setValue("name-format", self.settingsDialog.group_name.input_name.text)
        settings.setValue("copy-link", self.settingsDialog.group_clipboard.checkbox_copy_link.checked)
        
        settings.endGroup()
        settings.endGroup()

    def getFilename(self):
        self.loadSettings()
        return ScreenCloud.formatFilename(self.nameFormat)

    def showSettingsUI(self, parentWidget):
        self.parentWidget = parentWidget
        self.settingsDialog = self.uil.load(QFile(workingDir + "/settings.ui"), parentWidget)
        self.settingsDialog.group_name.input_name.connect("textChanged(QString)", self.nameFormatEdited)
        self.settingsDialog.connect("accepted()", self.saveSettings)
        self.updateUi()
        self.settingsDialog.open()

    def updateUi(self):
        self.loadSettings()
        self.settingsDialog.group_name.input_name.setText(self.nameFormat)
        self.settingsDialog.group_clipboard.checkbox_copy_link.setChecked(self.copyLink)

    def upload(self, screenshot, name):
        self.loadSettings()
        tmpFilename = QDesktopServices.storageLocation(QDesktopServices.TempLocation) + "/" + ScreenCloud.formatFilename(str(time.time()))
        screenshot.save(QFile(tmpFilename), ScreenCloud.getScreenshotFormat())
        data = {"name": name}
        files = {"file": open(tmpFilename, "rb")} 
        
        try:
            response = requests.post("http://uguu.se/api.php?d=upload-tool", data=data, files=files)
            response.raise_for_status()
            if self.copyLink:
                ScreenCloud.setUrl(response.text)
        except RequestException as e:
            ScreenCloud.setError("Failed to upload to Uguu.se: " + e.message)
            return False
        
        return True

    def nameFormatEdited(self, nameFormat):
        self.settingsDialog.group_name.label_example.setText(ScreenCloud.formatFilename(nameFormat, False))
