import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="bg-light min-vh-100">
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div className="container">
          <Link className="navbar-brand" to="/">
            Календарь звонков
          </Link>
          <div className="navbar-nav">
            <NavLink className="nav-link" to="/" end>
              Виды брони
            </NavLink>
            <NavLink className="nav-link" to="/admin/event-types">
              Типы событий
            </NavLink>
            <NavLink className="nav-link" to="/admin/bookings">
              Предстоящие встречи
            </NavLink>
          </div>
        </div>
      </nav>
      <main className="container pb-4">{children}</main>
    </div>
  );
}
