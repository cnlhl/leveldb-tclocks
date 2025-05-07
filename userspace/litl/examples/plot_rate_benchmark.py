import matplotlib.pyplot as plt
import pandas as pd
import io
import re

# --- 将你的 C 程序输出粘贴在这里 ---
# --- Paste your C program output here ---
benchmark_output_data = """
Profiling pthread_mutex with 1 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 1 threads (5.000 s runtime):
  Total Trylock Attempts: 120313628
  Total Trylock Successes: 120313628 (100.00%)
  Total Trylock Failures: 0 (0.00%)
  Blocking Locks after Trylock Fail: 0
  Approx. Avg Attempts/Window (20ms): 481243
  Approx. Avg Successes/Window (20ms): 481243
  Approx. Avg Failures/Window (20ms): 0
--------------------------------------------------
Profiling komb_mutex with 1 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 1 threads (5.000 s runtime):
  Total Trylock Attempts: 132052022
  Total Trylock Successes: 132052022 (100.00%)
  Total Trylock Failures: 0 (0.00%)
  Blocking Locks after Trylock Fail: 0
  Approx. Avg Attempts/Window (20ms): 528196
  Approx. Avg Successes/Window (20ms): 528196
  Approx. Avg Failures/Window (20ms): 0
--------------------------------------------------
Profiling pthread_mutex with 2 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 2 threads (5.000 s runtime):
  Total Trylock Attempts: 56638751
  Total Trylock Successes: 54260122 (95.80%)
  Total Trylock Failures: 2378629 (4.20%)
  Blocking Locks after Trylock Fail: 2378629
  Approx. Avg Attempts/Window (20ms): 226549
  Approx. Avg Successes/Window (20ms): 217034
  Approx. Avg Failures/Window (20ms): 9514
--------------------------------------------------
Profiling komb_mutex with 2 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 2 threads (5.000 s runtime):
  Total Trylock Attempts: 46866476
  Total Trylock Successes: 44768795 (95.52%)
  Total Trylock Failures: 2097681 (4.48%)
  Blocking Locks after Trylock Fail: 2097681
  Approx. Avg Attempts/Window (20ms): 187462
  Approx. Avg Successes/Window (20ms): 179072
  Approx. Avg Failures/Window (20ms): 8390
--------------------------------------------------
Profiling pthread_mutex with 3 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 3 threads (5.000 s runtime):
  Total Trylock Attempts: 60245403
  Total Trylock Successes: 56521765 (93.82%)
  Total Trylock Failures: 3723638 (6.18%)
  Blocking Locks after Trylock Fail: 3723638
  Approx. Avg Attempts/Window (20ms): 240976
  Approx. Avg Successes/Window (20ms): 226082
  Approx. Avg Failures/Window (20ms): 14894
--------------------------------------------------
Profiling komb_mutex with 3 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 3 threads (5.000 s runtime):
  Total Trylock Attempts: 67368836
  Total Trylock Successes: 67362957 (99.99%)
  Total Trylock Failures: 5879 (0.01%)
  Blocking Locks after Trylock Fail: 5879
  Approx. Avg Attempts/Window (20ms): 269468
  Approx. Avg Successes/Window (20ms): 269445
  Approx. Avg Failures/Window (20ms): 23
--------------------------------------------------
Profiling pthread_mutex with 4 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 4 threads (5.000 s runtime):
  Total Trylock Attempts: 66892848
  Total Trylock Successes: 59721509 (89.28%)
  Total Trylock Failures: 7171339 (10.72%)
  Blocking Locks after Trylock Fail: 7171339
  Approx. Avg Attempts/Window (20ms): 267565
  Approx. Avg Successes/Window (20ms): 238880
  Approx. Avg Failures/Window (20ms): 28684
--------------------------------------------------
Profiling komb_mutex with 4 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 4 threads (5.000 s runtime):
  Total Trylock Attempts: 50836432
  Total Trylock Successes: 50820963 (99.97%)
  Total Trylock Failures: 15469 (0.03%)
  Blocking Locks after Trylock Fail: 15469
  Approx. Avg Attempts/Window (20ms): 203340
  Approx. Avg Successes/Window (20ms): 203278
  Approx. Avg Failures/Window (20ms): 61
--------------------------------------------------
Profiling pthread_mutex with 6 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 6 threads (5.000 s runtime):
  Total Trylock Attempts: 47663145
  Total Trylock Successes: 40294680 (84.54%)
  Total Trylock Failures: 7368465 (15.46%)
  Blocking Locks after Trylock Fail: 7368465
  Approx. Avg Attempts/Window (20ms): 190648
  Approx. Avg Successes/Window (20ms): 161175
  Approx. Avg Failures/Window (20ms): 29473
--------------------------------------------------
Profiling komb_mutex with 6 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 6 threads (5.000 s runtime):
  Total Trylock Attempts: 57209891
  Total Trylock Successes: 56975312 (99.59%)
  Total Trylock Failures: 234579 (0.41%)
  Blocking Locks after Trylock Fail: 234579
  Approx. Avg Attempts/Window (20ms): 228834
  Approx. Avg Successes/Window (20ms): 227896
  Approx. Avg Failures/Window (20ms): 938
--------------------------------------------------
Profiling pthread_mutex with 8 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 8 threads (5.000 s runtime):
  Total Trylock Attempts: 45170824
  Total Trylock Successes: 38533976 (85.31%)
  Total Trylock Failures: 6636848 (14.69%)
  Blocking Locks after Trylock Fail: 6636848
  Approx. Avg Attempts/Window (20ms): 180679
  Approx. Avg Successes/Window (20ms): 154132
  Approx. Avg Failures/Window (20ms): 26546
--------------------------------------------------
Profiling komb_mutex with 8 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 8 threads (5.000 s runtime):
  Total Trylock Attempts: 32729428
  Total Trylock Successes: 29838491 (91.17%)
  Total Trylock Failures: 2890937 (8.83%)
  Blocking Locks after Trylock Fail: 2890937
  Approx. Avg Attempts/Window (20ms): 130914
  Approx. Avg Successes/Window (20ms): 119350
  Approx. Avg Failures/Window (20ms): 11563
--------------------------------------------------
Profiling pthread_mutex with 12 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 12 threads (5.000 s runtime):
  Total Trylock Attempts: 46015842
  Total Trylock Successes: 39845796 (86.59%)
  Total Trylock Failures: 6170046 (13.41%)
  Blocking Locks after Trylock Fail: 6170046
  Approx. Avg Attempts/Window (20ms): 184061
  Approx. Avg Successes/Window (20ms): 159381
  Approx. Avg Failures/Window (20ms): 24679
--------------------------------------------------
Profiling komb_mutex with 12 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 12 threads (5.000 s runtime):
  Total Trylock Attempts: 26506222
  Total Trylock Successes: 23206777 (87.55%)
  Total Trylock Failures: 3299445 (12.45%)
  Blocking Locks after Trylock Fail: 3299445
  Approx. Avg Attempts/Window (20ms): 106022
  Approx. Avg Successes/Window (20ms): 92825
  Approx. Avg Failures/Window (20ms): 13197
--------------------------------------------------
Profiling pthread_mutex with 16 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 16 threads (5.000 s runtime):
  Total Trylock Attempts: 46074296
  Total Trylock Successes: 39732315 (86.24%)
  Total Trylock Failures: 6341981 (13.76%)
  Blocking Locks after Trylock Fail: 6341981
  Approx. Avg Attempts/Window (20ms): 184295
  Approx. Avg Successes/Window (20ms): 158927
  Approx. Avg Failures/Window (20ms): 25367
--------------------------------------------------
Profiling komb_mutex with 16 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 16 threads (5.000 s runtime):
  Total Trylock Attempts: 12916743
  Total Trylock Successes: 8439430 (65.34%)
  Total Trylock Failures: 4477313 (34.66%)
  Blocking Locks after Trylock Fail: 4477313
  Approx. Avg Attempts/Window (20ms): 51665
  Approx. Avg Successes/Window (20ms): 33756
  Approx. Avg Failures/Window (20ms): 17908
--------------------------------------------------
Profiling pthread_mutex with 20 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 20 threads (5.000 s runtime):
  Total Trylock Attempts: 45843579
  Total Trylock Successes: 40176073 (87.64%)
  Total Trylock Failures: 5667506 (12.36%)
  Blocking Locks after Trylock Fail: 5667506
  Approx. Avg Attempts/Window (20ms): 183372
  Approx. Avg Successes/Window (20ms): 160702
  Approx. Avg Failures/Window (20ms): 22669
--------------------------------------------------
Profiling komb_mutex with 20 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 20 threads (5.000 s runtime):
  Total Trylock Attempts: 8199077
  Total Trylock Successes: 3104269 (37.86%)
  Total Trylock Failures: 5094808 (62.14%)
  Blocking Locks after Trylock Fail: 5094808
  Approx. Avg Attempts/Window (20ms): 32795
  Approx. Avg Successes/Window (20ms): 12416
  Approx. Avg Failures/Window (20ms): 20378
--------------------------------------------------
Profiling pthread_mutex with 24 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 24 threads (5.000 s runtime):
  Total Trylock Attempts: 41321451
  Total Trylock Successes: 37071047 (89.71%)
  Total Trylock Failures: 4250404 (10.29%)
  Blocking Locks after Trylock Fail: 4250404
  Approx. Avg Attempts/Window (20ms): 165283
  Approx. Avg Successes/Window (20ms): 148282
  Approx. Avg Failures/Window (20ms): 17001
--------------------------------------------------
Profiling komb_mutex with 24 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 24 threads (5.000 s runtime):
  Total Trylock Attempts: 7282762
  Total Trylock Successes: 2078376 (28.54%)
  Total Trylock Failures: 5204386 (71.46%)
  Blocking Locks after Trylock Fail: 5204386
  Approx. Avg Attempts/Window (20ms): 29130
  Approx. Avg Successes/Window (20ms): 8313
  Approx. Avg Failures/Window (20ms): 20817
--------------------------------------------------
Profiling pthread_mutex with 28 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 28 threads (5.000 s runtime):
  Total Trylock Attempts: 47663782
  Total Trylock Successes: 40317741 (84.59%)
  Total Trylock Failures: 7346041 (15.41%)
  Blocking Locks after Trylock Fail: 7346041
  Approx. Avg Attempts/Window (20ms): 190652
  Approx. Avg Successes/Window (20ms): 161269
  Approx. Avg Failures/Window (20ms): 29383
--------------------------------------------------
Profiling komb_mutex with 28 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 28 threads (5.000 s runtime):
  Total Trylock Attempts: 6267118
  Total Trylock Successes: 1125831 (17.96%)
  Total Trylock Failures: 5141287 (82.04%)
  Blocking Locks after Trylock Fail: 5141287
  Approx. Avg Attempts/Window (20ms): 25067
  Approx. Avg Successes/Window (20ms): 4503
  Approx. Avg Failures/Window (20ms): 20564
--------------------------------------------------
Profiling pthread_mutex with 32 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 32 threads (5.000 s runtime):
  Total Trylock Attempts: 43895458
  Total Trylock Successes: 39811686 (90.70%)
  Total Trylock Failures: 4083772 (9.30%)
  Blocking Locks after Trylock Fail: 4083772
  Approx. Avg Attempts/Window (20ms): 175579
  Approx. Avg Successes/Window (20ms): 159244
  Approx. Avg Failures/Window (20ms): 16334
--------------------------------------------------
Profiling komb_mutex with 32 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 32 threads (5.000 s runtime):
  Total Trylock Attempts: 5626231
  Total Trylock Successes: 266897 (4.74%)
  Total Trylock Failures: 5359334 (95.26%)
  Blocking Locks after Trylock Fail: 5359334
  Approx. Avg Attempts/Window (20ms): 22504
  Approx. Avg Successes/Window (20ms): 1067
  Approx. Avg Failures/Window (20ms): 21437
--------------------------------------------------
Profiling pthread_mutex with 40 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 40 threads (5.000 s runtime):
  Total Trylock Attempts: 45224669
  Total Trylock Successes: 40128632 (88.73%)
  Total Trylock Failures: 5096037 (11.27%)
  Blocking Locks after Trylock Fail: 5096037
  Approx. Avg Attempts/Window (20ms): 180895
  Approx. Avg Successes/Window (20ms): 160511
  Approx. Avg Failures/Window (20ms): 20383
--------------------------------------------------
Profiling komb_mutex with 40 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 40 threads (5.000 s runtime):
  Total Trylock Attempts: 6414459
  Total Trylock Successes: 1335862 (20.83%)
  Total Trylock Failures: 5078597 (79.17%)
  Blocking Locks after Trylock Fail: 5078597
  Approx. Avg Attempts/Window (20ms): 25657
  Approx. Avg Successes/Window (20ms): 5343
  Approx. Avg Failures/Window (20ms): 20313
--------------------------------------------------
Profiling pthread_mutex with 56 threads for 5000 ms (window: 20 ms)...
Results for pthread_mutex with 56 threads (5.000 s runtime):
  Total Trylock Attempts: 43044501
  Total Trylock Successes: 38979652 (90.56%)
  Total Trylock Failures: 4064849 (9.44%)
  Blocking Locks after Trylock Fail: 4064849
  Approx. Avg Attempts/Window (20ms): 172174
  Approx. Avg Successes/Window (20ms): 155915
  Approx. Avg Failures/Window (20ms): 16259
--------------------------------------------------
Profiling komb_mutex with 56 threads for 5000 ms (window: 20 ms)...
Results for komb_mutex with 56 threads (5.000 s runtime):
  Total Trylock Attempts: 5775589
  Total Trylock Successes: 488431 (8.46%)
  Total Trylock Failures: 5287158 (91.54%)
  Blocking Locks after Trylock Fail: 5287158
  Approx. Avg Attempts/Window (20ms): 23101
  Approx. Avg Successes/Window (20ms): 1953
  Approx. Avg Failures/Window (20ms): 21148
--------------------------------------------------
""" # --- 结束粘贴区域 ---

def parse_benchmark_output(output_data):
    """
    Parses the benchmark output text to extract relevant statistics.
    """
    results = []
    current_lock_type = None
    current_threads = None
    current_window_ms_from_profiling = None # Window size from "Profiling..." line

    # Regex to capture main profiling line
    profile_line_re = re.compile(r"Profiling (.*?) with (\d+) threads.*?\(window: (\d+) ms\)")
    # Regex to capture "Approx. Avg Failures/Window"
    failures_re = re.compile(r"Approx\. Avg Failures/Window \((\d+)ms\): (\d+)")
    # Regex to capture "Approx. Avg Successes/Window"
    successes_re = re.compile(r"Approx\. Avg Successes/Window \((\d+)ms\): (\d+)")

    # Store data in a dictionary to allow updating successes for an existing entry
    # Key: (lock_type, threads)
    # Value: dictionary of stats
    parsed_data_dict = {}

    for line in output_data.splitlines():
        match_profile = profile_line_re.search(line)
        if match_profile:
            current_lock_type = match_profile.group(1).strip()
            current_threads = int(match_profile.group(2))
            current_window_ms_from_profiling = int(match_profile.group(3))
            
            # Initialize entry in dictionary
            if (current_lock_type, current_threads) not in parsed_data_dict:
                parsed_data_dict[(current_lock_type, current_threads)] = {
                    "lock_type": current_lock_type,
                    "threads": current_threads,
                    "window_ms": current_window_ms_from_profiling,
                    "avg_failures_per_window": None, # Initialize
                    "avg_successes_per_window": None # Initialize
                }
            continue

        if current_lock_type and current_threads and current_window_ms_from_profiling is not None:
            # Check for failures line
            match_failures = failures_re.search(line)
            if match_failures:
                window_ms_in_line = int(match_failures.group(1))
                if window_ms_in_line == current_window_ms_from_profiling:
                    parsed_data_dict[(current_lock_type, current_threads)]["avg_failures_per_window"] = int(match_failures.group(2))
                continue # Move to next line

            # Check for successes line
            match_successes = successes_re.search(line)
            if match_successes:
                window_ms_in_line = int(match_successes.group(1))
                if window_ms_in_line == current_window_ms_from_profiling:
                    parsed_data_dict[(current_lock_type, current_threads)]["avg_successes_per_window"] = int(match_successes.group(2))
                # This typically marks the end of a block for relevant stats,
                # but we rely on the next profile_line_re to reset context.
                continue 

    # Convert dictionary values to a list for DataFrame creation
    results = list(parsed_data_dict.values())
    return pd.DataFrame(results)

# Parse the data
df = parse_benchmark_output(benchmark_output_data)

# Filter out rows where essential data might be missing (if any parsing issues)
df.dropna(subset=['lock_type', 'threads', 'window_ms'], inplace=True)


# Separate data for pthread and komb
df_pthread = df[df['lock_type'] == 'pthread_mutex'].copy()
df_komb = df[df['lock_type'] == 'komb_mutex'].copy()

# Ensure data is sorted by threads for plotting
df_pthread = df_pthread.sort_values(by='threads').reset_index(drop=True)
df_komb = df_komb.sort_values(by='threads').reset_index(drop=True)


# --- Plotting ---
plt.style.use('seaborn-v0_8-whitegrid') 
fig, axs = plt.subplots(2, 1, figsize=(14, 12), sharex=True) # Increased figure size

# Plot 1: pthread_mutex - Avg Failures per Window
if not df_pthread.empty and 'avg_failures_per_window' in df_pthread.columns and df_pthread['avg_failures_per_window'].notna().any():
    window_val_pthread = df_pthread["window_ms"].iloc[0] if not df_pthread["window_ms"].empty else "N/A"
    axs[0].plot(df_pthread['threads'], df_pthread['avg_failures_per_window'], marker='o', linestyle='-', color='red', label=f'pthread_mutex Avg Failures / Window')
    axs[0].set_ylabel(f'Avg Failures / {window_val_pthread}ms Window')
    axs[0].set_title(f'pthread_mutex: Trylock Failures vs. Thread Count (Window: {window_val_pthread}ms)')
    axs[0].legend()
    axs[0].grid(True)
    # Add text annotations for pthread data points
    for i, row in df_pthread.iterrows():
        if pd.notna(row['avg_failures_per_window']):
            axs[0].text(row['threads'], row['avg_failures_per_window'], f" {int(row['avg_failures_per_window'])}", va='center', ha='left', fontsize=9, color='darkred')
else:
    axs[0].text(0.5, 0.5, 'No failure data for pthread_mutex or data missing', ha='center', va='center')
    axs[0].set_title('pthread_mutex: Trylock Failures vs. Thread Count')


# Plot 2: komb_mutex - Avg Successes per Window
if not df_komb.empty and 'avg_successes_per_window' in df_komb.columns and df_komb['avg_successes_per_window'].notna().any():
    window_val_komb = df_komb["window_ms"].iloc[0] if not df_komb["window_ms"].empty else "N/A"
    axs[1].plot(df_komb['threads'], df_komb['avg_successes_per_window'], marker='s', linestyle='--', color='green', label=f'komb_mutex Avg Successes / Window')
    axs[1].set_ylabel(f'Avg Successes / {window_val_komb}ms Window')
    axs[1].set_title(f'komb_mutex: Trylock Successes vs. Thread Count (Window: {window_val_komb}ms)')
    axs[1].legend()
    axs[1].grid(True)
    # Add text annotations for komb data points
    for i, row in df_komb.iterrows():
         if pd.notna(row['avg_successes_per_window']):
            axs[1].text(row['threads'], row['avg_successes_per_window'], f" {int(row['avg_successes_per_window'])}", va='center', ha='right', fontsize=9, color='darkgreen')
else:
    axs[1].text(0.5, 0.5, 'No success data for komb_mutex or data missing', ha='center', va='center')
    axs[1].set_title('komb_mutex: Trylock Successes vs. Thread Count')


axs[1].set_xlabel('Number of Concurrent Threads')
fig.suptitle('Trylock Behavior Analysis for Lock Switching Thresholds', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96]) 
plt.show()
fig.savefig("trylock_analysis.png", dpi=300, bbox_inches='tight')

# --- Guidance for setting thresholds based on these plots ---
print("\n--- Parsed DataFrame (pthread_mutex) ---")
if not df_pthread.empty:
    print(df_pthread[['threads', 'window_ms', 'avg_failures_per_window', 'avg_successes_per_window']].to_string())
else:
    print("No data parsed for pthread_mutex.")

print("\n--- Parsed DataFrame (komb_mutex) ---")
if not df_komb.empty:
    print(df_komb[['threads', 'window_ms', 'avg_failures_per_window', 'avg_successes_per_window']].to_string())
else:
    print("No data parsed for komb_mutex.")


print("\n--- Guidance for PTHREAD -> TCLOCK (based on pthread_mutex failures) ---")
if not df_pthread.empty and 'avg_failures_per_window' in df_pthread.columns and df_pthread['avg_failures_per_window'].notna().any():
    print("Consider the 'avg_failures_per_window' for pthread_mutex.")
    print(f"Example: If your kWindowNs is {window_val_pthread}ms, look at the corresponding 'avg_failures_per_window'.")
    print("If at 4 threads, this value is X, then X can be a starting point for kThreshold.")
    try:
        val_at_4_threads = df_pthread[df_pthread['threads'] == 4]['avg_failures_per_window'].iloc[0]
        if pd.notna(val_at_4_threads):
            print(f"At 4 threads, avg_failures_per_window for pthread_mutex (window: {window_val_pthread}ms) is: {int(val_at_4_threads)}")
    except IndexError:
        print("Data for 4 threads not found in pthread_mutex results.")
else:
    print("Not enough data to provide guidance for pthread_mutex failures.")


print("\n--- Guidance for TCLOCK -> PTHREAD (based on komb_mutex successes) ---")
if not df_komb.empty and 'avg_successes_per_window' in df_komb.columns and df_komb['avg_successes_per_window'].notna().any():
    print("Consider the 'avg_successes_per_window' for komb_mutex.")
    print(f"Example: If your kBackWindowNs is {window_val_komb}ms (or if using the same window as above), look at the 'avg_successes_per_window'.")
    print("If at 2 or 3 threads, this value is Y, then Y can be a starting point for kBackToThreadThreshold.")
    try:
        val_at_2_threads = df_komb[df_komb['threads'] == 2]['avg_successes_per_window'].iloc[0]
        if pd.notna(val_at_2_threads):
             print(f"At 2 threads, avg_successes_per_window for komb_mutex (window: {window_val_komb}ms) is: {int(val_at_2_threads)}")
    except IndexError:
        print("Data for 2 threads not found in komb_mutex results.")
else:
    print("Not enough data to provide guidance for komb_mutex successes.")