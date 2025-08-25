import random
import pandas as pd

# ------------------------------
# JARGON LEXICON
# ------------------------------
JARGON_LEXICON = {
    # Medicine
    "arrhythmia": "irregular heartbeat", "stenosis": "narrowing",
    "tachycardia": "fast heart rate", "bradycardia": "slow heart rate",
    "myocardial infarction": "heart attack", "echocardiogram": "heart ultrasound",
    "hypertension": "high blood pressure", "hypotension": "low blood pressure",
    "catheterization": "tube procedure", "angioplasty": "artery widening surgery",
    "pacemaker": "heart rhythm device", "ischemia": "reduced blood flow",
    "edema": "swelling", "prognosis": "likely outcome",
    "acute": "severe", "chronic": "long-term",

    # Law
    "statute": "law", "indemnify": "protect against loss",
    "litigant": "person in a lawsuit", "injunction": "court order",
    "encroachment": "intrusion", "arbitration": "dispute resolution",
    "mediation": "negotiation", "stipulation": "condition",
    "liability": "legal responsibility", "plaintiff": "person suing",
    "defendant": "person being sued", "prohibits": "forbids",
    "breached": "broke", "adjudicated": "judged",
    "rescinded": "canceled", "contested": "disputed",

    # Tech
    "virtualization": "creating a virtual version", "latency": "delay",
    "provisioning": "setting up", "scalability": "ability to handle more load",
    "API gateway": "API management tool", "containerization": "packaging software",
    "firewall": "security barrier", "load balancer": "traffic distributor",
    "microservice": "small independent service", "throughput": "processing rate",
    "observability": "system monitoring", "deployed": "launched",
    "orchestrated": "managed", "migrated": "moved",
    "authenticated": "verified", "cached": "stored temporarily",
    "ephemeral": "temporary", "serverless": "no managed server",
    "redundant": "has backups", "bandwidth": "data transfer capacity",
}

# ------------------------------
# VERBS + OUTCOMES
# ------------------------------
VERBS = [
    "diagnosed", "treated", "monitored", "prescribed", "revealed",
    "adjudicated", "rescinded", "contested", "orchestrated", "deployed",
    "implemented", "executed", "managed", "optimized"
]
OUTCOMES = [
    "recovery", "failure", "success", "resolution", "improvement",
    "growth", "decline", "efficiency", "performance", "stability"
]

# ------------------------------
# MADLIBS TEMPLATES
# ------------------------------
TEMPLATES = [
    "The patient's {jargon} was {verb} by the doctor.",
    "The {jargon} procedure was {verb} successfully.",
    "We {verb} the case due to {jargon}.",
    "The contract was {verb} because of {jargon}.",
    "The {jargon} resulted in a {outcome}.",
    "Engineers {verb} the system using {jargon}.",
    "The {jargon} improved overall {outcome}.",
    "The {jargon} is often {verb} in practice.",
    "Our team {verb} a {jargon} for better {outcome}.",
    "The {jargon} dispute was {verb} by the court."
]

# ------------------------------
# DATASET GENERATION
# ------------------------------
def generate_dataset(n_samples=1000, seed=42, test_ratio=0.2):
    random.seed(seed)
    jargon_terms = list(JARGON_LEXICON.keys())
    random.shuffle(jargon_terms)

    # Split jargon terms to reserve some for the test set
    split_idx = int(len(jargon_terms) * (1 - test_ratio))
    train_jargon = jargon_terms[:split_idx]
    test_jargon = jargon_terms[split_idx:]

    # Generate training data
    train_data = []
    num_train_samples = int(n_samples * (1 - test_ratio))
    for _ in range(num_train_samples):
        template = random.choice(TEMPLATES)
        jargon = random.choice(train_jargon)
        verb = random.choice(VERBS)
        outcome = random.choice(OUTCOMES)
        
        jargon_sentence = template.format(jargon=jargon, verb=verb, outcome=outcome)
        simple_sentence = template.format(jargon=JARGON_LEXICON[jargon], verb=verb, outcome=outcome)
        train_data.append({"Original": jargon_sentence, "Simplified": simple_sentence})

    # Generate testing data (with unseen jargon terms)
    test_data = []
    num_test_samples = int(n_samples * test_ratio)
    for _ in range(num_test_samples):
        template = random.choice(TEMPLATES)
        jargon = random.choice(test_jargon)
        verb = random.choice(VERBS)
        outcome = random.choice(OUTCOMES)

        jargon_sentence = template.format(jargon=jargon, verb=verb, outcome=outcome)
        simple_sentence = template.format(jargon=JARGON_LEXICON[jargon], verb=verb, outcome=outcome)
        test_data.append({"Original": jargon_sentence, "Simplified": simple_sentence})

    # Return the two separate, correctly constructed DataFrames
    return pd.DataFrame(train_data), pd.DataFrame(test_data)

# ------------------------------
# RUN + SAVE
# ------------------------------
# --- FIX ---
# The function returns two DataFrames, so we unpack them into two variables.
train_df, test_df = generate_dataset(n_samples=2000)

# --- FIX ---
# The random splitting (.sample() and .drop()) is removed because the function
# already created the train/test sets correctly, with holdout jargon for testing.

train_df.to_csv("train.csv", index=False)
test_df.to_csv("test.csv", index=False)

print("✅ Dataset generated!")
print("\n--- Training Set Head ---")
print(train_df.head())
print("\n--- Test Set Head ---")
print(test_df.head())
print(f"\nTraining set size: {len(train_df)} rows")
print(f"Test set size: {len(test_df)} rows")