let token = '';

const loginModal = document.getElementById('loginModal');
const adminPanel = document.getElementById('adminPanel');

async function api(path, method='GET', body){
  const res = await fetch(path,{method,headers:{'Content-Type':'application/json', ...(token?{Authorization:`Bearer ${token}`}:{})},body:body?JSON.stringify(body):undefined});
  const data = await res.json(); if(!res.ok) throw new Error(data.error||'Error'); return data;
}

function youtubeIframe(url){ return `<iframe src="${url}" allowfullscreen></iframe>`; }

async function renderPublic(){
  const data = await api('/api/public-data');
  const box = document.getElementById('lessons');
  box.innerHTML = data.lessons.map(l=>`<article class="lesson"><h4>Clase ${l.id}</h4><p>${l.title}<br><small>${l.speaker}</small></p>${l.youtube?youtubeIframe(l.youtube):'<small>Sin video asignado</small>'}</article>`).join('');
  lessonSelect.innerHTML = data.lessons.map(l=>`<option value="${l.id}">Clase ${l.id} - ${l.title}</option>`).join('');
  downloads.innerHTML = data.downloads.length?data.downloads.map(d=>`<a href="${d.url}" target="_blank">${d.title} (${d.type})</a>`).join(''):'<p>Aún no hay recursos publicados.</p>';
}

async function renderUsers(){
  const users = await api('/api/admin/users');
  userList.innerHTML = users.map(u=>`<li>${u.name} — ${u.email} (${u.role})</li>`).join('');
}

renderPublic();
btnLogin.onclick = ()=> loginModal.classList.remove('hidden');
closeAdmin.onclick = ()=> adminPanel.classList.add('hidden');

loginForm.onsubmit = async (e)=>{
  e.preventDefault();
  try {
    const r = await api('/api/login','POST',{email:email.value,password:password.value});
    token = r.token; loginModal.classList.add('hidden');
    if(r.user.role!=='admin') return alert('Solo administrador puede gestionar');
    adminPanel.classList.remove('hidden');
    await renderUsers();
  } catch(err){ alert(err.message); }
};

userForm.onsubmit = async (e)=>{ e.preventDefault(); try{ await api('/api/admin/users','POST',{name:newName.value,email:newEmail.value,password:newPass.value}); e.target.reset(); await renderUsers(); }catch(err){alert(err.message);} };
videoForm.onsubmit = async (e)=>{ e.preventDefault(); try{ await api('/api/admin/lesson-video','PUT',{lessonId:lessonSelect.value,youtubeUrl:youtubeUrl.value}); e.target.reset(); await renderPublic(); }catch(err){alert(err.message);} };
downloadForm.onsubmit = async (e)=>{ e.preventDefault(); try{ await api('/api/admin/downloads','POST',{title:downloadTitle.value,type:downloadType.value,url:downloadUrl.value}); e.target.reset(); await renderPublic(); }catch(err){alert(err.message);} };

document.querySelectorAll('.tab').forEach(btn=>btn.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(x=>x.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
});
