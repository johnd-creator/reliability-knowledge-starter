"""Restore catalogs remain exact reviewed capabilities, version-gated and fail-closed."""
import unittest
from src.repositories import projection_coverage as coverage

class RestoreCatalogPinsTest(unittest.TestCase):
    def test_original_fresh_catalogs_keep_existing_acceptance(self):
        for module in (coverage,):
            self.assertTrue(module.reviewed_catalog(module.CATALOG_SIGNATURE))
            self.assertTrue(module.reviewed_catalog(module.SQL_CATALOG_SIGNATURE,'180006'))

    def test_only_exact_pg16_14_restored_catalog_is_accepted(self):
        for module in (coverage,):
            for signature in module.PG16_14_RESTORED_CATALOGS:
                for version in ('160014',160014):
                    self.assertTrue(module.reviewed_catalog(signature,version))

    def test_missing_wrong_or_unqualified_version_refuses_restore_catalog(self):
        for module in (coverage,):
            for signature in module.PG16_14_RESTORED_CATALOGS:
                for version in (None,'160013','160015','180006','16.14','160014 ','160014-unreviewed',True):
                    self.assertFalse(module.reviewed_catalog(signature,version))

    def test_unknown_and_modified_whole_catalogs_are_never_trusted(self):
        for module in (coverage,):
            reviewed=next(iter(module.PG16_14_RESTORED_CATALOGS))
            changed=('0' if reviewed[0]!='0' else '1')+reviewed[1:]
            for signature in ('',None,'a'*64,changed,reviewed+' ',module.CATALOG_SIGNATURE+' '):
                self.assertFalse(module.reviewed_catalog(signature,'160014'))

if __name__=='__main__':unittest.main()
