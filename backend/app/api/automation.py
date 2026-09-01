from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, RoleEnum
from app.models.automation import AutomationRule
from app.schemas.automation import AutomationRuleCreate, AutomationRuleResponse, AutomationRuleUpdate
from app.services.audit_service import AuditService

router = APIRouter(prefix="/automation", tags=["Automation"])

@router.get("/rules", response_model=List[AutomationRuleResponse])
def get_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all configured automation rules"""
    return db.query(AutomationRule).order_by(AutomationRule.priority.desc()).all()

@router.post("/rules", response_model=AutomationRuleResponse)
def create_rule(
    rule_data: AutomationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Create a new automation rule"""
    rule = AutomationRule(
        name=rule_data.name,
        description=rule_data.description,
        conditions=rule_data.conditions,
        actions=rule_data.actions,
        enabled=rule_data.enabled,
        priority=rule_data.priority
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="AUTOMATION_RULE_CREATED",
        resource="automation_rule",
        resource_id=str(rule.id),
        result="Success"
    )
    return rule

@router.patch("/rules/{rule_id}", response_model=AutomationRuleResponse)
def update_rule(
    rule_id: int,
    rule_update: AutomationRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Update an automation rule"""
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    for key, val in rule_update.model_dump(exclude_unset=True).items():
        setattr(rule, key, val)
        
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN]))
):
    """Delete an automation rule"""
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"status": "deleted"}
