#!/usr/bin/env python3
"""
Test Flask integration with Link Transformation feature.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

def test_flask_app():
    """Test Flask app can start with link transformation feature."""
    
    try:
        from src.app import create_app
        
        # Create Flask app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test that link transformation blueprint is registered
        blueprints = [bp.name for bp in app.blueprints.values()]
        print(f"📋 Registered blueprints: {', '.join(blueprints)}")
        
        if 'api_v2_link_transformation' in blueprints:
            print("✅ Link Transformation blueprint registered")
        else:
            print("❌ Link Transformation blueprint NOT found")
            return False
            
        # Test specific routes
        with app.test_client() as client:
            # Test match types endpoint
            response = client.get('/api/v2/link-transformation/match-types')
            print(f"📡 Match types endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    match_types = [mt['value'] for mt in data.get('data', [])]
                    print(f"✅ Match types available: {', '.join(match_types)}")
                    
                    if 'markdown_link' in match_types:
                        print("✅ MARKDOWN_LINK type is supported")
                    else:
                        print("❌ MARKDOWN_LINK type missing")
                        return False
                else:
                    print("❌ Invalid response format")
                    return False
            else:
                print("❌ Match types endpoint failed")
                return False
                
            # Test templates endpoint
            response = client.get('/api/v2/link-transformation/templates') 
            print(f"📡 Templates endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    templates = data.get('data', [])
                    template_names = [t['name'] for t in templates]
                    print(f"✅ Templates available: {', '.join(template_names)}")
                    
                    markdown_template = any('Markdown' in name for name in template_names)
                    if markdown_template:
                        print("✅ Markdown template available")
                    else:
                        print("❌ Markdown template missing")
                        return False
                else:
                    print("❌ Invalid templates response")
                    return False
            else:
                print("❌ Templates endpoint failed") 
                return False
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during Flask integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TESTING FLASK INTEGRATION")
    print("=" * 50)
    
    success = test_flask_app()
    
    print("=" * 50)
    if success:
        print("✅ Flask integration test completed successfully!")
    else:
        print("❌ Flask integration test failed!")
        
    sys.exit(0 if success else 1)













