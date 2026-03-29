//This is the main JavaScript file for the OpenTickets frontend application. It handles user authentication, ticket management, and interaction with the backend API. The code is structured to listen for DOMContentLoaded events to initialize event listeners for forms and buttons, and it defines functions to load tickets, add comments, and manage user sessions. The API endpoint is set to "https://
const API = "https://127.0.0.1:8000";

//Helper function to handle 403 errors
const checkForForbidden = (response) => {
    if (response.status === 403) {
        window.location.href = "/error/403";
    }
    return response;
};

//These functions get the session info through session storage and the IP addressed used for the API calls.
function getToken() { return sessionStorage.getItem("session_token"); }
function getIP() { return "127.0.0.1"; }

//Function to convert status code ENUM to readable text
function getStatusText(code) {
  const statusMap = {
    "O": "Open",
    "C": "Closed",
    "E": "Escalated",
    "R": "In Review",
    "P": "In Progress"
  };
  return statusMap[code] || "Unknown";
}

//Function to convert priority code ENUM to readable text
function getPriorityText(code) {
  const priorityMap = {
    "L": "Low",
    "M": "Medium",
    "H": "High",
    "C": "Critical"
  };
  return priorityMap[code] || "Unknown";
}

//This is the ticket loading function that sends a request to the backend API to obtain the tickets for any staff member and displays them in a table format on the frontend.
async function loadTickets() {
  const res = await fetch(API + "/tickets/mytickets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: getToken(), ip_address: getIP() })
  });
  const tickets = await res.json();
  const tbody = document.querySelector("#ticketsTable tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  tickets.forEach(t => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><a href="ticket.html?id=${t.ticket_uuid}">#${t.ticket_uuid}</a></td>
      <td>${t.ticket_name}</td>
      <td>${getPriorityText(t.priority_code)}</td>
      <td>${getStatusText(t.status_code)}</td>
      <td>${t.assigned_staff_name || "Unassigned"}</td>
      <td>${new Date(t.create_time).toLocaleString()}</td> 
    `;
    tbody.appendChild(tr);
  });
}

//DomContent loaded event listener that is used to initialize the event listeners for the login form and ticket creation form that obtains form data (username/email and password) and sends a login request.
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async e => {
      e.preventDefault();
      const form = new FormData(e.target);
      const res = await fetch(API + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password")
        })
      });
      const data = await res.json();
      if (data.status) {
        sessionStorage.setItem("session_token", data.session_token);
        sessionStorage.setItem("user_id", data.user_id);
        validateSession();
        document.getElementById("loginCard").classList.add("hidden");
        document.getElementById("dashboard").classList.remove("hidden");
        loadTickets();

      } else {
        if (errorDiv) {
          errorDiv.textContent = data.message || "Login failed. Please check your credentials.";
          errorDiv.classList.remove("hidden");
        }
      }
    });
  }
//This is the ticket creation form event listener that obtains form data through the form and sends a request to the backend API to create a new ticket.
  const ticketForm = document.getElementById("ticketForm");
  if (ticketForm) {
    ticketForm.addEventListener("submit", async e => {
      e.preventDefault();
      const form = new FormData(e.target);
      const title = form.get("title") || document.getElementById("title").value;
      const description = form.get("description") || document.getElementById("description").value;
      const res = await fetch(API + "/tickets/create", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({
          title: document.getElementById("title").value,
          description: document.getElementById("description").value
        })
      });
      const data = await res.json();
      if (data.status) {
        alert("Ticket created successfully");
        form.reset();
        loadTickets();
      } else {
        alert("Error creating ticket: " + (data.message || ""));
      }
    });
  }

  const commentForm = document.getElementById("commentForm");
  if (commentForm) {
    commentForm.addEventListener("submit", async e => {
      e.preventDefault();
      const params = new URLSearchParams(window.location.search);
      const ticket_uuid = params.get("id");
      if (!ticket_uuid) {
        alert("Invalid ticket ID");
        return;
      }
      const form = new FormData(e.target);
      const message = form.get("message");
      await addComment(ticket_uuid, message);
      commentForm.reset();
    });
  }
});
// This is the function that displays the tickets that are assigned to or created by the guest and managed by the staff.
async function loadTicket() {
  const params = new URLSearchParams(window.location.search);
  const ticket_uuid = params.get("id");
  if (!ticket_uuid) return;
  const res = await fetch(API + "/tickets/detail", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: getToken(), ip_address: getIP(), ticket_uuid })
  }).then(checkForForbidden);
  const data = await res.json();
  if (!data.success) {
    alert("Cannot load ticket: " + (data.message || ""));
    return;
  }
  const t = data.ticket;
  document.getElementById("tTitle").textContent = t.ticket_name;
  document.getElementById("tDesc").textContent = t.ticket_description;
  const commentsEl = document.getElementById("comments");
  if (commentsEl) {
    commentsEl.innerHTML = "";
    (data.comments || []).forEach(c => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${c.author}</strong> <span class="muted">${new Date(c.createdAt).toLocaleString()}</span><div>${c.message}</div>`;
      commentsEl.appendChild(li);
    });
  }
}
//this is the function that allows staff members to add comments to the tickets that they are managing and assigned to.
async function addComment(ticket_uuid, text) {
  const res = await fetch(API + "/tickets/comment", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      token: getToken(),
      ip_address: getIP(),
      ticket_uuid,
      comment_text: text
    })
  }).then(checkForForbidden);
  const data = await res.json();
  if (data.success) {
    alert("Comment added");
    loadTicket();
  } else {
    alert("Failed to add comment: " + (data.message || ""));
  }
}