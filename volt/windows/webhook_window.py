from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QLineEdit, QPushButton, 
                                QLabel, QComboBox, QTextEdit, QGroupBox, QVBoxLayout)
from PySide6.QtCore import Qt

from volt.models.webhook import Webhook

class WebhookWindow(QWidget):
    def __init__(self, parent, webhook=None):
        super(WebhookWindow, self).__init__()

        self.setWindowTitle("Webhook Editor")
        self._parent = parent
        self._webhook = webhook or Webhook()

        geo = self.geometry()
        geo.moveCenter(self.screen().availableGeometry().center())
        self.setGeometry(geo)
        self.setMinimumWidth(600)

        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # Name
        self.name_input = QLineEdit(self)
        self.name_input.setText(self._webhook.name)
        self.name_input.setPlaceholderText("e.g., Discord Notifications")
        self.layout.addWidget(QLabel("Name:"), 0, 0)
        self.layout.addWidget(self.name_input, 0, 1, 1, 2)

        # URL
        self.url_input = QLineEdit(self)
        self.url_input.setText(self._webhook.url)
        self.url_input.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.layout.addWidget(QLabel("URL:"), 1, 0)
        self.layout.addWidget(self.url_input, 1, 1, 1, 2)

        # HTTP Method
        self.method_input = QComboBox(self)
        self.method_input.addItems(["POST", "GET", "PUT", "PATCH"])
        self.method_input.setCurrentText(self._webhook.method)
        self.layout.addWidget(QLabel("Method:"), 2, 0)
        self.layout.addWidget(self.method_input, 2, 1, 1, 2)

        # Content-Type
        self.content_type_input = QComboBox(self)
        self.content_type_input.addItems([
            "application/json",
            "application/x-www-form-urlencoded",
            "text/plain"
        ])
        self.content_type_input.setCurrentText(self._webhook.content_type)
        self.content_type_input.setEditable(True)
        self.layout.addWidget(QLabel("Content-Type:"), 3, 0)
        self.layout.addWidget(self.content_type_input, 3, 1, 1, 2)

        # Authentication Section
        auth_group = QGroupBox("Authentication")
        auth_layout = QGridLayout()

        self.auth_type_input = QComboBox(self)
        self.auth_type_input.addItems(["None", "Bearer Token", "API Key", "Custom Header"])
        self.auth_type_input.setCurrentText(self._webhook.auth_type)
        self.auth_type_input.currentTextChanged.connect(self.onAuthTypeChanged)
        auth_layout.addWidget(QLabel("Auth Type:"), 0, 0)
        auth_layout.addWidget(self.auth_type_input, 0, 1)

        self.auth_header_label = QLabel("Header Name:")
        self.auth_header_input = QLineEdit(self)
        self.auth_header_input.setText(self._webhook.auth_header)
        self.auth_header_input.setPlaceholderText("e.g., X-API-Key")
        auth_layout.addWidget(self.auth_header_label, 1, 0)
        auth_layout.addWidget(self.auth_header_input, 1, 1)

        self.auth_value_label = QLabel("Value:")
        self.auth_value_input = QLineEdit(self)
        self.auth_value_input.setText(self._webhook.auth_value)
        self.auth_value_input.setPlaceholderText("Your token/key")
        self.auth_value_input.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.auth_value_label, 2, 0)
        auth_layout.addWidget(self.auth_value_input, 2, 1)

        auth_group.setLayout(auth_layout)
        self.layout.addWidget(auth_group, 4, 0, 1, 3)

        # Custom Headers Section
        headers_group = QGroupBox("Custom Headers (JSON format)")
        headers_layout = QVBoxLayout()
        
        self.custom_headers_input = QTextEdit(self)
        self.custom_headers_input.setPlaceholderText('{\n  "X-Custom-Header": "value",\n  "Another-Header": "value"\n}')
        self.custom_headers_input.setMaximumHeight(100)
        
        # Convert dict to JSON string for display
        if self._webhook.custom_headers:
            import json
            self.custom_headers_input.setPlainText(json.dumps(self._webhook.custom_headers, indent=2))
        
        headers_layout.addWidget(self.custom_headers_input)
        headers_group.setLayout(headers_layout)
        self.layout.addWidget(headers_group, 5, 0, 1, 3)

        # Help text
        help_label = QLabel("Tip: Use variables like {S}, {C}, {1}, {2} in your trigger's webhook message")
        help_label.setStyleSheet("color: gray; font-style: italic;")
        help_label.setWordWrap(True)
        self.layout.addWidget(help_label, 6, 0, 1, 3)

        # Buttons
        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.saveWebhook)

        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelWebhook)

        self.button_layout = QGridLayout()
        self.button_layout.addWidget(self.saveBtn, 0, 0)
        self.button_layout.addWidget(self.cancelBtn, 0, 1)

        self.layout.addLayout(self.button_layout, 7, 0, 1, 3, alignment=Qt.AlignRight)

        self.setLayout(self.layout)
        
        # Initialize auth field visibility
        self.onAuthTypeChanged(self._webhook.auth_type)

    def onAuthTypeChanged(self, auth_type):
        """Show/hide auth fields based on selected auth type"""
        if auth_type == "None":
            self.auth_header_label.hide()
            self.auth_header_input.hide()
            self.auth_value_label.hide()
            self.auth_value_input.hide()
        elif auth_type == "Bearer Token":
            self.auth_header_label.hide()
            self.auth_header_input.hide()
            self.auth_value_label.setText("Token:")
            self.auth_value_label.show()
            self.auth_value_input.show()
            self.auth_value_input.setPlaceholderText("Your bearer token")
        elif auth_type == "API Key":
            self.auth_header_label.hide()
            self.auth_header_input.hide()
            self.auth_value_label.setText("API Key:")
            self.auth_value_label.show()
            self.auth_value_input.show()
            self.auth_value_input.setPlaceholderText("Your API key")
        elif auth_type == "Custom Header":
            self.auth_header_label.show()
            self.auth_header_input.show()
            self.auth_value_label.setText("Value:")
            self.auth_value_label.show()
            self.auth_value_input.show()
            self.auth_value_input.setPlaceholderText("Header value")

    def saveWebhook(self):
        self._webhook.setName(self.name_input.text())
        self._webhook.setUrl(self.url_input.text())
        self._webhook.setMethod(self.method_input.currentText())
        self._webhook.setContentType(self.content_type_input.currentText())
        self._webhook.setAuthType(self.auth_type_input.currentText())
        self._webhook.setAuthHeader(self.auth_header_input.text())
        self._webhook.setAuthValue(self.auth_value_input.text())
        
        # Parse custom headers JSON
        try:
            import json
            headers_text = self.custom_headers_input.toPlainText().strip()
            if headers_text:
                self._webhook.custom_headers = json.loads(headers_text)
            else:
                self._webhook.custom_headers = {}
        except json.JSONDecodeError:
            # If invalid JSON, just use empty dict
            self._webhook.custom_headers = {}
        
        self._parent.webhook_list.addItem(self._webhook)
        QApplication.instance().save()
        self.destroy()

    def cancelWebhook(self):
        self.destroy()

    def destroy(self):
        self.name_input.setText("")
        self.url_input.setText("")
        self.close()
        self.deleteLater()

