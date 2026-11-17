import { useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function App() {
  const [apiState, setApiState] = useState('checking');
  const [accessToken, setAccessToken] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [loginError, setLoginError] = useState('');
  const [loggingIn, setLoggingIn] = useState(false);
  const [vehicles, setVehicles] = useState([]);
  const [vehiclesError, setVehiclesError] = useState('');
  const [drivers, setDrivers] = useState([]);
  const [driversError, setDriversError] = useState('');
  const [driverSearch, setDriverSearch] = useState('');
  const [driverStatusFilter, setDriverStatusFilter] = useState('all');
  const [showDriverForm, setShowDriverForm] = useState(false);
  const [savingDriver, setSavingDriver] = useState(false);
  const [driverFormError, setDriverFormError] = useState('');
  const [activePage, setActivePage] = useState('dashboard');
  const [vehicleSearch, setVehicleSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [formError, setFormError] = useState('');
  const [showVehicleForm, setShowVehicleForm] = useState(false);
  const [savingVehicle, setSavingVehicle] = useState(false);
  const vehicleStatuses = ['available', 'assigned', 'maintenance', 'inactive'];
  const vehicleCounts = Object.fromEntries(vehicleStatuses.map((status) => [
    status,
    vehicles.filter((vehicle) => vehicle.current_status === status).length,
  ]));
  const filteredVehicles = vehicles.filter((vehicle) => {
    const query = vehicleSearch.trim().toLowerCase();
    const matchesSearch = !query || [vehicle.vehicle_id, vehicle.registration_no, vehicle.vehicle_type, vehicle.fuel_type]
      .some((value) => String(value).toLowerCase().includes(query));
    return matchesSearch && (statusFilter === 'all' || vehicle.current_status === statusFilter);
  });
  const filteredDrivers = drivers.filter((driver) => {
    const query = driverSearch.trim().toLowerCase();
    const matchesSearch = !query || [driver.full_name, driver.email, driver.phone, driver.license_number]
      .some((value) => String(value || '').toLowerCase().includes(query));
    return matchesSearch && (driverStatusFilter === 'all' || driver.current_status === driverStatusFilter);
  });

  async function loadVehicles() {
    try {
      const response = await fetch(`${API_URL}/api/vehicles`);
      if (!response.ok) throw new Error('Could not load vehicles.');
      setVehicles(await response.json());
      setVehiclesError('');
    } catch {
      setVehiclesError('Could not load vehicles. Check that the backend is running.');
    }
  }

  async function loadDrivers(token = accessToken) {
    if (!token) return;
    try {
      const response = await fetch(`${API_URL}/api/drivers`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Could not load drivers.');
      setDrivers(await response.json());
      setDriversError('');
    } catch {
      setDriversError('Could not load drivers. Check that the backend is running.');
    }
  }

  async function handleLogin(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());
    setLoggingIn(true);
    setLoginError('');
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || 'Sign in failed.');
      const profileResponse = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${result.access_token}` },
      });
      if (!profileResponse.ok) throw new Error('Could not load your user profile.');
      setCurrentUser(await profileResponse.json());
      setAccessToken(result.access_token);
      await loadVehicles();
      await loadDrivers(result.access_token);
      form.reset();
    } catch (error) {
      setLoginError(error.message || 'Could not sign in.');
    } finally {
      setLoggingIn(false);
    }
  }

  useEffect(() => {
    let active = true;
    fetch(`${API_URL}/api/health`)
      .then((response) => {
        if (!response.ok) throw new Error('API returned an error');
        return response.json();
      })
      .then((data) => active && setApiState(data.status === 'ok' ? 'online' : 'unavailable'))
      .catch(() => active && setApiState('unavailable'));
    loadVehicles();
    return () => { active = false; };
  }, []);

  async function handleVehicleSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    setSavingVehicle(true);
    setFormError('');
    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData.entries());
    payload.capacity_kg = Number(payload.capacity_kg);
    try {
      const response = await fetch(`${API_URL}/api/vehicles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(typeof result.detail === 'string' ? result.detail : 'Please check the vehicle details.');
      }
      form.reset();
      setShowVehicleForm(false);
      await loadVehicles();
    } catch (error) {
      setFormError(error.message || 'Could not save the vehicle.');
    } finally {
      setSavingVehicle(false);
    }
  }

  async function handleDriverSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    setSavingDriver(true);
    setDriverFormError('');
    const payload = Object.fromEntries(new FormData(form).entries());
    payload.email = payload.email.trim() || null;
    try {
      const response = await fetch(`${API_URL}/api/drivers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Please check the driver details.');
      form.reset();
      setShowDriverForm(false);
      await loadDrivers(accessToken);
    } catch (error) {
      setDriverFormError(error.message || 'Could not save the driver.');
    } finally {
      setSavingDriver(false);
    }
  }

  if (!accessToken) {
    return (
      <main className="login-shell">
        <form className="login-card" onSubmit={handleLogin}>
          <div className="brand login-brand"><span className="brand-mark">F</span><span>FleetFlow</span></div>
          <p className="eyebrow">FLEET OPERATIONS</p>
          <h1>Sign in</h1>
          <p className="login-intro">Use your FleetFlow account to continue.</p>
          <label>Email<input name="email" type="email" autoComplete="username" required /></label>
          <label>Password<input name="password" type="password" autoComplete="current-password" required /></label>
          {loginError && <p className="form-error" role="alert">{loginError}</p>}
          <button className="primary-button" type="submit" disabled={loggingIn}>{loggingIn ? 'Signing in…' : 'Sign in'}</button>
          <p className="login-help">Create the first Administrator account from the backend terminal.</p>
        </form>
      </main>
    );
  }

  const vehicleRegistrationForm = showVehicleForm && <form className="vehicle-form" onSubmit={handleVehicleSubmit}>
    <label>Registration number<input name="registration_no" required maxLength="20" placeholder="e.g. KA01AB1234" /></label>
    <label>Vehicle type<input name="vehicle_type" required maxLength="50" placeholder="e.g. Truck" /></label>
    <label>Capacity (kg)<input name="capacity_kg" required type="number" min="0.01" step="0.01" placeholder="e.g. 5000" /></label>
    <label>Fuel type<input name="fuel_type" required maxLength="30" placeholder="e.g. Diesel" /></label>
    <label>Status<select name="current_status" defaultValue="available"><option value="available">Available</option><option value="assigned">Assigned</option><option value="maintenance">Maintenance</option><option value="inactive">Inactive</option></select></label>
    {formError && <p className="form-error" role="alert">{formError}</p>}
    <button className="primary-button" type="submit" disabled={savingVehicle}>{savingVehicle ? 'Saving…' : 'Save vehicle'}</button>
  </form>;

  const driverRegistrationForm = showDriverForm && <form className="vehicle-form driver-form" onSubmit={handleDriverSubmit}>
    <label>Full name<input name="full_name" required maxLength="100" placeholder="e.g. Ananya Rao" /></label>
    <label>Email (optional)<input name="email" type="email" maxLength="254" placeholder="e.g. driver@example.com" /></label>
    <label>Phone number<input name="phone" type="tel" required minLength="7" maxLength="20" placeholder="e.g. +91 98765 43210" /></label>
    <label>License number<input name="license_number" required maxLength="40" placeholder="Driver license number" /></label>
    <label>License expiry<input name="license_expiry" type="date" required /></label>
    <label>Status<select name="current_status" defaultValue="active"><option value="active">Active</option><option value="inactive">Inactive</option></select></label>
    {driverFormError && <p className="form-error" role="alert">{driverFormError}</p>}
    <button className="primary-button" type="submit" disabled={savingDriver}>{savingDriver ? 'Saving…' : 'Save driver'}</button>
  </form>;

  const statusBar = <>
    <div className="status-bar" role="img" aria-label={vehicleStatuses.map((status) => `${status}: ${vehicleCounts[status]}`).join(', ')}>
      {vehicleStatuses.map((status) => vehicleCounts[status] > 0 && <span key={status} className={`status-segment ${status}`} style={{ width: `${(vehicleCounts[status] / vehicles.length) * 100}%` }} />)}
    </div>
    <div className="status-legend">
      {vehicleStatuses.map((status) => <div className="status-legend-item" key={status}><span className={`legend-dot ${status}`} /><span>{status}</span><strong>{vehicleCounts[status]}</strong></div>)}
    </div>
  </>;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">F</span><span>FleetFlow</span></div>
        <p className="nav-label">WORKSPACE</p>
        <nav aria-label="Main navigation">
          <button className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`} onClick={() => setActivePage('dashboard')}>▦ <span>Dashboard</span></button>
          <button className={`nav-item ${activePage === 'vehicles' ? 'active' : ''}`} onClick={() => setActivePage('vehicles')}>▣ <span>Fleet Management</span></button>
          <button className={`nav-item ${activePage === 'drivers' ? 'active' : ''}`} onClick={() => setActivePage('drivers')}>♙ <span>Drivers</span></button>
          <a className="nav-item disabled" href="#trips" aria-disabled="true">⇄ <span>Trips & Shipments</span></a>
          <a className="nav-item disabled" href="#maintenance" aria-disabled="true">⚙ <span>Maintenance</span></a>
          <a className="nav-item disabled" href="#reports" aria-disabled="true">▤ <span>Reports</span></a>
        </nav>
        <div className="sidebar-foot">Milestone 1 · Setup</div>
      </aside>

      <main className="main-content" id={activePage}>
        <header className="topbar">
          <div><p className="eyebrow">FLEET OPERATIONS</p><h1>{activePage === 'dashboard' ? 'Dashboard' : activePage === 'vehicles' ? 'Fleet Management' : 'Driver Management'}</h1></div>
          <div className="user-chip"><span className="avatar">{currentUser?.full_name?.slice(0, 1) || 'F'}</span><span>{currentUser?.full_name || 'FleetFlow user'}</span><button className="text-button" onClick={() => { setAccessToken(''); setCurrentUser(null); }}>Sign out</button></div>
        </header>

        {activePage === 'dashboard' && <><section className="welcome-row">
          <div><h2>Operations overview</h2><p>Your FleetFlow workspace is ready for the next implementation steps.</p></div>
          <span className={`api-badge ${apiState}`}><span className="status-dot" />API {apiState}</span>
        </section>

        <section className="metric-grid" aria-label="Fleet metrics">
          <article className="metric-card"><span className="metric-icon blue">▣</span><p>Total vehicles</p><strong>{vehicles.length}</strong><small>Registered fleet vehicles</small></article>
          <article className="metric-card"><span className="metric-icon green">✓</span><p>Available</p><strong>{vehicleCounts.available}</strong><small>Ready for assignment</small></article>
          <article className="metric-card"><span className="metric-icon blue">↗</span><p>Assigned</p><strong>{vehicleCounts.assigned}</strong><small>Currently assigned</small></article>
          <article className="metric-card"><span className="metric-icon amber">⚙</span><p>Maintenance</p><strong>{vehicleCounts.maintenance}</strong><small>Under maintenance</small></article>
          <article className="metric-card"><span className="metric-icon violet">—</span><p>Inactive</p><strong>{vehicleCounts.inactive}</strong><small>Not in service</small></article>
        </section>

        <section className="content-grid">
          <article className="panel fleet-panel"><div className="panel-heading"><div><h2>Vehicle status</h2><p>Current availability across {vehicles.length} registered vehicles</p></div><button className="secondary-button" onClick={() => setActivePage('vehicles')}>View fleet</button></div>{statusBar}</article>
          <article className="panel activity-panel">
            <div className="panel-heading"><div><h2>Recent activity</h2><p>Latest changes across operations</p></div></div>
            <div className="activity-empty"><span className="activity-line" /><div><strong>Activity feed is ready</strong><p>Trip and shipment updates will be listed here.</p></div></div>
          </article>
        </section>
        </>}

        {activePage === 'vehicles' && <section className="panel management-panel">
          <div className="panel-heading management-heading"><div><h2>Fleet assets</h2><p>Search and filter the vehicles saved in PostgreSQL.</p></div><button className="primary-button" onClick={() => { setShowVehicleForm(!showVehicleForm); setFormError(''); }}>{showVehicleForm ? 'Cancel' : 'Register vehicle'}</button></div>
          {vehicleRegistrationForm}
          <div className="fleet-controls">
            <label className="search-field"><span aria-hidden="true">⌕</span><input value={vehicleSearch} onChange={(event) => setVehicleSearch(event.target.value)} placeholder="Search by ID, registration, type or fuel" aria-label="Search vehicles" /></label>
            <label className="filter-field">Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">All statuses</option>{vehicleStatuses.map((status) => <option key={status} value={status}>{status[0].toUpperCase() + status.slice(1)}</option>)}</select></label>
          </div>
          {vehiclesError ? <p className="form-error" role="alert">{vehiclesError}</p> : <div className="table-wrap"><table className="fleet-table"><thead><tr><th>Vehicle ID</th><th>Registration</th><th>Type & capacity</th><th>Fuel type</th><th>Status</th></tr></thead><tbody>
            {filteredVehicles.map((vehicle) => <tr key={vehicle.vehicle_id}><td>VH-{String(vehicle.vehicle_id).padStart(3, '0')}</td><td className="registration-cell">{vehicle.registration_no}</td><td>{vehicle.vehicle_type}<small>{Number(vehicle.capacity_kg).toLocaleString()} kg</small></td><td>{vehicle.fuel_type}</td><td><span className={`vehicle-status ${vehicle.current_status}`}>{vehicle.current_status}</span></td></tr>)}
            {filteredVehicles.length === 0 && <tr><td colSpan="5" className="table-empty">{vehicles.length === 0 ? 'No vehicles registered yet.' : 'No vehicles match those filters.'}</td></tr>}
          </tbody></table></div>}
          <p className="table-count">Showing {filteredVehicles.length} of {vehicles.length} vehicles</p>
        </section>}

        {activePage === 'drivers' && <section className="panel management-panel">
          <div className="panel-heading management-heading"><div><h2>Driver records</h2><p>Maintain driver contact and license details for future trip assignments.</p></div><button className="primary-button" onClick={() => { setShowDriverForm(!showDriverForm); setDriverFormError(''); }}>{showDriverForm ? 'Cancel' : 'Register driver'}</button></div>
          {driverRegistrationForm}
          <div className="fleet-controls">
            <label className="search-field"><span aria-hidden="true">⌕</span><input value={driverSearch} onChange={(event) => setDriverSearch(event.target.value)} placeholder="Search by name, phone or license" aria-label="Search drivers" /></label>
            <label className="filter-field">Status<select value={driverStatusFilter} onChange={(event) => setDriverStatusFilter(event.target.value)}><option value="all">All statuses</option><option value="active">Active</option><option value="inactive">Inactive</option></select></label>
          </div>
          {driversError ? <p className="form-error" role="alert">{driversError}</p> : <div className="table-wrap"><table className="fleet-table"><thead><tr><th>Driver</th><th>Phone</th><th>License number</th><th>License expiry</th><th>Status</th></tr></thead><tbody>
            {filteredDrivers.map((driver) => <tr key={driver.driver_id}><td className="driver-name-cell">{driver.full_name}<small>{driver.email || 'No email provided'}</small></td><td>{driver.phone}</td><td>{driver.license_number}</td><td>{driver.license_expiry}</td><td><span className={`driver-status ${driver.current_status}`}>{driver.current_status}</span></td></tr>)}
            {filteredDrivers.length === 0 && <tr><td colSpan="5" className="table-empty">{drivers.length === 0 ? 'No drivers registered yet.' : 'No drivers match those filters.'}</td></tr>}
          </tbody></table></div>}
          <p className="table-count">Showing {filteredDrivers.length} of {drivers.length} drivers</p>
        </section>}
        <footer className="page-footer"><span>FleetFlow Fleet Management Platform</span><span>Backend connection: {apiState}</span></footer>
      </main>
    </div>
  );
}
