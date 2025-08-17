"""
Document Requirements System

This module manages document upload requirements based on entity type and roles,
following the semantic specification for document requirements.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DocumentRequirement:
    """Document requirement specification."""
    
    entity_type: str
    role_id: Optional[str]
    document_code: str
    description: str
    required_rule: str
    accepted_formats: List[str]
    max_size_mb: int
    capture_phase: str
    condition: Optional[str] = None


class DocumentRequirementsManager:
    """Manager for document requirements."""
    
    def __init__(self):
        self._requirements = self._load_document_requirements()
    
    def _load_document_requirements(self) -> List[DocumentRequirement]:
        """Load document requirements from JSON."""
        try:
            data_path = Path(__file__).parent / "data" / "document_requirements.json"
            with open(data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            requirements = []
            for req_data in data.get("document_requirements", []):
                requirements.append(DocumentRequirement(**req_data))
            
            return requirements
            
        except Exception as e:
            print(f"Warning: Could not load document requirements: {e}")
            return []
    
    def get_requirements_for_entity_type(self, entity_type: str, roles: List[str] = None) -> List[DocumentRequirement]:
        """
        Get document requirements for an entity type and roles.
        
        Args:
            entity_type: The entity type code (e.g., 'COMPANY')
            roles: List of role IDs that are present
            
        Returns:
            List of applicable document requirements
        """
        applicable_requirements = []
        roles = roles or []
        
        for req in self._requirements:
            # Check if requirement applies to this entity type
            if req.entity_type != "ALL" and req.entity_type != entity_type:
                continue
            
            # Check if requirement applies to any of the roles
            if req.role_id and req.role_id not in roles:
                continue
            
            # Check if it's a general entity requirement (no role specified)
            if not req.role_id or req.role_id in roles:
                applicable_requirements.append(req)
        
        return applicable_requirements
    
    def get_required_documents(self, entity_type: str, roles: List[str] = None, 
                              context: Dict[str, Any] = None) -> List[DocumentRequirement]:
        """
        Get documents that are absolutely required for submission.
        
        Args:
            entity_type: The entity type code
            roles: List of role IDs that are present
            context: Additional context for conditional requirements
            
        Returns:
            List of required document requirements
        """
        requirements = self.get_requirements_for_entity_type(entity_type, roles)
        required_docs = []
        context = context or {}
        
        for req in requirements:
            if req.required_rule == "REQUIRED":
                required_docs.append(req)
            elif req.required_rule == "CONDITIONAL":
                if self._evaluate_condition(req, context):
                    required_docs.append(req)
        
        return required_docs
    
    def get_optional_documents(self, entity_type: str, roles: List[str] = None) -> List[DocumentRequirement]:
        """Get documents that are optional for submission."""
        requirements = self.get_requirements_for_entity_type(entity_type, roles)
        return [req for req in requirements if req.required_rule == "OPTIONAL"]
    
    def validate_uploaded_documents(self, entity_type: str, roles: List[str], 
                                   uploaded_docs: Dict[str, Any], 
                                   context: Dict[str, Any] = None) -> tuple[bool, List[str]]:
        """
        Validate that all required documents have been uploaded.
        
        Args:
            entity_type: The entity type code
            roles: List of role IDs that are present
            uploaded_docs: Dict mapping document codes to uploaded file info
            context: Additional context for conditional requirements
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        required_docs = self.get_required_documents(entity_type, roles, context)
        errors = []
        
        for req in required_docs:
            doc_key = self._get_document_key(req)
            
            if doc_key not in uploaded_docs or not uploaded_docs[doc_key]:
                errors.append(f"Required document missing: {req.description}")
            else:
                # Validate file format and size
                file_info = uploaded_docs[doc_key]
                format_errors = self._validate_file_format(req, file_info)
                size_errors = self._validate_file_size(req, file_info)
                errors.extend(format_errors)
                errors.extend(size_errors)
        
        return len(errors) == 0, errors
    
    def get_document_upload_schema(self, entity_type: str, roles: List[str] = None) -> Dict[str, Any]:
        """
        Get the document upload schema for UI generation.
        
        Returns a structured schema that can be used to generate upload UI.
        """
        requirements = self.get_requirements_for_entity_type(entity_type, roles)
        
        schema = {
            "entity_documents": [],
            "role_documents": {}
        }
        
        for req in requirements:
            doc_info = {
                "document_code": req.document_code,
                "description": req.description,
                "required": req.required_rule == "REQUIRED",
                "accepted_formats": req.accepted_formats,
                "max_size_mb": req.max_size_mb,
                "condition": req.condition
            }
            
            if req.role_id:
                if req.role_id not in schema["role_documents"]:
                    schema["role_documents"][req.role_id] = []
                schema["role_documents"][req.role_id].append(doc_info)
            else:
                schema["entity_documents"].append(doc_info)
        
        return schema
    
    def _evaluate_condition(self, requirement: DocumentRequirement, context: Dict[str, Any]) -> bool:
        """Evaluate conditional requirement."""
        if not requirement.condition:
            return True
        
        condition = requirement.condition
        
        if condition == "if_beneficial_owner_exists":
            return context.get("has_beneficial_owners", False)
        elif condition == "ownership_over_5_percent":
            return context.get("has_beneficial_owners", False)
        
        return True  # Default to required if condition unknown
    
    def _get_document_key(self, requirement: DocumentRequirement) -> str:
        """Generate unique key for document requirement."""
        if requirement.role_id:
            return f"{requirement.role_id}_{requirement.document_code}"
        else:
            return requirement.document_code
    
    def _validate_file_format(self, requirement: DocumentRequirement, file_info: Dict[str, Any]) -> List[str]:
        """Validate file format against accepted formats."""
        errors = []
        
        file_extension = file_info.get("type", "").lower().split(".")[-1]
        if file_extension not in requirement.accepted_formats:
            errors.append(f"{requirement.description}: Invalid file format. "
                         f"Accepted formats: {', '.join(requirement.accepted_formats)}")
        
        return errors
    
    def _validate_file_size(self, requirement: DocumentRequirement, file_info: Dict[str, Any]) -> List[str]:
        """Validate file size against maximum."""
        errors = []
        
        file_size_mb = file_info.get("size", 0) / (1024 * 1024)  # Convert bytes to MB
        if file_size_mb > requirement.max_size_mb:
            errors.append(f"{requirement.description}: File size ({file_size_mb:.1f}MB) "
                         f"exceeds maximum allowed size ({requirement.max_size_mb}MB)")
        
        return errors
    
    def get_document_codes_for_entity(self, entity_type: str) -> List[str]:
        """Get all document codes that apply to an entity type."""
        requirements = self.get_requirements_for_entity_type(entity_type)
        return list(set(req.document_code for req in requirements))
    
    def get_requirement_by_code(self, document_code: str, entity_type: str = None, 
                               role_id: str = None) -> Optional[DocumentRequirement]:
        """Get specific document requirement by code."""
        for req in self._requirements:
            if req.document_code == document_code:
                if entity_type and req.entity_type not in ["ALL", entity_type]:
                    continue
                if role_id and req.role_id != role_id:
                    continue
                return req
        return None


# Global instance
_doc_requirements_manager = DocumentRequirementsManager()


# ===== API FUNCTIONS =====

def get_document_requirements_manager() -> DocumentRequirementsManager:
    """Get the global document requirements manager."""
    return _doc_requirements_manager

def get_required_documents_for_entity(entity_type: str, roles: List[str] = None, 
                                     context: Dict[str, Any] = None) -> List[DocumentRequirement]:
    """Get required documents for an entity type and roles."""
    return _doc_requirements_manager.get_required_documents(entity_type, roles, context)

def get_document_upload_schema(entity_type: str, roles: List[str] = None) -> Dict[str, Any]:
    """Get document upload schema for UI generation."""
    return _doc_requirements_manager.get_document_upload_schema(entity_type, roles)

def validate_document_uploads(entity_type: str, roles: List[str], uploaded_docs: Dict[str, Any], 
                            context: Dict[str, Any] = None) -> tuple[bool, List[str]]:
    """Validate uploaded documents against requirements."""
    return _doc_requirements_manager.validate_uploaded_documents(entity_type, roles, uploaded_docs, context)

def get_document_requirement(document_code: str, entity_type: str = None, 
                           role_id: str = None) -> Optional[DocumentRequirement]:
    """Get specific document requirement."""
    return _doc_requirements_manager.get_requirement_by_code(document_code, entity_type, role_id)


if __name__ == "__main__":
    # Test the document requirements system
    print("=== Document Requirements Test ===")
    
    manager = get_document_requirements_manager()
    
    print("\nRequired documents for Company:")
    company_docs = get_required_documents_for_entity("COMPANY", ["AUTHORISED_REPRESENTATIVE", "DIRECTOR"])
    for doc in company_docs:
        print(f"  {doc.description} ({doc.document_code})")
        print(f"    Role: {doc.role_id or 'Entity'}, Required: {doc.required_rule}")
    
    print("\nDocument upload schema for Trust:")
    trust_schema = get_document_upload_schema("TRUST", ["AUTHORISED_REPRESENTATIVE", "TRUSTEE"])
    print(f"  Entity documents: {len(trust_schema['entity_documents'])}")
    print(f"  Role documents: {list(trust_schema['role_documents'].keys())}")
    
    print("\nDocument validation test:")
    uploaded_docs = {
        "CERTIFICATE_OF_INCORPORATION": {"type": "pdf", "size": 1024 * 1024},  # 1MB
        "MEMORANDUM_OF_INCORPORATION": {"type": "doc", "size": 2 * 1024 * 1024}  # 2MB
    }
    
    is_valid, errors = validate_document_uploads("COMPANY", ["DIRECTOR"], uploaded_docs)
    print(f"  Valid: {is_valid}")
    for error in errors:
        print(f"  Error: {error}")
