import json
import random

def generate_synthetic_data(num_entries=500):
    data = []

    # Configuration for variety
    algorithms = ["AES-256", "AES-128", "ChaCha20", "RSA-2048", "DES", "Blowfish", "Twofish", "XOR"]
    
    # Text Templates to ensure variety in the AI Report
    templates = {
        "CRITICAL": {
            "threat": [
                "The simulation achieved a high-velocity encryption rate ({speed} files/sec). This suggests that your current disk monitoring tools would likely be bypassed.",
                "Extremely high encryption throughput ({speed} files/sec) indicates sophisticated malware or insider threat targeting bulk data.",
                "Massive write-speed anomaly detected ({speed} files/sec). This behavior is consistent with enterprise-grade ransomware strains.",
                "Critical file system IO spike detected. The encryption rate of {speed} files/sec signifies an automated, optimized attack script."
            ],
            "impact": [
                "At this speed, an entire workstation's user data would be inaccessible within 30 seconds.",
                "Complete system compromise possible within seconds, leading to total data loss and operational paralysis.",
                "Massive data compromise imminent; critical database files are at immediate risk of irreversible locking.",
                "Immediate operational failure expected. Cloud sync services may propagate encrypted versions before versioning can react."
            ],
            "mitigation": [
                "1. Immediate system isolation. 2. Deploy advanced endpoint detection and response (EDR) tools. 3. Conduct forensic analysis.",
                "1. Emergency network sever. 2. Snapshot rollback of VM instances. 3. Kill all processes signed by unknown publishers.",
                "1. Automated kill-switch activation. 2. Quarantine host from Active Directory. 3. Initiate disaster recovery protocol.",
                "1. Block outbound SMB traffic. 2. Dump RAM for key retrieval analysis. 3. Force shutdown of affected endpoints."
            ]
        },
        "HIGH": {
            "threat": [
                "Moderate to high encryption velocity detected ({speed} files/sec). Standard antivirus might detect this, but rapid response is crucial.",
                "Rapid encryption detected ({speed} files/sec). Could indicate ransomware activity attempting to stay under heuristic radar.",
                "Sustained file modification rate of {speed} files/sec detected. This exceeds normal user behavior significantly.",
                "Heuristic match for crypto-locking process. Speed ({speed} files/sec) suggests a single-threaded attack process."
            ],
            "impact": [
                "Partial data encryption could occur before intervention, affecting productivity.",
                "Significant data at risk within minutes, potential for widespread encryption of user directories.",
                "Departmental share drives could be compromised if the host has write access.",
                "User profile corruption likely. Recent work files will be lost without immediate backups."
            ],
            "mitigation": [
                "1. Deploy real-time file integrity monitoring. 2. Implement automated backup triggers on suspicious activity.",
                "1. Activate incident response plan. 2. Isolate affected systems. 3. Check for backup integrity.",
                "1. Suspend user account temporarily. 2. Scan memory for injected code. 3. Verify Volume Shadow Copy status.",
                "1. Terminate parent process tree. 2. Review firewall logs for C2 communication. 3. Reset user credentials."
            ]
        },
        "MEDIUM": {
            "threat": [
                "Slow encryption rate ({speed} files/sec) suggests opportunistic attack or background process masquerading as legit software.",
                "Unusual file modification pattern detected. Speed ({speed} files/sec) is borderline malicious/benign.",
                "Steady but slow encryption ({speed} files/sec). Likely an attempt to evade 'blast radius' detection tools.",
                "Anomalous file header changes detected at {speed} files/sec. May indicate a low-resource background miner or encryptor."
            ],
            "impact": [
                "Limited immediate impact, but cumulative effect could be significant over time.",
                "Potential for data loss if not addressed promptly; low risk of immediate catastrophic failure.",
                "Specific subfolders may be lost, but full disk encryption is unlikely at this speed.",
                "System performance degradation and slow data corruption."
            ],
            "mitigation": [
                "1. Monitor for unusual file access patterns. 2. Review access logs for unauthorized users.",
                "1. Investigate source of encryption. 2. Implement temporary access restrictions.",
                "1. Run full anti-malware scan. 2. Check scheduled tasks for unknown scripts.",
                "1. Increase logging verbosity. 2. Cross-reference file extensions with known ransomware list."
            ]
        },
        "LOW": {
            "threat": [
                "Very slow encryption activity ({speed} files/sec), likely test, benign operation, or compression tool.",
                "Extremely slow encryption ({speed} files/sec), likely not malicious or manual user file protection.",
                "Trace levels of file obfuscation ({speed} files/sec). Likely false positive or authorized security tool test.",
                "Negligible write speed on encrypted files ({speed} files/sec). Consistent with document password protection."
            ],
            "impact": [
                "Minimal disruption, easily contained.",
                "Negligible business impact.",
                "No operational risk detected.",
                "Zero downtime expected."
            ],
            "mitigation": [
                "1. Log the activity for review. 2. Verify user authorization.",
                "1. Monitor for changes in pattern. 2. Document the activity.",
                "1. No immediate action required. 2. Whitelist process if verified.",
                "1. Close alert as False Positive after user verification."
            ]
        }
    }

    for _ in range(num_entries):
        # 1. Generate Input Data
        time_sec = random.randint(5, 45)
        
        # Determine scenario based on probability
        rand_val = random.random()
        if rand_val < 0.2:
            severity = "LOW"
            speed = round(random.uniform(0.1, 4.0), 1)
            algo = random.choice(["XOR", "DES", "RSA-2048", "RC4"])
        elif rand_val < 0.5:
            severity = "MEDIUM"
            speed = round(random.uniform(4.1, 15.0), 1)
            algo = random.choice(["DES", "AES-128", "Blowfish"])
        elif rand_val < 0.8:
            severity = "HIGH"
            speed = round(random.uniform(15.1, 45.0), 1)
            algo = random.choice(["AES-128", "AES-256", "ChaCha20"])
        else:
            severity = "CRITICAL"
            speed = round(random.uniform(45.1, 150.0), 1)
            algo = random.choice(["AES-256", "ChaCha20", "Twofish"])

        # Calculate files based on speed (Files = Speed * Time)
        files_encrypted = int(speed * time_sec)
        
        # Formulate Input String
        input_str = f"Encryption speed: {speed} files/sec, Files encrypted: {files_encrypted}, Time: {time_sec} seconds, Algorithm: {algo}"

        # 2. Generate Output Data using Templates
        t_threat = random.choice(templates[severity]["threat"]).format(speed=speed)
        t_impact = random.choice(templates[severity]["impact"])
        t_mitigation = random.choice(templates[severity]["mitigation"])

        output_str = f"[AI SECURITY REPORT: {severity}]\n\nThreat Analysis: {t_threat}\n\nBusiness Impact: {t_impact}\n\nMitigation: {t_mitigation}"

        data.append({
            "input": input_str,
            "output": output_str
        })

    return data

# Generate and save to file
dataset = generate_synthetic_data(500)
with open('synthetic_security_data.json', 'w') as f:
    json.dump(dataset, f, indent=2)

print("Generated 500 entries in synthetic_security_data.json")