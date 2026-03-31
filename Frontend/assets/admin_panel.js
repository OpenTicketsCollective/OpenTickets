document.addEventListener("DOMContentLoaded", () => {
const API = "https://127.0.0.1:8000"

const token = sessionStorage.getItem("session_token");

// Helper function to handle 403 errors
const checkForForbidden = (response) => {
    if (response.status === 403) {
        window.location.href = "/error/403";
    }
    return response;
};


//User management system for the admin dashboard so that the admin can manage user accounts effectively
    async function loaduser(){
        const response = await fetch(API +"/admin/users", {
            method: "POST",
            headers: {"Authorization": sessionStorage.getItem("session_token")}
        }).then(checkForForbidden)
        const res = await response.json()
        const table = document.getElementById('userTable')
        table.innerHTML = ""
        res.forEach(u=>{
            const row = document.createElement('tr')
            
            const idCell = document.createElement("td");
            idCell.textContent = u.user_id;
            row.appendChild(idCell);

            const emailCell = document.createElement("td");
            emailCell.textContent = u.email;
            row.appendChild(emailCell);

            const nameCell = document.createElement("td");
            nameCell.textContent = `${u.first_name} ${u.last_name}`;
            row.appendChild(nameCell);

            const accessCell = document.createElement("td");
            accessCell.textContent = u.access_level;
            row.appendChild(accessCell);

            const actionCell = document.createElement("td");
            const resetBtn = document.createElement("button");
            resetBtn.textContent = "Reset Password";
            resetBtn.addEventListener("click", () => resetPassword(u.user_id));
            actionCell.appendChild(resetBtn);

            const deleteBtn = document.createElement("button");
            deleteBtn.textContent = "Delete User";
            deleteBtn.addEventListener("click", () => deleteUser(u.user_id));
            actionCell.appendChild(deleteBtn);
            row.appendChild(actionCell);
            
            table.appendChild(row)
        })  
    }

//IT personel account creation for the admin dashboard so that the admin can create user accounts effectively
    document.getElementById("createUserForm").addEventListener("submit", async e => {
        e.preventDefault()
        const form=new FormData(e.target)
        const data = Object.fromEntries(form.entries())
        await fetch(API + "/admin/createuser", {
            method:"POST",
            headers:{"Content-Type":"application/json", "Authorization":sessionStorage.getItem("session_token")},
            body:JSON.stringify(data)
        }).then(checkForForbidden)
        loaduser()
        loadSessions()
    })

//IT personel user deletion for the admin dashboard so that the admin can delete user accounts effectively
    async function deleteUser(userId){
        if(confirm("Are you sure you want to delete this user?")){
            await fetch(API + "/admin/deleteuser", {
                method:"POST",
                headers:{"Content-Type":"application/json", "Authorization":sessionStorage.getItem("session_token")},
                body:JSON.stringify({userId})
            }).then(checkForForbidden)
            loaduser()
            loadSessions()
        }
    }

//IT personel password reset for the admin dashboard so that the admin can reset user passwords effectively
    async function resetPassword(userId){
        if(confirm("Are you sure you want to reset this user's password?")){
            await fetch(API + "/admin/resetpassword", {
                method:"POST",
                headers:{"Content-Type":"application/json", "Authorization":sessionStorage.getItem("session_token")},
                body:JSON.stringify({userId})
            }).then(checkForForbidden)
            alert("Password reset successfully")
            loaduser()
        }
    }

//session management for the admin dashboard so that the admin can manage user sessions effectively
    async function loadSessions(){
        const response = await fetch(API +"/admin/sessions", {
            method: "POST",
            headers:{"Authorization":sessionStorage.getItem("session_token")}
        }).then(checkForForbidden)
        const sessions = await response.json()
        const table = document.getElementById('sessionTable')
        table.innerHTML = ""
        sessions.forEach(s=>{
            const row = document.createElement('tr')
            
            const sessionCell = document.createElement("td");
            sessionCell.textContent = s.session_id;
            row.appendChild(sessionCell);

            const userCell = document.createElement("td");
            userCell.textContent = s.user_id;
            row.appendChild(userCell);

            const createdCell = document.createElement("td");
            createdCell.textContent = s.created_time;
            row.appendChild(createdCell);

            const expireCell = document.createElement("td");
            expireCell.textContent = s.expire_time;
            row.appendChild(expireCell);

            const ipCell = document.createElement("td");
            ipCell.textContent = s.ip_address;
            row.appendChild(ipCell);

            const agentCell = document.createElement("td");
            agentCell.textContent = s.user_agent_header;
            row.appendChild(agentCell);
            
            table.appendChild(row)
        })
    }
loaduser()
loadSessions()

// Show logout button for authenticated users
document.getElementById("logoutBtn").style.display = "block";

// Logout handler
document.getElementById("logoutBtn").addEventListener("click", () => {
    sessionStorage.removeItem("session_token");
    sessionStorage.removeItem("user_id");
    location.reload();
});
})
