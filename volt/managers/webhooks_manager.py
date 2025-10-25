from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QListWidget
from PySide6.QtCore import Qt

from volt.windows import webhook_window
from volt.models.webhook import Webhook

class WebhooksManager(QWidget):
    def __init__(self, parent):
        super(WebhooksManager, self).__init__()

        self._parent = parent
        self.webhooks = []  # Store webhook objects for easy lookup

        self.button = QPushButton("Add Webhook")
        self.buttona = QPushButton("Edit Webhook")
        self.buttonb = QPushButton("Remove Webhook")

        self.buttona.setEnabled(False)
        self.buttonb.setEnabled(False)

        self.button.clicked.connect(self.addWebhookWindow)
        self.buttona.clicked.connect(self.editWebhookWindow)
        self.buttonb.clicked.connect(self.removeWebhookWindow)

        # Add buttons to parent layout (will be added in home_manager)
        # Layout position will be set by home_manager

        self.webhook_list = QListWidget()
        self.webhook_list.itemClicked.connect(self.webhookListItemClicked)
        self.webhook_list.doubleClicked.connect(self.editWebhookWindow)

    def load(self, json):
        for webhook_data in json:
            webhook = Webhook(
                self.webhook_list,
                webhook_id=webhook_data.get("webhook_id"),
                name=webhook_data.get("name", ""),
                url=webhook_data.get("url", ""),
                method=webhook_data.get("method", "POST"),
                content_type=webhook_data.get("content_type", "application/json"),
                auth_type=webhook_data.get("auth_type", "None"),
                auth_header=webhook_data.get("auth_header", ""),
                auth_value=webhook_data.get("auth_value", ""),
                custom_headers=webhook_data.get("custom_headers", {})
            )
            self.webhooks.append(webhook)

    def serialize(self):
        webhooks = []
        for i in range(self.webhook_list.count()):
            item = self.webhook_list.item(i)
            webhooks.append(item.serialize())
        return webhooks

    def editWebhookWindow(self, item):
        current_item = self.webhook_list.currentItem()
        self.addWebhookWindow(current_item)

    def addWebhookWindow(self, item=None):
        self.webhook_window = webhook_window.WebhookWindow(self, item)
        self.webhook_window.show()

    def removeWebhookWindow(self):
        item = self.webhook_list.currentItem()
        if item:
            # Remove from webhooks list
            if item in self.webhooks:
                self.webhooks.remove(item)
            self.webhook_list.takeItem(self.webhook_list.row(item))
            QApplication.instance().save()

    def webhookListItemClicked(self, item):
        self.button.setEnabled(True)
        self.buttona.setEnabled(True)
        self.buttonb.setEnabled(True)

    def getWebhookById(self, webhook_id):
        """Get webhook by ID for trigger execution"""
        for i in range(self.webhook_list.count()):
            webhook = self.webhook_list.item(i)
            if webhook.webhook_id == webhook_id:
                return webhook
        return None

    def getWebhookByName(self, name):
        """Get webhook by name for trigger execution"""
        for i in range(self.webhook_list.count()):
            webhook = self.webhook_list.item(i)
            if webhook.name == name:
                return webhook
        return None

