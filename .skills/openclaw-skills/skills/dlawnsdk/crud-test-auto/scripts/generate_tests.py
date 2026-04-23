#!/usr/bin/env python3
"""
CRUD Test Generator

Generates Python test scripts from configuration file.

Usage:
    python3 generate_tests.py --config <config.json> [--output <dir>]

Example:
    python3 generate_tests.py --config my-service-config.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

TEST_TEMPLATE = '''#!/usr/bin/env python3
"""
Auto-generated CRUD Test: {feature_name}
Generated: {timestamp}
Service: {service_name}
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE = "{api_base}"
AUTH_METHOD = "{auth_method}"

class {class_name}Test:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.resource_id = None
    
    def login(self):
        """Login and get authentication token"""
        print("🔐 Logging in...")
        
        r = requests.post(
            f"{{API_BASE}}{login_endpoint}",
            data={{
                'email': '{email}',
                'password': '{password}'
            }},
            timeout=10
        )
        
        if r.status_code == 200:
            data = r.json()
            {token_extraction}
            {user_id_extraction}
            print(f"  ✅ Login successful")
            return True
        else:
            print(f"  ❌ Login failed: {{r.status_code}}")
            return False
    
    def get_auth_headers(self):
        """Get authentication headers"""
        {auth_headers}
    
    def test_create(self):
        """Test CREATE operation"""
        print("\\n[CREATE] Creating {feature_name}...")
        
        try:
            data = {create_data}
            data.update({{
                'userId': self.user_id
            }})
            
            r = requests.{http_create_method}(
                f"{{API_BASE}}{create_endpoint}",
                data=data,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if r.status_code in [200, 201]:
                result = r.json()
                self.resource_id = {id_extraction}
                print(f"  ✅ CREATE success (ID: {{self.resource_id}})")
                return True
            else:
                print(f"  ❌ CREATE failed: {{r.status_code}}")
                return False
        except Exception as e:
            print(f"  ❌ CREATE error: {{e}}")
            return False
    
    {read_method}
    {update_method}
    
    def test_delete(self):
        """Test DELETE operation (rollback)"""
        if not self.resource_id:
            print("\\n[DELETE] No resource to delete")
            return True
        
        print("\\n[DELETE] Deleting {feature_name} (rollback)...")
        
        try:
            endpoint = "{delete_endpoint}".format(id=self.resource_id)
            
            r = requests.{http_delete_method}(
                f"{{API_BASE}}{{endpoint}}",
                data={{'userId': self.user_id, {delete_id_param}}},
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if r.status_code in [200, 204]:
                print(f"  ✅ DELETE success (rollback complete)")
                self.resource_id = None
                return True
            else:
                print(f"  ⚠️  DELETE failed: {{r.status_code}}")
                return False
        except Exception as e:
            print(f"  ❌ DELETE error: {{e}}")
            return False
    
    def run(self):
        """Run full test suite"""
        print("="*70)
        print("🧪 CRUD Test: {feature_name}")
        print("="*70)
        print(f"Time: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
        print()
        
        if not self.login():
            return
        
        passed = 0
        total = 0
        
        try:
            # CREATE
            total += 1
            if self.test_create():
                passed += 1
            
            {test_sequence}
            
        finally:
            # Always try to delete (rollback)
            self.test_delete()
        
        print()
        print("="*70)
        print(f"🎉 Test Complete: {{passed}}/{{total}} passed ({{passed*100//total if total > 0 else 0}}%)")
        print("="*70)

if __name__ == '__main__':
    tester = {class_name}Test()
    tester.run()
'''

READ_METHOD_TEMPLATE = '''
    def test_read(self):
        """Test READ operation"""
        print("\\n[READ] Reading {feature_name}...")
        
        try:
            {read_code}
            
            if r.status_code == 200:
                result = r.json()
                print(f"  ✅ READ success")
                return True
            else:
                print(f"  ❌ READ failed: {{r.status_code}}")
                return False
        except Exception as e:
            print(f"  ❌ READ error: {{e}}")
            return False
'''

UPDATE_METHOD_TEMPLATE = '''
    def test_update(self):
        """Test UPDATE operation"""
        if not self.resource_id:
            print("\\n[UPDATE] No resource to update")
            return False
        
        print("\\n[UPDATE] Updating {feature_name}...")
        
        try:
            endpoint = "{update_endpoint}".format(id=self.resource_id)
            data = {update_data}
            data.update({{
                'userId': self.user_id,
                {update_id_param}
            }})
            
            r = requests.{http_method}(
                f"{{API_BASE}}{{endpoint}}",
                data=data,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if r.status_code in [200, 201]:
                print(f"  ✅ UPDATE success")
                return True
            else:
                print(f"  ❌ UPDATE failed: {{r.status_code}}")
                return False
        except Exception as e:
            print(f"  ❌ UPDATE error: {{e}}")
            return False
'''

def extract_json_path(path):
    """Convert JSON path to Python code"""
    if '.' in path:
        parts = path.split('.')
        code = "data"
        for part in parts:
            code += f".get('{part}')"
        return code
    else:
        return f"data.get('{path}')"

def generate_auth_headers(auth_config):
    """Generate authentication headers code"""
    method = auth_config.get('method', 'header')
    
    if method == 'header':
        token_key = auth_config.get('token_key', 'Authorization')
        token_prefix = auth_config.get('token_prefix', 'Bearer')
        return f'''return {{
            '{token_key}': '{token_prefix} {{self.token}}'
        }}'''
    
    elif method == 'custom':
        headers = auth_config.get('headers', {})
        lines = ["return {"]
        for key, value in headers.items():
            value = value.replace('{token}', '{self.token}')
            value = value.replace('{user_id}', '{self.user_id}')
            lines.append(f"            '{key}': '{value}',")
        lines.append("        }")
        return '\n'.join(lines)
    
    else:
        return "return {}"

def generate_test(config, feature_key, feature_config, output_dir):
    """Generate test file for a feature"""
    
    service_name = config['service']['name']
    api_base = config['service']['api_base']
    feature_name = feature_config.get('name', feature_key)
    class_name = ''.join(word.capitalize() for word in feature_key.split('_'))
    
    # Authentication
    auth_config = config.get('auth', {'method': 'header'})
    test_account = config.get('test_account', {})
    
    token_path = test_account.get('token_path', 'token')
    user_id_path = test_account.get('user_id_path', 'user_id')
    
    token_extraction = f"self.token = str({extract_json_path(token_path)})"
    user_id_extraction = f"self.user_id = {extract_json_path(user_id_path)}"
    
    # CREATE
    create_config = feature_config.get('create', {})
    create_endpoint = create_config.get('endpoint', f'/{feature_key}')
    create_method = create_config.get('method', 'POST')
    id_field = create_config.get('id_field', 'id')
    test_data = create_config.get('test_data', {})
    
    if not test_data:
        test_data = {
            'content': f'[AutoTest] Test {feature_name}',
            'name': f'Test {feature_name}'
        }
    
    id_extraction = extract_json_path(id_field) if '.' in id_field else f"result.get('{id_field}')"
    
    # READ
    read_method_code = ""
    read_test = ""
    if 'read' in feature_config:
        read_config = feature_config['read']
        read_endpoint = read_config.get('endpoint', f'/{feature_key}')
        
        if 'detail_endpoint' in read_config:
            detail_endpoint = read_config['detail_endpoint']
            read_code = f'''endpoint = "{detail_endpoint}".format(id=self.resource_id)
            r = requests.get(
                f"{{API_BASE}}{{endpoint}}",
                headers=self.get_auth_headers(),
                timeout=10
            )'''
        else:
            read_code = f'''r = requests.get(
                f"{{API_BASE}}{read_endpoint}",
                headers=self.get_auth_headers(),
                timeout=10
            )'''
        
        read_method_code = READ_METHOD_TEMPLATE.format(
            feature_name=feature_name,
            read_code=read_code
        )
        read_test = '''
            # READ
            total += 1
            if self.test_read():
                passed += 1
'''
    
    # UPDATE
    update_method_code = ""
    update_test = ""
    if 'update' in feature_config:
        update_config = feature_config['update']
        update_endpoint = update_config.get('endpoint', f'/{feature_key}/{{id}}')
        update_method = update_config.get('method', 'PUT')
        update_data = test_data.copy()
        update_data['content'] = f'[AutoTest] Updated {feature_name}'
        
        update_id_param = f"'{feature_key}_id': self.resource_id"
        
        update_method_code = UPDATE_METHOD_TEMPLATE.format(
            feature_name=feature_name,
            update_endpoint=update_endpoint,
            http_method=update_method.lower(),
            update_data=json.dumps(update_data),
            update_id_param=update_id_param
        )
        update_test = '''
            # UPDATE
            total += 1
            if self.test_update():
                passed += 1
'''
    
    # DELETE
    delete_config = feature_config.get('delete', {})
    delete_endpoint = delete_config.get('endpoint', f'/{feature_key}/{{id}}')
    delete_method = delete_config.get('method', 'DELETE')
    delete_id_param = f"'{feature_key}_id': self.resource_id"
    
    test_sequence = read_test + update_test
    
    # Generate final code
    code = TEST_TEMPLATE.format(
        feature_name=feature_name,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        service_name=service_name,
        api_base=api_base,
        auth_method=auth_config.get('method', 'header'),
        class_name=class_name,
        login_endpoint=test_account.get('login_endpoint', '/login'),
        email=test_account.get('email', 'test@example.com'),
        password=test_account.get('password', 'password'),
        token_extraction=token_extraction,
        user_id_extraction=user_id_extraction,
        auth_headers=generate_auth_headers(auth_config),
        http_create_method=create_method.lower(),
        create_endpoint=create_endpoint,
        create_data=json.dumps(test_data),
        id_extraction=id_extraction,
        read_method=read_method_code,
        update_method=update_method_code,
        delete_endpoint=delete_endpoint,
        http_delete_method=delete_method.lower(),
        delete_id_param=delete_id_param,
        test_sequence=test_sequence
    )
    
    # Write file
    output_file = output_dir / f"test_{feature_key}_crud.py"
    output_file.write_text(code)
    output_file.chmod(0o755)
    
    print(f"✅ Generated: {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Generate CRUD tests from configuration')
    parser.add_argument('--config', required=True, help='Configuration file path')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--dry-run', action='store_true', help='Generate tests without write operations')
    parser.add_argument('--read-only', action='store_true', help='Generate read-only tests (no create/update/delete)')
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Safety check: environment validation
    api_base = config['service']['api_base']
    environment = config['service'].get('environment', 'unknown')
    
    # Warn on production-like URLs
    if any(prod_pattern in api_base.lower() for prod_pattern in ['production', 'prod.', 'api.myservice.com', 'live']):
        print("="*70)
        print("⚠️  WARNING: Production-like API detected!")
        print(f"   API: {api_base}")
        print(f"   Environment: {environment}")
        print()
        print("   This skill is designed for dev/staging ONLY.")
        print("   Running tests against production may:")
        print("   - Create real data")
        print("   - Trigger real notifications")
        print("   - Consume quotas/credits")
        print("   - Leave orphaned resources")
        print()
        if not args.dry_run and not args.read_only:
            response = input("   Type 'YES' to continue anyway: ")
            if response != 'YES':
                print("   Aborted.")
                return
        print("="*70)
        print()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # Generate tests for each feature
    print("="*70)
    print("🔧 Generating CRUD Tests")
    print("="*70)
    print(f"Config: {config_path}")
    print(f"Service: {config['service']['name']}")
    print(f"Features: {len(config['features'])}")
    print()
    
    generated_files = []
    for feature_key, feature_config in config['features'].items():
        test_file = generate_test(config, feature_key, feature_config, output_dir)
        generated_files.append(test_file)
    
    print()
    print("="*70)
    print(f"🎉 Generated {len(generated_files)} test files")
    print("="*70)
    print()
    print("Next steps:")
    for f in generated_files:
        print(f"  python3 {f}")

if __name__ == '__main__':
    main()
