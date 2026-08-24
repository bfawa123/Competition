import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import InfoPage from "./pages/InfoPage";

const RecommendPage = lazy(() => import("./pages/RecommendPage"));
const ResultPage = lazy(() => import("./pages/ResultPage"));
const RoutePage = lazy(() => import("./pages/RoutePage"));
const MemoriesPage = lazy(() => import("./pages/MemoriesPage"));
const BooksPage = lazy(() => import("./pages/BooksPage"));
const TracePage = lazy(() => import("./pages/TracePage"));
const UsersPage = lazy(() => import("./pages/UsersPage"));

export default function App() {
  return <Layout><Suspense fallback={<div className="page-loading" aria-label="正在加载页面"><i /><i /><i /></div>}><Routes>
    <Route path="/recommend" element={<RecommendPage />} />
    <Route path="/result/:runId" element={<ResultPage />} />
    <Route path="/route" element={<RoutePage />} />
    <Route path="/result" element={<Navigate to="/result/latest" replace />} />
    <Route path="/memories" element={<MemoriesPage />} />
    <Route path="/books" element={<BooksPage />} />
    <Route path="/trace" element={<TracePage />} />
    <Route path="/users" element={<UsersPage />} />
    <Route path="/about" element={<InfoPage kind="about" />} />
    <Route path="/features" element={<InfoPage kind="features" />} />
    <Route path="/help" element={<InfoPage kind="help" />} />
    <Route path="/privacy" element={<InfoPage kind="privacy" />} />
    <Route path="/terms" element={<InfoPage kind="terms" />} />
    <Route path="*" element={<Navigate to="/recommend" replace />} />
  </Routes></Suspense></Layout>;
}
