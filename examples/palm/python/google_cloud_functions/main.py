import functions_framework
import google.ai.generativelanguage as glm
import google.generativeai as palm
from google.oauth2 import credentials
import json
import requests

SCOPES = [
  'https://www.googleapis.com/auth/cloud-platform',
  'https://www.googleapis.com/auth/generative-language.tuning',
]

def get_credentials():
  """Generate scoped OAuth2 credentials."""
  token_full_url = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token?scopes=' + ','.join(SCOPES)
  token_response = requests.get(token_full_url, headers={'Metadata-Flavor': 'Google'})
  if token_response.status_code != 200:
    raise ValueError(f'Cant auth - {token_response.status_code}: {token_response.text}')

  token = json.loads(token_response.text)
  return credentials.Credentials(token=token['access_token'])


@functions_framework.http
def load_model(request):
  """Load a PaLM model using a service account."""

  # Build a google.auth.credentials.Credentials object from the running service account's
  # authorisation, with the desired scopes defined above.
  o2_creds = get_credentials()
  # Each PaLM API uses a different client, e.g. ModelServiceClient, TextServiceClient, etc.
  # You will need to build the respective client for the API you are using.
  model_client = glm.ModelServiceClient(credentials=o2_creds)

  # Test tuning by passing name=tunedModels/your-model-id. You must ensure that the model is shared
  # with the running service account, or you will see a permission denied error (in the logs).
  model_name = request.args.get('name', 'models/text-bison-001')
  model = palm.get_model(model_name, client=model_client)
  return f'<pre>{model}</pre>'
