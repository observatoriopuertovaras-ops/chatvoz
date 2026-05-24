import http from 'http';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PORT = process.env.PORT || 3000;
const DB_FILE = path.join(__dirname, 'data.json');

const sessions = new Map();

const seed = {
  users: [{ id: 1, name: 'Administrador', email: 'admin@sindical.cl', passwordHash: hash('admin123'), role: 'admin' }],
  lessons: [
    { id: 1, title: 'La productividad y formas de medirla', speaker: 'Gonzalo Durán', youtube: '' },
    { id: 2, title: 'Normas laborales y acción sindical', speaker: 'María Estrella Zúñiga', youtube: '' },
    { id: 3, title: 'Estado y repercusión en trabajadores', speaker: 'Cristian Cepeda', youtube: '' },
    { id: 4, title: 'Estrategias de organización y lucha', speaker: 'Sergio Alegría', youtube: '' },
    { id: 5, title: 'Formación del líder sindical', speaker: 'Isolina Acosta', youtube: '' },
    { id: 6, title: 'Rol de la Dirección del Trabajo', speaker: 'Hernán Larraín', youtube: '' },
    { id: 7, title: 'Trabajo a honorarios y contratos', speaker: 'Diego López', youtube: '' },
    { id: 8, title: 'Reformas laborales y movimiento sindical', speaker: 'Por confirmar', youtube: '' }
  ],
  downloads: []
};

function hash(text) { return crypto.createHash('sha256').update(text).digest('hex'); }
function readDB(){ if(!fs.existsSync(DB_FILE)) fs.writeFileSync(DB_FILE, JSON.stringify(seed,null,2)); return JSON.parse(fs.readFileSync(DB_FILE,'utf8')); }
function writeDB(db){ fs.writeFileSync(DB_FILE, JSON.stringify(db,null,2)); }
function send(res, code, data){ res.writeHead(code, {'Content-Type':'application/json','Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'Content-Type, Authorization','Access-Control-Allow-Methods':'GET,POST,PUT,OPTIONS'}); res.end(JSON.stringify(data)); }
function parseBody(req){ return new Promise((resolve)=>{ let b=''; req.on('data',c=>b+=c); req.on('end',()=>resolve(b?JSON.parse(b):{})); }); }
function auth(req){ const token=(req.headers.authorization||'').replace('Bearer ',''); return sessions.get(token); }
function youtubeToEmbed(url){ const m=url.match(/(?:v=|youtu\.be\/)([\w-]{6,})/); return m?`https://www.youtube.com/embed/${m[1]}`:null; }

const server = http.createServer(async (req,res)=>{
  if(req.method==='OPTIONS') return send(res,200,{ok:true});
  const u = new URL(req.url, `http://localhost:${PORT}`);

  if(req.method==='GET' && (u.pathname==='/' || u.pathname==='/index.html')){
    res.writeHead(200, {'Content-Type':'text/html'}); return res.end(fs.readFileSync(path.join(__dirname,'index.html')));
  }
  if(req.method==='GET' && u.pathname==='/styles.css'){ res.writeHead(200, {'Content-Type':'text/css'}); return res.end(fs.readFileSync(path.join(__dirname,'styles.css'))); }
  if(req.method==='GET' && u.pathname==='/app.js'){ res.writeHead(200, {'Content-Type':'application/javascript'}); return res.end(fs.readFileSync(path.join(__dirname,'app.js'))); }

  if(req.method==='POST' && u.pathname==='/api/login'){
    const {email,password}=await parseBody(req); const db=readDB();
    const user=db.users.find(x=>x.email===email && x.passwordHash===hash(password||''));
    if(!user) return send(res,401,{error:'Credenciales inválidas'});
    const token=crypto.randomBytes(24).toString('hex'); sessions.set(token,{id:user.id,role:user.role,name:user.name});
    return send(res,200,{token,user:{id:user.id,name:user.name,role:user.role,email:user.email}});
  }

  if(req.method==='GET' && u.pathname==='/api/public-data'){ const db=readDB(); return send(res,200,{lessons:db.lessons,downloads:db.downloads}); }

  if(u.pathname.startsWith('/api/admin/')){
    const me=auth(req); if(!me || me.role!=='admin') return send(res,403,{error:'Solo admin'});
    const db=readDB();

    if(req.method==='GET' && u.pathname==='/api/admin/users') return send(res,200,db.users.map(u=>({id:u.id,name:u.name,email:u.email,role:u.role})));
    if(req.method==='POST' && u.pathname==='/api/admin/users'){
      const {name,email,password}=await parseBody(req); if(!name||!email||!password) return send(res,400,{error:'Faltan campos'});
      if(db.users.some(u=>u.email===email)) return send(res,409,{error:'Email existente'});
      const id=Math.max(...db.users.map(u=>u.id),0)+1; db.users.push({id,name,email,passwordHash:hash(password),role:'student'}); writeDB(db); return send(res,201,{ok:true});
    }

    if(req.method==='PUT' && u.pathname==='/api/admin/lesson-video'){
      const {lessonId,youtubeUrl}=await parseBody(req); const embed=youtubeToEmbed(youtubeUrl||''); if(!embed) return send(res,400,{error:'YouTube inválido'});
      const l=db.lessons.find(x=>x.id===Number(lessonId)); if(!l) return send(res,404,{error:'Clase no encontrada'}); l.youtube=embed; writeDB(db); return send(res,200,{ok:true});
    }

    if(req.method==='POST' && u.pathname==='/api/admin/downloads'){
      const {title,type,url}=await parseBody(req); if(!url?.startsWith('https://')) return send(res,400,{error:'URL https requerida'});
      db.downloads.push({id:Date.now(),title,type,url}); writeDB(db); return send(res,201,{ok:true});
    }
  }

  send(res,404,{error:'No encontrado'});
});

server.listen(PORT, ()=> console.log(`Servidor en http://localhost:${PORT}`));
