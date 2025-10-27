from PySide6.QtWidgets import QListWidgetItem

class Webhook(QListWidgetItem):
    def __init__(self, parent=None, webhook_id=None, name="", url="", method="POST", 
                 content_type="application/json", auth_type="None", auth_header="", 
                 auth_value="", custom_headers=None):
        super().__init__(name, parent)
        self._parent = parent
        self.webhook_id = webhook_id if webhook_id is not None else id(self)
        self.setName(name)
        self.setUrl(url)
        self.setMethod(method)
        self.setContentType(content_type)
        self.setAuthType(auth_type)
        self.setAuthHeader(auth_header)
        self.setAuthValue(auth_value)
        self.custom_headers = custom_headers if custom_headers is not None else {}

    def setName(self, val):
        self.name = val
        self.setText(val)

    def setUrl(self, val):
        self.url = val

    def setMethod(self, val):
        self.method = val

    def setContentType(self, val):
        self.content_type = val

    def setAuthType(self, val):
        self.auth_type = val

    def setAuthHeader(self, val):
        self.auth_header = val

    def setAuthValue(self, val):
        self.auth_value = val

    def serialize(self):
        hash = {
            "webhook_id": self.webhook_id,
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "content_type": self.content_type,
            "auth_type": self.auth_type,
            "auth_header": self.auth_header,
            "auth_value": self.auth_value,
            "custom_headers": self.custom_headers
        }
        return hash

