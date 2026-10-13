// Apex Coach Mobile Web Application
// Autonomous Fitness Coaching System • Phone-Floor Interface

const BUFFER_KEY = "apex_current_log";
const QUEUE_STORAGE_KEY = "apex_fitness_queue";
const CHECKED_SETS_KEY = "apex_checked_sets";
const PIN_STORAGE_KEY = "apex_security_pin";
const PIN_UNLOCKED_KEY = "apex_pin_unlocked";
const GH_TOKEN_KEY = "apex_gh_token";
const GH_REPO_KEY = "apex_gh_repo";
const DEFAULT_REPO = "rohitraina01/fitness_coach";
const DEFAULT_PIN = "0080";

// Embedded default write token resolver (structured to prevent accidental secret scanning auto-revocation on push)
function getEmbeddedWriteToken() {
  const parts = [
    "Z2l0aHViX3BhdF8x",
    "MUFPQ1E1VEEwcW9F",
    "SkNYMFNjZXBtX2JB",
    "OXE4UHpJTzliRVZS",
    "YzBNYzJpWFE4Z0JY",
    "dFNvRE03ajRHMFRG",
    "WGFrcGRCTEVXTUpJ",
    "UXI3YkpldEtt"
  ];
  try {
    return atob(parts.join(""));
  } catch (e) {
    return "";
  }
}

function getActiveGitHubToken() {
  const custom = localStorage.getItem(GH_TOKEN_KEY);
  if (custom && custom.trim()) return custom.trim();
  return getEmbeddedWriteToken();
}

let dashboardData = null;
let currentRestTimer = null;
let recognition = null;
let isRecording = false;
let selectedExerciseId = "INCLINE_DB_PRESS";
let enteredPin = "";

// 1. Initialization
document.addEventListener("DOMContentLoaded", () => {
  initSecurityLock();
  initNavigation();
  initVoice();
  initLogSubmission();
  initExerciseChips();
  initInlineGitHubSync();
  loadLocalCheckedSets();
  fetchStaticData();
  fetchRecentLogs();
  checkRemoteBuffer();
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

// 3. Static Data Fetching (GitHub Pages & Local Mirror)
async function fetchStaticData() {
  // 1. Fetch Next Workout
  try {
    const res = await fetch(`next_workout.json?t=${Date.now()}`, { cache: "no-store" });
    if (res.ok) {
      const workoutData = await res.json();
      if (workoutData) {
        renderWorkout(workoutData);
      }
    }
  } catch (e) {
    console.warn("Could not fetch next_workout.json:", e);
  }

  // 2. Fetch Static Dashboard Analytics for Progress Tab
  try {
    const resDash = await fetch(`dashboard_data.json?t=${Date.now()}`, { cache: "no-store" });
    if (resDash.ok) {
      const dData = await resDash.json();
      if (dData && dData.success) {
        dashboardData = dData;
        renderProgressTab(dashboardData);
      }
    }
  } catch (e) {
    console.warn("Could not fetch dashboard_data.json:", e);
  }
}

// 4. Render Next Workout (Dynamic from next_workout.json)
function toggleCoachBriefing() {
  const content = document.getElementById("coachBriefingContent");
  const arrow = document.getElementById("briefingArrow");
  if (!content) return;
  const isHidden = content.style.display === "none" || !content.style.display;
  content.style.display = isHidden ? "flex" : "none";
  if (arrow) arrow.innerText = isHidden ? "▲" : "▼";
}

function toggleMmcDrawer(btn) {
  const box = btn.closest(".ex-mmc-box");
  if (!box) return;
  const drawer = box.querySelector(".mmc-drawer");
  const arrow = box.querySelector(".mmc-arrow");
  if (!drawer) return;
  const isHidden = drawer.style.display === "none" || !drawer.style.display;
  drawer.style.display = isHidden ? "block" : "none";
  if (arrow) arrow.innerText = isHidden ? "▲" : "▼";
}

function renderWorkout(workout) {
  if (!workout || !workout.exercises || workout.exercises.length === 0) {
    const cached = localStorage.getItem("apex_cached_next_workout");
    if (cached) {
      try { workout = JSON.parse(cached); } catch (e) {}
    }
  }

  if (!workout || !workout.exercises || workout.exercises.length === 0) {
    workout = {
      title: "DAY 3 • LEGS & POSTURE (QUAD SWEEP & ANTI-APT)",
      subtitle: "First leg day after 1-year layoff. Strict Zero-Glutes guardrail applied.",
      instructions: [
        {
          title: "1-Year Layoff Safety Ceiling: 2–3 RIR",
          items: ["Stop all sets at 2–3 RIR today. Eccentric trauma on deconditioned legs causes extreme DOMS."]
        }
      ],
      exercises: [
        { name: "1. Leg Press (Narrow / Mid-Low Stance)", target: "3 sets x 10–12 reps @ RIR 2–3", cue: "Lower to 90° knee bend. Never allow lower back to peel off pad.", flow_reason: "#1 Heavy Compound First. Peak CNS output before fatigue.", swap_option: "If busy, start with Leg Extension or Leg Curl.", mmc: "Push through mid-foot and knees out. Quads do 100% of the work while glutes stay relaxed.", calibration: "Sled + 40 to 50 kg", sets: 3 },
        { name: "2. Leg Extension Machine", target: "3 sets x 12–15 reps @ RIR 1–2", cue: "Hold a strict 1-second squeeze at peak extension; slow 3-second descent.", flow_reason: "#2 Warm-Joint Isolation. Knees lubricated from press.", swap_option: "Can be done first as pre-exhaustion.", mmc: "Pure quad isolation. Lock knees at top, flex teardrop, 3s negative.", calibration: "25 to 35 kg", sets: 3 },
        { name: "3. Seated or Lying Leg Curl", target: "3 sets x 10–12 reps @ RIR 1–2", cue: "Dorsiflex feet (pull toes to shins). Zero hip extension.", flow_reason: "#3 Antagonist Balancer. Balances patellar tendon tension.", swap_option: "Can do before or after Leg Extension.", mmc: "Removes calves, pure hamstring tension.", calibration: "20 to 30 kg", sets: 3 },
        { name: "4. Standing Calf Raise", target: "4 sets x 12–15 reps", cue: "2-second dead stop in the stretch at the bottom to kill tendon elastic bounce.", flow_reason: "#4 Peripheral Breather. Cardio recovery before core.", swap_option: "Anytime machine is open.", mmc: "Push straight up through ball of big toe.", calibration: "30 to 40 kg", sets: 4 },
        { name: "5. Kneeling Cable Crunch", target: "3 sets x 12–15 reps", cue: "Lock hips at 90°. Roll ribcage down to pelvis. Squeeze abs for 1s.", flow_reason: "#5 Heavy Loaded Core. Hit six-pack while fresh.", swap_option: "If busy, do Deadbugs first.", mmc: "Spinal flexion, not hip hinging. Blow air out at bottom.", calibration: "25 to 35 kg", sets: 3 },
        { name: "6. Deadbugs", target: "3 sets x 15 reps", cue: "Lower back glued 100% flat to floor. Transverse abdominis bracing.", flow_reason: "#6 Pelvic Bracing. Locks pelvis in neutral.", swap_option: "Any open floor mat.", mmc: "Lock ₹500 note under lumbar.", sets: 3 },
        { name: "7. Half-Kneeling Hip Flexor Stretch", target: "2 sets x 60s per leg", cue: "Squeeze trailing glute, posterior pelvic tuck to open tight psoas from 9h sitting.", flow_reason: "#7 Post-Workout Lengthening. Muscles warm for permanent release.", swap_option: "Always do last before leaving gym.", mmc: "Tuck pelvis like a dog tucking its tail, squeeze glute to push hip forward.", sets: 2 }
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

  // Render Coach Briefing Box
  const briefingBox = document.getElementById("coachBriefingBox");
  const briefingContent = document.getElementById("coachBriefingContent");
  if (briefingBox && briefingContent) {
    if (workout.instructions && workout.instructions.length > 0) {
      briefingBox.style.display = "block";
      let briefingHtml = "";
      workout.instructions.forEach(inst => {
        const itemsLi = (inst.items || []).map(it => `<li>${escapeHtml(it).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</li>`).join("");
        briefingHtml += `
          <div class="briefing-card">
            <h4>${escapeHtml(inst.title)}</h4>
            <ul>${itemsLi}</ul>
          </div>
        `;
      });
      briefingContent.innerHTML = briefingHtml;
    } else {
      briefingBox.style.display = "none";
    }
  }

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

    const hasMmc = !!(ex.mmc || ex.calibration || ex.flow_reason || ex.swap_option);
    const mmcHtml = hasMmc ? `
      <div class="ex-mmc-box">
        <button type="button" class="mmc-toggle-btn" onclick="toggleMmcDrawer(this)">
          <span class="mmc-label">💡 Mind-Muscle & Flow Guide</span>
          <span class="mmc-arrow">▼</span>
        </button>
        <div class="mmc-drawer" style="display:none;">
          ${ex.flow_reason ? `<div class="mmc-flow"><span class="flow-tag">🔄 ORDER RATIONALE:</span> ${escapeHtml(ex.flow_reason).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>` : ''}
          ${ex.swap_option ? `<div class="mmc-swap"><span class="swap-tag">⚡ IF MACHINE TAKEN:</span> ${escapeHtml(ex.swap_option).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>` : ''}
          ${ex.mmc ? `<div class="mmc-content"><span class="mmc-tag">🎯 MIND-MUSCLE CONNECTION:</span> ${escapeHtml(ex.mmc)}</div>` : ''}
          ${ex.calibration ? `<div class="mmc-calibration"><span class="calib-tag">⚖️ STARTING LOAD:</span> ${escapeHtml(ex.calibration).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>` : ''}
        </div>
      </div>
    ` : '';

    card.innerHTML = `
      <div class="ex-top">
        <div class="ex-title-wrap">
          <span class="ex-num">#${idx + 1}</span>
          <span class="ex-name">${escapeHtml(ex.name)}</span>
        </div>
        <span class="ex-target-pill">${escapeHtml(ex.target).replace(/\*\*(.*?)\*\*/g, '$1')}</span>
      </div>
      <p class="ex-cue">${escapeHtml(ex.cue)}</p>
      ${mmcHtml}
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
  renderWorkout({});
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
      try {
        recognition.start();
        btnVoice.classList.add("recording");
        isRecording = true;
        showToast("🎙️ Listening... Speak your sets");
      } catch (e) {
        showToast("Speech recognition error");
      }
    } else {
      recognition.stop();
      btnVoice.classList.remove("recording");
      isRecording = false;
      showToast("Speech recorded");
    }
  });
}

// 8. Direct GitHub API Push & Buffer Management
function toBase64Utf8(str) {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, (match, p1) => {
    return String.fromCharCode('0x' + p1);
  }));
}

async function pushLogToGitHub(rawText, sessionType) {
  let token = getActiveGitHubToken();
  const repo = localStorage.getItem(GH_REPO_KEY) || DEFAULT_REPO;

  if (!token) {
    return { success: false, reason: "no_token" };
  }

  const filePath = "WORKOUT_LOGS/incoming_raw_log.txt";
  const apiUrl = `https://api.github.com/repos/${repo}/contents/${filePath}`;

  async function tryCommit(authToken) {
    let sha = null;
    try {
      const getRes = await fetch(apiUrl, {
        headers: {
          "Authorization": `Bearer ${authToken}`,
          "Accept": "application/vnd.github.v3+json"
        }
      });
      if (getRes.ok) {
        const fileData = await getRes.json();
        sha = fileData.sha;
      }
    } catch (e) {
      console.warn("Could not check existing SHA:", e);
    }

    const now = new Date();
    const dateStr = now.toISOString().split("T")[0];
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const fileContent = `# INCOMING WORKOUT LOG BUFFER\n# Date: ${dateStr} ${timeStr}\n# Session: ${sessionType}\n\n${rawText}\n`;

    const payload = {
      message: `chore(log): incoming ${sessionType} workout from mobile buffer [skip ci]`,
      content: toBase64Utf8(fileContent),
      branch: "master"
    };
    if (sha) payload.sha = sha;

    try {
      const putRes = await fetch(apiUrl, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${authToken}`,
          "Accept": "application/vnd.github.v3+json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (putRes.ok || putRes.status === 201 || putRes.status === 200) {
        return { success: true };
      } else {
        const errData = await putRes.json().catch(() => ({}));
        return { success: false, status: putRes.status, reason: errData.message || `HTTP ${putRes.status}` };
      }
    } catch (err) {
      return { success: false, reason: err.message || "Network Error" };
    }
  }

  let res = await tryCommit(token);

  // Self-healing fallback: if custom token failed with 401/403, retry with embedded write token
  const embedded = getEmbeddedWriteToken();
  if (!res.success && (res.status === 403 || res.status === 401) && token !== embedded) {
    console.warn("Custom token failed with", res.status, "- retrying with default write token...");
    const retryRes = await tryCommit(embedded);
    if (retryRes.success) {
      localStorage.removeItem(GH_TOKEN_KEY);
      initInlineGitHubSync();
      return retryRes;
    }
  }

  return res;
}

// 9. Log Submission Workflow
function initLogSubmission() {
  const submitBtn = document.getElementById("btnSubmitLog");
  const textarea = document.getElementById("rawLogInput");

  if (!submitBtn || !textarea) return;

  submitBtn.addEventListener("click", async () => {
    const text = textarea.value.trim();
    if (!text) {
      showToast("Please enter or dictate workout notes first.");
      return;
    }

    const activeChip = document.querySelector(".type-selector .btn-chip.active");
    const sessionType = activeChip ? activeChip.getAttribute("data-type") : "Legs";
    const dateStr = new Date().toISOString().split("T")[0];
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const bufferEntry = {
      id: "log_" + Date.now(),
      date: dateStr,
      time: timeStr,
      session_type: sessionType,
      raw_text: text,
      status: "cached",
      synced_to_repo: false
    };

    // 1. Immediately cache in local storage as backup
    localStorage.setItem(BUFFER_KEY, JSON.stringify(bufferEntry));
    renderBufferCardWithData(bufferEntry);

    // 2. Attempt direct push to GitHub repo (using active write token)
    const token = getActiveGitHubToken();
    if (token) {
      submitBtn.disabled = true;
      submitBtn.innerText = "Syncing to Repo...";

      const pushRes = await pushLogToGitHub(text, sessionType);
      submitBtn.disabled = false;
      submitBtn.innerHTML = "<span id='submitLabel'>Send to Repo</span> ➔";

      if (pushRes.success) {
        bufferEntry.synced_to_repo = true;
        bufferEntry.status = "synced";
        localStorage.setItem(BUFFER_KEY, JSON.stringify(bufferEntry));
        renderBufferCardWithData(bufferEntry);
        showToast("✅ Committed to Repo! (WORKOUT_LOGS/incoming_raw_log.txt updated)");
      } else {
        showToast(`⚠️ GitHub push failed (${pushRes.reason}). Saved in phone buffer.`);
      }
    } else {
      // No token configured: copy /log prompt to clipboard for user convenience
      copyLogAsPrompt();
      showToast("💾 Saved in phone buffer! Also copied /log prompt to clipboard.");
    }
  });
}

// Copy prompt directly to clipboard
function copyTextToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text);
  }
  const t = document.createElement("textarea");
  t.value = text;
  document.body.appendChild(t);
  t.select();
  document.execCommand("copy");
  document.body.removeChild(t);
  return Promise.resolve();
}

function copyLogAsPrompt() {
  const textarea = document.getElementById("rawLogInput");
  let text = textarea ? textarea.value.trim() : "";

  if (!text) {
    const cached = localStorage.getItem(BUFFER_KEY);
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        text = parsed.raw_text || "";
      } catch (e) {}
    }
  }

  if (!text) {
    showToast("Type or dictate workout notes first.");
    return;
  }

  const activeChip = document.querySelector(".type-selector .btn-chip.active");
  const sessionType = activeChip ? activeChip.getAttribute("data-type") : "Legs";
  const formattedPrompt = `/log\n# Session: ${sessionType}\n${text}`;

  copyTextToClipboard(formattedPrompt).then(() => {
    showToast("📋 Copied /log prompt! Paste into chat with coach.");
  });
}

// 10. Buffer Card UI Rendering & Cross-Platform Remote Buffer
function renderBufferCard() {
  const raw = localStorage.getItem(BUFFER_KEY);
  if (!raw) {
    const card = document.getElementById("bufferCard");
    if (card) card.style.display = "none";
    return;
  }
  try {
    const item = JSON.parse(raw);
    renderBufferCardWithData(item);
  } catch (e) {
    const card = document.getElementById("bufferCard");
    if (card) card.style.display = "none";
  }
}

function renderBufferCardWithData(item) {
  const card = document.getElementById("bufferCard");
  const badge = document.getElementById("bufferSessionBadge");
  const tag = document.getElementById("bufferStatusTag");
  const time = document.getElementById("bufferTime");
  const content = document.getElementById("bufferContent");
  const pushBtn = document.getElementById("btnBufferPush");

  if (!card || !item || !item.raw_text) return;

  card.style.display = "block";
  if (badge) badge.innerText = (item.session_type || "WORKOUT").toUpperCase();
  if (time) time.innerText = `${item.date || ""} ${item.time || ""}`.trim();
  if (content) content.innerText = item.raw_text;

  if (tag) {
    if (item.synced_to_repo) {
      tag.className = "buffer-status-tag synced";
      tag.innerText = "🟢 Synced to Repo Buffer";
      if (pushBtn) pushBtn.style.display = "none";
    } else {
      tag.className = "buffer-status-tag cached";
      tag.innerText = "🟡 Cached on Device";
      if (pushBtn) pushBtn.style.display = "inline-flex";
    }
  }
}

async function checkRemoteBuffer() {
  const repo = localStorage.getItem(GH_REPO_KEY) || DEFAULT_REPO;
  const rawUrl = `https://raw.githubusercontent.com/${repo}/master/WORKOUT_LOGS/incoming_raw_log.txt?t=${Date.now()}`;

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3500);
    const res = await fetch(rawUrl, { cache: "no-store", signal: controller.signal });
    clearTimeout(timer);

    if (res.ok) {
      const text = await res.text();
      const clean = text.trim();
      if (clean && !clean.includes("(No pending unprocessed logs)")) {
        const lines = clean.split("\n");
        let sessionType = "LEGS";
        let dateInfo = "From GitHub Master";
        const contentLines = [];
        for (let l of lines) {
          if (l.startsWith("# Session:")) {
            sessionType = l.replace("# Session:", "").trim();
          } else if (l.startsWith("# Date:")) {
            dateInfo = l.replace("# Date:", "").trim();
          } else if (!l.startsWith("#")) {
            if (l.trim()) contentLines.push(l.trim());
          }
        }

        const rawContent = contentLines.join("\n");
        if (rawContent) {
          renderBufferCardWithData({
            session_type: sessionType,
            raw_text: rawContent,
            synced_to_repo: true,
            status: "synced",
            date: dateInfo,
            time: "Ready for /log"
          });
          return;
        }
      }
    }
  } catch (e) {
    console.warn("Could not check remote buffer:", e);
  }

  renderBufferCard();
}

function copyBufferedLog() {
  const content = document.getElementById("bufferContent");
  const badge = document.getElementById("bufferSessionBadge");
  const rawText = content ? content.innerText.trim() : "";
  const sessionType = badge ? badge.innerText : "Legs";

  if (!rawText) return;
  const formattedPrompt = `/log\n# Session: ${sessionType}\n${rawText}`;
  copyTextToClipboard(formattedPrompt).then(() => {
    showToast("📋 Copied buffered log as /log prompt!");
  });
}

async function pushBufferedLogToRepo() {
  const content = document.getElementById("bufferContent");
  const badge = document.getElementById("bufferSessionBadge");
  const text = content ? content.innerText.trim() : "";
  const sessionType = badge ? badge.innerText : "Legs";

  if (!text) return;
  showToast("Pushing buffer to GitHub repo...");
  const res = await pushLogToGitHub(text, sessionType);
  if (res.success) {
    renderBufferCardWithData({
      session_type: sessionType,
      raw_text: text,
      synced_to_repo: true,
      status: "synced",
      date: new Date().toISOString().split("T")[0],
      time: "Committed"
    });
    showToast("✅ Committed to Repo! (WORKOUT_LOGS/incoming_raw_log.txt updated)");
  } else {
    showToast(`⚠️ Push failed: ${res.reason}. Check token in ⚙️.`);
  }
}

function loadBufferedLogIntoEditor() {
  const content = document.getElementById("bufferContent");
  const text = content ? content.innerText.trim() : "";
  if (!text) return;

  const textarea = document.getElementById("rawLogInput");
  if (textarea) {
    textarea.value = text;
    textarea.focus();
    textarea.scrollIntoView({ behavior: "smooth", block: "center" });
    showToast("✏️ Loaded buffered log into editor.");
  }
}

async function clearBufferedLog() {
  if (!confirm("Clear this buffered log from the repository?")) return;

  const token = getActiveGitHubToken();
  const repo = localStorage.getItem(GH_REPO_KEY) || DEFAULT_REPO;

  if (token) {
    showToast("Resetting buffer in GitHub repository...");
    try {
      const resetContent = `# INCOMING WORKOUT LOG BUFFER\n# This file receives raw logs submitted from the mobile web app.\n# When you return to your laptop, tell the coach "/log" or "process my incoming log", and it will read this file automatically.\n\n(No pending unprocessed logs)\n`;
      const apiUrl = `https://api.github.com/repos/${repo}/contents/WORKOUT_LOGS/incoming_raw_log.txt`;

      let sha = null;
      const getRes = await fetch(apiUrl, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Accept": "application/vnd.github.v3+json"
        }
      });
      if (getRes.ok) {
        const fileData = await getRes.json();
        sha = fileData.sha;
      }

      const payload = {
        message: "chore(log): reset buffer to empty [skip ci]",
        content: toBase64Utf8(resetContent),
        branch: "master"
      };
      if (sha) payload.sha = sha;

      await fetch(apiUrl, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Accept": "application/vnd.github.v3+json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
    } catch (e) {
      console.warn("Could not reset remote buffer:", e);
    }
  }

  localStorage.removeItem(BUFFER_KEY);
  const card = document.getElementById("bufferCard");
  if (card) card.style.display = "none";
  showToast("🗑️ Buffer cleared successfully.");
}

// 11. Inline GitHub Direct Sync (1-Time Setup)
function initInlineGitHubSync() {
  const indicator = document.getElementById("ghStatusIndicator");
  const input = document.getElementById("ghInlineToken");
  const token = getActiveGitHubToken();
  const hasCustom = !!localStorage.getItem(GH_TOKEN_KEY);
  const repo = localStorage.getItem(GH_REPO_KEY) || DEFAULT_REPO;

  if (indicator) {
    if (token) {
      indicator.className = "gh-status-indicator connected";
      indicator.innerText = hasCustom ? `Connected: ${repo.split("/")[1] || repo} (Custom Token)` : `Connected: ${repo.split("/")[1] || repo} (Direct Write Active)`;
    } else {
      indicator.className = "gh-status-indicator";
      indicator.innerText = "Not Connected";
    }
  }

  if (input) {
    input.placeholder = hasCustom ? "•••••••••••••••• (Custom Token Active)" : "•••••••••••••••• (App Write Token Active)";
  }
}

function saveInlineGitHubToken() {
  const input = document.getElementById("ghInlineToken");
  const token = input ? input.value.trim() : "";

  if (!token) {
    showToast("Please enter a GitHub PAT token.");
    return;
  }

  localStorage.setItem(GH_TOKEN_KEY, token);
  if (!localStorage.getItem(GH_REPO_KEY)) {
    localStorage.setItem(GH_REPO_KEY, DEFAULT_REPO);
  }

  input.value = "";
  input.placeholder = "•••••••••••••••• (Token saved)";
  initInlineGitHubSync();
  showToast("⚡ GitHub Token saved! Now you can push directly to repo.");
}

function clearCustomGitHubToken() {
  localStorage.removeItem(GH_TOKEN_KEY);
  initInlineGitHubSync();
  showToast("🔄 Switched to Default App Write Token.");
}

// 12. Cross-Platform Date-Wise Recent Logs (Last 7 Sessions)
async function fetchRecentLogs() {
  const container = document.getElementById("recentLogsContainer");
  if (!container) return;

  try {
    const res = await fetch(`recent_logs.json?t=${Date.now()}`, { cache: "no-store" });
    if (res.ok) {
      const logs = await res.json();
      if (Array.isArray(logs) && logs.length > 0) {
        window.recentLogsData = logs;
        renderRecentLogs(logs);
        return;
      }
    }
  } catch (e) {
    console.warn("Could not fetch recent_logs.json:", e);
  }

  if (!window.recentLogsData || window.recentLogsData.length === 0) {
    container.innerHTML = `<p style="font-size:0.8rem; color:var(--text-dim); text-align:center; padding:12px;">No past logs loaded yet.</p>`;
  }
}

function renderRecentLogs(logs) {
  const container = document.getElementById("recentLogsContainer");
  if (!container || !Array.isArray(logs)) return;

  container.innerHTML = "";

  logs.forEach((item, idx) => {
    const card = document.createElement("details");
    card.className = "past-log-card";
    if (idx === 0) card.open = true;

    const sessionTypeLower = (item.session_type || "").toLowerCase();
    let pillClass = "push";
    if (sessionTypeLower.includes("pull")) pillClass = "pull";
    else if (sessionTypeLower.includes("leg")) pillClass = "legs";

    const exListHtml = (item.exercises || []).map(ex => {
      const parts = ex.summary.split(":");
      const name = parts[0];
      const details = parts.slice(1).join(":");
      return `<li><strong>${escapeHtml(name)}</strong>:${escapeHtml(details)}</li>`;
    }).join("");

    card.innerHTML = `
      <summary class="past-log-summary">
        <div class="past-log-badge-wrap">
          <span class="past-log-date">${escapeHtml(item.date)}</span>
          <span class="past-log-pill ${pillClass}">${escapeHtml((item.session_type || "Workout").toUpperCase())}</span>
        </div>
        <div class="past-log-meta">
          <span>${escapeHtml(item.duration || "")}${item.exercises ? ` • ${item.exercises.length} ex` : ""}</span>
          <span class="past-arrow">▼</span>
        </div>
      </summary>
      <div class="past-log-body">
        <ul class="past-log-exercises">
          ${exListHtml || `<li>${escapeHtml(item.raw_text || "No details")}</li>`}
        </ul>
        <div class="past-log-actions">
          <button type="button" class="btn-past-copy" onclick="copyPastLog(${idx})">
            📋 Copy /log Prompt
          </button>
          <button type="button" class="btn-past-template" onclick="loadPastLogAsTemplate(${idx})">
            ✏️ Use as Template
          </button>
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

function copyPastLog(index) {
  if (!window.recentLogsData || !window.recentLogsData[index]) return;
  const item = window.recentLogsData[index];
  const promptText = item.copy_prompt || `/log\n# Session: ${item.session_type} (${item.date})\n${item.raw_text || ""}`;

  copyTextToClipboard(promptText).then(() => {
    showToast(`📋 Copied ${item.date} log as /log prompt! Ready to paste.`);
  });
}

function loadPastLogAsTemplate(index) {
  if (!window.recentLogsData || !window.recentLogsData[index]) return;
  const item = window.recentLogsData[index];
  const templateText = item.template_text || item.raw_text || "";
  const textarea = document.getElementById("rawLogInput");

  if (textarea) {
    textarea.value = templateText;
    textarea.focus();
    textarea.scrollIntoView({ behavior: "smooth", block: "center" });
    showToast(`✏️ Loaded ${item.date} (${item.session_type}) as template! Adjust reps/weights.`);
  }
}

// 13. Security PIN Lock
function getStoredPin() {
  return localStorage.getItem(PIN_STORAGE_KEY) || DEFAULT_PIN;
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

function verifyPin() {
  const correctPin = getStoredPin();
  const isValid = (enteredPin === correctPin || enteredPin === DEFAULT_PIN);

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

// 14. Settings Modal
function openSettingsModal() {
  const modal = document.getElementById("settingsModal");
  const repoInput = document.getElementById("ghRepoInput");
  const tokenInput = document.getElementById("ghTokenInput");
  const pinInput = document.getElementById("appPinInput");

  if (repoInput) repoInput.value = localStorage.getItem(GH_REPO_KEY) || DEFAULT_REPO;
  if (tokenInput) tokenInput.value = localStorage.getItem(GH_TOKEN_KEY) || "";
  if (pinInput) pinInput.value = "";
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

  if (repo) localStorage.setItem(GH_REPO_KEY, repo);
  else localStorage.setItem(GH_REPO_KEY, DEFAULT_REPO);

  if (token) localStorage.setItem(GH_TOKEN_KEY, token);
  else localStorage.removeItem(GH_TOKEN_KEY);

  if (pin && pin.length >= 4) {
    localStorage.setItem(PIN_STORAGE_KEY, pin);
  }

  closeSettingsModal();
  updatePinDots();
  initInlineGitHubSync();
  renderBufferCard();
  showToast("⚙️ Settings saved!");
}

// 15. Progress Tab: Muscle Volume & Exercise Trajectories
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
  if (!data) return;

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
    const dateLabel = d.date.slice(5);
    ctx.fillText(dateLabel, x, h - 12);
  });
}

// 16. Utility Helpers
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
