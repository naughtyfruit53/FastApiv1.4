"""
Notification Service for Service CRM Integration

Handles multi-channel notifications (email, SMS, push) with template support,
automated triggers, and delivery tracking.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.config import settings
from app.models.base import (
    NotificationTemplate, NotificationLog, NotificationPreference,
    Customer, CustomerSegment, User
)
from app.schemas.base import (
    NotificationTemplateCreate, NotificationLogCreate,
    NotificationSendRequest, BulkNotificationRequest
)
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for managing multi-channel notifications with template support.
    """
    
    def __init__(self):
        self.email_service = EmailService()
    
    def create_template(
        self, 
        db: Session, 
        template_data: NotificationTemplateCreate, 
        organization_id: int,
        created_by: Optional[int] = None
    ) -> NotificationTemplate:
        """Create a new notification template."""
        
        # Convert variables list to JSON if provided
        variables_json = json.dumps(template_data.variables) if template_data.variables else None
        trigger_conditions_json = json.dumps(template_data.trigger_conditions) if template_data.trigger_conditions else None
        
        db_template = NotificationTemplate(
            organization_id=organization_id,
            name=template_data.name,
            description=template_data.description,
            template_type=template_data.template_type,
            channel=template_data.channel,
            subject=template_data.subject,
            body=template_data.body,
            html_body=template_data.html_body,
            trigger_event=template_data.trigger_event,
            trigger_conditions=trigger_conditions_json,
            variables=variables_json,
            is_active=template_data.is_active,
            created_by=created_by
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        logger.info(f"Created notification template {db_template.id} for organization {organization_id}")
        return db_template
    
    def get_templates(
        self, 
        db: Session, 
        organization_id: int,
        channel: Optional[str] = None,
        template_type: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[NotificationTemplate]:
        """Get notification templates with optional filtering."""
        
        query = db.query(NotificationTemplate).filter(
            NotificationTemplate.organization_id == organization_id
        )
        
        if channel:
            query = query.filter(NotificationTemplate.channel == channel)
        if template_type:
            query = query.filter(NotificationTemplate.template_type == template_type)
        if is_active is not None:
            query = query.filter(NotificationTemplate.is_active == is_active)
            
        return query.all()
    
    def get_template(
        self, 
        db: Session, 
        template_id: int, 
        organization_id: int
    ) -> Optional[NotificationTemplate]:
        """Get a specific notification template."""
        
        return db.query(NotificationTemplate).filter(
            and_(
                NotificationTemplate.id == template_id,
                NotificationTemplate.organization_id == organization_id
            )
        ).first()
    
    def update_template(
        self, 
        db: Session, 
        template_id: int, 
        organization_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[NotificationTemplate]:
        """Update a notification template."""
        
        template = self.get_template(db, template_id, organization_id)
        if not template:
            return None
            
        for field, value in update_data.items():
            if hasattr(template, field) and value is not None:
                if field in ['variables', 'trigger_conditions'] and isinstance(value, (list, dict)):
                    value = json.dumps(value)
                setattr(template, field, value)
        
        db.commit()
        db.refresh(template)
        
        logger.info(f"Updated notification template {template_id}")
        return template
    
    def delete_template(
        self, 
        db: Session, 
        template_id: int, 
        organization_id: int
    ) -> bool:
        """Delete a notification template (soft delete by setting inactive)."""
        
        template = self.get_template(db, template_id, organization_id)
        if not template:
            return False
            
        template.is_active = False
        db.commit()
        
        logger.info(f"Deactivated notification template {template_id}")
        return True
    
    def substitute_variables(
        self, 
        content: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Substitute variables in notification content."""
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def send_notification(
        self, 
        db: Session, 
        request: NotificationSendRequest,
        organization_id: int,
        created_by: Optional[int] = None
    ) -> Optional[NotificationLog]:
        """Send a single notification."""
        
        # Get recipient information
        recipient_info = self._get_recipient_info(db, request.recipient_type, request.recipient_id, organization_id)
        if not recipient_info:
            logger.error(f"Recipient not found: {request.recipient_type} {request.recipient_id}")
            return None
        
        # Get template if specified
        template = None
        if request.template_id:
            template = self.get_template(db, request.template_id, organization_id)
            if not template:
                logger.error(f"Template not found: {request.template_id}")
                return None
        
        # Prepare content
        subject = request.override_subject
        content = request.override_content
        
        if template:
            subject = subject or template.subject
            content = content or template.body
            
            # Substitute variables
            if request.variables:
                if subject:
                    subject = self.substitute_variables(subject, request.variables)
                content = self.substitute_variables(content, request.variables)
        
        # Create notification log
        log_data = NotificationLogCreate(
            template_id=request.template_id,
            recipient_type=request.recipient_type,
            recipient_id=request.recipient_id,
            recipient_identifier=recipient_info['identifier'],
            channel=request.channel,
            subject=subject,
            content=content,
            trigger_event="manual_send",
            context_data=request.variables
        )
        
        notification_log = self._create_notification_log(db, log_data, organization_id, created_by)
        
        # Send notification based on channel
        try:
            success = self._send_by_channel(
                request.channel,
                recipient_info['identifier'],
                subject,
                content,
                template.html_body if template else None
            )
            
            if success:
                notification_log.status = "sent"
                notification_log.sent_at = datetime.utcnow()
            else:
                notification_log.status = "failed"
                notification_log.error_message = "Failed to send notification"
                
        except Exception as e:
            notification_log.status = "failed"
            notification_log.error_message = str(e)
            logger.error(f"Failed to send notification: {e}")
        
        db.commit()
        return notification_log
    
    def send_bulk_notification(
        self, 
        db: Session, 
        request: BulkNotificationRequest,
        organization_id: int,
        created_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send notifications to multiple recipients."""
        
        # Get recipients based on type
        recipients = self._get_bulk_recipients(db, request, organization_id)
        
        results = {
            "total_recipients": len(recipients),
            "successful_sends": 0,
            "failed_sends": 0,
            "notification_ids": [],
            "errors": []
        }
        
        # Get template if specified
        template = None
        if request.template_id:
            template = self.get_template(db, request.template_id, organization_id)
            if not template:
                results["errors"].append(f"Template not found: {request.template_id}")
                return results
        
        for recipient in recipients:
            try:
                # Prepare notification request for each recipient
                send_request = NotificationSendRequest(
                    template_id=request.template_id,
                    recipient_type=recipient['type'],
                    recipient_id=recipient['id'],
                    channel=request.channel,
                    variables=request.variables,
                    override_subject=request.subject,
                    override_content=request.content
                )
                
                notification_log = self.send_notification(db, send_request, organization_id, created_by)
                
                if notification_log:
                    results["notification_ids"].append(notification_log.id)
                    if notification_log.status == "sent":
                        results["successful_sends"] += 1
                    else:
                        results["failed_sends"] += 1
                        results["errors"].append(f"Failed to send to {recipient['identifier']}: {notification_log.error_message}")
                else:
                    results["failed_sends"] += 1
                    results["errors"].append(f"Failed to create notification for {recipient['identifier']}")
                    
            except Exception as e:
                results["failed_sends"] += 1
                results["errors"].append(f"Error sending to {recipient.get('identifier', 'unknown')}: {str(e)}")
        
        logger.info(f"Bulk notification completed: {results['successful_sends']}/{results['total_recipients']} sent")
        return results
    
    def get_notification_logs(
        self, 
        db: Session, 
        organization_id: int,
        recipient_type: Optional[str] = None,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[NotificationLog]:
        """Get notification logs with filtering."""
        
        query = db.query(NotificationLog).filter(
            NotificationLog.organization_id == organization_id
        )
        
        if recipient_type:
            query = query.filter(NotificationLog.recipient_type == recipient_type)
        if status:
            query = query.filter(NotificationLog.status == status)
        if channel:
            query = query.filter(NotificationLog.channel == channel)
            
        return query.order_by(NotificationLog.created_at.desc()).offset(offset).limit(limit).all()
    
    def trigger_automated_notifications(
        self, 
        db: Session, 
        trigger_event: str,
        organization_id: int,
        context_data: Dict[str, Any]
    ):
        """Trigger automated notifications based on events."""
        
        # Get templates with matching trigger event
        templates = db.query(NotificationTemplate).filter(
            and_(
                NotificationTemplate.organization_id == organization_id,
                NotificationTemplate.trigger_event == trigger_event,
                NotificationTemplate.is_active == True
            )
        ).all()
        
        for template in templates:
            try:
                # Check trigger conditions if specified
                if template.trigger_conditions:
                    conditions = json.loads(template.trigger_conditions)
                    if not self._evaluate_trigger_conditions(conditions, context_data):
                        continue
                
                # Determine recipients based on context
                recipients = self._get_trigger_recipients(db, trigger_event, context_data, organization_id)
                
                for recipient in recipients:
                    send_request = NotificationSendRequest(
                        template_id=template.id,
                        recipient_type=recipient['type'],
                        recipient_id=recipient['id'],
                        channel=template.channel,
                        variables=context_data
                    )
                    
                    self.send_notification(db, send_request, organization_id)
                    
            except Exception as e:
                logger.error(f"Error in automated notification trigger: {e}")
    
    def _get_recipient_info(
        self, 
        db: Session, 
        recipient_type: str, 
        recipient_id: int,
        organization_id: int
    ) -> Optional[Dict[str, str]]:
        """Get recipient contact information."""
        
        if recipient_type == "customer":
            customer = db.query(Customer).filter(
                and_(Customer.id == recipient_id, Customer.organization_id == organization_id)
            ).first()
            if customer and customer.email:
                return {"identifier": customer.email, "name": customer.name}
                
        elif recipient_type == "user":
            user = db.query(User).filter(
                and_(User.id == recipient_id, User.organization_id == organization_id)
            ).first()
            if user and user.email:
                return {"identifier": user.email, "name": user.full_name or user.email}
        
        return None
    
    def _get_bulk_recipients(
        self, 
        db: Session, 
        request: BulkNotificationRequest,
        organization_id: int
    ) -> List[Dict[str, Any]]:
        """Get recipients for bulk notification."""
        
        recipients = []
        
        if request.recipient_type == "customers" and request.recipient_ids:
            customers = db.query(Customer).filter(
                and_(
                    Customer.id.in_(request.recipient_ids),
                    Customer.organization_id == organization_id,
                    Customer.email.isnot(None)
                )
            ).all()
            recipients = [
                {"type": "customer", "id": c.id, "identifier": c.email, "name": c.name}
                for c in customers
            ]
            
        elif request.recipient_type == "segment" and request.segment_name:
            # Get customers in the specified segment
            customers = db.query(Customer).join(CustomerSegment).filter(
                and_(
                    CustomerSegment.segment_name == request.segment_name,
                    CustomerSegment.organization_id == organization_id,
                    CustomerSegment.is_active == True,
                    Customer.email.isnot(None)
                )
            ).all()
            recipients = [
                {"type": "customer", "id": c.id, "identifier": c.email, "name": c.name}
                for c in customers
            ]
            
        elif request.recipient_type == "users" and request.recipient_ids:
            users = db.query(User).filter(
                and_(
                    User.id.in_(request.recipient_ids),
                    User.organization_id == organization_id,
                    User.email.isnot(None)
                )
            ).all()
            recipients = [
                {"type": "user", "id": u.id, "identifier": u.email, "name": u.full_name or u.email}
                for u in users
            ]
        
        return recipients
    
    def _create_notification_log(
        self, 
        db: Session, 
        log_data: NotificationLogCreate,
        organization_id: int,
        created_by: Optional[int] = None
    ) -> NotificationLog:
        """Create a notification log entry."""
        
        context_data_json = json.dumps(log_data.context_data) if log_data.context_data else None
        
        notification_log = NotificationLog(
            organization_id=organization_id,
            template_id=log_data.template_id,
            recipient_type=log_data.recipient_type,
            recipient_id=log_data.recipient_id,
            recipient_identifier=log_data.recipient_identifier,
            channel=log_data.channel,
            subject=log_data.subject,
            content=log_data.content,
            trigger_event=log_data.trigger_event,
            context_data=context_data_json,
            created_by=created_by
        )
        
        db.add(notification_log)
        db.flush()  # Get ID without committing
        return notification_log
    
    def _send_by_channel(
        self, 
        channel: str, 
        recipient: str, 
        subject: Optional[str], 
        content: str,
        html_content: Optional[str] = None
    ) -> bool:
        """Send notification via specified channel."""
        
        if channel == "email":
            return self._send_email(recipient, subject or "Notification", content, html_content)
        elif channel == "sms":
            return self._send_sms(recipient, content)
        elif channel == "push":
            return self._send_push(recipient, subject, content)
        elif channel == "in_app":
            return self._send_in_app(recipient, subject, content)
        else:
            logger.error(f"Unsupported notification channel: {channel}")
            return False
    
    def _send_email(
        self, 
        to_email: str, 
        subject: str, 
        content: str,
        html_content: Optional[str] = None
    ) -> bool:
        """Send email notification."""
        try:
            success = self.email_service.send_email(
                to_email=to_email,
                subject=subject,
                body=content,
                html_body=html_content
            )
            return success
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _send_sms(self, phone: str, content: str) -> bool:
        """Send SMS notification (placeholder for SMS integration)."""
        # TODO: Integrate with SMS service (Twilio, AWS SNS, etc.)
        logger.info(f"SMS sending not yet implemented. Would send to {phone}: {content}")
        return True  # Return True for now to avoid blocking
    
    def _send_push(self, device_token: str, title: Optional[str], content: str) -> bool:
        """Send push notification (placeholder for push service integration)."""
        # TODO: Integrate with push notification service (Firebase, OneSignal, etc.)
        logger.info(f"Push notification sending not yet implemented. Would send to {device_token}: {title} - {content}")
        return True  # Return True for now to avoid blocking
    
    def _send_in_app(self, user_identifier: str, title: Optional[str], content: str) -> bool:
        """Send in-app notification (placeholder for in-app messaging)."""
        # TODO: Implement in-app notification system
        logger.info(f"In-app notification sending not yet implemented. Would send to {user_identifier}: {title} - {content}")
        return True  # Return True for now to avoid blocking
    
    def _evaluate_trigger_conditions(
        self, 
        conditions: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> bool:
        """Evaluate trigger conditions against context data."""
        # Simple condition evaluation - can be extended
        for key, expected_value in conditions.items():
            if key not in context_data or context_data[key] != expected_value:
                return False
        return True
    
    def _get_trigger_recipients(
        self, 
        db: Session, 
        trigger_event: str,
        context_data: Dict[str, Any],
        organization_id: int
    ) -> List[Dict[str, Any]]:
        """Get recipients for automated triggers."""
        recipients = []
        
        # Example trigger recipient logic
        if trigger_event == "customer_interaction":
            customer_id = context_data.get("customer_id")
            if customer_id:
                customer = db.query(Customer).filter(
                    and_(Customer.id == customer_id, Customer.organization_id == organization_id)
                ).first()
                if customer and customer.email:
                    recipients.append({
                        "type": "customer",
                        "id": customer.id,
                        "identifier": customer.email,
                        "name": customer.name
                    })
        
        # Add more trigger recipient logic as needed
        
        return recipients