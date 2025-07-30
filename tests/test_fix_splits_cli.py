#!/usr/bin/env python3
"""
Simple test script for fix-splits functionality
"""

import sys
import os
sys.path.insert(0, 'src')

from cli.commands.fix_splits_command import FixSplitsCommand
import argparse

def test_fix_splits():
    """Test the fix-splits command"""
    
    # Create command instance
    command = FixSplitsCommand()
    
    # Create mock args for preview
    args = argparse.Namespace()
    args.preview = True
    args.force = False
    
    print("Testing fix-splits command with --preview...")
    print("=" * 50)
    
    try:
        result = command.run(args)
        if result == 0:
            print("\n✅ Fix-splits command test completed successfully!")
        else:
            print(f"\n❌ Fix-splits command failed with exit code: {result}")
    except Exception as e:
        print(f"\n❌ Error testing fix-splits command: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fix_splits() 