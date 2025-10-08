"""
<API Endpoint Name> - REST API v2

AI-CONTEXT: REST API Layer (v2) - Adapter in Hexagonal Architecture
AI-CONTEXT: <Main responsibility of this endpoint>
AI-CONTEXT: Uses use cases for business logic, no business logic here

Created: <YYYY-MM-DD>
"""

from flask import Blueprint, request, jsonify
from flask_httpauth import HTTPBasicAuth
from marshmallow import Schema, fields, ValidationError

# AI-LINK: core/usecases/<related_usecase>.py
# AI-HINT: Authentication handled by @auth.login_required decorator

api_bp = Blueprint('api_my_endpoint', __name__)
auth = HTTPBasicAuth()

# AI-HINT: Request/Response schemas for validation
class MyRequestSchema(Schema):
    """
    Request validation schema
    
    AI-HINT: See marshmallow docs for field types
    """
    field1 = fields.Str(required=True)
    field2 = fields.Int(required=False)

class MyResponseSchema(Schema):
    """Response serialization schema"""
    result = fields.Str()
    status = fields.Str()

# AI-WARNING: Backward compatibility! Don't change response structure
# AI-HINT: Version API if breaking changes needed
@api_bp.route('/my-endpoint', methods=['GET'])
@auth.login_required
# AI-LINK: core/usecases/<usecase>.py:<method_name>()
def get_endpoint():
    """
    GET /api/v2/my-endpoint
    
    Description: <What this endpoint does>
    
    Returns:
        JSON: <response structure>
        
    AI-HINT: Query params: <list params>
    AI-HINT: Authentication required
    """
    try:
        # AI-HINT: Get use case from application layer
        use_case = get_use_case()  # Your initialization logic
        
        # AI-HINT: Call use case, handle business logic there
        result = use_case.do_something()
        
        # AI-HINT: Serialize response
        schema = MyResponseSchema()
        return jsonify(schema.dump(result)), 200
        
    except ValidationError as e:
        # AI-HINT: Validation errors return 400
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        # AI-WARNING: Never expose internal errors to client
        # AI-HINT: Log error for debugging
        logger.error(f"Endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/my-endpoint', methods=['POST'])
@auth.login_required
# AI-LINK: core/usecases/<usecase>.py:<method_name>()
# AI-WARNING: Validate all input! Never trust user data
def create_endpoint():
    """
    POST /api/v2/my-endpoint
    
    Description: <What this endpoint does>
    
    Request body:
        <describe structure>
        
    Returns:
        JSON: <response structure>
        
    AI-HINT: Request validation via MyRequestSchema
    """
    try:
        # AI-HINT: Validate request
        schema = MyRequestSchema()
        data = schema.load(request.json)
        
        # AI-HINT: Call use case
        use_case = get_use_case()
        result = use_case.create_something(data)
        
        return jsonify({"status": "created", "id": result.id}), 201
        
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        logger.error(f"Create endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# AI-HINT: Register this blueprint in src/api/v2/__init__.py
# AI-HINT: Update MODULE_MAP.md with new endpoint
# AI-HINT: Add API docs to SWAGGER/OpenAPI

