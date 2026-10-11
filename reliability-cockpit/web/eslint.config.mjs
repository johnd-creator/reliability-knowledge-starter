import tseslint from "typescript-eslint";
import hooks from "eslint-plugin-react-hooks";
import a11y from "eslint-plugin-jsx-a11y";

// NADI presentation coverage, including legacy pages and Indonesian glossary.
export default tseslint.config({
  files: ["components/**/*.tsx", "app/**/*.tsx", "lib/navigation.ts", "lib/overview.ts", "lib/glossary.ts", "lib/id-copy.ts", "lib/product-records.ts", "lib/case-records.ts", "lib/advisory-records.ts", "lib/development-provenance.ts"],
  extends: [...tseslint.configs.recommended],
  plugins: { "react-hooks": hooks, "jsx-a11y": a11y },
  rules: { ...hooks.configs.recommended.rules, ...a11y.configs.recommended.rules, "jsx-a11y/no-noninteractive-tabindex": ["error", { roles: ["region"] }] },
});
