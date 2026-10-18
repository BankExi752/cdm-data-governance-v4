import { Route, Routes } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import OverviewPage from '@/pages/OverviewPage/OverviewPage';
import ManagePage from '@/pages/ManagePage/ManagePage';
import GovernPage from '@/pages/GovernPage/GovernPage';
import UsePage from '@/pages/UsePage/UsePage';
import ReportPage from '@/pages/ReportPage/ReportPage';
import NotFoundPage from '@/pages/NotFoundPage/NotFoundPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<OverviewPage />} />
        <Route path="manage" element={<ManagePage />} />
        <Route path="govern" element={<GovernPage />} />
        <Route path="use" element={<UsePage />} />
        <Route path="report" element={<ReportPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
