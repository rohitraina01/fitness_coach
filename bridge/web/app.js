// Apex Coach Mobile Web Application

const QUEUE_STORAGE_KEY = "apex_fitness_queue";
const CHECKED_SETS_KEY = "apex_checked_sets";
const PIN_STORAGE_KEY = "apex_security_pin";
const PIN_UNLOCKED_KEY = "apex_pin_unlocked";

let isOnline = false;
let dashboardData = null;
let currentRestTimer = null;
let recognition = null;
let isRecording = false;
let isTestMode = false;
let selectedExerciseId = "INCLINE_DB_PRESS";
let enteredPin = "";

// 1. Initialization
document.addEventListener("DOMContentLoaded", () => {
  initSecurityLock();
  initNavigation();
  initVoice();
  initLogSubmission();
  initExerciseChips();
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
      const pane = document.getElementById(tabId);
      if (pane) pane.classList.add("active");

      if (tabId === "tab-progress" && dashboardData) {
        renderProgressTab(dashboardData);
      }
    });
  });

  // Chip selector on log tab
  const chips = document.querySelectorAll(".type-selector .btn-chip");
  chips.forEach(c => {
    c.addEventListener("click", () => {
      chips.forEach(chip => chip.classList.remove("active"));
      c.classList.add("active");
    });
  });
}

// Mode toggle for Live vs Test/Dummy Run
function setEntryMode(isTest) {
  isTestMode = isTest;
  document.getElementById("modeLive").classList.toggle("active", !isTest);
  document.getElementById("modeDummy").classList.toggle("active", isTest);
  
  const banner = document.getElementById("testBanner");
  const submitLabel = document.getElementById("submitLabel");
  if (banner) banner.style.display = isTest ? "block" : "none";
  if (submitLabel) submitLabel.innerText = isTest ? "Simulate Dummy Run" : "Process Workout";
  
  if (isTest) {
    showToast("🧪 Test Mode: Zero database changes will be made.");
  }
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
      renderProgressTab(data);
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
  if (!feed) return;
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
    if (btnVoice) btnVoice.style.display = "none";
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

// 8. Log Submission & Smart Queue Management (With Dummy Mode Support)
function initLogSubmission() {
  const submitBtn = document.getElementById("btnSubmitLog");
  const textarea = document.getElementById("rawLogInput");

  submitBtn.addEventListener("click", async () => {
    const text = textarea.value.trim();
    if (!text) {
      showToast("Please enter or dictate workout notes first.");
      return;
    }

    const activeChip = document.querySelector(".type-selector .btn-chip.active");
    const sessionType = activeChip ? activeChip.getAttribute("data-type") : "Pull";
    const forceDummy = isTestMode || text.toLowerCase().includes("dummy") || text.toLowerCase().includes("test");

    const payload = {
      id: "entry_" + Date.now(),
      created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      date: new Date().toISOString().split("T")[0],
      session_type: sessionType,
      raw_text: text,
      duration: 60,
      is_dummy: forceDummy
    };

    if (isOnline) {
      submitBtn.disabled = true;
      submitBtn.innerText = forceDummy ? "Simulating via Coach..." : "Processing via Antigravity...";
      try {
        const res = await fetch("/api/log-workout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const resJson = await res.json();
        if (resJson.success) {
          if (resJson.dummy) {
            showSimulationResults(resJson.coach_feedback);
            showToast("🧪 DUMMY RUN VERIFIED! Zero database changes.");
          } else {
            showToast("✅ Workout processed & committed to PC!");
            textarea.value = "";
            fetchDashboardData();
          }
        } else {
          throw new Error(resJson.error);
        }
      } catch (e) {
        if (!forceDummy) {
          enqueueWorkout(payload);
          showToast("⚠️ Could not reach PC. Saved to local queue.");
        } else {
          showToast("Error running simulation: " + e.message);
        }
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = forceDummy ? "<span id='submitLabel'>Simulate Dummy Run</span> ➔" : "<span id='submitLabel'>Process Workout</span> ➔";
      }
    } else {
      // PC LOCALHOST IS DEAD / OFF -> DISPATCH TO GITHUB CLOUD
      const ghRepo = localStorage.getItem("apex_gh_repo");
      const ghToken = localStorage.getItem("apex_gh_token");

      if (ghRepo && ghToken && !forceDummy) {
        submitBtn.disabled = true;
        submitBtn.innerText = "Dispatching to Cloud Runner...";
        try {
          const ghRes = await fetch(`https://api.github.com/repos/${ghRepo}/dispatches`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${ghToken}`,
              "Accept": "application/vnd.github.v3+json",
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              event_type: "log_workout",
              client_payload: payload
            })
          });

          if (ghRes.ok || ghRes.status === 204) {
            showToast("⚡ SENT TO GITHUB CLOUD! Cloud runner is executing.");
            textarea.value = "";
          } else {
            throw new Error(`GitHub returned status ${ghRes.status}`);
          }
        } catch (err) {
          enqueueWorkout(payload);
          showToast("⚠️ Cloud dispatch failed. Saved in queue: " + err.message);
        } finally {
          submitBtn.disabled = false;
          submitBtn.innerHTML = "<span id='submitLabel'>Process Workout</span> ➔";
        }
      } else {
        if (!forceDummy) {
          enqueueWorkout(payload);
          textarea.value = "";
          showToast("⚠️ PC is Offline. Saved to queue. (Tap ⚙️ to configure 24/7 Cloud Sync)");
        } else {
          showToast("⚠️ PC is offline; dummy simulations require PC bridge connection.");
        }
      }
    }
  });
}

// Security PIN Lock
function getStoredPin() {
  return localStorage.getItem(PIN_STORAGE_KEY) || "123";
}

function initSecurityLock() {
  const isUnlocked = localStorage.getItem(PIN_UNLOCKED_KEY) === "true";
  const lockScreen = document.getElementById("lockScreen");
  if (lockScreen) {
    lockScreen.style.display = isUnlocked ? "none" : "flex";
  }
  updatePinDots();
}

function updatePinDots() {
  const display = document.getElementById("pinDisplay");
  if (!display) return;
  const targetLen = Math.max(3, getStoredPin().length);
  display.innerHTML = "";
  for (let i = 0; i < targetLen; i++) {
    const dot = document.createElement("span");
    dot.className = "pin-dot" + (i < enteredPin.length ? " filled" : "");
    display.appendChild(dot);
  }
}

function pressPin(digit) {
  if (enteredPin.length < 8) {
    enteredPin += digit;
    updatePinDots();
    if (navigator.vibrate) navigator.vibrate(30);

    const correctPin = getStoredPin();
    if (enteredPin === correctPin) {
      setTimeout(verifyPin, 120);
    } else if (enteredPin.length >= correctPin.length && correctPin.length >= 3) {
      setTimeout(verifyPin, 180);
    }
  }
}

function clearPin() {
  enteredPin = "";
  updatePinDots();
}

function backspacePin() {
  if (enteredPin.length > 0) {
    enteredPin = enteredPin.slice(0, -1);
    updatePinDots();
  }
}

function verifyPin() {
  const correctPin = getStoredPin();
  if (enteredPin === correctPin) {
    localStorage.setItem(PIN_UNLOCKED_KEY, "true");
    const lockScreen = document.getElementById("lockScreen");
    if (lockScreen) {
      lockScreen.style.opacity = "0";
      lockScreen.style.transition = "opacity 0.25s ease";
      setTimeout(() => {
        lockScreen.style.display = "none";
        lockScreen.style.opacity = "1";
      }, 250);
    }
    showToast("🔓 Unlocked. Welcome, Rohit.");
    enteredPin = "";
  } else {
    const keypad = document.querySelector(".pin-keypad");
    if (keypad) {
      keypad.classList.add("shake");
      setTimeout(() => keypad.classList.remove("shake"), 350);
    }
    if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
    showToast("❌ Incorrect PIN. Try again.");
    enteredPin = "";
    updatePinDots();
  }
}

function lockApp() {
  localStorage.removeItem(PIN_UNLOCKED_KEY);
  enteredPin = "";
  updatePinDots();
  const lockScreen = document.getElementById("lockScreen");
  if (lockScreen) lockScreen.style.display = "flex";
  showToast("🔒 System locked.");
}

// Cloud Settings Modal
function openSettingsModal() {
  const modal = document.getElementById("settingsModal");
  const repoInput = document.getElementById("ghRepoInput");
  const tokenInput = document.getElementById("ghTokenInput");
  const pinInput = document.getElementById("appPinInput");

  if (repoInput) repoInput.value = localStorage.getItem("apex_gh_repo") || "";
  if (tokenInput) tokenInput.value = localStorage.getItem("apex_gh_token") || "";
  if (pinInput) pinInput.value = getStoredPin();
  if (modal) modal.style.display = "flex";
}

function closeSettingsModal() {
  const modal = document.getElementById("settingsModal");
  if (modal) modal.style.display = "none";
}

function saveCloudSettings() {
  const repoInput = document.getElementById("ghRepoInput");
  const tokenInput = document.getElementById("ghTokenInput");
  const pinInput = document.getElementById("appPinInput");

  const repo = repoInput ? repoInput.value.trim() : "";
  const token = tokenInput ? tokenInput.value.trim() : "";
  const pin = pinInput ? pinInput.value.trim() : "";

  if (repo) localStorage.setItem("apex_gh_repo", repo);
  else localStorage.removeItem("apex_gh_repo");

  if (token) localStorage.setItem("apex_gh_token", token);
  else localStorage.removeItem("apex_gh_token");

  if (pin && pin.length >= 3) {
    localStorage.setItem(PIN_STORAGE_KEY, pin);
  }

  closeSettingsModal();
  updatePinDots();
  showToast("☁️ Settings & PIN saved!");
}

function showSimulationResults(feedbackText) {
  const card = document.getElementById("simulationCard");
  const body = document.getElementById("simBody");
  if (card && body) {
    body.innerText = feedbackText;
    card.style.display = "block";
    card.scrollIntoView({ behavior: "smooth" });
  }
}

function closeSimulation() {
  const card = document.getElementById("simulationCard");
  if (card) card.style.display = "none";
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

  if (!list || !countSpan) return;
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

// 9. PROGRESS TAB: Muscle Volume & Exercise Trajectories
function initExerciseChips() {
  const chips = document.querySelectorAll(".ex-chip");
  chips.forEach(c => {
    c.addEventListener("click", () => {
      chips.forEach(chip => chip.classList.remove("active"));
      c.classList.add("active");
      selectedExerciseId = c.getAttribute("data-eid");
      if (dashboardData) {
        renderExerciseTrajectory(dashboardData, selectedExerciseId);
      }
    });
  });
}

function renderProgressTab(data) {
  // 1. Trend Summary Cards
  if (data.trend_summary) {
    const rateEl = document.getElementById("trendOverloadRate");
    if (rateEl) rateEl.innerText = data.trend_summary.overload_rate || "85.7%";
  }

  // 2. Muscle Volume List
  if (data.muscle_progress) {
    const list = document.getElementById("muscleVolumeList");
    if (list) {
      list.innerHTML = "";
      data.muscle_progress.forEach(m => {
        const item = document.createElement("div");
        item.className = "mv-item";

        let badgeClass = "optimal";
        if (m.muscle === "Glutes") badgeClass = "locked";
        else if (m.weekly_sets === 0) badgeClass = "prescribed";

        const fillPct = m.muscle === "Glutes" ? 0 : Math.min(100, Math.round((m.weekly_sets / 16) * 100));

        item.innerHTML = `
          <div class="mv-header">
            <span>${m.muscle}</span>
            <span class="mv-status-badge ${badgeClass}">${m.status}</span>
          </div>
          <div class="mv-bar-wrap">
            <div class="mv-bar-fill ${badgeClass}" style="width: ${fillPct}%;"></div>
          </div>
          <div class="mv-sub">
            <span>${m.weekly_sets} sets/wk</span>
            <span>Target: ${m.target_range} (${m.priority})</span>
          </div>
        `;
        list.appendChild(item);
      });
    }
  }

  // 3. Exercise Trajectory Chart
  renderExerciseTrajectory(data, selectedExerciseId);
}

function renderExerciseTrajectory(data, eid) {
  const traj = data.exercise_trajectories ? data.exercise_trajectories[eid] : null;
  if (!traj) return;

  const nameEl = document.getElementById("focusName");
  const verdictEl = document.getElementById("focusVerdict");
  const targetEl = document.getElementById("focusTarget");

  if (nameEl) nameEl.innerText = traj.name;
  if (verdictEl) verdictEl.innerText = traj.progression_verdict;
  if (targetEl) targetEl.innerText = traj.next_target;

  drawExerciseChart(traj);
}

function drawExerciseChart(traj) {
  const canvas = document.getElementById("exerciseTrajectoryCanvas");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const history = traj.history || [];
  if (history.length < 2) return;

  const loads = history.map(d => d.top_load);
  const minL = Math.max(0, Math.min(...loads) - 2.5);
  const maxL = Math.max(...loads) + 2.5;

  const pad = 40;
  const stepX = (w - pad * 2) / (history.length - 1);

  // Grid lines
  ctx.strokeStyle = "rgba(255,255,255,0.06)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad + (h - pad * 2) * (i / 4);
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(w - pad, y);
    ctx.stroke();

    const val = (maxL - (maxL - minL) * (i / 4)).toFixed(1);
    ctx.fillStyle = "#64748B";
    ctx.font = "10px sans-serif";
    ctx.fillText(`${val}kg`, 5, y + 3);
  }

  // Line
  ctx.strokeStyle = "#38BDF8";
  ctx.lineWidth = 3;
  ctx.beginPath();

  history.forEach((d, i) => {
    const x = pad + i * stepX;
    const y = pad + (h - pad * 2) * ((maxL - d.top_load) / (maxL - minL));
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Dots & Rep text
  history.forEach((d, i) => {
    const x = pad + i * stepX;
    const y = pad + (h - pad * 2) * ((maxL - d.top_load) / (maxL - minL));

    ctx.fillStyle = "#38BDF8";
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();

    // Reps label
    ctx.fillStyle = "#F8FAFC";
    ctx.font = "bold 11px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`${d.top_reps} reps`, x, y - 10);

    // Date label at bottom
    ctx.fillStyle = "#94A3B8";
    ctx.font = "9px sans-serif";
    const dateLabel = d.date.slice(5); // e.g. '09-28'
    ctx.fillText(dateLabel, x, h - 12);
  });
}

// Helpers
function showToast(msg) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.innerText = msg;
  t.classList.add("show");
  setTimeout(() => { t.classList.remove("show"); }, 3500);
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
