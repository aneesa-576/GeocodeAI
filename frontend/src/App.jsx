import React, { useState, useEffect } from 'react';
import './App.css';

/**
 * GeoCode AI - Main Application Component
 * 
 * Flow: Home -> Processing -> Result -> Verify Again -> Home
 * Built using pure React (useState, useEffect), Vite, JavaScript, and Vanilla CSS.
 */
export default function App() {
  // =========================================================================
  // 1. STATE MANAGEMENT (Simple React useState hook)
  // =========================================================================

  // Controls current active screen: 'home' | 'processing' | 'result'
  const [step, setStep] = useState('home');

  // Stores the address typed by user or selected from preset chips
  const [addressInput, setAddressInput] = useState('');

  // Stores progress percentage (0 - 100) during processing step
  const [progress, setProgress] = useState(0);

  // Active step index during processing animation (0 to 3)
  const [processingStepIndex, setProcessingStepIndex] = useState(0);

  // Copy status message for UI feedback
  const [copyFeedback, setCopyFeedback] = useState(false);

  // Calculated or mock location result data
  const [resultData, setResultData] = useState(null);

  // Sample presets for quick testing during hackathon presentations
  const samplePresets = [
    {
      label: "Google HQ",
      address: "1600 Amphitheatre Pkwy, Mountain View, CA 94043",
      city: "Mountain View",
      state: "CA",
      zip: "94043",
      lat: 37.4220,
      lng: -122.0841,
      confidence: "99.8%"
    },
    {
      label: "Apple Park",
      address: "1 Apple Park Way, Cupertino, CA 95014",
      city: "Cupertino",
      state: "CA",
      zip: "95014",
      lat: 37.3349,
      lng: -122.0090,
      confidence: "99.4%"
    },
    {
      label: "Empire State",
      address: "350 5th Ave, New York, NY 10118",
      city: "New York",
      state: "NY",
      zip: "10118",
      lat: 40.7484,
      lng: -73.9857,
      confidence: "98.9%"
    }
  ];

  // Processing log steps shown in loading animation
  const processingSteps = [
    "Parsing & standardizing address string...",
    "Querying GeoCode AI neural geocoding engine...",
    "Cross-referencing global postal database & RDI...",
    "Computing high-precision rooftop coordinates..."
  ];

  // =========================================================================
  // 2. EVENT HANDLERS & NAVIGATION LOGIC
  // =========================================================================

  /**
   * Primary Action: Triggered when user clicks "Locate"
   * Moves application from 'home' -> 'processing' state
   */
  const handleLocate = (e) => {
    if (e) e.preventDefault();
    
    // Fallback default address if field was empty
    const targetAddress = addressInput.trim() || "1600 Amphitheatre Pkwy, Mountain View, CA 94043";
    setAddressInput(targetAddress);
    
    // Reset loading state
    setProgress(0);
    setProcessingStepIndex(0);
    
    // Transition to processing view
    setStep('processing');
  };

  /**
   * Simulates AI location intelligence lookup during 'processing' step
   */
  useEffect(() => {
    if (step !== 'processing') return;

    // Increment progress bar over ~2 seconds
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        
        // Update active processing sub-step based on progress
        const nextVal = prev + 5;
        if (nextVal > 75) setProcessingStepIndex(3);
        else if (nextVal > 50) setProcessingStepIndex(2);
        else if (nextVal > 25) setProcessingStepIndex(1);
        
        return nextVal;
      });
    }, 80);

    // Auto-transition to 'result' state when progress reaches 100%
    const timeout = setTimeout(() => {
      // Find matching preset or generate dynamic details
      const matched = samplePresets.find(p => 
        addressInput.toLowerCase().includes(p.city.toLowerCase()) || 
        addressInput.toLowerCase().includes(p.zip)
      ) || {
        label: "Verified Address",
        address: addressInput,
        city: "San Francisco",
        state: "CA",
        zip: "94105",
        lat: 37.7749,
        lng: -122.4194,
        confidence: "98.7%"
      };

      setResultData({
        original: addressInput,
        standardized: matched.address,
        street: matched.address.split(',')[0],
        city: matched.city,
        state: matched.state,
        zip: matched.zip,
        country: "United States",
        latitude: matched.lat.toFixed(4),
        longitude: matched.lng.toFixed(4),
        confidence: matched.confidence,
        deliverability: "Valid & Deliverable",
        propertyType: "Commercial / Office",
        rdi: "Commercial",
        dpvMatch: "Y - Fully Confirmed",
        timezone: "PST (UTC-8)"
      });

      setStep('result');
    }, 2100);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [step, addressInput]);

  /**
   * Reset Action: Triggered when user clicks "Verify Again" or Brand Logo
   * Returns application from 'result' -> 'home' state
   */
  const handleVerifyAgain = () => {
    setStep('home');
    setCopyFeedback(false);
  };

  /**
   * Quick Preset Selector
   */
  const handleSelectPreset = (presetAddress) => {
    setAddressInput(presetAddress);
  };

  /**
   * Copy formatted results to clipboard
   */
  const handleCopyResults = () => {
    if (!resultData) return;
    const textToCopy = `GeoCode AI Location Intelligence:\nAddress: ${resultData.standardized}\nCoordinates: ${resultData.latitude}, ${resultData.longitude}\nDeliverability: ${resultData.deliverability}\nConfidence: ${resultData.confidence}`;
    navigator.clipboard.writeText(textToCopy);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2000);
  };

  // =========================================================================
  // 3. RENDER UI SCHEME
  // =========================================================================

  return (
    <div className="app-container">
      {/* Background Decorative Grid */}
      <div className="bg-grid"></div>

      {/* Top Navigation Bar */}
      <header className="navbar">
        <div className="brand-logo" onClick={handleVerifyAgain} title="Click to go Home">
          <div className="logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div className="logo-text-group">
            <span className="brand-title">GeoCode AI</span>
            <span className="brand-tagline">Address Verification & Location Intelligence</span>
          </div>
        </div>

        <div className="nav-badges">
          <div className="badge badge-live">
            <span className="status-dot"></span>
            <span>API Online</span>
          </div>
          <div className="badge badge-version">v2.4 Hackathon Edition</div>
        </div>
      </header>

      {/* Main View Switcher */}
      <main className="main-content">
        
        {/* ===================================================================
            VIEW 1: HOME STATE (Input & Hero)
           =================================================================== */}
        {step === 'home' && (
          <div className="home-view">
            {/* Hero Header */}
            <div className="hero-section">
              <div className="hero-pill">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
                <span>Next-Gen Rooftop Precision</span>
              </div>
              <h1 className="hero-title">
                AI-Powered <span className="gradient-text">Address Verification</span> & Location Intelligence
              </h1>
              <p className="hero-subtitle">
                Instantly standardize unformatted addresses, resolve high-precision geographic coordinates, and validate deliverability worldwide.
              </p>
            </div>

            {/* Input Glass Card */}
            <div className="glass-card">
              <form onSubmit={handleLocate} className="input-section">
                <div className="input-label-group">
                  <label className="input-label" htmlFor="address-input">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2">
                      <circle cx="11" cy="11" r="8"/>
                      <path d="m21 21-4.3-4.3"/>
                    </svg>
                    Enter Full Street Address
                  </label>
                  <span className="preset-tag">Supports Global Format</span>
                </div>

                <div className="input-wrapper">
                  <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                  <input
                    id="address-input"
                    type="text"
                    className="search-input"
                    placeholder="e.g. 1600 Amphitheatre Pkwy, Mountain View, CA 94043"
                    value={addressInput}
                    onChange={(e) => setAddressInput(e.target.value)}
                  />
                </div>

                {/* Primary Action Button - MUST be "Locate" as per requirements */}
                <button type="submit" className="btn-locate">
                  <span>Locate</span>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </button>
              </form>

              {/* Preset Sample Chips for quick presentation demos */}
              <div className="presets-group">
                <div className="presets-title">Quick Demo Address Presets:</div>
                <div className="presets-grid">
                  {samplePresets.map((preset, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="preset-chip"
                      onClick={() => handleSelectPreset(preset.address)}
                    >
                      <span className="preset-tag">{preset.label}</span>
                      <div className="preset-text">{preset.address}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Feature Highlights Grid */}
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon-wrapper">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                  </svg>
                </div>
                <h3 className="feature-title">AI Standardization</h3>
                <p className="feature-desc">Cleans messy text, corrects spelling errors, and formats to official postal standards.</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon-wrapper">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                    <polyline points="2 17 12 22 22 17"/>
                    <polyline points="2 12 12 17 22 12"/>
                  </svg>
                </div>
                <h3 className="feature-title">Geocoding & Coords</h3>
                <p className="feature-desc">Generates exact rooftop latitude and longitude coordinates with sub-meter accuracy.</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon-wrapper">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                </div>
                <h3 className="feature-title">Deliverability Check</h3>
                <p className="feature-desc">Validates mailability, unit verification, and residential vs commercial property classification.</p>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            VIEW 2: PROCESSING STATE (Loading & Step Tracker)
           =================================================================== */}
        {step === 'processing' && (
          <div className="glass-card processing-card">
            {/* Animated Cyber Radar Pulse */}
            <div className="radar-spinner-container">
              <div className="radar-ring"></div>
              <div className="radar-ring-inner"></div>
              <svg className="radar-center-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>

            <h2 className="processing-title">Analyzing Location Data...</h2>
            <div className="processing-address">{addressInput}</div>

            {/* Simulated Progress Bar */}
            <div className="progress-bar-container">
              <div 
                className="progress-bar-fill"
                style={{ width: `${progress}%` }}
              ></div>
            </div>

            {/* Animated Log Step Items */}
            <div className="step-tracker">
              {processingSteps.map((stepText, index) => {
                const isCompleted = index < processingStepIndex;
                const isActive = index === processingStepIndex;
                return (
                  <div 
                    key={index} 
                    className={`step-item ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}
                  >
                    <div className="step-indicator">
                      {isCompleted ? '✓' : index + 1}
                    </div>
                    <span>{stepText}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ===================================================================
            VIEW 3: RESULT STATE (Intelligence Dashboard)
           =================================================================== */}
        {step === 'result' && resultData && (
          <div className="glass-card result-view">
            {/* Header Result Status Bar */}
            <div className="results-header">
              <div className="results-status-badge">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>Address Successfully Verified & Located</span>
              </div>

              <div className="confidence-box">
                <span className="preset-tag">AI Precision Score</span>
                <span className="confidence-score">{resultData.confidence}</span>
              </div>
            </div>

            {/* Results Grid - Breakdown & Map */}
            <div className="results-grid">
              
              {/* Left Column: Standardized Address vs Original */}
              <div className="address-comparison">
                <h3 className="card-title">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  Standardized Postal Format
                </h3>

                <div className="address-box standardized">
                  <div className="box-label">GeoCode AI Cleaned Address</div>
                  <div className="box-val">{resultData.standardized}</div>
                </div>

                <div className="address-box">
                  <div className="box-label">Original User Query</div>
                  <div className="box-val" style={{ color: 'var(--text-muted)' }}>{resultData.original}</div>
                </div>
              </div>

              {/* Right Column: Geographic Coordinates & Map Preview */}
              <div>
                <h3 className="card-title">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-purple)" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
                    <path d="M2 12h20"/>
                  </svg>
                  Geographic Coordinates
                </h3>

                <div className="coords-grid">
                  <div className="coord-card">
                    <div className="coord-label">Latitude</div>
                    <div className="coord-val">{resultData.latitude}° N</div>
                  </div>
                  <div className="coord-card">
                    <div className="coord-label">Longitude</div>
                    <div className="coord-val">{resultData.longitude}° W</div>
                  </div>
                </div>

                {/* Simulated Radar Map Preview Component */}
                <div className="map-preview-box">
                  <div className="map-grid-bg"></div>
                  <div className="map-marker">
                    <svg className="marker-pin" width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                    </svg>
                    <div className="marker-pulse"></div>
                  </div>
                  <div className="map-overlay-tag">
                    Rooftop Marker: [{resultData.latitude}, {resultData.longitude}]
                  </div>
                </div>
              </div>

            </div>

            {/* Detailed Component Breakdown */}
            <div style={{ marginTop: '1.5rem' }}>
              <h3 className="card-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="3" y1="9" x2="21" y2="9"/>
                  <line x1="9" y1="21" x2="9" y2="9"/>
                </svg>
                Location Intelligence & Breakdown
              </h3>

              <div className="components-list">
                <div className="comp-item">
                  <span className="comp-label">Street Address</span>
                  <span className="comp-val">{resultData.street}</span>
                </div>
                <div className="comp-item">
                  <span className="comp-label">City</span>
                  <span className="comp-val">{resultData.city}</span>
                </div>
                <div className="comp-item">
                  <span className="comp-label">State / Zip</span>
                  <span className="comp-val">{resultData.state} {resultData.zip}</span>
                </div>
                <div className="comp-item">
                  <span className="comp-label">Country</span>
                  <span className="comp-val">{resultData.country}</span>
                </div>
                <div className="comp-item">
                  <span className="comp-label">Deliverability</span>
                  <span className="comp-val" style={{ color: 'var(--accent-emerald)' }}>{resultData.deliverability}</span>
                </div>
                <div className="comp-item">
                  <span className="comp-label">Property Usage</span>
                  <span className="comp-val">{resultData.propertyType}</span>
                </div>
              </div>
            </div>

            {/* Action Buttons - MUST include "Verify Again" to reset flow to Home */}
            <div className="action-footer">
              <button className="btn-verify-again" onClick={handleVerifyAgain}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                  <path d="M3 3v5h5"/>
                </svg>
                <span>Verify Again</span>
              </button>

              <button className="btn-copy" onClick={handleCopyResults}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                <span>{copyFeedback ? 'Copied to Clipboard!' : 'Copy Intelligence Summary'}</span>
              </button>
            </div>

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="footer">
        <p>GeoCode AI &copy; 2026 — AI-Powered Address Verification & Location Intelligence. Built for Hackathons.</p>
      </footer>
    </div>
  );
}
