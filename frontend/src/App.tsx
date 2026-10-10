import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardPage } from './pages/DashboardPage';
import { NewScreeningPage } from './pages/NewScreeningPage';
import { ScreeningResultsPage } from './pages/ScreeningResultsPage';
import { CandidateDetailPage } from './pages/CandidateDetailPage';
import { ScreeningHistoryPage } from './pages/ScreeningHistoryPage';
import { CandidatesPage } from './pages/CandidatesPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="screenings/new" element={<NewScreeningPage />} />
          <Route path="screenings" element={<ScreeningHistoryPage />} />
          <Route path="screenings/:id" element={<ScreeningResultsPage />} />
          <Route path="screenings/:screeningId/candidates/:candidateId" element={<CandidateDetailPage />} />
          <Route path="candidates" element={<CandidatesPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
