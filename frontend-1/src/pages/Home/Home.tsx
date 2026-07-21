import { Link } from 'react-router-dom';
import { UserPlus, ClipboardList, BarChart3, Leaf, Users, Shield, FileText, Map, Building2 } from 'lucide-react';
import { useCounter } from '../../hooks/useCounter';

export default function Home() {
  const blocksCounter = useCounter({ target: 3 });
  const questionsCounter = useCounter({ target: 20 });
  const levelsCounter = useCounter({ target: 4 });

  return (
    <div className="home">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-inner">
          <Link to="/" className="logo">ESG<span>Campus</span></Link>
          <div className="nav-links">
            <Link to="/login" className="btn btn-outline">Войти</Link>
            <Link to="/register" className="btn btn-primary">Зарегистрироваться</Link>
          </div>
        </div>
      </nav>
