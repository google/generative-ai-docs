"""Sample functions illustrating how to share models using the permission service."""
import google.generativeai as palm
import google.ai.generativelanguage as glm
from google.ai.generativelanguage_v1beta3 import types

client_config = {
    # Add any client config here, e.g. credentials=... for service accounts.
}
perm_client = glm.PermissionServiceClient(**client_config)

# Listing existing permissions on a tuned model.
model_name = 'tunedModels/...'
list_response = perm_client.list_permissions(parent=model_name)
print(list_response)

# Sharing a model with another user (e.g. service account), or "adding a permission"
new_user = "my-service@my-project.iam.gserviceaccount.com"
perm = types.Permission(
    grantee_type=types.Permission.GranteeType.USER,
    role=types.Permission.Role.READER,
    email_address=new_user,
)

model_name = 'tunedModels/...'
new_perm_response = perm_client.create_permission(permission=perm, parent=model_name)
print(new_perm_response)
