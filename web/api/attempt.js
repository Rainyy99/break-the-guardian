import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";
import { makeToken } from "./_token.js";

const CONTRACT_ADDRESS = "0x6AD4FD30F266f43ecF95BC80514F50BE92e2AE1F";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { challenge_level, prompt_text } = req.body || {};

  if (typeof prompt_text !== "string" || !prompt_text.trim()) {
    return res.status(400).json({ error: "prompt_text is required" });
  }
  const level = parseInt(challenge_level, 10);
  if (![1, 2].includes(level)) {
    return res.status(400).json({ error: "challenge_level must be 1 or 2" });
  }

  const privateKey = process.env.OPERATOR_PRIVATE_KEY;
  if (!privateKey) {
    console.error("OPERATOR_PRIVATE_KEY is not set");
    return res.status(500).json({ error: "Server misconfigured" });
  }
  if (!process.env.SESSION_SECRET) {
    console.error("SESSION_SECRET is not set");
    return res.status(500).json({ error: "Server misconfigured" });
  }

  try {
    const account = createAccount(privateKey);
    const client = createClient({ chain: studionet, account });

    const txHash = await client.writeContract({
      address: CONTRACT_ADDRESS,
      functionName: "attempt_hack",
      args: [level, prompt_text],
      value: 0n,
    });

    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      retries: 60,
      interval: 3000,
    });

    const leaderReceipt = receipt.consensus_data?.leader_receipt?.find(
      (r) => r.mode === "leader"
    );
    if (!leaderReceipt || leaderReceipt.error) {
      return res.status(502).json({
        error: leaderReceipt?.error || "No leader receipt found",
      });
    }

    console.log("leaderReceipt.result type:", typeof leaderReceipt.result);
    console.log("leaderReceipt.result value:", JSON.stringify(leaderReceipt.result));

    const raw = leaderReceipt.result;
    let output;
    if (typeof raw === "string") {
      output = JSON.parse(raw);
    } else if (raw && typeof raw === "object" && "payload" in raw) {
      output = typeof raw.payload === "string" ? JSON.parse(raw.payload) : raw.payload;
    } else {
      output = raw;
    }
    console.log("extracted output:", JSON.stringify(output));

    const token = makeToken(output.attempt_id);
    return res.status(200).json({ ...output, token });
  } catch (err) {
    console.error("attempt_hack relay failed:", err);
    return res.status(502).json({ error: "Transaction failed, please try again" });
  }
}
