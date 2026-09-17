# Security Notes

## Secrets & Key Management
- OPERATOR_PRIVATE_KEY is used server-side only (Vercel API routes) to relay
  transactions on behalf of users who do not connect their own wallet.
- This key is never prefixed with NEXT_PUBLIC_ — doing so would bundle it
  into client-side JavaScript, making it readable by anyone via browser DevTools.
- .env is git-ignored; only .env.example (a template with no real values) is
  committed. Verified via git check-ignore -v .env.
- This project targets GenLayer testnet (Studio / Bradbury) only. The operator
  wallet should never hold real/mainnet funds.

## Honeypot-Specific Design Notes
- **Confirmed (docs.genlayer.com/developers/intelligent-contracts/storage +
  the gen_getContractState RPC method): GenLayer contract storage is public
  on-chain, readable by anyone regardless of whether a @gl.public.view
  method exposes it.** This rules out storing any literal secret value in
  contract storage (e.g. via gl.random()) — it would be trivially
  extractable by reading raw state, defeating the honeypot.
- Design response: the Guardian protects a *forbidden behavior*, not a
  *secret value*. The LLM is instructed to never emit a specific phrase
  (e.g. "ACCESS GRANTED") regardless of user input. There is no secret
  data to leak, so the public-storage constraint no longer applies.
- Leak/win detection is done deterministically (forbidden-phrase search
  in the LLM's response), not by asking the LLM to self-report whether it
  complied — a manipulated LLM could lie about it, but can't hide the phrase
  itself if it actually printed it.

## Rate Limiting
- Because the operator wallet pays gas for every attempt (users never sign),
  the backend enforces MAX_ATTEMPTS_PER_IP_PER_HOUR and
  MAX_TOTAL_ATTEMPTS_PER_DAY before relaying to chain, to bound cost and
  prevent automated spam from draining the operator wallet.
