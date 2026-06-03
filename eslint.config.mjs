import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // The audit script is a Node-only tool, not a Next.js module —
    // keeping it out of the lint scope avoids `require`-style-import
    // false positives and other framework-specific rules.
    "scripts/**",
  ]),
]);

export default eslintConfig;
