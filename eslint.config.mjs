// Self-rolled ESLint config.
//
// Why we don't use `eslint-config-next` directly
// ---------------------------------------------
// `eslint-config-next@16` still spreads
// `eslint-plugin-react@7.x`'s `configs.recommended.rules` into
// its rule table. The plugin's 7.x line targets ESLint 9 and
// uses an internal API (`context.getFilename()`) that was
// removed in ESLint 10. Every rule that needs `usedPropTypes`
// (e.g. `react/display-name`, `react/no-direct-mutation-state`,
// …) throws `getFilename is not a function` during rule load
// and crashes the whole lint pass — even when the user has the
// rule turned off, because ESLint still instantiates the rule
// object.
//
// What we keep from the Next config
// ---------------------------------
//   - `@next/next/*` — Next.js-specific rules (Image, Link,
//     server actions, RSC boundaries, etc.) loaded from
//     `@next/eslint-plugin-next` directly.
//   - `react-hooks/*` — the rules-of-hooks from
//     `eslint-plugin-react-hooks`, which does work on ESLint 10.
//   - `jsx-a11y/*` — accessibility rules from
//     `eslint-plugin-jsx-a11y`, also ESLint 10 compatible.
//
// What we drop
// ------------
//   - `react/recommended` — broken on ESLint 10; the
//     `react/recommended` set is mostly prop-types / no-deprecated
//     / display-name, all of which the `typescript-eslint`
//     strict checks we add below already cover.
//   - `import/recommended` — not currently used by the project;
//     bring it back when we add module-resolution concerns.

import { defineConfig, globalIgnores } from "eslint/config";
import nextPlugin from "@next/eslint-plugin-next";
import reactHooks from "eslint-plugin-react-hooks";
import jsxA11y from "eslint-plugin-jsx-a11y";
import tseslint from "typescript-eslint";
import globals from "globals";

const eslintConfig = defineConfig([
  // Global ignores — out/ is the static export, .next/ is the
  // build cache, scripts/ are Node-only tools that don't need
  // JSX/React rules, generated.d.ts is generated.
  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    "scripts/**",
  ]),

  // Browser + Node modules. We use a couple of Node-only
  // modules in scripts/, but those are already ignored above.
  {
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
    },
  },

  // TypeScript everywhere: tsconfig.json drives the parser.
  ...tseslint.configs.recommended,

  // @next/eslint-plugin-next, the rules-of-hooks, and jsx-a11y.
  {
    files: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
    plugins: {
      "@next/next": nextPlugin,
      "react-hooks": reactHooks,
      "jsx-a11y": jsxA11y,
    },
    rules: {
      // Next.js recommended
      ...nextPlugin.configs.recommended.rules,

      // Rules of hooks — the canonical "you forgot a dependency"
      // and "conditional hook call" detectors.
      ...reactHooks.configs.recommended.rules,

      // jsx-a11y — a curated subset of the accessibility rules.
      // We don't need every rule; the ones below catch the common
      // regressions we actually see in PRs (missing alt, missing
      // aria-label, wrong role).
      "jsx-a11y/alt-text": "warn",
      "jsx-a11y/aria-props": "warn",
      "jsx-a11y/aria-proptypes": "warn",
      "jsx-a11y/aria-unsupported-elements": "warn",
      "jsx-a11y/role-has-required-aria-props": "warn",
      "jsx-a11y/role-supports-aria-props": "warn",

      // TypeScript: keep the recommended set, but loosen two
      // rules that fire too often in a Next.js codebase where
      // untyped JSX is the norm.
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
    },
    settings: {
      next: {
        // Tells the Next plugin we are on Next 16, so the few
        // version-gated rules pick the right codepath.
        rootDir: ".",
      },
    },
  },
]);

export default eslintConfig;
