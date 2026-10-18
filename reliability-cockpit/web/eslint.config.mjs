import tseslint from "typescript-eslint";
import hooks from "eslint-plugin-react-hooks";
import a11y from "eslint-plugin-jsx-a11y";

// NADI presentation coverage, including legacy pages and Indonesian glossary.
export default tseslint.config({
  files: ["middleware.ts", "lib/local-session.ts", "lib/factual-gateway.ts", "lib/factual-policy.ts", "components/**/*.tsx", "app/**/*.tsx", "app/api/**/*.ts", "lib/api.ts", "lib/navigation.ts", "lib/overview.ts", "lib/glossary.ts", "lib/id-copy.ts", "lib/product-records.ts", "lib/pdm-input.ts", "lib/pdm-workbook.ts", "lib/case-records.ts", "lib/case-form.ts", "lib/login-navigation.ts", "lib/development-status-view.ts", "lib/advisory-records.ts", "lib/development-provenance.ts"],
  extends: [...tseslint.configs.recommended],
  plugins: { "react-hooks": hooks, "jsx-a11y": a11y },
  rules: { ...hooks.configs.recommended.rules, ...a11y.configs.recommended.rules, "jsx-a11y/no-noninteractive-tabindex": ["error", { roles: ["region"] }] },
});
