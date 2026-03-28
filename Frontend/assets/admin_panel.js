document.addEventListener("DOMContentLoaded", () => {
const API = "https://127.0.0.1:8000"

const token = sessionStorage.getItem("session_token");

// Only initialize dashboard if user is logged in (app.js handles login)
if (!token) {
    return; // User not logged in, app.js will show login form
}

// User is logged in - show dashboard and initialize admin functions
document.getElementById("loginCard").classList.add("hidden");
document.getElementById("dashboard").classList.remove("hidden");

//User management system for the admin dashboard so that the admin can manage user accounts effectively
    async function loaduser(){
        const response = await fetch(API +"/admin/users", {
            method: "POST",
            headers: {"Authorization": sessionStorage.getItem("session_token")}
        })
        const res = await response.json()
        const table = document.getElementById('userTable')
        table.innerHTML = ""
        res.forEach(u=>{
            const row = document.createElement('tr')
            row.innerHTML=`
                <td>${u.user_id}</td>
                <td>${u.email}</td>
                <td>${u.first_name} ${u.last_name}</td>
                <td>${u.access_level}</td>
         <td>
         <button onclick="resetPassword(${u.user_id})">Reset Password</button>
         <button onclick="deleteUser(${u.user_id})">Delete User</button>
         </td>
            `
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
        })
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
            })
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
            })
            alert("Password reset successfully")
            loaduser()
        }
    }

//session management for the admin dashboard so that the admin can manage user sessions effectively
    async function loadSessions(){
        const response = await fetch(API +"/admin/sessions", {
            method: "POST",
            headers:{"Authorization":sessionStorage.getItem("session_token")}
        })
        const sessions = await response.json()
        const table = document.getElementById('sessionTable')
        table.innerHTML = ""
        sessions.forEach(s=>{
            const row = document.createElement('tr')
            row.innerHTML=`
                <td>${s.session_id}</td>
                <td>${s.user_id}</td>
                <td>${s.created_time}</td>
                <td>${s.expire_time}</td>
                <td>${s.ip_address}</td>
                <td>${s.user_agent_header}</td>
            `
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
