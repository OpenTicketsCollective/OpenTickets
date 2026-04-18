async function validateSession() {
  const authAPI = "/api";
  const token = sessionStorage.getItem("session_token");
  
  // Skip validation if no token exists
  if (!token) {
    return;
  }

  const res = await fetch(authAPI + "/validate_session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      token: token,
      ip_address: window.location.hostname
    })
  });

  const data = await res.json();
  if (data.status) {
    // Session valid
    if (window.location.pathname === "/" || window.location.pathname === "/index.html" || window.location.pathname === "/index") {
      // Current page is root/index, redirect to staff dashboard
      window.location.href = "staff.html";
    }
    if (window.location.pathname === "/staff.html" || window.location.pathname === "/staff") {
        if (document.getElementById("dashboard")) {
            document.getElementById("dashboard").classList.remove("hidden");
            loadTickets();
        }
    }
    if (window.location.pathname === "/ticket.html" || window.location.pathname === "/ticket") {
        loadTicket()
        }
        
    
    // If current page is anything else, don't redirect
    } 
    else {
    // Token invalid, clear and show login
    sessionStorage.clear();
    if (window.location.pathname !== "/" && window.location.pathname !== "/index.html" && window.location.pathname !== "/index") {
      window.location.href = "/";
    }
  }
}

// Validate session on page load
validateSession();