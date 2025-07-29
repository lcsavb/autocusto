"""
CRITICAL PRODUCTION SAFETY TEST

This test MUST pass before any deployment. If this test fails, deployment should be STOPPED.

Tests the integrity of the clinic versioning system to ensure no production breakage.
"""
from tests.test_base import BaseTestCase
from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from clinicas.models import Clinica, ClinicaVersion, ClinicaUsuario, ClinicaUsuarioVersion, Emissor
from processos.models import Processo

Usuario = get_user_model()


class CriticalProductionSafetyTest(BaseTestCase):
    """
    CRITICAL: These tests verify production safety.
    If ANY test fails, deployment MUST be stopped.
    """
    
    def test_01_post_migration_data_integrity(self):
        """CRITICAL: After migration, all clinics must have versions"""
        clinic_count = Clinica.objects.count()
        
        if clinic_count > 0:
            # Every clinic must have at least one version after migration runs
            clinics_without_versions = Clinica.objects.filter(versions__isnull=True).count()
            
            self.assertEqual(
                clinics_without_versions, 0, 
                f"PRODUCTION BLOCKER: {clinics_without_versions}/{clinic_count} clinics missing versions after migration"
            )
            
            # Every user-clinic relation must have version assignment
            user_clinic_count = ClinicaUsuario.objects.count()
            user_version_count = ClinicaUsuarioVersion.objects.count()
            
            self.assertEqual(
                user_clinic_count, user_version_count,
                f"PRODUCTION BLOCKER: {user_clinic_count} user-clinic relations but only {user_version_count} version assignments"
            )
        else:
            # No clinics exist - this is fine for fresh deployment
            self.assertEqual(ClinicaVersion.objects.count(), 0)
            self.assertEqual(ClinicaUsuarioVersion.objects.count(), 0)
    
    def test_02_cns_uniqueness_enforced(self):
        """CRITICAL: CNS must be unique - no duplicates allowed"""
        from django.db import transaction
        
        # Test CNS uniqueness constraint
        test_cns = "9999999"
        
        # Ensure our test CNS doesn't exist
        Clinica.objects.filter(cns_clinica=test_cns).delete()
        
        # Create first clinic
        clinic1 = Clinica.objects.create(
            nome_clinica="Test Clinic 1",
            cns_clinica=test_cns,
            logradouro="Test Street",
            logradouro_num="1",
            cidade="Test City", 
            bairro="Test District",
            cep="12345-678",
            telefone_clinica="(11) 1234-5678"
        )
        
        try:
            # Try to create duplicate in separate transaction - should fail
            with transaction.atomic():
                with self.assertRaises(IntegrityError, msg="PRODUCTION BLOCKER: CNS uniqueness not enforced"):
                    Clinica.objects.create(
                        nome_clinica="Test Clinic 2",
                        cns_clinica=test_cns,  # Same CNS - should fail
                        logradouro="Different Street",
                        logradouro_num="2",
                        cidade="Different City",
                        bairro="Different District", 
                        cep="98765-432",
                        telefone_clinica="(22) 9876-5432"
                    )
        finally:
            # Cleanup in separate transaction to avoid transaction management error
            clinic1.delete()
    
    def test_03_foreign_key_relationships_intact(self):
        """CRITICAL: All foreign key relationships must be preserved"""
        
        # Check Processo -> Clinica relationships
        processo_count = Processo.objects.count()
        if processo_count > 0:
            broken_processos = Processo.objects.filter(clinica__isnull=True).count()
            self.assertEqual(
                broken_processos, 0,
                f"PRODUCTION BLOCKER: {broken_processos}/{processo_count} Processos with broken clinic references"
            )
        
        # Check Emissor -> Clinica relationships  
        emissor_count = Emissor.objects.count()
        if emissor_count > 0:
            broken_emissores = Emissor.objects.filter(clinica__isnull=True).count()
            self.assertEqual(
                broken_emissores, 0,
                f"PRODUCTION BLOCKER: {broken_emissores}/{emissor_count} Emissores with broken clinic references"
            )
    
    def test_04_version_retrieval_system(self):
        """CRITICAL: Version retrieval must work for all users"""
        users_with_clinics = Usuario.objects.filter(clinicas__isnull=False).distinct()
        
        failed_retrievals = []
        for user in users_with_clinics:
            user_clinics = Clinica.objects.filter(usuarios=user)
            for clinic in user_clinics:
                version = clinic.get_version_for_user(user)
                if not version:
                    failed_retrievals.append(f"User {user.email} -> Clinic {clinic.id}")
        
        self.assertEqual(
            len(failed_retrievals), 0,
            f"PRODUCTION BLOCKER: Version retrieval failed for: {', '.join(failed_retrievals)}"
        )
    
    def test_05_original_model_fields_preserved(self):
        """CRITICAL: Original Clinica fields must be accessible"""
        clinic = Clinica.objects.first()
        if clinic:
            # These fields MUST exist for backward compatibility
            critical_fields = [
                'nome_clinica', 'cns_clinica', 'logradouro', 'logradouro_num',
                'cidade', 'bairro', 'cep', 'telefone_clinica'
            ]
            
            missing_fields = []
            for field in critical_fields:
                if not hasattr(clinic, field):
                    missing_fields.append(field)
                else:
                    # Verify field is accessible
                    try:
                        getattr(clinic, field)
                    except Exception as e:
                        missing_fields.append(f"{field} (access error: {e})")
            
            self.assertEqual(
                len(missing_fields), 0,
                f"PRODUCTION BLOCKER: Critical fields missing/broken: {', '.join(missing_fields)}"
            )
    
    def test_06_analytics_integration_preserved(self):
        """CRITICAL: Analytics models must still work with Clinica"""
        try:
            from analytics.models import PDFGenerationLog, ClinicMetrics
            
            # Verify foreign key references still work
            clinic = Clinica.objects.first()
            if clinic:
                # These should not raise exceptions
                _ = PDFGenerationLog.objects.filter(clinica=clinic)
                _ = ClinicMetrics.objects.filter(clinic=clinic)
                
        except ImportError:
            # Analytics app not available - skip test
            pass
        except Exception as e:
            self.fail(f"PRODUCTION BLOCKER: Analytics integration broken: {e}")
    
    def test_07_existing_queries_compatibility(self):
        """CRITICAL: Existing code queries must still work"""
        try:
            # These are common queries that existing code uses
            _ = list(Clinica.objects.all())
            _ = list(Clinica.objects.filter(usuarios__isnull=False))
            _ = list(Clinica.objects.select_related())
            _ = list(Clinica.objects.prefetch_related('usuarios', 'medicos'))
            
            # Test specific relationships
            if Clinica.objects.exists():
                clinic = Clinica.objects.first()
                _ = list(clinic.usuarios.all())
                _ = list(clinic.medicos.all())
                _ = list(clinic.processos.all())
                
        except Exception as e:
            self.fail(f"PRODUCTION BLOCKER: Existing query compatibility broken: {e}")
    
    def test_08_version_model_integrity(self):
        """CRITICAL: Version model must have proper constraints"""
        if Clinica.objects.exists():
            for clinic in Clinica.objects.all():
                # Version numbers must be unique per clinic
                version_count = clinic.versions.count()
                if version_count > 0:
                    unique_version_count = clinic.versions.values('version_number').distinct().count()
                    
                    self.assertEqual(
                        version_count, unique_version_count,
                        f"PRODUCTION BLOCKER: Duplicate version numbers found for clinic {clinic.id}"
                    )
                    
                    # All versions must have required fields
                    for version in clinic.versions.all():
                        self.assertIsNotNone(version.version_number, f"Clinic {clinic.id} version missing version_number")
                        self.assertIsNotNone(version.status, f"Clinic {clinic.id} version missing status")
                        self.assertIsNotNone(version.nome_clinica, f"Clinic {clinic.id} version missing nome_clinica")
    
    def test_09_cns_not_in_versions(self):
        """CRITICAL: CNS must NOT be duplicated in version tables"""
        version_fields = [f.name for f in ClinicaVersion._meta.get_fields()]
        self.assertNotIn(
            'cns_clinica', version_fields,
            "PRODUCTION BLOCKER: CNS should not be stored in version table"
        )


class ProductionRollbackSafetyTest(TestCase):
    """
    Tests to ensure migrations can be safely rolled back if needed.
    """
    
    def test_migration_reversibility(self):
        """Verify migration can be safely reversed"""
        # Check that original Clinica model has all data needed for rollback
        clinic = Clinica.objects.first()
        if clinic:
            # These fields must exist in original model for rollback safety
            rollback_critical_fields = [
                'nome_clinica', 'cns_clinica', 'logradouro', 'logradouro_num',
                'cidade', 'bairro', 'cep', 'telefone_clinica'
            ]
            
            missing_fields = []
            for field in rollback_critical_fields:
                if not hasattr(clinic, field):
                    missing_fields.append(field)
            
            self.assertEqual(
                len(missing_fields), 0,
                f"ROLLBACK RISK: Fields missing - rollback would lose data: {', '.join(missing_fields)}"
            )
    
    def test_version_data_preservation(self):
        """Verify version data can be preserved during rollback"""
        version_count = ClinicaVersion.objects.count()
        
        # If we have versions, make sure they contain meaningful data
        if version_count > 0:
            sample_version = ClinicaVersion.objects.first()
            self.assertIsNotNone(sample_version.nome_clinica, "Version data incomplete")
            self.assertIsNotNone(sample_version.clinica, "Version missing clinic reference")


class ProductionDeploymentGateTest(TestCase):
    """
    Final gate test - if this fails, deployment MUST be blocked.
    """
    
    def test_deployment_readiness(self):
        """Final check - system ready for production deployment"""
        checks = []
        issues = []
        
        # Check 1: Data consistency
        clinic_count = Clinica.objects.count()
        version_count = ClinicaVersion.objects.count()
        
        if clinic_count > 0:
            data_migrated = version_count > 0
            if not data_migrated:
                issues.append("Clinics exist but no versions created")
        else:
            data_migrated = True  # No clinics = nothing to migrate
        checks.append(("Data migrated", data_migrated))
        
        # Check 2: User assignments
        user_clinic_count = ClinicaUsuario.objects.count()
        user_version_count = ClinicaUsuarioVersion.objects.count()
        user_assignments_ok = user_clinic_count == user_version_count
        if not user_assignments_ok:
            issues.append(f"User assignments mismatch: {user_clinic_count} relations, {user_version_count} assignments")
        checks.append(("User assignments", user_assignments_ok))
        
        # Check 3: Model integrity
        version_fields_ok = 'cns_clinica' not in [f.name for f in ClinicaVersion._meta.get_fields()]
        if not version_fields_ok:
            issues.append("CNS field found in version model")
        checks.append(("Model integrity", version_fields_ok))
        
        # Check 4: Backward compatibility
        clinic = Clinica.objects.first()
        backward_compat = True
        if clinic:
            try:
                _ = clinic.nome_clinica
                _ = clinic.cns_clinica
            except Exception as e:
                backward_compat = False
                issues.append(f"Backward compatibility broken: {e}")
        checks.append(("Backward compatibility", backward_compat))
        
        # Check 5: CNS uniqueness
        try:
            # Try to create duplicate CNS
            test_cns = "TEST123"
            Clinica.objects.filter(cns_clinica=test_cns).delete()
            
            c1 = Clinica.objects.create(
                nome_clinica="Test", 
                cns_clinica=test_cns,
                logradouro="Test",
                logradouro_num="1",
                cidade="Test",
                bairro="Test",
                cep="12345-678",
                telefone_clinica="(11) 1234-5678"
            )
            try:
                Clinica.objects.create(
                    nome_clinica="Test2", 
                    cns_clinica=test_cns,
                    logradouro="Test2",
                    logradouro_num="2",
                    cidade="Test2",
                    bairro="Test2",
                    cep="98765-432",
                    telefone_clinica="(22) 9876-5432"
                )
                cns_unique = False
                issues.append("CNS uniqueness constraint not working")
            except IntegrityError:
                cns_unique = True
            finally:
                try:
                    c1.delete()
                except:
                    pass
        except Exception as e:
            if "already exists" in str(e) or "duplicate key" in str(e):
                cns_unique = True  # Constraint is working
            else:
                cns_unique = False
                issues.append(f"CNS uniqueness test failed: {e}")
        
        checks.append(("CNS uniqueness", cns_unique))
        
        # Generate deployment report
        failed_checks = [name for name, passed in checks if not passed]
        
        if failed_checks:
            error_msg = (
                f"🚨 DEPLOYMENT BLOCKED 🚨\n"
                f"Failed checks: {', '.join(failed_checks)}\n"
                f"Issues found: {'; '.join(issues)}\n"
                f"DO NOT DEPLOY TO PRODUCTION"
            )
            self.fail(error_msg)
        
        # If we get here, all checks passed
        success_msg = (
            f"✅ DEPLOYMENT APPROVED ✅\n"
            f"All {len(checks)} safety checks passed\n"
            f"System ready for production deployment"
        )
        
        # This will show in test output
        print(success_msg)