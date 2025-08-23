"""
Unit tests for the notification service.

Tests the core notification functionality including template management,
notification sending, and automated triggers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.notification_service import NotificationService
from app.models.base import NotificationTemplate, NotificationLog, Customer, User
from app.schemas.base import NotificationTemplateCreate, NotificationSendRequest


class TestNotificationService:
    """Test cases for the NotificationService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.notification_service = NotificationService()
        self.mock_db = Mock(spec=Session)
        self.organization_id = 1
        self.user_id = 1
    
    def test_create_template_success(self):
        """Test successful template creation."""
        # Arrange
        template_data = NotificationTemplateCreate(
            name="Test Template",
            template_type="appointment_reminder",
            channel="email",
            subject="Test Subject",
            body="Hello {customer_name}",
            variables=["customer_name"]
        )
        
        mock_template = NotificationTemplate(
            id=1,
            organization_id=self.organization_id,
            name=template_data.name,
            template_type=template_data.template_type,
            channel=template_data.channel,
            subject=template_data.subject,
            body=template_data.body,
            is_active=True
        )
        
        # Mock database operations
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        # Act
        with patch.object(NotificationTemplate, '__init__', return_value=None):
            with patch.object(self.notification_service, 'get_templates') as mock_get:
                mock_get.return_value = [mock_template]
                result = self.notification_service.create_template(
                    self.mock_db,
                    template_data,
                    self.organization_id,
                    self.user_id
                )
        
        # Assert
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
    
    def test_substitute_variables(self):
        """Test variable substitution in content."""
        # Arrange
        content = "Hello {customer_name}, your appointment is on {appointment_date}"
        variables = {
            "customer_name": "John Doe",
            "appointment_date": "2024-01-15 10:00 AM"
        }
        expected = "Hello John Doe, your appointment is on 2024-01-15 10:00 AM"
        
        # Act
        result = self.notification_service.substitute_variables(content, variables)
        
        # Assert
        assert result == expected
    
    def test_substitute_variables_missing_variables(self):
        """Test variable substitution with missing variables."""
        # Arrange
        content = "Hello {customer_name}, your {missing_variable} is ready"
        variables = {"customer_name": "John Doe"}
        expected = "Hello John Doe, your {missing_variable} is ready"
        
        # Act
        result = self.notification_service.substitute_variables(content, variables)
        
        # Assert
        assert result == expected
    
    def test_get_recipient_info_customer(self):
        """Test getting customer recipient information."""
        # Arrange
        customer_id = 1
        mock_customer = Mock()
        mock_customer.id = customer_id
        mock_customer.email = "customer@example.com"
        mock_customer.name = "John Doe"
        
        query_mock = Mock()
        filter_mock = Mock()
        first_mock = Mock(return_value=mock_customer)
        
        self.mock_db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_customer
        
        # Act
        result = self.notification_service._get_recipient_info(
            self.mock_db, "customer", customer_id, self.organization_id
        )
        
        # Assert
        assert result is not None
        assert result["identifier"] == "customer@example.com"
        assert result["name"] == "John Doe"
    
    def test_get_recipient_info_user(self):
        """Test getting user recipient information."""
        # Arrange
        user_id = 1
        mock_user = Mock()
        mock_user.id = user_id
        mock_user.email = "user@example.com"
        mock_user.full_name = "Jane Smith"
        
        query_mock = Mock()
        filter_mock = Mock()
        first_mock = Mock(return_value=mock_user)
        
        self.mock_db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_user
        
        # Act
        result = self.notification_service._get_recipient_info(
            self.mock_db, "user", user_id, self.organization_id
        )
        
        # Assert
        assert result is not None
        assert result["identifier"] == "user@example.com"
        assert result["name"] == "Jane Smith"
    
    def test_get_recipient_info_not_found(self):
        """Test getting recipient info when recipient not found."""
        # Arrange
        query_mock = Mock()
        filter_mock = Mock()
        first_mock = Mock(return_value=None)
        
        self.mock_db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        
        # Act
        result = self.notification_service._get_recipient_info(
            self.mock_db, "customer", 999, self.organization_id
        )
        
        # Assert
        assert result is None
    
    def test_send_email_success(self):
        """Test successful email sending."""
        # Arrange
        with patch.object(self.notification_service.email_service, 'send_email') as mock_send:
            mock_send.return_value = True
            
            # Act
            result = self.notification_service._send_email(
                "test@example.com", 
                "Test Subject", 
                "Test Content"
            )
            
            # Assert
            assert result is True
            mock_send.assert_called_once_with(
                to_email="test@example.com",
                subject="Test Subject",
                body="Test Content",
                html_body=None
            )
    
    def test_send_email_failure(self):
        """Test email sending failure."""
        # Arrange
        with patch.object(self.notification_service.email_service, 'send_email') as mock_send:
            mock_send.side_effect = Exception("SMTP Error")
            
            # Act
            result = self.notification_service._send_email(
                "test@example.com", 
                "Test Subject", 
                "Test Content"
            )
            
            # Assert
            assert result is False
    
    def test_send_by_channel_email(self):
        """Test sending notification via email channel."""
        # Arrange
        with patch.object(self.notification_service, '_send_email') as mock_send_email:
            mock_send_email.return_value = True
            
            # Act
            result = self.notification_service._send_by_channel(
                "email",
                "test@example.com",
                "Test Subject",
                "Test Content"
            )
            
            # Assert
            assert result is True
            mock_send_email.assert_called_once_with(
                "test@example.com", "Test Subject", "Test Content", None
            )
    
    def test_send_by_channel_sms(self):
        """Test sending notification via SMS channel."""
        # Arrange
        with patch.object(self.notification_service, '_send_sms') as mock_send_sms:
            mock_send_sms.return_value = True
            
            # Act
            result = self.notification_service._send_by_channel(
                "sms",
                "+1234567890",
                None,
                "Test SMS Content"
            )
            
            # Assert
            assert result is True
            mock_send_sms.assert_called_once_with("+1234567890", "Test SMS Content")
    
    def test_send_by_channel_unsupported(self):
        """Test sending notification via unsupported channel."""
        # Act
        result = self.notification_service._send_by_channel(
            "unsupported",
            "recipient",
            "Subject",
            "Content"
        )
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_templates_with_filters(self):
        """Test getting templates with filters."""
        # Arrange
        mock_templates = [
            Mock(id=1, channel="email", template_type="appointment_reminder", is_active=True),
            Mock(id=2, channel="sms", template_type="marketing", is_active=True)
        ]
        
        query_mock = Mock()
        filter_mock = Mock()
        all_mock = Mock(return_value=mock_templates)
        
        self.mock_db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.filter.return_value = filter_mock  # Chain filters
        filter_mock.all.return_value = mock_templates
        
        # Act
        result = self.notification_service.get_templates(
            self.mock_db,
            self.organization_id,
            channel="email",
            template_type="appointment_reminder"
        )
        
        # Assert
        assert len(result) == 2
        self.mock_db.query.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])