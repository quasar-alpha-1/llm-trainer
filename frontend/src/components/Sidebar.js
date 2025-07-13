import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-title">LLM Trainer</div>
      <ul>
        <li><NavLink to="/" end>Dashboard</NavLink></li>
        <li><NavLink to="/new-job">New Training Job</NavLink></li>
        <li><NavLink to="/jobs">Jobs</NavLink></li>
        <li><NavLink to="/local-models">Local Models</NavLink></li>
        <li><NavLink to="/settings">Settings</NavLink></li>
      </ul>
    </nav>
  );
}

export default Sidebar;