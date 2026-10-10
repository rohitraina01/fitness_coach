// Apex Coach Mobile Web Application

const QUEUE_STORAGE_KEY = "apex_fitness_queue";
const CHECKED_SETS_KEY = "apex_checked_sets";

let isOnline = false;
let dashboardData = null;
let currentRestTimer = null;
let recognition = null;
let isRecording = false;

// 1. Initialization
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initVoice();
  initLogSubmission();
  checkConnection();
  setInterval(checkConnection, 8000); // Poll status every 8s
  renderQueue();
  loadLocalCheckedSets();
});

// 2. Tab Navigation
function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      navBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const tabId = btn.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");

      if (tabId === "tab-progress" && dashboardData) {
        renderCharts(dashboardData);
      }
    });
  });

  // Chip selector on log tab
  const chips = document.querySelectorAll(".btn-chip");
  chips.forEach(c => {
    c.addEventListener("click", () => {
      chips.forEach(chip => chip.classList.remove("active"));
      c.classList.add("active");
    });
  });
}

// 3. Connectivity & Data Fetching
async function checkConnection() {
  const statusBadge = document.getElementById("bridgeStatusBadge");
  const dot = statusBadge.querySelector(".status-dot");
  const text = document.getElementById("statusText");

  try {
    const res = await fetch("/api/status", { cache: "no-store" });
    if (res.ok) {
      isOnline = true;
      dot.className = "status-dot online";
      text.innerText = "PC Online";
      if (!dashboardData) {
        fetchDashboardData();
      }
    } else {
      throw new Error();
    }
  } catch (e) {
    isOnline = false;
    dot.className = "status-dot offline";
    text.innerText = "PC Offline";
  }
}

async function fetchDashboardData() {
  try {
    const res = await fetch("/api/dashboard-data");
    const data = await res.json();
    if (data.success) {
      dashboardData = data;
      renderWorkout(data);
      renderKPIs(data);
      renderCharts(data);
    }
  } catch (e) {
    console.warn("Could not fetch remote dashboard data:", e);
  }
}

// 4. Render Next Workout
const FALLBACK_EXERCISES = [
  { name: "Lat Pulldown (Neutral Grip)", target: "3 sets x 8–10 reps @ 50kg", cue: "Slight torso lean, drive elbows into hip pockets. Full stretch." },
  { name: "Chest-Supported Row", target: "3 sets x 8–10 reps @ 25kg", cue: "Chest glued to pad, elbows 45°, 1s squeeze on retraction." },
  { name: "Straight-Arm Pulldown", target: "3 sets x 12–15 reps @ 15–20kg", cue: "Soft elbows. Arc bar into quads. Lat isolation." },
  { name: "Reverse Pec Deck (Rear Delt)", target: "3 sets x 12–15 reps @ 15kg", cue: "Horizontal abduction. Zero upper trap shrugging." },
  { name: "Standing Cable Bicep Curl", target: "3 sets x 10–12 reps @ 20–22.5kg", cue: "Upper arms vertical by sides. Constant cable tension." },
  { name: "Dumbbell Hammer Curl", target: "3 sets x 8–10 reps @ 7.5kg", cue: "Neutral grip. Builds arm thickness and brachialis." }
];

function renderWorkout(data) {
  const feed = document.getElementById("exerciseFeed");
  feed.innerHTML = "";

  const exercises = FALLBACK_EXERCISES;
  const savedChecks = JSON.parse(localStorage.getItem(CHECKED_SETS_KEY) || "{}");

  exercises.forEach((ex, idx) => {
    const card = document.createElement("div");
    card.className = "ex-card";

    let setsHtml = "";
    for (let s = 1; s <= 3; s++) {
      const checkKey = `ex_${idx}_s_${s}`;
      const isChecked = savedChecks[checkKey] ? "completed" : "";
      setsHtml += `
        <div class="set-check ${isChecked}" data-key="${checkKey}" onclick="toggleSetCheck(this)">
          Set ${s}
        </div>
      `;
    }

    card.innerHTML = `
      <div class="ex-top">
        <div class="ex-title-wrap">
          <span class="ex-num">#${idx + 1}</span>
          <span class="ex-name">${ex.name}</span>
        </div>
        <span class="ex-target-pill">${ex.target}</span>
      </div>
      <p class="ex-cue">${ex.cue}</p>
      <div class="set-row">
        ${setsHtml}
      </div>
    `;
    feed.appendChild(card);
  });
}

function toggleSetCheck(el) {
  const key = el.getAttribute("data-key");
  const savedChecks = JSON.parse(localStorage.getItem(CHECKED_SETS_KEY) || "{}");
  
  if (el.classList.contains("completed")) {
    el.classList.remove("completed");
    delete savedChecks[key];
  } else {
    el.classList.add("completed");
    savedChecks[key] = true;
    if (navigator.vibrate) navigator.vibrate(50);
  }
  localStorage.setItem(CHECKED_SETS_KEY, JSON.stringify(savedChecks));
}

function loadLocalCheckedSets() {
  if (!dashboardData) {
    renderWorkout({});
  }
}

// 5. Rest Timer with Audio & Vibration
function startRest(seconds) {
  clearInterval(currentRestTimer);
  const display = document.getElementById("timerDigits");
  let remaining = seconds;

  const updateDisplay = () => {
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    display.innerText = `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  updateDisplay();
  currentRestTimer = setInterval(() => {
    remaining--;
    if (remaining <= 0) {
      clearInterval(currentRestTimer);
      display.innerText = "DONE!";
      playBuzzer();
      if (navigator.vibrate) navigator.vibrate([200, 100, 200, 100, 400]);
    } else {
      updateDisplay();
    }
  }, 1000);
}

function resetTimer() {
  clearInterval(currentRestTimer);
  document.getElementById("timerDigits").innerText = "00:00";
}

function playBuzzer() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch (e) {}
}

// 6. Posture Hold Timers
function startHoldTimer(seconds, btn) {
  if (btn.classList.contains("running")) return;
  btn.classList.add("running");
  const origText = btn.innerText;
  let rem = seconds;

  const intv = setInterval(() => {
    rem--;
    if (rem <= 0) {
      clearInterval(intv);
      btn.innerText = "Completed!";
      btn.classList.remove("running");
      playBuzzer();
      if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
      setTimeout(() => { btn.innerText = origText; }, 2500);
    } else {
      btn.innerText = `Hold: ${rem}s`;
    }
  }, 1000);
}

// 7. Voice Dictation
function initVoice() {
  const btnVoice = document.getElementById("btnVoice");
  const textarea = document.getElementById("rawLogInput");

  if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
    btnVoice.style.display = "none";
    return;
  }

  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRec();
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    textarea.value += (textarea.value ? "\n" : "") + transcript;
  };

  recognition.onerror = () => {
    btnVoice.classList.remove("recording");
    isRecording = false;
  };

  btnVoice.addEventListener("click", () => {
    if (!isRecording) {
      recognition.start();
      btnVoice.classList.add("recording");
      isRecording = true;
      showToast("🎙️ Listening... Speak your workout");
    } else {
      recognition.stop();
      btnVoice.classList.remove("recording");
      isRecording = false;
      showToast("Speech recognized");
    }
  });
}

// 8. Log Submission & Smart Queue Management
function initLogSubmission() {
  const submitBtn = document.getElementById("btnSubmitLog");
  const textarea = document.getElementById("rawLogInput");

  submitBtn.addEventListener("click", async () => {
    const text = textarea.value.trim();
    if (!text) {
      showToast("Please enter or dictate workout notes first.");
      return;
    }

    const activeChip = document.querySelector(".btn-chip.active");
    const sessionType = activeChip ? activeChip.getAttribute("data-type") : "Push";

    const payload = {
      id: "entry_" + Date.now(),
      created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      date: new Date().toISOString().split("T")[0],
      session_type: sessionType,
      raw_text: text,
      duration: 60
    };

    if (isOnline) {
      submitBtn.disabled = true;
      submitBtn.innerText = "Processing via Antigravity...";
      try {
        const res = await fetch("/api/log-workout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const resJson = await res.json();
        if (resJson.success) {
          showToast("✅ Workout processed & committed to PC!");
          textarea.value = "";
          fetchDashboardData();
        } else {
          throw new Error(resJson.error);
        }
      } catch (e) {
        enqueueWorkout(payload);
        showToast("⚠️ Could not reach PC. Saved to local queue.");
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = "<span>Process Workout</span> ➔";
      }
    } else {
      enqueueWorkout(payload);
      textarea.value = "";
      showToast("⚠️ PC is Offline. Workout saved in queue.");
    }
  });
}

function enqueueWorkout(item) {
  const queue = JSON.parse(localStorage.getItem(QUEUE_STORAGE_KEY) || "[]");
  queue.unshift(item);
  localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
  renderQueue();
}

function renderQueue() {
  const list = document.getElementById("queueList");
  const countSpan = document.getElementById("queueCount");
  const queue = JSON.parse(localStorage.getItem(QUEUE_STORAGE_KEY) || "[]");

  countSpan.innerText = queue.length;
  list.innerHTML = "";

  if (queue.length === 0) {
    list.innerHTML = `<p style="font-size:0.8rem; color:var(--text-dim); text-align:center; padding:12px;">Queue is empty. All workouts synced.</p>`;
    return;
  }

  queue.forEach((item, idx) => {
    const el = document.createElement("div");
    el.className = "queue-item";
    el.innerHTML = `
      <div class="queue-item-meta">
        <strong>${item.session_type} Workout</strong>
        <span>${item.date} • ${item.created_at}</span>
      </div>
      <div class="queue-snippet">${escapeHtml(item.raw_text)}</div>
      <div class="queue-actions">
        <button class="btn-queue-sync" onclick="syncQueueItem(${idx})">Sync to PC ➔</button>
        <button class="btn-queue-discard" onclick="discardQueueItem(${idx})">Discard / Delete</button>
      </div>
    `;
    list.appendChild(el);
  });
}

async function syncQueueItem(index) {
  const queue = JSON.parse(localStorage.getItem(QUEUE_STORAGE_KEY) || "[]");
  const item = queue[index];
  if (!item) return;

  if (!isOnline) {
    showToast("⚠️ PC is still offline. Please check connection.");
    return;
  }

  showToast("Syncing to PC...");
  try {
    const res = await fetch("/api/log-workout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item)
    });
    const resJson = await res.json();
    if (resJson.success) {
      queue.splice(index, 1);
      localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
      renderQueue();
      showToast("✅ Successfully synced to PC records!");
      fetchDashboardData();
    } else {
      showToast("Error syncing item: " + resJson.error);
    }
  } catch (e) {
    showToast("Sync failed: PC bridge disconnected.");
  }
}

function discardQueueItem(index) {
  const queue = JSON.parse(localStorage.getItem(QUEUE_STORAGE_KEY) || "[]");
  if (confirm("Discard this queued workout? (Use this if you already entered it on your PC to avoid duplicate records).")) {
    queue.splice(index, 1);
    localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
    renderQueue();
    showToast("Item discarded.");
  }
}

// 9. KPIs & Canvas Chart Rendering
function renderKPIs(data) {
  if (data.latest_weight) document.getElementById("kpiWeight").innerText = `${data.latest_weight} kg`;
  if (data.avg_protein_30d) document.getElementById("kpiProtein").innerText = `${data.avg_protein_30d} g`;
}

function renderCharts(data) {
  drawWeightChart(data.weight_history || []);
  drawProteinChart(data.nutrition_history || []);
}

function drawWeightChart(history) {
  const canvas = document.getElementById("weightCanvas");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  if (history.length < 2) return;

  const weights = history.map(d => d.weight);
  const minW = Math.min(...weights) - 0.5;
  const maxW = Math.max(...weights) + 0.5;

  const pad = 40;
  const stepX = (w - pad * 2) / (history.length - 1);

  // Draw grid lines
  ctx.strokeStyle = "rgba(255,255,255,0.06)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad + (h - pad * 2) * (i / 4);
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(w - pad, y);
    ctx.stroke();

    const val = (maxW - (maxW - minW) * (i / 4)).toFixed(1);
    ctx.fillStyle = "#64748B";
    ctx.font = "10px sans-serif";
    ctx.fillText(`${val}kg`, 5, y + 3);
  }

  // Draw Line
  ctx.strokeStyle = "#38BDF8";
  ctx.lineWidth = 3;
  ctx.beginPath();

  history.forEach((d, i) => {
    const x = pad + i * stepX;
    const y = pad + (h - pad * 2) * ((maxW - d.weight) / (maxW - minW));
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Draw dots
  history.forEach((d, i) => {
    const x = pad + i * stepX;
    const y = pad + (h - pad * 2) * ((maxW - d.weight) / (maxW - minW));
    ctx.fillStyle = "#38BDF8";
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });
}

function drawProteinChart(history) {
  const canvas = document.getElementById("proteinCanvas");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  if (history.length < 2) return;

  const pad = 40;
  const stepX = (w - pad * 2) / history.length;
  const maxP = 160;

  // Goal line at 150g
  const goalY = pad + (h - pad * 2) * ((maxP - 150) / maxP);
  ctx.strokeStyle = "rgba(52, 211, 153, 0.4)";
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(pad, goalY);
  ctx.lineTo(w - pad, goalY);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "#34D399";
  ctx.font = "10px sans-serif";
  ctx.fillText("Goal 150g", w - pad - 50, goalY - 4);

  // Draw Bars
  history.forEach((d, i) => {
    const prot = d.protein || 0;
    const barH = (h - pad * 2) * (prot / maxP);
    const x = pad + i * stepX + 3;
    const y = h - pad - barH;

    ctx.fillStyle = prot >= 140 ? "#34D399" : (prot < 90 ? "#F87171" : "#38BDF8");
    ctx.fillRect(x, y, stepX - 6, barH);
  });
}

// Toast
function showToast(msg) {
  const t = document.getElementById("toast");
  t.innerText = msg;
  t.classList.add("show");
  setTimeout(() => { t.classList.remove("show"); }, 3000);
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
