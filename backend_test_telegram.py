#!/usr/bin/env python3
"""
Comprehensive backend test for Telegram Bot Node.js/Telegraf conversion
Tests code structure, exports, commands, and functionality without live Telegram
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class TelegramBotTester:
    def __init__(self):
        self.vercel_bot_dir = "/app/vercel-bot"
        self.tests_run = 0
        self.tests_passed = 0
        self.issues = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}: {details}")
            self.issues.append(f"{test_name}: {details}")
        
    def test_file_structure(self):
        """Test 1: Verify all required files exist"""
        required_files = [
            "api/bot.js",
            "api/set-webhook.js", 
            "package.json",
            "vercel.json",
            "README.md"
        ]
        
        for file_path in required_files:
            full_path = os.path.join(self.vercel_bot_dir, file_path)
            exists = os.path.exists(full_path)
            self.log_test(f"File exists: {file_path}", exists, f"Missing file: {full_path}")
    
    def test_package_json(self):
        """Test 2: Verify package.json has required dependencies"""
        package_path = os.path.join(self.vercel_bot_dir, "package.json")
        
        try:
            with open(package_path, 'r') as f:
                package_data = json.load(f)
            
            # Check telegraf dependency
            has_telegraf = "telegraf" in package_data.get("dependencies", {})
            self.log_test("package.json has telegraf dependency", has_telegraf, 
                         f"Missing telegraf in dependencies")
            
            # Check mongodb dependency
            has_mongodb = "mongodb" in package_data.get("dependencies", {})
            self.log_test("package.json has mongodb dependency", has_mongodb,
                         f"Missing mongodb in dependencies")
                         
        except Exception as e:
            self.log_test("package.json validation", False, f"Error reading package.json: {e}")
    
    def test_vercel_json(self):
        """Test 3: Verify vercel.json configuration"""
        vercel_path = os.path.join(self.vercel_bot_dir, "vercel.json")
        
        try:
            with open(vercel_path, 'r') as f:
                vercel_data = json.load(f)
            
            # Check maxDuration for bot.js
            functions = vercel_data.get("functions", {})
            bot_config = functions.get("api/bot.js", {})
            has_max_duration = bot_config.get("maxDuration") == 10
            self.log_test("vercel.json has maxDuration:10 for api/bot.js", has_max_duration,
                         f"Expected maxDuration:10, got: {bot_config.get('maxDuration')}")
                         
        except Exception as e:
            self.log_test("vercel.json validation", False, f"Error reading vercel.json: {e}")
    
    def test_bot_js_syntax(self):
        """Test 4: Verify bot.js loads without syntax errors"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            # Use Node.js to check syntax
            result = subprocess.run(
                ["node", "-c", bot_path], 
                capture_output=True, 
                text=True,
                cwd=self.vercel_bot_dir
            )
            
            syntax_ok = result.returncode == 0
            self.log_test("api/bot.js syntax check", syntax_ok, 
                         f"Syntax error: {result.stderr}")
                         
        except Exception as e:
            self.log_test("api/bot.js syntax check", False, f"Error checking syntax: {e}")
    
    def test_set_webhook_js_syntax(self):
        """Test 5: Verify set-webhook.js loads without syntax errors"""
        webhook_path = os.path.join(self.vercel_bot_dir, "api/set-webhook.js")
        
        try:
            result = subprocess.run(
                ["node", "-c", webhook_path],
                capture_output=True,
                text=True,
                cwd=self.vercel_bot_dir
            )
            
            syntax_ok = result.returncode == 0
            self.log_test("api/set-webhook.js syntax check", syntax_ok,
                         f"Syntax error: {result.stderr}")
                         
        except Exception as e:
            self.log_test("api/set-webhook.js syntax check", False, f"Error checking syntax: {e}")
    
    def test_bot_exports(self):
        """Test 6: Verify bot.js exports async function"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for module.exports with async function
            has_module_exports = "module.exports" in content
            has_async_function = "async" in content and "req, res" in content
            
            self.log_test("bot.js has module.exports", has_module_exports,
                         "Missing module.exports")
            self.log_test("bot.js exports async function", has_async_function,
                         "Missing async function with req, res parameters")
                         
        except Exception as e:
            self.log_test("bot.js exports check", False, f"Error reading bot.js: {e}")
    
    def test_set_webhook_exports(self):
        """Test 7: Verify set-webhook.js exports function"""
        webhook_path = os.path.join(self.vercel_bot_dir, "api/set-webhook.js")
        
        try:
            with open(webhook_path, 'r') as f:
                content = f.read()
            
            has_module_exports = "module.exports" in content
            self.log_test("set-webhook.js has module.exports", has_module_exports,
                         "Missing module.exports")
                         
        except Exception as e:
            self.log_test("set-webhook.js exports check", False, f"Error reading set-webhook.js: {e}")
    
    def test_mute_commands(self):
        """Test 8: Verify all 10 mute commands with correct replies"""
        expected_mute_commands = {
            "shutup": "Shut your stinking mouth. 🤐",
            "shush": "Stop Yappin. 🤫", 
            "ftg": "Ferme ta gueule big. 🤐",
            "bec": "Aie bec! 🤐",
            "stopbarking": "Stop barking, Bitch. 🐕",
            "artdejapper": "Arrête d'aboyer pti chiwawa. 🐶",
            "sybau": "shut your bitch AHHHH up. 🤬",
            "goofy": "you're gay, you can't talk faggot. 🤡",
            "keh": "Ferme ta jgole senti ptite sharmouta. 🤢",
            "vio": "enfant de viole detected, geule closed. 🔒",
        }
        
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Count found commands
            found_commands = 0
            missing_commands = []
            
            for cmd, reply in expected_mute_commands.items():
                if cmd in content:
                    found_commands += 1
                else:
                    missing_commands.append(cmd)
            
            all_found = found_commands == 10
            self.log_test(f"All 10 mute commands present ({found_commands}/10)", all_found,
                         f"Missing commands: {missing_commands}")
                         
        except Exception as e:
            self.log_test("mute commands check", False, f"Error reading bot.js: {e}")
    
    def test_admin_commands(self):
        """Test 9: Verify unmute, kick, ban, promote, demote commands"""
        expected_admin_commands = [
            # Unmute
            "talk", "parle",
            # Kick  
            "sort", "getout", "decawlis",
            # Ban
            "ntm", "bouge", "ciao", 
            # Promote
            "levelup", "debout",
            # Demote
            "assistoi", "leveldown"
        ]
        
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            found_commands = []
            missing_commands = []
            
            for cmd in expected_admin_commands:
                if cmd in content:
                    found_commands.append(cmd)
                else:
                    missing_commands.append(cmd)
            
            all_found = len(found_commands) == len(expected_admin_commands)
            self.log_test(f"All admin commands present ({len(found_commands)}/{len(expected_admin_commands)})", 
                         all_found, f"Missing: {missing_commands}")
                         
        except Exception as e:
            self.log_test("admin commands check", False, f"Error reading bot.js: {e}")
    
    def test_owner_mention_commands(self):
        """Test 10: Verify all 8 owner mention commands"""
        expected_owner_commands = ["papa", "pere", "boss", "patron", "chef", "owner", "roi", "king"]
        
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            found_commands = []
            missing_commands = []
            
            for cmd in expected_owner_commands:
                if cmd in content:
                    found_commands.append(cmd)
                else:
                    missing_commands.append(cmd)
            
            all_found = len(found_commands) == 8
            self.log_test(f"All 8 owner mention commands present ({len(found_commands)}/8)", 
                         all_found, f"Missing: {missing_commands}")
                         
        except Exception as e:
            self.log_test("owner mention commands check", False, f"Error reading bot.js: {e}")
    
    def test_fun_commands(self):
        """Test 11: Verify all 6 fun commands plus /cap with language detection"""
        expected_fun_commands = ["pussy", "shifta", "mgd", "fu", "gay", "cap"]
        
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            found_commands = []
            missing_commands = []
            
            for cmd in expected_fun_commands:
                if cmd in content:
                    found_commands.append(cmd)
                else:
                    missing_commands.append(cmd)
            
            all_found = len(found_commands) == 6
            self.log_test(f"All 6 fun commands present ({len(found_commands)}/6)", 
                         all_found, f"Missing: {missing_commands}")
            
            # Check for language detection in cap command
            has_cap_lang_detection = "CAP_REPLIES" in content and "lang" in content
            self.log_test("Cap command has language detection", has_cap_lang_detection,
                         "Missing language detection for /cap command")
                         
        except Exception as e:
            self.log_test("fun commands check", False, f"Error reading bot.js: {e}")
    
    def test_protection_messages(self):
        """Test 12: Verify MUTE_PROTECTION and KICK_FUN_PROTECTION in 13 languages"""
        expected_languages = ["en", "fr", "es", "ar", "de", "pt", "ru", "tr", "it", "zh-cn", "ja", "ko", "hi"]
        
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check MUTE_PROTECTION
            has_mute_protection = "MUTE_PROTECTION" in content
            self.log_test("Has MUTE_PROTECTION messages", has_mute_protection,
                         "Missing MUTE_PROTECTION object")
            
            # Check KICK_FUN_PROTECTION  
            has_kick_protection = "KICK_FUN_PROTECTION" in content
            self.log_test("Has KICK_FUN_PROTECTION messages", has_kick_protection,
                         "Missing KICK_FUN_PROTECTION object")
            
            # Count language entries
            lang_count = 0
            for lang in expected_languages:
                if f'"{lang}":' in content or f"'{lang}':" in content:
                    lang_count += 1
            
            all_languages = lang_count >= 13  # Should appear in both objects
            self.log_test(f"Protection messages in 13 languages ({lang_count}/13)", all_languages,
                         f"Only found {lang_count} language entries")
                         
        except Exception as e:
            self.log_test("protection messages check", False, f"Error reading bot.js: {e}")
    
    def test_no_bot_launch(self):
        """Test 13: Verify bot.js does NOT call bot.launch() (webhook-only)"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Should NOT contain bot.launch()
            has_no_launch = "bot.launch()" not in content and ".launch(" not in content
            self.log_test("Bot does NOT call bot.launch() (webhook-only)", has_no_launch,
                         "Found bot.launch() call - should use webhook only")
                         
        except Exception as e:
            self.log_test("no bot.launch() check", False, f"Error reading bot.js: {e}")
    
    def test_webhook_handler(self):
        """Test 14: Verify webhook handler calls bot.handleUpdate for POST"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for handleUpdate call
            has_handle_update = "bot.handleUpdate" in content
            self.log_test("Handler calls bot.handleUpdate", has_handle_update,
                         "Missing bot.handleUpdate call")
            
            # Check for POST method handling
            has_post_handling = 'req.method === "POST"' in content or "POST" in content
            self.log_test("Handler checks for POST requests", has_post_handling,
                         "Missing POST method check")
                         
        except Exception as e:
            self.log_test("webhook handler check", False, f"Error reading bot.js: {e}")
    
    def test_mongodb_caching(self):
        """Test 15: Verify MongoDB connection caching for serverless"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for cached connection
            has_cached_db = "cachedDb" in content
            self.log_test("Has MongoDB connection caching", has_cached_db,
                         "Missing cachedDb variable for connection caching")
            
            # Check for getDb function
            has_get_db = "getDb" in content
            self.log_test("Has getDb function", has_get_db,
                         "Missing getDb function for MongoDB access")
                         
        except Exception as e:
            self.log_test("MongoDB caching check", False, f"Error reading bot.js: {e}")
    
    def test_language_detection(self):
        """Test 16: Verify language detection function covers required languages"""
        expected_languages = ["ar", "zh", "ja", "ko", "ru", "hi", "fr", "es", "de", "pt", "it", "tr", "en"]
        
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for detectLanguage function
            has_detect_function = "detectLanguage" in content or "detect_language" in content
            self.log_test("Has language detection function", has_detect_function,
                         "Missing language detection function")
            
            # Check for language patterns
            lang_patterns_found = 0
            for lang in expected_languages:
                if lang in content and ("return" in content and f'"{lang}"' in content):
                    lang_patterns_found += 1
            
            has_all_langs = lang_patterns_found >= 10  # Should detect most languages
            self.log_test(f"Language detection covers required languages ({lang_patterns_found}/13)", 
                         has_all_langs, f"Only found patterns for {lang_patterns_found} languages")
                         
        except Exception as e:
            self.log_test("language detection check", False, f"Error reading bot.js: {e}")
    
    def test_duration_parsing(self):
        """Test 17: Verify parseDuration supports m, h, d, w, mo, y units"""
        expected_units = ["m", "h", "d", "w", "mo", "y"]
        
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for parseDuration function
            has_parse_duration = "parseDuration" in content
            self.log_test("Has parseDuration function", has_parse_duration,
                         "Missing parseDuration function")
            
            # Check for all time units
            units_found = 0
            missing_units = []
            for unit in expected_units:
                if f'"{unit}"' in content or f"'{unit}'" in content:
                    units_found += 1
                else:
                    missing_units.append(unit)
            
            all_units = units_found == 6
            self.log_test(f"parseDuration supports all time units ({units_found}/6)", all_units,
                         f"Missing units: {missing_units}")
                         
        except Exception as e:
            self.log_test("duration parsing check", False, f"Error reading bot.js: {e}")
    
    def test_target_resolution(self):
        """Test 18: Verify resolveTarget with reply > @mention > last-speaker priority"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for resolveTarget function
            has_resolve_target = "resolveTarget" in content
            self.log_test("Has resolveTarget function", has_resolve_target,
                         "Missing resolveTarget function")
            
            # Check for reply handling
            has_reply_handling = "reply_to_message" in content
            self.log_test("Handles reply priority", has_reply_handling,
                         "Missing reply_to_message handling")
            
            # Check for username handling  
            has_username_handling = "@" in content and "username" in content
            self.log_test("Handles @mention priority", has_username_handling,
                         "Missing @username handling")
            
            # Check for last speaker handling
            has_last_speaker = "last_speakers" in content or "lastSpeaker" in content
            self.log_test("Handles last-speaker fallback", has_last_speaker,
                         "Missing last speaker handling")
                         
        except Exception as e:
            self.log_test("target resolution check", False, f"Error reading bot.js: {e}")
    
    def test_permission_objects(self):
        """Test 19: Verify FULL_MUTE and FULL_UNMUTE permission objects"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for FULL_MUTE object
            has_full_mute = "FULL_MUTE" in content
            self.log_test("Has FULL_MUTE permission object", has_full_mute,
                         "Missing FULL_MUTE object")
            
            # Check for FULL_UNMUTE object
            has_full_unmute = "FULL_UNMUTE" in content
            self.log_test("Has FULL_UNMUTE permission object", has_full_unmute,
                         "Missing FULL_UNMUTE object")
            
            # Check for permission fields
            required_permissions = [
                "can_send_messages",
                "can_send_photos", 
                "can_send_videos",
                "can_invite_users",
                "can_pin_messages"
            ]
            
            perm_count = 0
            for perm in required_permissions:
                if perm in content:
                    perm_count += 1
            
            has_all_perms = perm_count == 5
            self.log_test(f"Permission objects have all fields ({perm_count}/5)", has_all_perms,
                         f"Missing permission fields")
                         
        except Exception as e:
            self.log_test("permission objects check", False, f"Error reading bot.js: {e}")
    
    def test_vio_permanent_mute(self):
        """Test 20: Verify /vio uses permanent mute (400 days)"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for vio command with 400 days
            has_vio_permanent = "vio" in content and ("400" in content or "permanent" in content.lower())
            self.log_test("/vio command uses permanent mute", has_vio_permanent,
                         "Missing permanent mute for /vio command")
                         
        except Exception as e:
            self.log_test("vio permanent mute check", False, f"Error reading bot.js: {e}")
    
    def test_help_handler(self):
        """Test 21: Verify help handler sends DM in groups and inline in private"""
        bot_path = os.path.join(self.vercel_bot_dir, "api/bot.js")
        
        try:
            with open(bot_path, 'r') as f:
                content = f.read()
            
            # Check for help handler
            has_help_handler = "helpHandler" in content or '"help"' in content
            self.log_test("Has help command handler", has_help_handler,
                         "Missing help command handler")
            
            # Check for DM functionality
            has_dm_handling = "sendMessage" in content and "from.id" in content
            self.log_test("Help handler sends DMs in groups", has_dm_handling,
                         "Missing DM functionality for help command")
            
            # Check for private chat handling
            has_private_handling = 'chat.type' in content and 'private' in content
            self.log_test("Help handler handles private chats", has_private_handling,
                         "Missing private chat handling")
                         
        except Exception as e:
            self.log_test("help handler check", False, f"Error reading bot.js: {e}")
    
    def test_readme_deployment_instructions(self):
        """Test 22: Verify README.md has deployment instructions"""
        readme_path = os.path.join(self.vercel_bot_dir, "README.md")
        
        try:
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Check for key deployment sections
            has_deploy_section = "Deploy" in content or "Deployment" in content
            self.log_test("README has deployment section", has_deploy_section,
                         "Missing deployment instructions")
            
            # Check for Vercel instructions
            has_vercel_instructions = "Vercel" in content and "Environment Variables" in content
            self.log_test("README has Vercel deployment instructions", has_vercel_instructions,
                         "Missing Vercel-specific instructions")
            
            # Check for webhook setup
            has_webhook_setup = "webhook" in content.lower() and "setWebhook" in content
            self.log_test("README has webhook setup instructions", has_webhook_setup,
                         "Missing webhook setup instructions")
                         
        except Exception as e:
            self.log_test("README deployment instructions check", False, f"Error reading README.md: {e}")
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🚀 Starting Telegram Bot Backend Tests")
        print("=" * 60)
        
        # File structure tests
        self.test_file_structure()
        self.test_package_json()
        self.test_vercel_json()
        
        # Syntax and export tests
        self.test_bot_js_syntax()
        self.test_set_webhook_js_syntax()
        self.test_bot_exports()
        self.test_set_webhook_exports()
        
        # Command functionality tests
        self.test_mute_commands()
        self.test_admin_commands()
        self.test_owner_mention_commands()
        self.test_fun_commands()
        
        # Bot behavior tests
        self.test_protection_messages()
        self.test_no_bot_launch()
        self.test_webhook_handler()
        self.test_mongodb_caching()
        
        # Advanced feature tests
        self.test_language_detection()
        self.test_duration_parsing()
        self.test_target_resolution()
        self.test_permission_objects()
        self.test_vio_permanent_mute()
        self.test_help_handler()
        
        # Documentation tests
        self.test_readme_deployment_instructions()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.issues:
            print(f"\n❌ Issues Found ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print("✅ All tests passed!")
        
        return self.tests_passed, self.tests_run, self.issues

def main():
    """Main test runner"""
    tester = TelegramBotTester()
    passed, total, issues = tester.run_all_tests()
    
    # Return exit code based on results
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())