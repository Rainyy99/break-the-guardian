import { createClient } from "https://esm.sh/genlayer-js@latest";
import { studionet } from "https://esm.sh/genlayer-js@latest/chains";

const CONTRACT_ADDRESS = "0x6AD4FD30F266f43ecF95BC80514F50BE92e2AE1F";

const readClient = createClient({ chain: studionet });

const levelSelect = document.getElementById("level-select");
const promptInput = document.getElementById("prompt-input");
const attemptBtn = document.getElementById("attempt-btn");
const resultBox = document.getElementById("result-box");
const claimArea = document.getElementById("claim-area");
const walletInput = document.getElementById("wallet-input");
const claimBtn = document.getElementById("claim-btn");
const claimStatus = document.getElementById("claim-status");
const feedEl = document.getElementById("feed");

let lastAttemptId = null;
let lastToken = null;

attemptBtn.addEventListener("click", sendAttempt);
claimBtn.addEventListener("click", claimReward);

async function sendAttempt() {
  const level = parseInt(levelSelect.value, 10);
  const prompt = promptInput.value.trim();
  if (!prompt) return;

  attemptBtn.disabled = true;
  claimArea.style.display = "none";
  lastAttemptId = null;
  lastToken = null;
  showResult("pending", "Sending attempt... this can take 30-90 seconds while validators reach consensus.");

  try {
    const res = await fetch("/api/attempt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ challenge_level: level, prompt_text: prompt }),
    });
    const output = await res.json();

    if (!res.ok) {
      showResult("fail", `Error: ${output.error || "Unknown error"}`);
      return;
    }

    lastAttemptId = output.attempt_id;
    lastToken = output.token;

    if (output.leaked) {
      showResult("success", `Success! The Guardian leaked the phrase. (attempt #${output.attempt_id})`);
      claimArea.style.display = "block";
      claimStatus.textContent = "";
      claimBtn.disabled = false;
      claimBtn.textContent = "Claim Reward (0.01 GEN)";
    } else {
      showResult("fail", `The Guardian held firm. Try a different approach. (attempt #${output.attempt_id})`);
    }
  } catch (err) {
    showResult("fail", `Network error: ${err.message}`);
  } finally {
    attemptBtn.disabled = false;
    loadFeed();
  }
}

async function claimReward() {
  const wallet = walletInput.value.trim();
  if (!wallet) {
    claimStatus.textContent = "Please enter a wallet address.";
    return;
  }
  if (!lastAttemptId || !lastToken) {
    claimStatus.textContent = "No valid attempt to claim. Please send an attempt first.";
    return;
  }

  claimBtn.disabled = true;
  claimBtn.textContent = "Claiming...";
  claimStatus.textContent = "This can take 30-90 seconds...";

  try {
    const res = await fetch("/api/claim", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        attempt_id: lastAttemptId,
        wallet_address: wallet,
        token: lastToken,
      }),
    });
    const output = await res.json();

    if (!res.ok) {
      claimBtn.textContent = "Claim failed";
      claimStatus.textContent = output.error || "Unknown error";
      return;
    }

    claimBtn.textContent = "Claimed!";
    claimStatus.textContent = "Reward sent to your wallet.";
    loadFeed();
  } catch (err) {
    claimBtn.textContent = "Claim failed";
    claimStatus.textContent = `Network error: ${err.message}`;
  }
}

function showResult(kind, text) {
  resultBox.className = kind;
  resultBox.textContent = text;
}

async function loadFeed() {
  try {
    const raw = await readClient.readContract({
      address: CONTRACT_ADDRESS,
      functionName: "get_recent_attempts",
      args: [10],
    });
    const attempts = JSON.parse(raw);
    if (attempts.length === 0) {
      feedEl.textContent = "No attempts yet. Be the first!";
      return;
    }
    feedEl.innerHTML = attempts
      .map(
        (a) => `
        <div class="feed-item">
          <div class="prompt">"${escapeHtml(a.prompt)}"</div>
          <div class="status ${a.leaked ? "leaked" : "blocked"}">
            ${a.leaked ? "Leaked" : "Blocked"}${a.claimed ? " · claimed" : ""}
          </div>
        </div>`
      )
      .join("");
  } catch (err) {
    feedEl.textContent = "Could not load feed.";
    console.error(err);
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

loadFeed();
