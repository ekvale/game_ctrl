import pytest
from unittest.mock import patch, mock_open
from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError
from django.core import serializers
import os
from datetime import datetime

class TestBackupCommand(TestCase):
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('products.management.commands.backup_db.datetime')
    def test_backup_db_command(self, mock_datetime, mock_exists, mock_file):
        """Test backup_db command creates backup file with correct content"""
        # Setup
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0)
        mock_exists.return_value = True
        mock_file().read.return_value = b'test data'  # Mock file read to return bytes
        
        # Execute
        call_command('backup_db')
        
        # Verify
        expected_filename = f'backup_{datetime(2024, 1, 1, 12, 0).strftime("%Y%m%d_%H%M")}.json'
        expected_path = os.path.join('backups', expected_filename)
        
        # Check if the expected call was made (might not be the only call)
        mock_file.assert_any_call(expected_path, 'w')

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_backup_creates_directory(self, mock_exists, mock_makedirs):
        """Test backup_db command creates backup directory if it doesn't exist"""
        # Setup
        mock_exists.return_value = False
        
        # Execute
        call_command('backup_db')
        
        # Verify
        mock_makedirs.assert_called_once_with('backups')

    @patch('builtins.open', mock_open())
    @patch('products.management.commands.backup_db.serializers')
    def test_backup_content(self, mock_serializers):
        """Test backup contains correct serialized data"""
        # Setup
        mock_serializers.serialize.return_value = '[{"model": "test"}]'
        
        # Execute
        call_command('backup_db')
        
        # Verify
        mock_serializers.serialize.assert_called_once()
        self.assertEqual(mock_serializers.serialize.call_args[0][0], 'json')

    @patch('builtins.open')
    def test_backup_file_error(self, mock_open):
        """Test command handles file write errors"""
        # Setup
        mock_open.side_effect = IOError("Test error")
        
        # Verify
        with self.assertRaises(CommandError):
            call_command('backup_db') 