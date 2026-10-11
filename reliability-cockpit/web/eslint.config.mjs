import tseslint from "typescript-eslint";
import hooks from "eslint-plugin-react-hooks";
import a11y from "eslint-plugin-jsx-a11y";

// NADI presentation coverage, including legacy pages and Indonesian glossary.
export default tseslint.config({
  files: ["components/**/*.tsx", "app/**/*.tsx", "components/Glossary.tsx", "lib/glossary.ts", "lib/id-copy.ts", "app/panduan/istilah/page.tsx", "components/ui.tsx", "components/AppNavigation.tsx", "components/ExecutiveOverview.tsx", "lib/navigation.ts", "lib/overview.ts", "app/page.tsx", "app/work-orders/page.tsx", "app/equipment/*/page.tsx", "components/AssetHealthSummary.tsx", "app/assets/page.tsx", "app/assets/*/page.tsx", "app/asset-health/page.tsx", "components/useQaRecords.ts", "components/QaProductBoundary.tsx", "components/QaRecordReader.tsx", "components/InspectionDetail.tsx", "components/PdmCenter.tsx", "lib/product-records.ts", "app/pdm/page.tsx", "components/RecommendationDetail.tsx", "components/RecommendationWorkspace.tsx", "components/LocalLogin.tsx", "components/LoginPage.tsx", "app/login/page.tsx", "app/recommendations/page.tsx", "app/action-board/page.tsx", "components/RecommendationActions.tsx", "components/CaseForm.tsx", "components/CaseWorkspace.tsx", "components/AdvisoryWorkspace.tsx", "components/useQaCommand.ts", "lib/case-records.ts", "lib/advisory-records.ts", "app/engineering/cases/page.tsx", "app/engineering/advisories/page.tsx", "app/engineering/inbox/page.tsx"],
  extends: [...tseslint.configs.recommended],
  plugins: { "react-hooks": hooks, "jsx-a11y": a11y },
  rules: { ...hooks.configs.recommended.rules, ...a11y.configs.recommended.rules, "jsx-a11y/no-noninteractive-tabindex": ["error", { roles: ["region"] }] },
});
