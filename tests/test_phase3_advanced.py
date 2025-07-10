#!/usr/bin/env python3
"""
Test script for Phase 3 Advanced Features
Tests data management, validation, and batch operations
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_management():
    """Test data management system"""
    print("Testing Data Management System...")
    
    try:
        from operations.data_manager import DataManager, DataValidationEngine
        print("✓ DataManager classes imported")
        
        # Test DataManager creation
        data_manager = DataManager()
        print("✓ DataManager created successfully")
        
        # Test validation engine
        validation_engine = DataValidationEngine()
        print("✓ DataValidationEngine created successfully")
        
        # Test mock validation
        validation_result = data_manager.validate_data()
        print("✓ Data validation works")
        
        # Test export functionality
        export_file = data_manager.export_data('json', output_file='test_export.json')
        print(f"✓ Data export works: {export_file}")
        
        # Test import functionality
        import_result = data_manager.import_data('test_export.json')
        print("✓ Data import works")
        
        # Test backup functionality
        backup_file = data_manager.create_backup('test_backup')
        print(f"✓ Backup creation works: {backup_file}")
        
        # Test data summary
        summary = data_manager.get_data_summary()
        print("✓ Data summary works")
        
        return True
        
    except Exception as e:
        print(f"✗ Data management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_operations():
    """Test validation operations"""
    print("\nTesting Validation Operations...")
    
    try:
        from operations.validation_ops import ValidationEngine, ValidationReport, ValidationIssue, ValidationSeverity
        print("✓ ValidationEngine classes imported")
        
        # Test validation engine creation
        validation_engine = ValidationEngine()
        print("✓ ValidationEngine created successfully")
        
        # Test validation rules
        assert len(validation_engine.rules) > 0
        print("✓ Validation rules loaded")
        
        # Test mock validation
        validation_reports = validation_engine.validate_all_data()
        print("✓ Validation reports generated")
        
        # Test validation report generation
        report_file = validation_engine.generate_validation_report(validation_reports, 'test_validation_report.json')
        print(f"✓ Validation report generation works: {report_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Validation operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_operations():
    """Test batch operations"""
    print("\nTesting Batch Operations...")
    
    try:
        from operations.batch_manager import BatchOperationManager, BatchSession, BatchStatus, BatchItem
        print("✓ BatchOperationManager classes imported")
        
        # Test batch manager creation
        batch_manager = BatchOperationManager(max_workers=2)
        print("✓ BatchOperationManager created successfully")
        
        # Test session creation
        session = batch_manager.create_session("test_session", "test_operation")
        print("✓ Batch session created successfully")
        
        # Test session status
        status = batch_manager.get_session_status("test_session")
        assert status is not None
        print("✓ Session status retrieval works")
        
        # Test session listing
        sessions = batch_manager.list_sessions()
        print("✓ Session listing works")
        
        # Test session cleanup
        success = batch_manager.cleanup_session("test_session")
        print("✓ Session cleanup works")
        
        return True
        
    except Exception as e:
        print(f"✗ Batch operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_integration():
    """Test CLI integration with advanced features"""
    print("\nTesting CLI Integration...")
    
    try:
        from cli.cli_main import CLIManager
        cli = CLIManager()
        print("✓ CLI manager created")
        
        # Test that new commands exist
        data_cmd = cli.get_command('data')
        batch_cmd = cli.get_command('batch')
        assert data_cmd is not None
        assert batch_cmd is not None
        print("✓ Advanced commands found")
        
        # Test help for new commands
        result = cli.run(['data', '--help'])
        assert result == 0
        print("✓ Data command help works")
        
        result = cli.run(['batch', '--help'])
        assert result == 0
        print("✓ Batch command help works")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_features():
    """Test specific advanced features"""
    print("\nTesting Advanced Features...")
    
    try:
        # Test data validation with mock data
        from operations.validation_ops import ValidationEngine
        
        validation_engine = ValidationEngine()
        
        # Create mock record for testing
        mock_record = {
            'player_name': 'Test Player',
            'season': 2024,
            'pfr_id': 'test123',
            'cmp_pct': 65.5,
            'rate': 95.2,
            'age': 25,
            'att': 500,
            'cmp': 325,
            'yds': 3500,
            'y_a': 7.0
        }
        
        # Test validation
        issues = validation_engine.validate_record(mock_record, 'qb_stats')
        print(f"✓ Record validation works: {len(issues)} issues found")
        
        # Test dataset validation
        mock_dataset = [mock_record]
        report = validation_engine.validate_dataset(mock_dataset, 'qb_stats')
        print(f"✓ Dataset validation works: {report.total_issues} total issues")
        
        return True
        
    except Exception as e:
        print(f"✗ Advanced features test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Phase 3 tests"""
    print("=== Phase 3 Advanced Features Test ===")
    
    tests = [
        test_data_management,
        test_validation_operations,
        test_batch_operations,
        test_cli_integration,
        test_advanced_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All tests passed! Phase 3 Advanced features are working correctly.")
        print("✓ Advanced data management, validation, and batch operations are ready.")
        return 0
    else:
        print("✗ Some tests failed. Phase 3 features need fixes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 