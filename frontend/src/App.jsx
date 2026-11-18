import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RegisterDevice from './pages/RegisterDevice';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  return (
    <Router>
      <div>
        <header style={{ padding: '20px', textAlign: 'center', backgroundColor: '#f0f0f0', marginBottom: '30px', display: 'flex', justifyContent: 'space-between' }}>
          <h1 style={{ margin: 0 }}>CampusSentinel</h1>
          <nav style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <Link to="/">Register</Link>
            <Link to="/admin">Admin</Link>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<RegisterDevice />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
