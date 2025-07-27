"""
Unit Tests for DomainRepository

Tests the domain entity repository layer focusing on disease, clinic, and protocol lookups.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from processos.repositories.domain_repository import DomainRepository
from processos.models import Doenca, Protocolo
from clinicas.models import Clinica, Emissor

User = get_user_model()


class TestDomainRepositoryUnit(TestCase):
    """Unit tests for DomainRepository data access methods."""
    
    def setUp(self):
        self.repo = DomainRepository()
        self.mock_user = Mock()
        self.mock_user.email = "test@example.com"
        self.mock_user.id = 1
        
    def test_repository_initialization(self):
        """Test repository initializes correctly."""
        repo = DomainRepository()
        self.assertIsNotNone(repo.logger)
        
    @patch('processos.repositories.domain_repository.Doenca.objects')
    def test_get_disease_by_cid_found(self, mock_objects):
        """Test get_disease_by_cid returns disease when found."""
        # Arrange
        mock_disease = Mock()
        mock_disease.id = 123
        mock_disease.cid = "H30"
        mock_disease.nome = "Coriorretinite"
        mock_objects.get.return_value = mock_disease
        
        # Act
        result = self.repo.get_disease_by_cid("H30")
        
        # Assert
        mock_objects.get.assert_called_once_with(cid="H30")
        self.assertEqual(result, mock_disease)
        
    @patch('processos.repositories.domain_repository.Doenca.objects')
    def test_get_disease_by_cid_not_found(self, mock_objects):
        """Test get_disease_by_cid raises exception when not found."""
        # Arrange
        mock_objects.get.side_effect = Doenca.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Doenca.DoesNotExist):
            self.repo.get_disease_by_cid("INVALID")
            
    @patch('processos.repositories.domain_repository.Protocolo.objects')
    def test_get_protocol_by_cid_found(self, mock_objects):
        """Test get_protocol_by_cid returns protocol when found."""
        # Arrange
        mock_protocol = Mock()
        mock_protocol.id = 456
        mock_protocol.cid = "H30"
        mock_protocol.nome = "Protocolo H30"
        mock_objects.get.return_value = mock_protocol
        
        # Act
        result = self.repo.get_protocol_by_cid("H30")
        
        # Assert
        mock_objects.get.assert_called_once_with(doenca__cid="H30")
        self.assertEqual(result, mock_protocol)
        
    @patch('processos.repositories.domain_repository.Protocolo.objects')
    def test_get_protocol_by_cid_not_found(self, mock_objects):
        """Test get_protocol_by_cid raises exception when not found."""
        # Arrange
        mock_objects.get.side_effect = Protocolo.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Protocolo.DoesNotExist):
            self.repo.get_protocol_by_cid("INVALID")
            
    @patch('processos.repositories.domain_repository.Clinica.objects')
    def test_get_clinics_by_user(self, mock_objects):
        """Test get_clinics_by_user filters correctly."""
        # Arrange
        mock_queryset = Mock()
        mock_objects.filter.return_value = mock_queryset
        
        # Act
        result = self.repo.get_clinics_by_user(self.mock_user)
        
        # Assert
        mock_objects.filter.assert_called_once_with(usuarios=self.mock_user)
        self.assertEqual(result, mock_queryset)
        
    @patch('processos.repositories.domain_repository.Emissor.objects')
    def test_get_emissor_by_medico_clinica_found(self, mock_objects):
        """Test get_emissor_by_medico_clinica returns emissor when found."""
        # Arrange
        mock_medico = Mock()
        mock_medico.id = 123
        mock_clinica = Mock()
        mock_clinica.id = 456
        
        mock_emissor = Mock()
        mock_emissor.id = 789
        mock_objects.get.return_value = mock_emissor
        
        # Act
        result = self.repo.get_emissor_by_medico_clinica(mock_medico, mock_clinica)
        
        # Assert
        mock_objects.get.assert_called_once_with(
            medico=mock_medico,
            clinica=mock_clinica
        )
        self.assertEqual(result, mock_emissor)
        
    @patch('processos.repositories.domain_repository.Emissor.objects')
    def test_get_emissor_by_medico_clinica_not_found(self, mock_objects):
        """Test get_emissor_by_medico_clinica raises exception when not found."""
        # Arrange
        mock_medico = Mock()
        mock_clinica = Mock()
        mock_objects.get.side_effect = Emissor.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Emissor.DoesNotExist):
            self.repo.get_emissor_by_medico_clinica(mock_medico, mock_clinica)
            
    @patch('processos.repositories.domain_repository.Doenca.objects')
    def test_get_all_diseases(self, mock_objects):
        """Test get_all_diseases returns all diseases."""
        # Arrange
        mock_queryset = Mock()
        mock_objects.all.return_value = mock_queryset
        
        # Act
        result = self.repo.get_all_diseases()
        
        # Assert
        mock_objects.all.assert_called_once()
        self.assertEqual(result, mock_queryset)


class TestDomainRepositoryIntegration(TestCase):
    """Integration tests for DomainRepository with real database."""
    
    def setUp(self):
        self.repo = DomainRepository()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
    def test_get_disease_by_cid_real_database(self):
        """Test get_disease_by_cid with real database."""
        # Arrange
        disease = Doenca.objects.create(
            cid="H30",
            nome="Coriorretinite"
        )
        
        # Act
        result = self.repo.get_disease_by_cid("H30")
        
        # Assert
        self.assertEqual(result.id, disease.id)
        self.assertEqual(result.nome, "Coriorretinite")
        
    def test_get_disease_by_cid_not_found_real_database(self):
        """Test get_disease_by_cid raises exception for non-existent disease."""
        # Act & Assert
        with self.assertRaises(Doenca.DoesNotExist):
            self.repo.get_disease_by_cid("INVALID")
            
    def test_get_all_diseases_real_database(self):
        """Test get_all_diseases returns all diseases in database."""
        # Arrange
        disease1 = Doenca.objects.create(cid="H30", nome="Coriorretinite")
        disease2 = Doenca.objects.create(cid="H31", nome="Outras doenças da retina")
        
        # Act
        result = self.repo.get_all_diseases()
        
        # Assert
        result_list = list(result)
        self.assertEqual(len(result_list), 2)
        disease_ids = [d.id for d in result_list]
        self.assertIn(disease1.id, disease_ids)
        self.assertIn(disease2.id, disease_ids)