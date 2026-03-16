#!/usr/bin/env python3

import requests
import sys
from datetime import datetime
import json

class TelegramBotAPITester:
    def __init__(self, base_url="https://casper-moderation.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def run_test(self, name, method, endpoint, expected_status=200, expected_fields=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response: {response.text}")

            # Check expected fields if provided
            if success and expected_fields and response_data:
                for field in expected_fields:
                    if field not in response_data:
                        print(f"   ❌ Missing expected field: {field}")
                        success = False
                    else:
                        print(f"   ✅ Found expected field: {field}")

            if success:
                self.tests_passed += 1
                print(f"✅ {name} - PASSED")
                self.results.append({"test": name, "status": "PASSED", "response": response_data})
            else:
                print(f"❌ {name} - FAILED (Expected {expected_status}, got {response.status_code})")
                self.results.append({"test": name, "status": "FAILED", "response": response_data})

            return success, response_data

        except requests.exceptions.RequestException as e:
            print(f"❌ {name} - FAILED - Network Error: {str(e)}")
            self.results.append({"test": name, "status": "FAILED", "error": str(e)})
            return False, {}
        except Exception as e:
            print(f"❌ {name} - FAILED - Error: {str(e)}")
            self.results.append({"test": name, "status": "FAILED", "error": str(e)})
            return False, {}

    def test_root_endpoint(self):
        """Test GET /api/ returns root message"""
        return self.run_test(
            "Root API Endpoint",
            "GET", 
            "",
            expected_status=200,
            expected_fields=["message"]
        )

    def test_bot_status(self):
        """Test GET /api/bot/status returns online status with uptime"""
        return self.run_test(
            "Bot Status Endpoint",
            "GET",
            "bot/status",
            expected_status=200,
            expected_fields=["status", "uptime_seconds"]
        )

    def test_bot_stats(self):
        """Test GET /api/bot/stats returns correct stat structure"""
        return self.run_test(
            "Bot Stats Endpoint",
            "GET",
            "bot/stats", 
            expected_status=200,
            expected_fields=["total_commands", "mute_count", "unmute_count", "kick_count", 
                           "ban_count", "promote_count", "demote_count", "fun_count", "groups_count"]
        )

    def test_bot_commands(self):
        """Test GET /api/bot/commands returns all command categories"""
        success, data = self.run_test(
            "Bot Commands Endpoint",
            "GET",
            "bot/commands",
            expected_status=200
        )
        
        # Check for specific command categories
        expected_categories = ["mute", "unmute", "kick", "ban", "admin", "fun", "owner", "help"]
        if success and data:
            for category in expected_categories:
                if category in data:
                    print(f"   ✅ Found command category: {category}")
                    if isinstance(data[category], list) and data[category]:
                        print(f"      Commands count: {len(data[category])}")
                else:
                    print(f"   ❌ Missing command category: {category}")
                    success = False
        
        return success, data

    def validate_command_structure(self, commands_data):
        """Validate the structure of command data"""
        issues = []
        
        # Check mute commands (should have 10 variants)
        if "mute" in commands_data:
            mute_commands = commands_data["mute"]
            if len(mute_commands) != 10:
                issues.append(f"Mute commands count mismatch: expected 10, got {len(mute_commands)}")
        else:
            issues.append("Missing mute commands category")

        # Check unmute commands (should have 2)
        if "unmute" in commands_data:
            unmute_commands = commands_data["unmute"]
            if len(unmute_commands) != 2:
                issues.append(f"Unmute commands count mismatch: expected 2, got {len(unmute_commands)}")
        else:
            issues.append("Missing unmute commands category")

        # Check kick commands (should have 3)
        if "kick" in commands_data:
            kick_commands = commands_data["kick"]
            if len(kick_commands) != 3:
                issues.append(f"Kick commands count mismatch: expected 3, got {len(kick_commands)}")
        else:
            issues.append("Missing kick commands category")

        # Check ban commands (should have 3)
        if "ban" in commands_data:
            ban_commands = commands_data["ban"]
            if len(ban_commands) != 3:
                issues.append(f"Ban commands count mismatch: expected 3, got {len(ban_commands)}")
        else:
            issues.append("Missing ban commands category")

        # Check admin commands (should have 4)
        if "admin" in commands_data:
            admin_commands = commands_data["admin"]
            if len(admin_commands) != 4:
                issues.append(f"Admin commands count mismatch: expected 4, got {len(admin_commands)}")
        else:
            issues.append("Missing admin commands category")

        # Check fun commands (should have 6)
        if "fun" in commands_data:
            fun_commands = commands_data["fun"]
            if len(fun_commands) != 6:
                issues.append(f"Fun commands count mismatch: expected 6, got {len(fun_commands)}")
        else:
            issues.append("Missing fun commands category")

        return issues

def main():
    print("🚀 Starting Telegram Moderation Bot API Tests")
    print("=" * 60)
    
    # Setup
    tester = TelegramBotAPITester()
    
    # Run all API tests
    print("\n📊 RUNNING API ENDPOINT TESTS")
    print("-" * 40)
    
    # Test 1: Root endpoint
    tester.test_root_endpoint()
    
    # Test 2: Bot status
    tester.test_bot_status()
    
    # Test 3: Bot stats
    tester.test_bot_stats()
    
    # Test 4: Bot commands
    success, commands_data = tester.test_bot_commands()
    
    # Validate command structure
    if success and commands_data:
        print("\n🔍 Validating Command Structure...")
        issues = tester.validate_command_structure(commands_data)
        if issues:
            print("   ❌ Command structure issues found:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ Command structure validation passed")

    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️ {tester.tests_run - tester.tests_passed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())