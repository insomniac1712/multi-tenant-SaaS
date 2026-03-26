from .models import Membership

def get_membership(user, org_id):
    return Membership.objects.filter(user=user, organization_id=org_id, is_active=True).first()

def is_org_member(user, org_id):
    return get_membership(user, org_id) is not None

def is_org_admin_or_owner(user, org_id):
    membership = get_membership(user, org_id)
    return membership is not None and membership.role in [Membership.Role.ADMIN, Membership.Role.OWNER]

def is_org_owner(user, org_id):
    membership = get_membership(user, org_id)
    return membership is not None and membership.role == Membership.Role.OWNER