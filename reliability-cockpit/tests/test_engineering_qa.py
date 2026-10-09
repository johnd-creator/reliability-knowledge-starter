from test_bundle_c_integration import BundleCPostgresIntegrationTest
from src.api.engineering_qa import create_qa_app
from fastapi.testclient import TestClient
class QaFactoryTest(BundleCPostgresIntegrationTest):
 def setUp(self):
  super().setUp()
  app=create_qa_app(authority=self.authority,cases=self.cases,inspections=self.inspections,recommendations=self.recommendations,context=self.context,environment='development')
  self.client.close();self.client=TestClient(app,base_url='https://nadi.example.invalid')
