# XPLOIT Vault System — Reverse Engineering Writeup

**Author:** Vedansh Tyagi

---

# 1. Initial Recon

## Goal

The objective was to analyze the provided binary `chal` and make it output:

```
VAULT SYSTEM CLEARED.
All authentication layers bypassed successfully.
```

---

# Step 1 — Inspecting the File

The first step was to determine the type of binary.

Command:

```bash
file chal
```

Output:

```
ELF 64-bit LSB executable, x86-64
```

This confirms the binary is a **64-bit Linux executable**.

### Screenshot

Include screenshot of:

```
file chal
```

---

# Step 2 — Checking Permissions

Command:

```bash
ls -l chal
```

Output:

```
-rwxrwxrwx 1 vedansh_tyagi vedansh_tyagi 17640 Mar 14 chal
```

This confirms the binary has execute permissions.

### Screenshot

Terminal output of `ls -l chal`.

---

# Step 3 — Running the Program

Running the binary:

```bash
./chal
```

Output:

```
Initializing XPLOIT Vault System...
[SYS] kernel handshake initialised.
Input Operator ID: XPLOIT_VAULT_SYSTEM_V2

[-] AUTHORIZATION: Level 0 Guest.
[-] Access to Omega Protocol denied.
```

From this output we can infer:

* The system performs an **authentication check**
* Unauthorized users are blocked from accessing the vault

### Screenshot

Full terminal output from running the binary.

---

# Step 4 — Listing Functions

To understand the structure of the binary we list symbols using:

```bash
objdump -t chal
```

Important functions discovered:

```
emit_system_diagnostics
check_vault_state
initialize_telemetry
verify_network_cert
init_secure_channel
scan_memory_integrity
load_crypto_module
compute_session_hash
destroy_secure_channel
omega_protocol_legacy
security_watchdog
user_authentication_module
unlock_vault_sequence
main
```

### Screenshot

Output of `objdump -t chal`.

---

# 2. Function Map

Below is the role of each function identified during reverse engineering.

---

# main()

The `main` function orchestrates the entire system workflow.

Execution flow:

```
emit_system_diagnostics
check_vault_state
initialize_telemetry
verify_network_cert
init_secure_channel
scan_memory_integrity
load_crypto_module
compute_session_hash
destroy_secure_channel
omega_protocol_legacy
security_watchdog
user_authentication_module
```

After authentication the program prints:

```
Terminating session...
```

Important observation:

**The program never calls `unlock_vault_sequence`, which is responsible for unlocking the vault.**

### Screenshot

Disassembly of `main`.

Command used:

```bash
objdump -d chal
```

---

# Supporting Functions

These functions simulate layers of system security.

---

## emit_system_diagnostics

Prints system initialization messages.

---

## check_vault_state

Verifies that the vault subsystem is initialized.

---

## initialize_telemetry

Simulates telemetry initialization.

---

## verify_network_cert

Pretends to validate network certificates.

---

## init_secure_channel

Simulates creation of a secure communication channel.

---

## scan_memory_integrity

Checks program memory integrity.

---

## load_crypto_module

Loads simulated cryptographic modules.

---

## compute_session_hash

Generates a session hash.

---

## destroy_secure_channel

Closes the secure channel after the session.

---

## omega_protocol_legacy

Legacy authentication protocol.

---

## security_watchdog

Monitors system security status.

---

## user_authentication_module

Handles user authentication.

When the authentication value is patched, it prints:

```
[+] AUTHORIZATION ACCEPTED: Level 999 Admin.
```

However, the program still terminates afterward.

### Screenshot

Terminal output showing **Admin authorization**.

---

# Critical Function — unlock_vault_sequence

This function performs the **final vault unlock procedure**.

It:

1. Computes a vault unlock byte
2. Prompts the user for an unlock code
3. Compares the input to the expected value

Relevant logic derived from disassembly:

```
expected = g_pid_seed ^ g_vault_byte ^ strlen(argv0)
```

Variables used:

| Variable     | Address      | Description            |
| ------------ | ------------ | ---------------------- |
| g_pid_seed   | 0x4028       | seed byte              |
| g_vault_byte | 0x4029       | vault byte             |
| argv0        | program name | used to compute length |

If the input matches the computed value, the program prints:

```
VAULT SYSTEM CLEARED.
All authentication layers bypassed successfully.
```

### Screenshot

Disassembly of `unlock_vault_sequence`.

---

# 3. Binary Modification

## Problem

Even when authentication succeeds, the program does not unlock the vault.

The reason:

`main()` never calls `unlock_vault_sequence`.

Instead it prints:

```
Terminating session...
```

Therefore execution must be redirected.

---

# Patch Applied

Original instruction in `main`:

```
call puts
```

This prints:

```
Terminating session...
```

We patched this instruction to instead call:

```
unlock_vault_sequence
```

Binary patch command:

```bash
printf '\xe8\x5f\xfe\xff\xff' | dd of=chal bs=1 seek=$((0x1b8e)) conv=notrunc
```

This changes the call target so execution jumps into the vault unlock routine.

### Screenshot

Terminal showing the patch command execution.

---

# 4. Unlock Code Calculation

Inside `unlock_vault_sequence`, the program calculates the unlock code using:

```
expected = g_pid_seed ^ g_vault_byte ^ strlen(argv0)
```

To retrieve the values stored in the binary:

```bash
xxd -s 0x4028 -l 2 chal
```

Output:

```
00004028: a1 00
```

Therefore:

```
g_pid_seed  = 0xA1
g_vault_byte = 0x00
```

The program name used to execute the binary was:

```
./chal
```

Length:

```
strlen("./chal") = 6
```

Calculation:

```
0xA1 ^ 0x00 ^ 0x06
= 0xA7
```

Convert to decimal:

```
0xA7 = 167
```

Therefore the unlock code is:

```
167
```

### Screenshot

Terminal showing:

```
xxd -s 0x4028 -l 2 chal
```

---

# 5. Final Output

Run the patched binary:

```bash
./chal
```

Enter the unlock code:

```
167
```

Final output:

```
VAULT SYSTEM CLEARED.
All authentication layers bypassed successfully.
```

### Screenshot

Full terminal output showing the successful vault unlock.

---

# Screenshots Checklist

Include screenshots for the following:

1. `file chal`
2. `ls -l chal`
3. First execution of the binary
4. `objdump -t chal`
5. Disassembly of `main`
6. Disassembly of `unlock_vault_sequence`
7. Hex dump showing seed values (`xxd`)
8. Patch command using `dd`
9. Final successful run showing:

```
VAULT SYSTEM CLEARED
```

---

# Conclusion

The XPLOIT Vault System binary contains multiple simulated security layers. However, the final vault unlocking routine (`unlock_vault_sequence`) is never called during normal execution. By redirecting execution to this function and calculating the correct unlock code derived from internal binary constants, the vault can be successfully cleared.

This approach preserves the program’s intended logic while enabling the correct execution path required to unlock the system.
