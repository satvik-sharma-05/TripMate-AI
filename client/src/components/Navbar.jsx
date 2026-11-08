// Top navigation. NavLink adds the "active" class to the link of the current page.
import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="container">
        <Link to="/" className="brand">
          <span className="brand-mark">TM</span> TripMate AI
        </Link>
        <nav className="nav-links">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/about">About</NavLink>
          <Link to="/plan" className="btn btn-primary btn-sm">Plan a trip</Link>
        </nav>
      </div>
    </header>
  );
}
