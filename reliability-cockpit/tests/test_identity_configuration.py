import unittest
from dataclasses import replace
from src.services.identity_configuration import OidcTrustConfiguration, SessionRuntimePolicy


class IdentityConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.config = OidcTrustConfiguration(
            "https://identity.example.invalid/tenant", "qa-client",
            "https://nadi-qa.example.invalid/auth/callback",
            "https://nadi-qa.example.invalid/auth/logout",
            "https://nadi-qa.example.invalid", ("RS256",), 5)

    def test_namespaced_stable_subject_not_email_authority(self):
        ref = self.config.subject_ref(self.config.issuer, "immutable-subject")
        self.assertEqual(ref, self.config.subject_ref(self.config.issuer, "immutable-subject"))
        self.assertNotEqual(ref, self.config.subject_ref(self.config.issuer, "different"))
        self.assertLessEqual(len(ref), 160)
        other = replace(self.config, issuer="https://identity.example.invalid/other")
        self.assertNotEqual(ref, other.subject_ref(other.issuer, "immutable-subject"))

    def test_forged_issuer_empty_control_subject_denied(self):
        for issuer, subject in [("https://forged.invalid", "x"),
                                (self.config.issuer, ""), (self.config.issuer, " x"),
                                (self.config.issuer, "x\n"), (self.config.issuer, "x"*256)]:
            with self.assertRaises(ValueError):
                self.config.subject_ref(issuer, subject)

    def test_trust_settings_fail_closed(self):
        for change in [{"issuer": "http://identity.invalid"}, {"issuer": "https://user:secret@identity.invalid"},
                       {"redirect_uri": "https://other.invalid/callback"},
                       {"logout_uri": "https://nadi-qa.example.invalid/#fragment"},
                       {"browser_origin": "https://*.invalid"}, {"client_id": ""},
                       {"algorithms": ("none",)}, {"algorithms": ("HS256",)},
                       {"algorithms": ()}, {"provider_timeout_seconds": True},
                       {"provider_timeout_seconds": 0}, {"provider_timeout_seconds": 31}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                replace(self.config, **change)

    def test_explicit_bounded_session_policy(self):
        policy = SessionRuntimePolicy(300, 3600, 4, 5, 8)
        self.assertEqual(policy.engine_options()["max_overflow"], 0)
        for changes in [{"idle_seconds": 0}, {"absolute_seconds": 1}, {"pool_size": 65},
                        {"pool_timeout_seconds": 0}, {"lease_capacity": True}]:
            with self.assertRaises(ValueError):
                replace(policy, **changes)
