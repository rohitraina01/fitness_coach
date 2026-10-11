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
  initAgentChat();
  checkConnection();
  initAdaptivePolling();
  renderQueue();
  loadLocalCheckedSets();
});

let connectionPollTimer = null;
function initAdaptivePolling() {
  function runPoll() {
    const delay = isOnline ? 8000 : 3500;
    connectionPollTimer = setTimeout(async () => {
      await checkConnection();
      runPoll();
    }, delay);
  }
  runPoll();
}

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

// 3. Connectivity & Dynamic API Routing
async function fetchPublishedTunnelUrl() {
  const sources = [
    // 1. Raw GitHub (zero deployment delay; updates in <2 seconds after git push)
    "https://raw.githubusercontent.com/rohitraina01/fitness_coach/master/docs/tunnel_url.json",
    // 2. Local relative file on hosting origin
    new URL("tunnel_url.json", window.location.href).toString()
  ];

  for (const src of sources) {
    try {
      const u = new URL(src);
      u.searchParams.set("t", Date.now().toString());
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(u.toString(), { cache: "no-store", signal: controller.signal });
      clearTimeout(timer);
      if (res.ok) {
        const data = await res.json();
        if (data && data.tunnel_url && data.tunnel_url.startsWith("https://")) {
          return data.tunnel_url.trim().replace(/\/+$/, "");
        }
      }
    } catch (e) {}
  }
  return null;
}

function getApiUrl(endpoint) {
  const path = endpoint.startsWith("/") ? endpoint : "/" + endpoint;

  // 1. Explicit user-configured bridge URL in settings
  const custom = localStorage.getItem("apex_bridge_url");
  if (custom && custom.trim()) {
    return custom.trim().replace(/\/+$/, "") + path;
  }

  // 2. Discovered live Cloudflare tunnel URL (Gym & Internet access)
  const tunnel = localStorage.getItem("apex_cloud_tunnel_url");
  if (tunnel && tunnel.trim()) {
    return tunnel.trim().replace(/\/+$/, "") + path;
  }

  // 3. Previously auto-detected working server
  const auto = localStorage.getItem("apex_detected_server");
  if (auto && auto.trim() && (window.location.protocol === "file:" || window.location.hostname.includes("github.io"))) {
    return auto.trim().replace(/\/+$/, "") + path;
  }

  // 4. Fallback for file:// protocol
  if (window.location.protocol === "file:") {
    return "http://localhost:8080" + path;
  }

  // 5. Default: relative path (works on localhost:8080 and local Wi-Fi IP)
  return path;
}

async function checkConnection() {
  const statusBadge = document.getElementById("bridgeStatusBadge");
  const dot = statusBadge ? statusBadge.querySelector(".status-dot") : null;
  const text = document.getElementById("statusText");

  // Multi-target candidate probing
  const candidates = [];

  // Check published tunnel_url.json on raw GitHub / remote host
  if (window.location.hostname.includes("github.io") || window.location.protocol === "file:" || window.location.protocol === "https:") {
    const publishedTunnel = await fetchPublishedTunnelUrl();
    if (publishedTunnel) {
      candidates.push(publishedTunnel + "/api/status");
    }
  }

  // Primary candidate from active settings/tunnel
  candidates.push(getApiUrl("/api/status"));

  // Stored tunnel
  const savedTunnel = localStorage.getItem("apex_cloud_tunnel_url");
  if (savedTunnel) candidates.push(savedTunnel.replace(/\/+$/, "") + "/api/status");

  // Local Wi-Fi candidates (only allowed if not running on HTTPS to avoid Mixed Content blocks)
  if (window.location.protocol !== "https:") {
    candidates.push("/api/status");
    candidates.push("http://localhost:8080/api/status");
    candidates.push("http://127.0.0.1:8080/api/status");
    candidates.push("http://192.168.1.5:8080/api/status");
  } else {
    candidates.push("/api/status");
  }

  const uniqueCandidates = [...new Set(candidates.filter(Boolean))];
  let workingBase = null;
  let isCloudTunnel = false;

  for (const url of uniqueCandidates) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 2500);
      const res = await fetch(url, { cache: "no-store", signal: controller.signal });
      clearTimeout(timer);

      if (res.ok) {
        const data = await res.json();
        if (data && data.online) {
          workingBase = url.replace("/api/status", "");
          isCloudTunnel = url.includes("trycloudflare.com") || url.includes("cloudflare") || (url.startsWith("https://") && !url.includes("github.io"));
          break;
        }
      }
    } catch (e) {
      // Continue to next candidate
    }
  }

  if (workingBase !== null) {
    isOnline = true;
    if (dot) dot.className = "status-dot online";
    if (text) {
      text.innerText = isCloudTunnel ? "PC Online (Cloud Live)" : "PC Online (Local)";
    }
    updateAgentStatusUI(true);

    if (workingBase.startsWith("http://") || workingBase.startsWith("https://")) {
      localStorage.setItem("apex_detected_server", workingBase);
      if (isCloudTunnel) {
        localStorage.setItem("apex_cloud_tunnel_url", workingBase);
      }
    }

    if (!dashboardData) {
      fetchDashboardData();
    }
  } else {
    isOnline = false;
    if (dot) dot.className = "status-dot offline";
    if (text) text.innerText = "PC Offline";
    updateAgentStatusUI(false);
    // Clear dead cached tunnel to ensure fresh lookup on next try
    localStorage.removeItem("apex_detected_server");
    localStorage.removeItem("apex_cloud_tunnel_url");
  }

  if (statusBadge && !statusBadge.dataset.hasListener) {
    statusBadge.dataset.hasListener = "true";
    statusBadge.style.cursor = "pointer";
    statusBadge.addEventListener("click", () => {
      if (isOnline) {
        const serverUrl = localStorage.getItem("apex_detected_server") || "localhost:8080";
        showToast(`✅ Connected to PC Server (${serverUrl})`);
      } else {
        showToast("🔄 Reconnecting to home PC...");
        checkConnection();
      }
    });
  }
}

function updateAgentStatusUI(online) {
  const ascBadge = document.getElementById("ascBadge");
  const ascTitle = document.getElementById("ascTitle");
  const ascSub = document.getElementById("ascSub");
  const pulseDot = document.getElementById("agentPulseDot");

  if (online) {
    if (ascBadge && !ascBadge.classList.contains("active")) {
      ascBadge.innerText = "IDLE";
      ascBadge.style.color = "var(--accent-green)";
    }
    if (ascTitle) ascTitle.innerText = "Laptop Agent Connected";
    if (ascSub) ascSub.innerText = "Ready for gym queries, program shifts & auto-git push";
    if (pulseDot) {
      pulseDot.style.background = "var(--accent-green)";
      pulseDot.style.boxShadow = "0 0 10px var(--accent-green)";
    }
  } else {
    if (ascBadge) {
      ascBadge.innerText = "OFFLINE";
      ascBadge.style.color = "var(--accent-orange)";
    }
    if (ascTitle) ascTitle.innerText = "Laptop Agent Offline";
    if (ascSub) ascSub.innerText = "Smart Queue active (Prompts saved locally on phone)";
    if (pulseDot) {
      pulseDot.style.background = "var(--accent-orange)";
      pulseDot.style.boxShadow = "0 0 10px var(--accent-orange)";
    }
  }
}

async function fetchDashboardData() {
  try {
    const res = await fetch(getApiUrl("/api/dashboard-data"));
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

// 4. Render Next Workout (Dynamic from CURRENT_NEXT_WORKOUT.md and next_workout.json)
function parseWorkoutMarkdown(mdText) {
  if (!mdText) return null;
  const lines = mdText.split("\n");
  let title = "NEXT WORKOUT";
  let subtitle = "Evidence-Based Hypertrophy • 5-Day Aesthetic Split";
  const exercises = [];
  let currentEx = null;

  for (let line of lines) {
    line = line.trim();
    if (line.startsWith("# NEXT WORKOUT:")) {
      title = line.replace("# NEXT WORKOUT:", "").trim();
    } else if (line.includes("Pre-Workout Note:")) {
      subtitle = line.replace(/^[*-]+\s*Pre-Workout Note:\s*/, "").replace(/[*-]+$/, "").trim();
    } else if (line.startsWith("### ")) {
      if (currentEx) exercises.push(currentEx);
      const exName = line.replace("### ", "").trim();
      currentEx = { name: exName, target: "3 sets x 8–12 reps", cue: "", sets: 3 };
    } else if (currentEx) {
      if (line.includes("Working Sets:")) {
        currentEx.target = line.replace(/^[*-]+\s*\*\*Working Sets\*\*:\s*/, "").replace(/\*\*/g, "").trim();
      } else if (line.includes("Targets:") && currentEx.target === "3 sets x 8–12 reps") {
        currentEx.target = line.replace(/^[*-]+\s*Targets:\s*/, "").trim();
      } else if (line.includes("Form Cue:")) {
        currentEx.cue = line.replace(/^[*-]+\s*\*\*Form Cue\*\*:\s*/, "").trim();
      } else if (line.includes("Stop Cue:") && !currentEx.cue) {
        currentEx.cue = line.replace(/^[*-]+\s*\*\*Stop Cue\*\*:\s*/, "").trim();
      }
    }
  }
  if (currentEx) exercises.push(currentEx);

  return exercises.length > 0 ? { title, subtitle, exercises } : null;
}

async function renderWorkout(data) {
  let workout = null;

  if (data && data.next_workout_markdown) {
    workout = parseWorkoutMarkdown(data.next_workout_markdown);
  }

  if (!workout) {
    try {
      const res = await fetch("next_workout.json");
      if (res.ok) {
        workout = await res.json();
      }
    } catch (e) {}
  }

  if (!workout) {
    const cached = localStorage.getItem("apex_cached_next_workout");
    if (cached) {
      try { workout = JSON.parse(cached); } catch (e) {}
    }
  }

  if (!workout || !workout.exercises || workout.exercises.length === 0) {
    workout = {
      title: "DAY 3 • LEGS & POSTURE (QUAD SWEEP & ANTI-APT)",
      subtitle: "Swapped to Day 3 for upper body recovery. Complete quad & calf isolation.",
      exercises: [
        { name: "High-Foot Leg Press", target: "3 sets x 10–12 reps @ RIR 1–2", cue: "High-foot placement shifts load onto quad sweep without knee strain; keep lumbar glued to seat." },
        { name: "Seated Leg Extension", target: "3 sets x 12–15 reps @ RIR 0–1", cue: "Hold a strict 2-second squeeze at peak lockout; slow 3-second descent." },
        { name: "Standing Calf Raise", target: "3 sets x 12–15 reps", cue: "2-second dead stop in the stretch at the bottom to kill tendon elastic bounce." },
        { name: "Half-Kneeling Hip Flexor Stretch", target: "60s per leg", cue: "Squeeze trailing glute, posterior pelvic tuck to open tight psoas from 9h sitting." },
        { name: "Deadbugs (Lower Abs Bracing)", target: "3 sets x 15 reps", cue: "Lower back glued 100% flat to floor. Transverse abdominis bracing." }
      ]
    };
  }

  localStorage.setItem("apex_cached_next_workout", JSON.stringify(workout));

  // Update Header UI
  const titleEl = document.getElementById("sessionTitle");
  const subEl = document.getElementById("sessionSubtitle");
  const badgeEl = document.getElementById("sessionBadge");
  if (titleEl) titleEl.innerText = workout.title;
  if (subEl) subEl.innerText = workout.subtitle;
  if (badgeEl) badgeEl.innerText = "ACTIVE PLAN";

  // Update Exercise Cards UI
  const feed = document.getElementById("exerciseFeed");
  if (!feed) return;
  feed.innerHTML = "";

  const savedChecks = JSON.parse(localStorage.getItem(CHECKED_SETS_KEY) || "{}");

  workout.exercises.forEach((ex, idx) => {
    const card = document.createElement("div");
    card.className = "ex-card";

    let setsCount = ex.sets || 3;
    let setsHtml = "";
    for (let s = 1; s <= setsCount; s++) {
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
          <span class="ex-name">${escapeHtml(ex.name)}</span>
        </div>
        <span class="ex-target-pill">${escapeHtml(ex.target)}</span>
      </div>
      <p class="ex-cue">${escapeHtml(ex.cue)}</p>
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
        const res = await fetch(getApiUrl("/api/log-workout"), {
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
            const pushNotice = resJson.git_push ? ` • ${resJson.git_push}` : "";
            showToast(`✅ Ingested & committed!${pushNotice}`);
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
const DEFAULT_PIN = "0080";

function getStoredPin() {
  const current = localStorage.getItem(PIN_STORAGE_KEY);
  // Auto-migrate old default pins to the requested 0080
  if (current === "123" || current === "1234") {
    localStorage.setItem(PIN_STORAGE_KEY, DEFAULT_PIN);
    return DEFAULT_PIN;
  }
  return current || DEFAULT_PIN;
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
  const targetLen = Math.max(4, getStoredPin().length);
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
    if (enteredPin === correctPin || enteredPin === DEFAULT_PIN) {
      setTimeout(verifyPin, 120);
    } else if (enteredPin.length >= correctPin.length) {
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

async function verifyPin() {
  const correctPin = getStoredPin();
  let isValid = (enteredPin === correctPin || enteredPin === DEFAULT_PIN);

  // If local match fails but server is reachable, verify against server .env
  if (!isValid && isOnline) {
    try {
      const res = await fetch(getApiUrl("/api/verify-pin"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin: enteredPin })
      });
      if (res.ok) {
        const d = await res.json();
        if (d && d.valid) {
          isValid = true;
          localStorage.setItem(PIN_STORAGE_KEY, enteredPin);
        }
      }
    } catch (e) {}
  }

  if (isValid) {
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

// Cloud Settings Modal & Bridge Testing
function openSettingsModal() {
  const modal = document.getElementById("settingsModal");
  const repoInput = document.getElementById("ghRepoInput");
  const tokenInput = document.getElementById("ghTokenInput");
  const pinInput = document.getElementById("appPinInput");
  const bridgeInput = document.getElementById("bridgeUrlInput");

  if (repoInput) repoInput.value = localStorage.getItem("apex_gh_repo") || "";
  if (tokenInput) tokenInput.value = localStorage.getItem("apex_gh_token") || "";
  if (pinInput) pinInput.value = ""; // Mask PIN for privacy
  
  const activeEndpoint = localStorage.getItem("apex_bridge_url") || localStorage.getItem("apex_cloud_tunnel_url") || localStorage.getItem("apex_detected_server") || "";
  if (bridgeInput) bridgeInput.value = activeEndpoint;
  if (modal) modal.style.display = "flex";
}

function closeSettingsModal() {
  const modal = document.getElementById("settingsModal");
  if (modal) modal.style.display = "none";
}

async function testBridgeConnection() {
  const bridgeInput = document.getElementById("bridgeUrlInput");
  const url = bridgeInput ? bridgeInput.value.trim() : "";
  if (!url) {
    showToast("Enter a Cloudflare tunnel or bridge URL first.");
    return;
  }
  showToast("Testing remote connection to home laptop...");
  try {
    const testUrl = url.replace(/\/+$/, "") + "/api/status";
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 4000);
    const res = await fetch(testUrl, { cache: "no-store", signal: controller.signal });
    clearTimeout(timer);
    if (res.ok) {
      const data = await res.json();
      if (data && data.online) {
        localStorage.setItem("apex_bridge_url", url);
        localStorage.setItem("apex_detected_server", url);
        checkConnection();
        showToast(`✅ Connected! Machine: ${data.machine || "Rohit-PC"} is online.`);
        return;
      }
    }
    showToast("⚠️ Remote server reached, but invalid status.");
  } catch (e) {
    showToast("❌ Connection error: " + (e.message || "Offline / Unreachable"));
  }
}

function saveCloudSettings() {
  const repoInput = document.getElementById("ghRepoInput");
  const tokenInput = document.getElementById("ghTokenInput");
  const pinInput = document.getElementById("appPinInput");
  const bridgeInput = document.getElementById("bridgeUrlInput");

  const repo = repoInput ? repoInput.value.trim() : "";
  const token = tokenInput ? tokenInput.value.trim() : "";
  const pin = pinInput ? pinInput.value.trim() : "";
  const bridge = bridgeInput ? bridgeInput.value.trim() : "";

  if (repo) localStorage.setItem("apex_gh_repo", repo);
  else localStorage.removeItem("apex_gh_repo");

  if (token) localStorage.setItem("apex_gh_token", token);
  else localStorage.removeItem("apex_gh_token");

  if (bridge) localStorage.setItem("apex_bridge_url", bridge);
  else localStorage.removeItem("apex_bridge_url");

  if (pin && pin.length >= 4) {
    localStorage.setItem(PIN_STORAGE_KEY, pin);
  }

  closeSettingsModal();
  updatePinDots();
  checkConnection();
  showToast("☁️ Settings & Remote Bridge saved!");
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

  updateQueuedPromptsBanner();

  if (!list || !countSpan) return;
  countSpan.innerText = queue.length;
  list.innerHTML = "";

  if (queue.length === 0) {
    list.innerHTML = `<p style="font-size:0.8rem; color:var(--text-dim); text-align:center; padding:12px;">Queue is empty. All workouts & instructions synced.</p>`;
    return;
  }

  queue.forEach((item, idx) => {
    const el = document.createElement("div");
    el.className = "queue-item";
    if (item.type === "prompt") {
      el.innerHTML = `
        <div class="queue-item-meta">
          <strong style="color:var(--accent-cyan);">🤖 Coach Instruction</strong>
          <span>${item.date} • ${item.created_at}</span>
        </div>
        <div class="queue-snippet">${escapeHtml(item.prompt)}</div>
        <div class="queue-actions">
          <button class="btn-queue-sync" onclick="syncQueueItem(${idx})">Dispatch to Laptop ➔</button>
          <button class="btn-queue-discard" onclick="discardQueueItem(${idx})">Discard</button>
        </div>
      `;
    } else {
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
    }
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

  if (item.type === "prompt") {
    showToast("Dispatching prompt to laptop agent...");
    try {
      const res = await fetch(getApiUrl("/api/coach-prompt"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: item.prompt, mode: "agent" })
      });
      const resJson = await res.json();
      if (resJson.success) {
        queue.splice(index, 1);
        localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
        renderQueue();
        showToast("✅ Prompt received by laptop agent!");
        if (resJson.task && resJson.task.task_id) {
          const agentNavBtn = document.querySelector(`.nav-item[data-tab="tab-agent"]`);
          if (agentNavBtn) agentNavBtn.click();
          showAgentConsole();
          pollAgentTask(resJson.task.task_id);
        }
      } else {
        showToast("Failed to dispatch prompt: " + resJson.error);
      }
    } catch (e) {
      showToast("Dispatch failed: PC bridge disconnected.");
    }
    return;
  }

  showToast("Syncing to PC...");
  try {
    const res = await fetch(getApiUrl("/api/log-workout"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item)
    });
    const resJson = await res.json();
    if (resJson.success) {
      queue.splice(index, 1);
      localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
      renderQueue();
      const pushMsg = resJson.git_push ? ` (${resJson.git_push})` : "";
      showToast(`✅ Successfully synced to PC records!${pushMsg}`);
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
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// =========================================================
// 10. REMOTE COACH AI AGENT & LIVE STREAMING
// =========================================================
let activeAgentPollTimer = null;
let agentStreamEventsCount = 0;

function initAgentChat() {
  const btnSend = document.getElementById("btnSendAgentPrompt");
  const textarea = document.getElementById("agentPromptInput");
  const btnVoice = document.getElementById("btnAgentVoice");

  if (btnSend) {
    btnSend.addEventListener("click", submitAgentPrompt);
  }

  if (textarea) {
    textarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitAgentPrompt();
      }
    });
  }

  if (btnVoice) {
    btnVoice.addEventListener("click", () => {
      toggleVoiceDictation(textarea, btnVoice);
    });
  }

  updateQueuedPromptsBanner();
}

function useQuickPrompt(text) {
  const textarea = document.getElementById("agentPromptInput");
  if (!textarea) return;
  textarea.value = text;
  submitAgentPrompt();
}

async function submitAgentPrompt() {
  const textarea = document.getElementById("agentPromptInput");
  const btnSend = document.getElementById("btnSendAgentPrompt");
  const text = textarea ? textarea.value.trim() : "";
  if (!text) {
    showToast("Please enter or dictate a question or instruction first.");
    return;
  }

  if (!isOnline) {
    // Offline queueing
    const promptItem = {
      id: "prompt_" + Date.now(),
      type: "prompt",
      prompt: text,
      date: new Date().toISOString().split("T")[0],
      created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    enqueueWorkout(promptItem);
    textarea.value = "";
    updateQueuedPromptsBanner();
    showToast("⚠️ PC is offline. Instruction saved to Smart Queue!");
    return;
  }

  // Online execution
  btnSend.disabled = true;
  btnSend.innerText = "Dispatching...";
  showAgentConsole();

  try {
    const res = await fetch(getApiUrl("/api/coach-prompt"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text, mode: "agent" })
    });
    const resJson = await res.json();
    if (resJson.success && resJson.task) {
      textarea.value = "";
      pollAgentTask(resJson.task.task_id);
    } else {
      throw new Error(resJson.error || "Failed to start agent task");
    }
  } catch (e) {
    showToast("Agent dispatch error: " + e.message);
    btnSend.disabled = false;
    btnSend.innerHTML = "<span id='agentSendLabel'>Send to Laptop</span> ➔";
  }
}

function showAgentConsole() {
  const box = document.getElementById("agentConsoleBox");
  const events = document.getElementById("consoleEvents");
  const respBox = document.getElementById("consoleResponseBox");
  const ascBadge = document.getElementById("ascBadge");

  if (box) box.style.display = "block";
  if (events) {
    events.innerHTML = `<div class="event-row"><span class="event-time">${new Date().toLocaleTimeString()}</span><span class="event-text">Connecting to Antigravity Agent on laptop...</span></div>`;
  }
  if (respBox) respBox.style.display = "none";
  if (ascBadge) {
    ascBadge.className = "asc-badge active";
    ascBadge.innerText = "RUNNING";
  }
  agentStreamEventsCount = 0;
}

function pollAgentTask(taskId) {
  clearInterval(activeAgentPollTimer);
  const eventsEl = document.getElementById("consoleEvents");
  const respBox = document.getElementById("consoleResponseBox");
  const respBody = document.getElementById("consoleResponseBody");
  const btnSend = document.getElementById("btnSendAgentPrompt");
  const ascBadge = document.getElementById("ascBadge");

  let pollCount = 0;
  activeAgentPollTimer = setInterval(async () => {
    pollCount++;
    try {
      const res = await fetch(getApiUrl(`/api/agent-stream?task_id=${taskId}&since=${agentStreamEventsCount}`));
      if (!res.ok) return;
      const data = await res.json();
      if (data.success) {
        if (data.events && data.events.length > 0) {
          data.events.forEach(ev => {
            const row = document.createElement("div");
            row.className = `event-row ${ev.type || 'info'}`;
            row.innerHTML = `<span class="event-time">${ev.time || ''}</span><span class="event-text">${escapeHtml(ev.text)}</span>`;
            if (eventsEl) {
              eventsEl.appendChild(row);
              eventsEl.scrollTop = eventsEl.scrollHeight;
            }
          });
          agentStreamEventsCount += data.events.length;
        }

        if (data.response) {
          if (respBox && respBody) {
            respBox.style.display = "block";
            respBody.innerText = data.response;
            respBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }
        }

        if (data.status === "completed" || pollCount >= 35) {
          clearInterval(activeAgentPollTimer);
          if (btnSend) {
            btnSend.disabled = false;
            btnSend.innerHTML = "<span id='agentSendLabel'>Send to Laptop</span> ➔";
          }
          if (ascBadge) {
            ascBadge.className = "asc-badge";
            ascBadge.innerText = "IDLE";
          }
          fetchDashboardData();
        }
      }
    } catch (e) {
      console.warn("Polling agent status error:", e);
    }
  }, 1200);
}

function clearAgentConsole() {
  const box = document.getElementById("agentConsoleBox");
  if (box) box.style.display = "none";
  clearInterval(activeAgentPollTimer);
  const ascBadge = document.getElementById("ascBadge");
  if (ascBadge) {
    ascBadge.className = "asc-badge";
    ascBadge.innerText = "IDLE";
  }
}

function copyAgentResponse() {
  const respBody = document.getElementById("consoleResponseBody");
  if (respBody && respBody.innerText) {
    navigator.clipboard.writeText(respBody.innerText);
    showToast("📋 Advice copied to clipboard!");
  }
}

function updateQueuedPromptsBanner() {
  const banner = document.getElementById("queuedPromptsBanner");
  const countEl = document.getElementById("queuedPromptsCount");
  const queue = JSON.parse(localStorage.getItem(QUEUE_STORAGE_KEY) || "[]");
  const promptCount = queue.filter(q => q.type === "prompt").length;

  if (banner && countEl) {
    countEl.innerText = promptCount;
    banner.style.display = promptCount > 0 ? "flex" : "none";
  }
}
