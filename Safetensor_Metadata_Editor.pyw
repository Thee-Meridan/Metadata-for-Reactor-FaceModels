#!/usr/bin/env python
import sys, os, subprocess

# --- Auto-install required packages if not already installed ---
def install_if_needed(package_name, import_name=None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_if_needed("PyQt5")
install_if_needed("safetensors")

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QListWidget, QMessageBox, QPlainTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from safetensors.torch import safe_open, save_file

# --- Custom QPlainTextEdit that saves on Enter ---
class SaveOnEnterTextEdit(QPlainTextEdit):
    # Emit a signal when Enter/Return is pressed
    saveTriggered = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Instead of inserting a newline, trigger save.
            self.saveTriggered.emit()
        else:
            super().keyPressEvent(event)

# --- Main Window: Two-panel interface with multi-selection ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Safetensors Metadata Editor")
        self.resize(1000, 600)
        self.lastDirectory = os.getcwd()
        self.selectedFilePaths = []  # stores full paths for selected files
        self.currentFilePath = None  # currently loaded file for metadata editing
        self.initUI()

    def initUI(self):
        centralWidget = QWidget()
        mainLayout = QHBoxLayout()  # Left: file list; Right: metadata editor

        # Left Panel: Directory Browser and File List
        leftPanel = QWidget()
        leftLayout = QVBoxLayout()
        self.dirButton = QPushButton("Select Directory")
        self.dirButton.clicked.connect(self.selectDirectory)
        leftLayout.addWidget(self.dirButton)

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QListWidget.ExtendedSelection)
        self.listWidget.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        leftLayout.addWidget(self.listWidget)
        leftPanel.setLayout(leftLayout)

        # Right Panel: Metadata Editor takes the entire panel.
        rightPanel = QWidget()
        rightLayout = QVBoxLayout()
        # Instead of QLineEdit, we now use our custom multi-line text edit.
        self.metadataEdit = SaveOnEnterTextEdit()
        self.metadataEdit.setPlaceholderText("Edit 'prompt' metadata here. Press Enter to save.")
        # Connect our custom signal to the save method.
        self.metadataEdit.saveTriggered.connect(self.saveMetadata)
        rightLayout.addWidget(self.metadataEdit, stretch=1)
        
        # Buttons at the bottom
        buttonLayout = QHBoxLayout()
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.saveMetadata)
        buttonLayout.addWidget(self.saveButton)
        
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancelEditing)
        buttonLayout.addWidget(self.cancelButton)
        
        rightLayout.addLayout(buttonLayout)
        rightPanel.setLayout(rightLayout)

        mainLayout.addWidget(leftPanel, 1)
        mainLayout.addWidget(rightPanel, 2)
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def selectDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.lastDirectory)
        if directory:
            self.lastDirectory = directory
            self.populateFileList(directory)

    def populateFileList(self, directory):
        self.listWidget.clear()
        files = [f for f in os.listdir(directory) if f.lower().endswith(".safetensors")]
        files.sort()
        for f in files:
            self.listWidget.addItem(f)

    def onSelectionChanged(self, selected, deselected):
        # Update selection: get full paths for selected items.
        items = self.listWidget.selectedItems()
        self.selectedFilePaths = [os.path.join(self.lastDirectory, item.text()) for item in items]
        if len(self.selectedFilePaths) == 1:
            self.currentFilePath = self.selectedFilePaths[0]
            self.loadMetadata(self.currentFilePath)
        elif len(self.selectedFilePaths) > 1:
            # Multiple files: clear the edit field, set a placeholder.
            self.currentFilePath = None
            self.metadataEdit.setPlainText("")
            self.metadataEdit.setPlaceholderText("Multiple files selected – editing here will override metadata for all.")
        else:
            self.currentFilePath = None
            self.metadataEdit.setPlainText("")
            self.metadataEdit.setPlaceholderText("Edit 'prompt' metadata here...")

    def loadMetadata(self, file_path):
        try:
            with safe_open(file_path, framework="pt") as f:
                metadata = f.metadata() or {}
            prompt_value = metadata.get("prompt", "")
            self.metadataEdit.setPlainText(prompt_value)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load metadata from:\n{file_path}\nError: {e}")

    def saveMetadata(self):
        if not self.selectedFilePaths:
            return
        new_prompt = self.metadataEdit.toPlainText().strip()
        errors = []
        for file_path in self.selectedFilePaths:
            try:
                with safe_open(file_path, framework="pt") as f:
                    tensors = {k: f.get_tensor(k).clone() for k in f.keys()}
                    metadata = f.metadata() or {}
                metadata["prompt"] = new_prompt
                save_file(tensors, file_path, metadata=metadata)
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {e}")
        if errors:
            QMessageBox.critical(self, "Error", "Failed to save metadata for:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "Success", "Metadata saved successfully!")
    
    def cancelEditing(self):
        # Reload metadata for single selection, or clear if multiple
        if len(self.selectedFilePaths) == 1:
            self.loadMetadata(self.selectedFilePaths[0])
        else:
            self.metadataEdit.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))  # Increase global font size by roughly 33%
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
