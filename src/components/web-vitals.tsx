'use client';

import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Log metrics in development
    if (process.env.NODE_ENV === 'development') {
      console.log(metric);
    }

    // Send to analytics in production
    if (process.env.NODE_ENV === 'production') {
      // You can send to your analytics service here
      // Example: sendToAnalytics(metric);

      // For now, just log important metrics
      if (metric.name === 'LCP' && metric.value > 2500) {
        console.warn(`LCP is slow: ${metric.value}ms`);
      }
      if (metric.name === 'INP' && metric.value > 200) {
        console.warn(`INP is slow: ${metric.value}ms`);
      }
      if (metric.name === 'CLS' && metric.value > 0.1) {
        console.warn(`CLS is high: ${metric.value}`);
      }
    }
  });

  return null;
}
