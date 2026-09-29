import { Routes, Route } from "react-router-dom";
import CreateSessionPage from "./pages/CreateSessionPage.jsx";
import SessionPage from "./pages/SessionPage.jsx";

export default function App() {
  return (
    <div className="container">
      <Routes>
        <Route path="/" element={<CreateSessionPage />} />
        <Route path="/s/:slug" element={<SessionPage />} />
      </Routes>
    </div>
  );
}
