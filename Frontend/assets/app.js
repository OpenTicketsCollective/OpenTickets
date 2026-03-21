// Simple localStorage-backed demo backend for OpenTickets
(function(){
  const DB_KEY = 'opentickets_db_v1'

  function now(){return new Date().toISOString()}

  function readDB(){
    const raw = localStorage.getItem(DB_KEY)
    if(!raw) return seedData()
    try{return JSON.parse(raw)}catch(e){return seedData()}
  }

  function writeDB(db){ localStorage.setItem(DB_KEY, JSON.stringify(db)) }

  function seedData(){
    const db = {
      users: [
        {username:'tech1', password:'password', role:'tech', display:'Tech One'},
        {username:'admin', password:'password', role:'admin', display:'Administrator'}
      ],
      tickets: [
        {id:1,title:'Email not sending',description:'Unable to send external email',priority:'urgent',assignedTo:null,status:'open',createdAt:now(),creatorName:'Alice',comments:[]},
        {id:2,title:'Printer jam',description:'Paper jam on floor 3 printer',priority:'regular',assignedTo:'tech1',status:'open',createdAt:now(),creatorName:'Bob',comments:[]}
      ],
      nextId:3
    }
    writeDB(db)
    return db
  }

  // Public API
  window.OT = {
    db: readDB(),
    save(){ writeDB(this.db) },
    createTicket(t){ t.id=this.db.nextId++; t.createdAt=now(); t.status='open'; t.comments=[]; this.db.tickets.push(t); this.save(); return t },
    getTickets(){ return this.db.tickets.slice() },
    getTicket(id){ return this.db.tickets.find(t=>t.id===Number(id)) },
    updateTicket(updated){ const i=this.db.tickets.findIndex(t=>t.id===updated.id); if(i>=0){this.db.tickets[i]=updated; this.save()} },
    addComment(id, comment){ const t=this.getTicket(id); if(!t) return; t.comments.push(comment); this.updateTicket(t); },
    users(){ return this.db.users.slice() },
    auth(username,password){ return this.db.users.find(u=>u.username===username && u.password===password) }
  }

  // Page wiring
  document.addEventListener('DOMContentLoaded', ()=>{
    if(document.getElementById('ticketForm')) bindSubmit()
    if(document.getElementById('recentTickets')) renderRecent()
    if(document.getElementById('loginForm')) bindLogin()
    if(document.getElementById('ticketsTable')) renderDashboard()
    if(document.getElementById('ticketCard')) renderTicketPage()
  })

  // Submission page
  function bindSubmit(){
    const form=document.getElementById('ticketForm')
    const msg=document.getElementById('submitMsg')
    form.addEventListener('submit', e=>{
      e.preventDefault()
      const data = new FormData(form)
      const t = {title:data.get('title'), description:data.get('description'), priority:data.get('priority')||'regular', creatorName:data.get('creatorName')||'Anonymous', creatorEmail:data.get('creatorEmail')||''}
      const created = OT.createTicket(t)
      msg.textContent = `Ticket #${created.id} submitted.`
      form.reset()
      renderRecent()
    })
  }

  function renderRecent(){
    const ul=document.getElementById('recentTickets')
    if(!ul) return
    ul.innerHTML=''
    const items = OT.getTickets().slice().sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt)).slice(0,8)
    items.forEach(t=>{
      const li=document.createElement('li')
      li.innerHTML = `<strong><a href="ticket.html?id=${t.id}">#${t.id} ${escapeHtml(t.title)}</a></strong> — <span class="muted">${t.priority}</span>`
      ul.appendChild(li)
    })
  }

  // Staff page
  function bindLogin(){
    const form=document.getElementById('loginForm')
    const msg=document.getElementById('loginMsg')
    form.addEventListener('submit', e=>{
      e.preventDefault()
      const data=new FormData(form)
      const user = OT.auth(data.get('username'), data.get('password'))
      if(!user){ msg.textContent='Invalid credentials'; return }
      // store session temporarily in sessionStorage
      sessionStorage.setItem('ot_user', JSON.stringify({username:user.username,display:user.display||user.username,role:user.role}))
      msg.textContent=''
      document.getElementById('loginCard').classList.add('hidden')
      document.getElementById('dashboard').classList.remove('hidden')
      initDashboard()
    })
  }

  function initDashboard(){
    renderDashboard()
    document.getElementById('oldestUrgent').addEventListener('click', ()=>{
      const t = OT.getTickets().filter(x=>x.priority==='urgent' && x.status==='open').sort((a,b)=>new Date(a.createdAt)-new Date(b.createdAt))[0]
      if(t) location.href = `ticket.html?id=${t.id}`
      else alert('No urgent open tickets')
    })
    document.getElementById('unassigned').addEventListener('click', ()=>{
      const t = OT.getTickets().filter(x=>!x.assignedTo && x.status==='open').sort((a,b)=>new Date(a.createdAt)-new Date(b.createdAt))[0]
      if(t) location.href = `ticket.html?id=${t.id}`
      else alert('No unassigned open tickets')
    })
    document.getElementById('sortBy').addEventListener('change', renderDashboard)
  }

  function renderDashboard(){
    const tickets = OT.getTickets()
    const ctx = document.getElementById('ticketChart')
    if(ctx){
      const urgent = tickets.filter(t=>t.priority==='urgent' && t.status==='open').length
      const regular = tickets.filter(t=>t.priority!=='urgent' && t.status==='open').length
      if(window._otChart) window._otChart.destroy()
      window._otChart = new Chart(ctx,{type:'pie',data:{labels:['Urgent','Regular'],datasets:[{data:[urgent,regular],backgroundColor:['#e74c3c','#f1c40f']}]}})
    }
    const tbody=document.querySelector('#ticketsTable tbody')
    if(!tbody) return
    const sortBy = document.getElementById('sortBy').value
    let rows = tickets.slice()
    if(sortBy==='createdAt') rows.sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt))
    if(sortBy==='assignedTo') rows.sort((a,b)=> (a.assignedTo||'').localeCompare(b.assignedTo||''))
    tbody.innerHTML=''
    rows.forEach(t=>{
      const tr=document.createElement('tr')
      tr.innerHTML = `<td><a href="ticket.html?id=${t.id}">#${t.id}</a></td><td>${escapeHtml(t.title)}</td><td>${t.priority}</td><td>${t.assignedTo||'<span class="muted">Unassigned</span>'}</td><td>${new Date(t.createdAt).toLocaleString()}</td>`
      tbody.appendChild(tr)
    })
  }

  // Ticket page
  function renderTicketPage(){
    const id = new URLSearchParams(location.search).get('id')
    if(!id) return
    const t = OT.getTicket(id)
    if(!t) return
    document.getElementById('tTitle').textContent = `#${t.id} ${t.title}`
    document.getElementById('tDesc').textContent = t.description
    document.getElementById('tMeta').textContent = `${t.priority.toUpperCase()} • ${t.status} • Created ${new Date(t.createdAt).toLocaleString()} by ${t.creatorName||'Anonymous'}`
    // assign dropdown
    const assign = document.getElementById('assignTo')
    assign.innerHTML = '<option value="">-- Unassigned --</option>'
    OT.users().forEach(u=>{
      const opt=document.createElement('option'); opt.value=u.username; opt.textContent = u.display||u.username; if(t.assignedTo===u.username) opt.selected=true; assign.appendChild(opt)
    })
    document.getElementById('status').value = t.status
    document.getElementById('saveTicket').addEventListener('click', ()=>{
      t.assignedTo = assign.value||null
      t.status = document.getElementById('status').value
      OT.updateTicket(t)
      alert('Saved')
    })
    // comments
    function renderComments(){
      const ul=document.getElementById('comments'); ul.innerHTML=''
      t.comments.forEach(c=>{
        const li=document.createElement('li'); li.innerHTML = `<strong>${escapeHtml(c.author)}</strong> <span class="muted">${new Date(c.createdAt).toLocaleString()}</span><div>${escapeHtml(c.message)}</div>`; ul.appendChild(li)
      })
    }
    renderComments()
    document.getElementById('commentForm').addEventListener('submit', e=>{
      e.preventDefault(); const fd=new FormData(e.target); const c={author:fd.get('author')||'Anonymous', message:fd.get('message'), createdAt:now()}; OT.addComment(t.id,c); t.comments.push(c); renderComments(); e.target.reset()
    })
  }

  // small util
  function escapeHtml(s){ if(!s) return ''; return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c])) }

})();
