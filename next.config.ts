import type { NextConfig } from 'next';
import { withSentryConfig } from '@sentry/nextjs';

// `GITHUB_REPOSITORY` is the GitHub Actions env var of the form
// "owner/repo". On CI we want the site to live at "/<repo>/" so
// the deploy workflow can publish it under
// https://<owner>.github.io/<repo>/. Locally (or in any other
// environment without that var) we drop the prefix so the dev
// server and the static `out/` build can be served from the
// filesystem root — no manual path rewriting required.
const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? '';
const basePath = repoName ? `/${repoName}` : '';

const nextConfig: NextConfig = {
  output: 'export',
  basePath,
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};

const sentryOptions: Parameters<typeof withSentryConfig>[1] = {
  // For all available options, see:
  // https://github.com/getsentry/sentry-webpack-plugin#options

  // Suppresses source map uploading logs during build
  silent: !process.env.CI,

  // Webpack-level Sentry options (the top-level ones are deprecated).
  webpack: {
    // Disable automatic instrumentation of Next.js features
    // to reduce bundle size
    autoInstrumentServerFunctions: false,
    autoInstrumentMiddleware: false,

    // Tree-shake Sentry logger statements to reduce bundle size
    treeshake: {
      removeDebugLogging: true,
    },

    // Enables automatic instrumentation of Vercel Cron Monitors.
    // See: https://docs.sentry.io/platforms/javascript/guides/nextjs/cron-jobs/
    automaticVercelMonitors: false,
  },

  // Disable source map upload (not needed for static export)
  sourcemaps: {
    disable: true,
  },

  // Disable telemetry data collection
  telemetry: false,
};

// Only set org/project when defined — exactOptionalPropertyTypes
// disallows passing `undefined` to a property typed as `string`.
if (process.env.SENTRY_ORG) sentryOptions.org = process.env.SENTRY_ORG;
if (process.env.SENTRY_PROJECT) sentryOptions.project = process.env.SENTRY_PROJECT;

export default withSentryConfig(nextConfig, sentryOptions);
