import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";
import { verifyToken } from "./_token.js";

const CONTRACT_ADDRESS = "0x6AD4FD30F266f43ecF95BC80514F50BE92e2AE1F";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { attempt_id, wallet_address, token } = req.body || {};

  if (typeof attempt_id !== "string" && typeof attempt_id !== "number") {
    return res.status(400).json({ error: "attempt_id is required" });
  }
  if (typeof wallet_address !== "string" || !wallet_address.trim()) {
    return res.status(400).json({ error: "wallet_address is required" });
  }

  if (!verifyToken(attempt_id, token)) {
    return res.status(403).json({ error: "Invalid or missing claim token" });
  }

  const privateKey = process.env.OPERATOR_PRIVATE_KEY;
  if (!privateKey) {
    console.error("OPERATOR_PRIVATE_KEY is not set");
    return res.status(500).json({ error: "Server misconfigured" });
  }

  try {
    const account = createAccount(privateKey);
    const client = createClient({ chain: studionet, account });

    const txHash = await client.writeContract({
      address: CONTRACT_ADDRESS,
      functionName: "claim_reward",
      args: [String(attempt_id), wallet_address],
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
        error: leaderReceipt?.error || "Claim failed on-chain",
      });
    }

    return res.status(200).json({ claimed: true });
  } catch (err) {
    console.error("claim_reward relay failed:", err);
    return res.status(502).json({ error: "Transaction failed, please try again" });
  }
}
