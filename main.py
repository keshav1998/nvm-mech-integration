#!/usr/bin/env python3
import os
import subprocess
import json
import sys
import logging

logger = logging.getLogger("NCLI LOGGER")

def run_command(cmd, cwd=None):
    """Run a shell command and return its stdout; exit on error."""
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        logger.error("Error executing command:")
        logger.error(result.stderr)
        logger.error(result.stdout)
        sys.exit(result.returncode)
    return result.stdout.strip()

def main():
    # === 1. Set up environment variables for the Base network ===
    GNOSIS_CONTRACTS_URL = os.environ.get("GNOSIS_CONTRACTS_URL")
    BASE_CONTRACT_URL = os.environ.get("BASE_CONTRACT_URL")

    # === 3. Download ABI artifacts ===
    run_command(["curl", "-v", "-L", "-o", "artifacts_base.tar.gz",
                 GNOSIS_CONTRACTS_URL])
    run_command(["curl", "-v", "-L", "-o", "artifacts_gnosis.tar.gz",
                 BASE_CONTRACT_URL])

    # === 4. Create artifacts folder and extract archives ===
    if not os.path.exists("artifacts"):
        os.mkdir("artifacts")
    run_command(["tar", "-xzvf", "../artifacts_base.tar.gz"], cwd="artifacts")
    run_command(["tar", "-xzvf", "../artifacts_gnosis.tar.gz"], cwd="artifacts")

    # === 5. Order the OLAS Plan via CLI ===
    plan_did = os.environ["PLAN_DID"]
    subscription_credits = os.environ["SUBSCRIPTION_CREDITS"]

    order_cmd = [
        "ncli", "nfts1155", "order",
        plan_did,
        "--amount", subscription_credits,
        "--json"
    ]
    order_output = run_command(order_cmd)
    print("\nOrder command output (JSON):")
    print(order_output)

    try:
        order_json = json.loads(order_output)
        agreement_id = order_json.get("agreementId")
    except Exception as e:
        print("Error parsing JSON output from order command:", e)
        sys.exit(1)

    if not agreement_id:
        print("No agreementId found in order output!")
        sys.exit(1)

    print(f"\nAgreement ID: {agreement_id}")

    # === 6. Transfer (claim) the NFT credits to the subscriber ===
    # Replace the placeholder with the actual subscriber address.
    subscriber_address = "0xYourSubscriberAddress"
    transfer_cmd = [
        "ncli", "nfts1155", "transfer",
        agreement_id,
        "--buyerAccount", subscriber_address
    ]
    transfer_output = run_command(transfer_cmd)
    print("\nTransfer command output:")
    print(transfer_output)

    # === 7. Verify by displaying the NFT details ===
    show_cmd = ["ncli", "nfts1155", "show", plan_did]
    show_output = run_command(show_cmd)
    print("\nNFT details:")
    print(show_output)

if __name__ == "__main__":
    main()
