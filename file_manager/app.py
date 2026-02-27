"""
File Manager sederhana via Web Browser
Akses di: http://localhost:5000
Bisa browse, edit, dan upload file URDF dan file ROS lainnya
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import os, json

app = Flask(__name__)
BASE_DIR = "/root/ros_ws/src"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>ROS File Manager</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #1e1e2e; color: #cdd6f4; height: 100vh; display: flex; flex-direction: column; }
  header { background: #181825; padding: 12px 20px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #313244; }
  header h1 { font-size: 18px; color: #cba6f7; }
  header span { font-size: 12px; color: #6c7086; }
  .container { display: flex; flex: 1; overflow: hidden; }
  .sidebar { width: 280px; background: #181825; border-right: 1px solid #313244; overflow-y: auto; padding: 8px 0; }
  .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  .toolbar { background: #1e1e2e; padding: 8px 12px; border-bottom: 1px solid #313244; display: flex; align-items: center; gap: 8px; font-size: 13px; }
  .editor-area { flex: 1; overflow: hidden; }
  textarea { width: 100%; height: 100%; background: #1e1e2e; color: #cdd6f4; border: none; outline: none; font-family: 'Consolas', monospace; font-size: 14px; padding: 16px; resize: none; line-height: 1.6; }
  .file-item { padding: 6px 16px; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; color: #cdd6f4; transition: background 0.1s; }
  .file-item:hover { background: #313244; }
  .file-item.active { background: #45475a; }
  .dir-label { padding: 8px 12px 4px; font-size: 11px; color: #6c7086; text-transform: uppercase; letter-spacing: 1px; }
  .icon { font-size: 14px; }
  button { background: #cba6f7; color: #1e1e2e; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; }
  button:hover { background: #b4befe; }
  button.secondary { background: #45475a; color: #cdd6f4; }
  .status { font-size: 12px; color: #a6e3a1; margin-left: auto; }
  .current-file { font-size: 12px; color: #89b4fa; }
</style>
</head>
<body>
<header>
  <h1>🤖 ROS File Manager</h1>
  <span>ros_ws/src</span>
</header>
<div class="container">
  <div class="sidebar" id="sidebar">Loading...</div>
  <div class="main">
    <div class="toolbar">
      <button onclick="saveFile()">💾 Save</button>
      <button class="secondary" onclick="refreshBuild()">🔨 Build WS</button>
      <button class="secondary" onclick="launchDisplay()">🚀 Launch Display</button>
      <span class="current-file" id="currentFile">Pilih file...</span>
      <span class="status" id="status"></span>
    </div>
    <div class="editor-area">
      <textarea id="editor" placeholder="Pilih file dari sidebar untuk mengedit..."></textarea>
    </div>
  </div>
</div>

<script>
let currentPath = null;

async function loadTree() {
  const res = await fetch('/api/tree');
  const data = await res.json();
  renderTree(data, document.getElementById('sidebar'));
}

function renderTree(items, container, depth=0) {
  container.innerHTML = '';
  items.forEach(item => {
    if (item.type === 'dir') {
      const label = document.createElement('div');
      label.className = 'dir-label';
      label.style.paddingLeft = (12 + depth*12) + 'px';
      label.textContent = '📁 ' + item.name;
      container.appendChild(label);
      const sub = document.createElement('div');
      renderTree(item.children || [], sub, depth+1);
      container.appendChild(sub);
    } else {
      const div = document.createElement('div');
      div.className = 'file-item';
      div.style.paddingLeft = (16 + depth*12) + 'px';
      const ext = item.name.split('.').pop();
      const icons = {urdf:'📄', xacro:'📄', py:'🐍', xml:'📋', yaml:'⚙️', rviz:'👁️', launch:'🚀'};
      div.innerHTML = `<span class="icon">${icons[ext] || '📄'}</span>${item.name}`;
      div.onclick = () => openFile(item.path, div);
      container.appendChild(div);
    }
  });
}

async function openFile(path, el) {
  document.querySelectorAll('.file-item').forEach(e => e.classList.remove('active'));
  el.classList.add('active');
  currentPath = path;
  document.getElementById('currentFile').textContent = path.replace('/root/ros_ws/src/', '');
  const res = await fetch('/api/file?path=' + encodeURIComponent(path));
  const data = await res.json();
  document.getElementById('editor').value = data.content;
  document.getElementById('status').textContent = '';
}

async function saveFile() {
  if (!currentPath) return;
  const content = document.getElementById('editor').value;
  const res = await fetch('/api/file', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({path: currentPath, content})
  });
  const data = await res.json();
  document.getElementById('status').textContent = data.ok ? '✅ Saved!' : '❌ Error';
  setTimeout(() => document.getElementById('status').textContent = '', 2000);
}

async function refreshBuild() {
  document.getElementById('status').textContent = '🔨 Building...';
  const res = await fetch('/api/build', {method: 'POST'});
  const data = await res.json();
  document.getElementById('status').textContent = data.ok ? '✅ Build OK' : '❌ Build Error';
}

async function launchDisplay() {
  const res = await fetch('/api/launch', {method: 'POST'});
  document.getElementById('status').textContent = '🚀 Launched!';
}

loadTree();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tree')
def get_tree():
    def walk(path, depth=0):
        items = []
        if depth > 4:
            return items
        try:
            for name in sorted(os.listdir(path)):
                if name.startswith('.') or name == 'build' or name == '__pycache__':
                    continue
                full = os.path.join(path, name)
                if os.path.isdir(full):
                    items.append({'name': name, 'type': 'dir', 'path': full, 'children': walk(full, depth+1)})
                else:
                    ext = name.split('.')[-1]
                    if ext in ['urdf', 'xacro', 'py', 'xml', 'yaml', 'yml', 'rviz', 'launch', 'md', 'txt']:
                        items.append({'name': name, 'type': 'file', 'path': full})
        except PermissionError:
            pass
        return items
    return jsonify(walk(BASE_DIR))

@app.route('/api/file', methods=['GET'])
def read_file():
    path = request.args.get('path')
    try:
        with open(path, 'r') as f:
            return jsonify({'content': f.read()})
    except Exception as e:
        return jsonify({'content': f'Error: {e}'}), 400

@app.route('/api/file', methods=['POST'])
def write_file():
    data = request.json
    try:
        with open(data['path'], 'w') as f:
            f.write(data['content'])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/build', methods=['POST'])
def build():
    import subprocess
    result = subprocess.run(
        'source /opt/ros/jazzy/setup.bash && cd /root/ros_ws && colcon build --symlink-install',
        shell=True, executable='/bin/bash', capture_output=True, text=True
    )
    return jsonify({'ok': result.returncode == 0, 'output': result.stdout + result.stderr})

@app.route('/api/launch', methods=['POST'])
def launch():
    import subprocess
    subprocess.Popen(
        'source /opt/ros/jazzy/setup.bash && source /root/ros_ws/install/setup.bash && ros2 launch krsti_description robot_description.launch.py',
        shell=True, executable='/bin/bash'
    )
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
