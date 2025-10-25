import requests
import json
from threading import Thread

class WebhookExecutor:
    """Handles sending HTTP requests to webhooks"""
    
    @staticmethod
    def send_webhook(webhook, message, async_mode=True):
        """
        Send a webhook request
        
        Args:
            webhook: Webhook model object with url, method, auth settings, etc.
            message: The processed message to send (after variable substitution)
            async_mode: If True, send in background thread (default: True)
        """
        if async_mode:
            # Send in background thread to avoid blocking the UI
            thread = Thread(target=WebhookExecutor._send_webhook_sync, args=(webhook, message))
            thread.daemon = True
            thread.start()
        else:
            WebhookExecutor._send_webhook_sync(webhook, message)
    
    @staticmethod
    def _send_webhook_sync(webhook, message):
        """
        Synchronously send webhook request
        
        Args:
            webhook: Webhook model object
            message: The message to send
        """
        try:
            # Prepare headers
            headers = {}
            
            # Set Content-Type
            if webhook.content_type:
                headers['Content-Type'] = webhook.content_type
            
            # Add authentication
            if webhook.auth_type == "Bearer Token" and webhook.auth_value:
                headers['Authorization'] = f'Bearer {webhook.auth_value}'
            elif webhook.auth_type == "API Key" and webhook.auth_value:
                headers['Authorization'] = webhook.auth_value
            elif webhook.auth_type == "Custom Header" and webhook.auth_header and webhook.auth_value:
                headers[webhook.auth_header] = webhook.auth_value
            
            # Add custom headers
            if webhook.custom_headers:
                headers.update(webhook.custom_headers)
            
            # Prepare payload based on content type
            if webhook.content_type == "application/json":
                # For JSON, wrap message in a standard format
                # Discord/Slack webhooks typically expect {"content": "message"}
                # Try to parse message as JSON first, otherwise wrap it
                try:
                    payload = json.loads(message)
                except (json.JSONDecodeError, TypeError):
                    # If message is not JSON, wrap it
                    payload = {"content": message}
                
                response = requests.request(
                    method=webhook.method,
                    url=webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
            elif webhook.content_type == "application/x-www-form-urlencoded":
                # For form data
                payload = {"message": message}
                response = requests.request(
                    method=webhook.method,
                    url=webhook.url,
                    data=payload,
                    headers=headers,
                    timeout=10
                )
            else:
                # For plain text or other types
                response = requests.request(
                    method=webhook.method,
                    url=webhook.url,
                    data=message,
                    headers=headers,
                    timeout=10
                )
            
            # Log response
            if response.status_code >= 200 and response.status_code < 300:
                print(f"Webhook sent successfully to {webhook.name}: {response.status_code}")
            else:
                print(f"Webhook failed for {webhook.name}: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"Webhook timeout for {webhook.name}: Request took too long")
        except requests.exceptions.ConnectionError:
            print(f"Webhook connection error for {webhook.name}: Could not connect to {webhook.url}")
        except requests.exceptions.RequestException as e:
            print(f"Webhook error for {webhook.name}: {str(e)}")
        except Exception as e:
            print(f"Unexpected webhook error for {webhook.name}: {str(e)}")

