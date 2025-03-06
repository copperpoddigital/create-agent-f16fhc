from datetime import datetime
from enum import Enum, auto
from typing import Optional, Dict, Any, List, Union
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
from sqlalchemy.orm import Session

from ..core.config import settings, APP_NAME, ENV
from ..core.logging import get_logger
from ..models.user import User
from ..core.exceptions import ApplicationException

# Constants for notification types and priorities
NOTIFICATION_TYPES = {
    "PRICE_MOVEMENT": "price_movement",
    "DATA_SOURCE": "data_source",
    "SYSTEM": "system",
    "SECURITY": "security"
}

NOTIFICATION_PRIORITIES = {
    "LOW": "low",
    "MEDIUM": "medium",
    "HIGH": "high",
    "CRITICAL": "critical"
}

# Configure logger
logger = get_logger(__name__)


class NotificationException(ApplicationException):
    """Exception raised when there are issues with sending notifications."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """
        Initializes the NotificationException.
        
        Args:
            message: Error message
            details: Additional details about the error
            original_exception: Original exception that was caught
        """
        super().__init__(message, details, original_exception)


class NotificationType(Enum):
    """Enumeration of notification types."""
    PRICE_MOVEMENT = auto()
    DATA_SOURCE = auto()
    SYSTEM = auto()
    SECURITY = auto()


class NotificationPriority(Enum):
    """Enumeration of notification priorities."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class Notification:
    """Data class representing a notification."""
    
    def __init__(self, user_id: str, title: str, message: str, 
                 notification_type: NotificationType, priority: NotificationPriority,
                 data: Optional[Dict[str, Any]] = None):
        """
        Initializes a new Notification instance.
        
        Args:
            user_id: ID of the user to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level of the notification
            data: Optional additional data associated with the notification
        """
        self.id = str(datetime.utcnow().timestamp())  # Simple ID generation
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.priority = priority
        self.data = data or {}
        self.created_at = datetime.utcnow()
        self.read = False
        self.read_at = None
    
    def mark_as_read(self) -> None:
        """Marks the notification as read."""
        self.read = True
        self.read_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts notification to dictionary representation.
        
        Returns:
            Dictionary representation of notification
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type.name,
            'priority': self.priority.name,
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'read': self.read,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }


class NotificationChannel:
    """Abstract base class for notification channels."""
    
    def __init__(self):
        """Initializes the NotificationChannel."""
        pass
    
    def send(self, user: User, notification: Notification) -> bool:
        """
        Sends a notification through this channel.
        
        Args:
            user: User to send notification to
            notification: Notification to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement send()")
    
    def format_notification(self, notification: Notification) -> Dict[str, Any]:
        """
        Formats a notification for this channel.
        
        Args:
            notification: Notification to format
            
        Returns:
            Formatted notification data
        """
        raise NotImplementedError("Subclasses must implement format_notification()")


class EmailChannel(NotificationChannel):
    """Email notification channel."""
    
    def __init__(self):
        """Initializes the EmailChannel."""
        super().__init__()
        # Initialize Jinja2 template environment for email templates
        self._template_env = jinja2.Environment(
            loader=jinja2.PackageLoader('src.backend', 'templates/email'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def send(self, user: User, notification: Notification) -> bool:
        """
        Sends an email notification.
        
        Args:
            user: User to send notification to
            notification: Notification to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Check if user has email notifications enabled
        if not user.email_notifications:
            logger.debug(f"Email notifications disabled for user {user.id}")
            return False
        
        try:
            # Format notification for email
            formatted_content = self.format_notification(notification)
            
            # Send email
            sent = self._send_email(
                recipient=user.email,
                subject=formatted_content['subject'],
                body=formatted_content['body'],
                is_html=formatted_content.get('is_html', True)
            )
            
            if sent:
                logger.info(f"Email notification sent to {user.email}: {notification.title}")
                return True
            else:
                logger.error(f"Failed to send email notification to {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}", exc_info=True)
            return False
    
    def format_notification(self, notification: Notification) -> Dict[str, Any]:
        """
        Formats a notification for email.
        
        Args:
            notification: Notification to format
            
        Returns:
            Formatted email content with subject and body
        """
        # Select appropriate template based on notification type
        template_name = f"{notification.notification_type.name.lower()}.html"
        
        try:
            template = self._template_env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            # Fall back to a generic template if specific one not found
            template = self._template_env.get_template("generic.html")
        
        # Render template with notification data
        context = {
            'title': notification.title,
            'message': notification.message,
            'app_name': settings.APP_NAME,
            'data': notification.data,
            'created_at': notification.created_at,
            'priority': notification.priority.name
        }
        
        body = template.render(**context)
        
        return {
            'subject': f"{settings.APP_NAME}: {notification.title}",
            'body': body,
            'is_html': True
        }
    
    def _send_email(self, recipient: str, subject: str, body: str, is_html: bool = True) -> bool:
        """
        Sends an email using SMTP.
        
        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_SENDER
            msg['To'] = recipient
            
            # Attach body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}", exc_info=True)
            return False


class SMSChannel(NotificationChannel):
    """SMS notification channel."""
    
    def __init__(self):
        """Initializes the SMSChannel."""
        super().__init__()
        # Initialize SMS service client
        # In a real implementation, this would connect to an SMS service like Twilio
    
    def send(self, user: User, notification: Notification) -> bool:
        """
        Sends an SMS notification.
        
        Args:
            user: User to send notification to
            notification: Notification to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Check if user has SMS notifications enabled
        if not user.sms_notifications:
            logger.debug(f"SMS notifications disabled for user {user.id}")
            return False
        
        # Check if user has phone number configured
        if not hasattr(user, 'phone_number') or not user.phone_number:
            logger.warning(f"User {user.id} has no phone number configured for SMS notifications")
            return False
        
        try:
            # Format notification for SMS
            sms_message = self.format_notification(notification)
            
            # Send SMS
            sent = self._send_sms(user.phone_number, sms_message)
            
            if sent:
                logger.info(f"SMS notification sent to {user.phone_number}: {notification.title}")
                return True
            else:
                logger.error(f"Failed to send SMS notification to {user.phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}", exc_info=True)
            return False
    
    def format_notification(self, notification: Notification) -> str:
        """
        Formats a notification for SMS.
        
        Args:
            notification: Notification to format
            
        Returns:
            Formatted SMS message
        """
        # Create a concise SMS message (limited to 160 chars for SMS)
        prefix = f"{settings.APP_NAME}: "
        
        # Calculate available space for content
        max_length = 160 - len(prefix)
        
        # Prioritize the title, then add as much of the message as fits
        title_length = len(notification.title)
        
        if title_length > max_length:
            # If title is too long, truncate it
            return f"{prefix}{notification.title[:max_length-3]}..."
        else:
            # Add title plus as much message as fits
            remaining_space = max_length - title_length - 2  # 2 for the separator
            
            if remaining_space > 3:  # Enough space for at least some message content
                message = notification.message
                if len(message) > remaining_space:
                    message = f"{message[:remaining_space-3]}..."
                
                return f"{prefix}{notification.title} - {message}"
            else:
                # Just the title fits
                return f"{prefix}{notification.title}"
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """
        Sends an SMS using service provider.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # In a real implementation, this would use an SMS service API
            # For example, with Twilio:
            #
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone_number
            # )
            
            # Simulated success for now
            logger.info(f"SMS would be sent to {phone_number}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}", exc_info=True)
            return False


class InAppChannel(NotificationChannel):
    """In-app notification channel."""
    
    def __init__(self):
        """Initializes the InAppChannel."""
        super().__init__()
    
    def send(self, user: User, notification: Notification) -> bool:
        """
        Sends an in-app notification.
        
        Args:
            user: User to send notification to
            notification: Notification to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Check if user has in-app notifications enabled
        if not user.in_app_notifications:
            logger.debug(f"In-app notifications disabled for user {user.id}")
            return False
        
        try:
            # Store notification in database
            stored = self._store_notification(notification)
            
            if stored:
                logger.info(f"In-app notification stored for user {user.id}: {notification.title}")
                return True
            else:
                logger.error(f"Failed to store in-app notification for user {user.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending in-app notification: {str(e)}", exc_info=True)
            return False
    
    def format_notification(self, notification: Notification) -> Dict[str, Any]:
        """
        Formats a notification for in-app display.
        
        Args:
            notification: Notification to format
            
        Returns:
            Formatted notification data
        """
        # Convert notification to dictionary with additional formatting for UI
        notification_dict = notification.to_dict()
        
        # Add any UI-specific formatting
        notification_dict['formatted_created_at'] = notification.created_at.strftime("%b %d, %Y %H:%M")
        
        # Add icon based on notification type
        notification_dict['icon'] = self._get_icon_for_type(notification.notification_type)
        
        # Add color based on priority
        notification_dict['color'] = self._get_color_for_priority(notification.priority)
        
        return notification_dict
    
    def _store_notification(self, notification: Notification) -> bool:
        """
        Stores a notification in the database.
        
        Args:
            notification: Notification to store
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # In a real implementation, this would store the notification in a database
            # For example:
            #
            # from ..models.notification import NotificationModel
            # db_notification = NotificationModel(
            #     id=notification.id,
            #     user_id=notification.user_id,
            #     title=notification.title,
            #     message=notification.message,
            #     notification_type=notification.notification_type.name,
            #     priority=notification.priority.name,
            #     data=notification.data,
            #     created_at=notification.created_at,
            #     read=notification.read,
            #     read_at=notification.read_at
            # )
            # db.session.add(db_notification)
            # db.session.commit()
            
            # Simulate success for now
            logger.info(f"In-app notification would be stored: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing notification: {str(e)}", exc_info=True)
            return False
    
    def _get_icon_for_type(self, notification_type: NotificationType) -> str:
        """
        Returns an appropriate icon for the notification type.
        
        Args:
            notification_type: Notification type
            
        Returns:
            Icon identifier
        """
        icons = {
            NotificationType.PRICE_MOVEMENT: "chart-line",
            NotificationType.DATA_SOURCE: "database",
            NotificationType.SYSTEM: "server",
            NotificationType.SECURITY: "shield-alt"
        }
        
        return icons.get(notification_type, "bell")
    
    def _get_color_for_priority(self, priority: NotificationPriority) -> str:
        """
        Returns an appropriate color for the notification priority.
        
        Args:
            priority: Notification priority
            
        Returns:
            Color code
        """
        colors = {
            NotificationPriority.LOW: "info",
            NotificationPriority.MEDIUM: "warning",
            NotificationPriority.HIGH: "danger",
            NotificationPriority.CRITICAL: "critical"
        }
        
        return colors.get(priority, "default")


class NotificationService:
    """Service for sending notifications through various channels."""
    
    def __init__(self):
        """Initializes the NotificationService."""
        # Initialize channels dictionary
        self._channels = {}
        
        # Register default channels
        self.register_channel("email", EmailChannel())
        self.register_channel("sms", SMSChannel())
        self.register_channel("in_app", InAppChannel())
        
        # Initialize database session
        # In a real implementation, this would be injected or retrieved from a session factory
        self._db_session = None
    
    def register_channel(self, channel_name: str, channel: NotificationChannel) -> None:
        """
        Registers a notification channel.
        
        Args:
            channel_name: Name to register the channel under
            channel: NotificationChannel instance
        """
        self._channels[channel_name] = channel
        logger.info(f"Registered notification channel: {channel_name}")
    
    def send_notification(self, user: Union[str, User], title: str, message: str,
                         notification_type: NotificationType, priority: NotificationPriority,
                         data: Optional[Dict[str, Any]] = None,
                         channels: Optional[List[str]] = None) -> bool:
        """
        Sends a notification to a user through appropriate channels.
        
        Args:
            user: User ID or User object
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            data: Optional additional data
            channels: Optional list of specific channels to use
            
        Returns:
            True if notification was sent through at least one channel
        """
        # Resolve user object
        user_obj = self._resolve_user(user)
        
        # Create notification object
        notification = Notification(
            user_id=user_obj.id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            data=data
        )
        
        # Determine which channels to use
        selected_channels = channels or self._get_channels_for_notification(user_obj, priority)
        
        if not selected_channels:
            logger.warning(f"No notification channels available for user {user_obj.id}")
            return False
        
        # Send through each channel
        success = False
        for channel_name in selected_channels:
            if channel_name in self._channels:
                channel = self._channels[channel_name]
                if channel.send(user_obj, notification):
                    success = True
            else:
                logger.warning(f"Unknown notification channel: {channel_name}")
        
        return success
    
    def notify_price_movement(self, user: Union[str, User], percentage_change: float,
                             route: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sends a notification about significant price movements.
        
        Args:
            user: User ID or User object
            percentage_change: Percentage change in price
            route: Route description
            additional_data: Optional additional data
            
        Returns:
            True if notification was sent successfully
        """
        # Determine priority based on percentage change
        if abs(percentage_change) > 15:
            priority = NotificationPriority.HIGH
        elif abs(percentage_change) > 5:
            priority = NotificationPriority.MEDIUM
        else:
            priority = NotificationPriority.LOW
        
        # Format the percentage with sign for display
        if percentage_change > 0:
            formatted_percentage = f"+{percentage_change:.1f}%"
        else:
            formatted_percentage = f"{percentage_change:.1f}%"
        
        # Create notification title and message
        title = f"Price Movement Alert: {formatted_percentage} on {route}"
        message = f"Freight prices on {route} have changed by {formatted_percentage}."
        
        # Prepare data payload
        data = {
            "percentage_change": percentage_change,
            "route": route,
            "formatted_percentage": formatted_percentage
        }
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
        
        # Send notification
        return self.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.PRICE_MOVEMENT,
            priority=priority,
            data=data
        )
    
    def notify_data_source_status(self, user: Union[str, User], source_name: str,
                                 status: str, error_message: Optional[str] = None,
                                 additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sends a notification about data source status changes.
        
        Args:
            user: User ID or User object
            source_name: Name of the data source
            status: Status of the data source
            error_message: Optional error message if status is error
            additional_data: Optional additional data
            
        Returns:
            True if notification was sent successfully
        """
        # Determine priority based on status
        if status.lower() == "error":
            priority = NotificationPriority.HIGH
        elif status.lower() == "warning":
            priority = NotificationPriority.MEDIUM
        else:
            priority = NotificationPriority.LOW
        
        # Create notification title and message
        title = f"Data Source Status: {source_name} is {status}"
        
        if status.lower() == "error" and error_message:
            message = f"The data source {source_name} reported an error: {error_message}"
        else:
            message = f"The data source {source_name} status is now {status}."
        
        # Prepare data payload
        data = {
            "source_name": source_name,
            "status": status
        }
        
        if error_message:
            data["error_message"] = error_message
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
        
        # Send notification
        return self.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.DATA_SOURCE,
            priority=priority,
            data=data
        )
    
    def notify_system_event(self, user: Union[str, User], event_type: str,
                           event_message: str, priority: NotificationPriority,
                           additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sends a notification about system events.
        
        Args:
            user: User ID or User object
            event_type: Type of system event
            event_message: Event message
            priority: Priority level
            additional_data: Optional additional data
            
        Returns:
            True if notification was sent successfully
        """
        # Create notification title
        title = f"System Event: {event_type}"
        
        # Prepare data payload
        data = {
            "event_type": event_type
        }
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
        
        # Send notification
        return self.send_notification(
            user=user,
            title=title,
            message=event_message,
            notification_type=NotificationType.SYSTEM,
            priority=priority,
            data=data
        )
    
    def notify_security_event(self, user: Union[str, User], event_type: str,
                             event_message: str, priority: NotificationPriority,
                             additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sends a notification about security events.
        
        Args:
            user: User ID or User object
            event_type: Type of security event
            event_message: Event message
            priority: Priority level
            additional_data: Optional additional data
            
        Returns:
            True if notification was sent successfully
        """
        # Create notification title
        title = f"Security Alert: {event_type}"
        
        # Prepare data payload
        data = {
            "event_type": event_type
        }
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
        
        # Send notification
        return self.send_notification(
            user=user,
            title=title,
            message=event_message,
            notification_type=NotificationType.SECURITY,
            priority=priority,
            data=data
        )
    
    def get_user_notifications(self, user: Union[str, User], include_read: bool = False,
                              limit: Optional[int] = None, offset: Optional[int] = None) -> List[Notification]:
        """
        Retrieves notifications for a user.
        
        Args:
            user: User ID or User object
            include_read: Whether to include read notifications
            limit: Optional limit on number of notifications
            offset: Optional offset for pagination
            
        Returns:
            List of notifications for the user
        """
        # Resolve user object
        user_obj = self._resolve_user(user)
        
        # In a real implementation, this would query the database
        # For example:
        #
        # from ..models.notification import NotificationModel
        # query = self._db_session.query(NotificationModel).filter(
        #     NotificationModel.user_id == user_obj.id
        # )
        #
        # if not include_read:
        #     query = query.filter(NotificationModel.read == False)
        #
        # query = query.order_by(NotificationModel.created_at.desc())
        #
        # if limit is not None:
        #     query = query.limit(limit)
        #
        # if offset is not None:
        #     query = query.offset(offset)
        #
        # db_notifications = query.all()
        #
        # notifications = []
        # for db_notification in db_notifications:
        #     notification = Notification(
        #         user_id=db_notification.user_id,
        #         title=db_notification.title,
        #         message=db_notification.message,
        #         notification_type=NotificationType[db_notification.notification_type],
        #         priority=NotificationPriority[db_notification.priority],
        #         data=db_notification.data
        #     )
        #     notification.id = db_notification.id
        #     notification.created_at = db_notification.created_at
        #     notification.read = db_notification.read
        #     notification.read_at = db_notification.read_at
        #     notifications.append(notification)
        #
        # return notifications
        
        # For now, return an empty list
        logger.info(f"Would fetch notifications for user {user_obj.id}")
        return []
    
    def mark_notification_as_read(self, notification_id: str, user: Union[str, User]) -> bool:
        """
        Marks a notification as read.
        
        Args:
            notification_id: ID of the notification
            user: User ID or User object
            
        Returns:
            True if notification was marked as read
        """
        # Resolve user object
        user_obj = self._resolve_user(user)
        
        # In a real implementation, this would update the database
        # For example:
        #
        # from ..models.notification import NotificationModel
        # db_notification = self._db_session.query(NotificationModel).filter(
        #     NotificationModel.id == notification_id,
        #     NotificationModel.user_id == user_obj.id
        # ).first()
        #
        # if db_notification:
        #     db_notification.read = True
        #     db_notification.read_at = datetime.utcnow()
        #     self._db_session.commit()
        #     return True
        # else:
        #     return False
        
        # For now, simulate success
        logger.info(f"Would mark notification {notification_id} as read for user {user_obj.id}")
        return True
    
    def mark_all_notifications_as_read(self, user: Union[str, User]) -> int:
        """
        Marks all notifications for a user as read.
        
        Args:
            user: User ID or User object
            
        Returns:
            Number of notifications marked as read
        """
        # Resolve user object
        user_obj = self._resolve_user(user)
        
        # In a real implementation, this would update the database
        # For example:
        #
        # from ..models.notification import NotificationModel
        # from sqlalchemy import update
        #
        # now = datetime.utcnow()
        # result = self._db_session.execute(
        #     update(NotificationModel)
        #     .where(
        #         NotificationModel.user_id == user_obj.id,
        #         NotificationModel.read == False
        #     )
        #     .values(read=True, read_at=now)
        # )
        # self._db_session.commit()
        #
        # return result.rowcount
        
        # For now, simulate success
        logger.info(f"Would mark all notifications as read for user {user_obj.id}")
        return 0
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieves a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        # In a real implementation, this would query the database
        # For example:
        #
        # return self._db_session.query(User).filter(User.id == user_id).first()
        
        # For now, return None (would be handled in _resolve_user)
        return None
    
    def _resolve_user(self, user: Union[str, User]) -> User:
        """
        Resolves a user object from user ID or User instance.
        
        Args:
            user: User ID or User object
            
        Returns:
            Resolved User object
            
        Raises:
            NotificationException: If user cannot be resolved
        """
        if isinstance(user, User):
            return user
        
        # If user is a string (user ID), get user by ID
        if isinstance(user, str):
            user_obj = self._get_user_by_id(user)
            if user_obj:
                return user_obj
        
        # If we get here, user could not be resolved
        raise NotificationException(f"Could not resolve user: {user}")
    
    def _get_channels_for_notification(self, user: User, priority: NotificationPriority,
                                      requested_channels: Optional[List[str]] = None) -> List[str]:
        """
        Determines appropriate channels for a notification based on priority and user preferences.
        
        Args:
            user: User to notify
            priority: Notification priority
            requested_channels: Optional specific channels requested
            
        Returns:
            List of channel names to use
        """
        # If specific channels are requested and valid, use them
        if requested_channels:
            return [channel for channel in requested_channels if channel in self._channels]
        
        # Otherwise, determine based on priority and user preferences
        channels = []
        
        # CRITICAL priority notifications go through all available channels regardless of preferences
        if priority == NotificationPriority.CRITICAL:
            return list(self._channels.keys())
        
        # HIGH priority gets email and in-app if enabled
        if priority == NotificationPriority.HIGH:
            if user.email_notifications:
                channels.append("email")
            if user.in_app_notifications:
                channels.append("in_app")
        
        # MEDIUM priority gets in-app and email if enabled
        elif priority == NotificationPriority.MEDIUM:
            if user.in_app_notifications:
                channels.append("in_app")
            if user.email_notifications:
                channels.append("email")
        
        # LOW priority gets only in-app if enabled
        elif priority == NotificationPriority.LOW:
            if user.in_app_notifications:
                channels.append("in_app")
        
        return channels