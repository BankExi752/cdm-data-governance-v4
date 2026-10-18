import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { ErrorFallback } from '@/components/ErrorFallback';
import { Toaster } from '@/components/ui/sonner';
import LabProvider from '@/store/LabProvider';
import App from './app';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={import.meta.env.MIAODA_CLIENT_BASE_PATH || '/'}>
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <LabProvider>
          <App />
          <Toaster position="top-center" richColors />
        </LabProvider>
      </ErrorBoundary>
    </BrowserRouter>
  </StrictMode>,
);
