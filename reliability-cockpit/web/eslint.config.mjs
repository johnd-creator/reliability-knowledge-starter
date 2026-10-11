import tseslint from "typescript-eslint";
import hooks from "eslint-plugin-react-hooks";
import a11y from "eslint-plugin-jsx-a11y";

// Bundle A's presentation surfaces. Existing Engineering checks retain their own scope.
export default tseslint.config({
  files: ["components/ui.tsx", "components/AppNavigation.tsx", "components/ExecutiveOverview.tsx", "lib/navigation.ts", "lib/overview.ts", "app/page.tsx", "app/work-orders/page.tsx", "app/equipment/*/page.tsx", "components/AssetHealthSummary.tsx", "app/assets/page.tsx", "app/assets/*/page.tsx", "app/asset-health/page.tsx", "components/useQaRecords.ts", "components/QaProductBoundary.tsx", "components/QaRecordReader.tsx", "components/InspectionDetail.tsx", "components/PdmCenter.tsx", "lib/product-records.ts", "app/pdm/page.tsx", "components/RecommendationDetail.tsx", "components/RecommendationWorkspace.tsx", "components/LocalLogin.tsx", "components/LoginPage.tsx", "app/login/page.tsx", "app/recommendations/page.tsx", "app/action-board/page.tsx"],
  extends: [...tseslint.configs.recommended],
  plugins: { "react-hooks": hooks, "jsx-a11y": a11y },
  rules: { ...hooks.configs.recommended.rules, ...a11y.configs.recommended.rules, "jsx-a11y/no-noninteractive-tabindex": ["error", { roles: ["region"] }] },
});
