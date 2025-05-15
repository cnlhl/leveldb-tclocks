import matplotlib.pyplot as plt
import pandas as pd
import io
import re

# --- 将你的 C 程序输出粘贴在这里 ---
# --- Paste your C program output here ---
benchmark_output_data = """
Profiling pthread_mutex with 1 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 1 threads (6.000 s runtime):
  Total Trylock Attempts: 255003915
  Total Trylock Successes: 255003915 (100.00%)
  Total Trylock Failures: 0 (0.00%)
  Blocking Locks after Trylock Fail: 0
  Approx. Avg Attempts/Window (24ms): 1019994
  Approx. Avg Successes/Window (24ms): 1019994
  Approx. Avg Failures/Window (24ms): 0
--------------------------------------------------
Profiling komb_mutex with 1 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 1 threads (6.000 s runtime):
  Total Trylock Attempts: 166294842
  Total Trylock Successes: 166294842 (100.00%)
  Total Trylock Failures: 0 (0.00%)
  Blocking Locks after Trylock Fail: 0
  Approx. Avg Attempts/Window (24ms): 665160
  Approx. Avg Successes/Window (24ms): 665160
  Approx. Avg Failures/Window (24ms): 0
--------------------------------------------------
Profiling pthread_mutex with 2 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 2 threads (6.000 s runtime):
  Total Trylock Attempts: 82193465
  Total Trylock Successes: 76596027 (93.19%)
  Total Trylock Failures: 5597438 (6.81%)
  Blocking Locks after Trylock Fail: 5597438
  Approx. Avg Attempts/Window (24ms): 328766
  Approx. Avg Successes/Window (24ms): 306377
  Approx. Avg Failures/Window (24ms): 22389
--------------------------------------------------
Profiling komb_mutex with 2 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 2 threads (6.000 s runtime):
  Total Trylock Attempts: 39384604
  Total Trylock Successes: 39384372 (100.00%)
  Total Trylock Failures: 232 (0.00%)
  Blocking Locks after Trylock Fail: 232
  Approx. Avg Attempts/Window (24ms): 157535
  Approx. Avg Successes/Window (24ms): 477534
  Approx. Avg Failures/Window (24ms): 0
--------------------------------------------------
Profiling pthread_mutex with 3 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 3 threads (6.000 s runtime):
  Total Trylock Attempts: 99680497
  Total Trylock Successes: 94590672 (94.89%)
  Total Trylock Failures: 5089825 (5.11%)
  Blocking Locks after Trylock Fail: 5089825
  Approx. Avg Attempts/Window (24ms): 398715
  Approx. Avg Successes/Window (24ms): 378356
  Approx. Avg Failures/Window (24ms): 24358
--------------------------------------------------
Profiling komb_mutex with 3 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 3 threads (6.000 s runtime):
  Total Trylock Attempts: 60433637
  Total Trylock Successes: 59526017 (98.50%)
  Total Trylock Failures: 907620 (1.50%)
  Blocking Locks after Trylock Fail: 907620
  Approx. Avg Attempts/Window (24ms): 241729
  Approx. Avg Successes/Window (24ms): 338099
  Approx. Avg Failures/Window (24ms): 3630
--------------------------------------------------
Profiling pthread_mutex with 4 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 4 threads (6.000 s runtime):
  Total Trylock Attempts: 84137879
  Total Trylock Successes: 74835820 (88.94%)
  Total Trylock Failures: 9302059 (11.06%)
  Blocking Locks after Trylock Fail: 9302059
  Approx. Avg Attempts/Window (24ms): 336544
  Approx. Avg Successes/Window (24ms): 299337
  Approx. Avg Failures/Window (24ms): 33207
--------------------------------------------------
Profiling komb_mutex with 4 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 4 threads (6.000 s runtime):
  Total Trylock Attempts: 83665011
  Total Trylock Successes: 83634596 (99.96%)
  Total Trylock Failures: 30415 (0.04%)
  Blocking Locks after Trylock Fail: 30415
  Approx. Avg Attempts/Window (24ms): 334652
  Approx. Avg Successes/Window (24ms): 284531
  Approx. Avg Failures/Window (24ms): 121
--------------------------------------------------
Profiling pthread_mutex with 6 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 6 threads (6.000 s runtime):
  Total Trylock Attempts: 59965280
  Total Trylock Successes: 49554179 (82.64%)
  Total Trylock Failures: 10411101 (17.36%)
  Blocking Locks after Trylock Fail: 10411101
  Approx. Avg Attempts/Window (24ms): 239856
  Approx. Avg Successes/Window (24ms): 198212
  Approx. Avg Failures/Window (24ms): 37643
--------------------------------------------------
Profiling komb_mutex with 6 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 6 threads (6.000 s runtime):
  Total Trylock Attempts: 40389326
  Total Trylock Successes: 35841099 (88.74%)
  Total Trylock Failures: 4548227 (11.26%)
  Blocking Locks after Trylock Fail: 4548227
  Approx. Avg Attempts/Window (24ms): 161554
  Approx. Avg Successes/Window (24ms): 203361
  Approx. Avg Failures/Window (24ms): 18192
--------------------------------------------------
Profiling pthread_mutex with 8 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 8 threads (6.000 s runtime):
  Total Trylock Attempts: 54142685
  Total Trylock Successes: 43881785 (81.05%)
  Total Trylock Failures: 10260900 (18.95%)
  Blocking Locks after Trylock Fail: 10260900
  Approx. Avg Attempts/Window (24ms): 216567
  Approx. Avg Successes/Window (24ms): 175524
  Approx. Avg Failures/Window (24ms): 39042
--------------------------------------------------
Profiling komb_mutex with 8 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 8 threads (6.000 s runtime):
  Total Trylock Attempts: 28084696
  Total Trylock Successes: 26886051 (95.73%)
  Total Trylock Failures: 1198645 (4.27%)
  Blocking Locks after Trylock Fail: 1198645
  Approx. Avg Attempts/Window (24ms): 112336
  Approx. Avg Successes/Window (24ms): 157542
  Approx. Avg Failures/Window (24ms): 4794
--------------------------------------------------
Profiling pthread_mutex with 12 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 12 threads (6.000 s runtime):
  Total Trylock Attempts: 49766407
  Total Trylock Successes: 41808402 (84.01%)
  Total Trylock Failures: 7958005 (15.99%)
  Blocking Locks after Trylock Fail: 7958005
  Approx. Avg Attempts/Window (24ms): 199063
  Approx. Avg Successes/Window (24ms): 167231
  Approx. Avg Failures/Window (24ms): 32831
--------------------------------------------------
Profiling komb_mutex with 12 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 12 threads (6.000 s runtime):
  Total Trylock Attempts: 32070545
  Total Trylock Successes: 31969338 (99.68%)
  Total Trylock Failures: 101207 (0.32%)
  Blocking Locks after Trylock Fail: 101207
  Approx. Avg Attempts/Window (24ms): 128279
  Approx. Avg Successes/Window (24ms): 127874
  Approx. Avg Failures/Window (24ms): 404
--------------------------------------------------
Profiling pthread_mutex with 16 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 16 threads (6.000 s runtime):
  Total Trylock Attempts: 42002474
  Total Trylock Successes: 35484761 (84.48%)
  Total Trylock Failures: 6517713 (15.52%)
  Blocking Locks after Trylock Fail: 6517713
  Approx. Avg Attempts/Window (24ms): 168008
  Approx. Avg Successes/Window (24ms): 141937
  Approx. Avg Failures/Window (24ms): 26070
--------------------------------------------------
Profiling komb_mutex with 16 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 16 threads (6.000 s runtime):
  Total Trylock Attempts: 37936840
  Total Trylock Successes: 37897956 (99.90%)
  Total Trylock Failures: 38884 (0.10%)
  Blocking Locks after Trylock Fail: 38884
  Approx. Avg Attempts/Window (24ms): 151743
  Approx. Avg Successes/Window (24ms): 151588
  Approx. Avg Failures/Window (24ms): 155
--------------------------------------------------
Profiling pthread_mutex with 20 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 20 threads (6.000 s runtime):
  Total Trylock Attempts: 41331070
  Total Trylock Successes: 35691040 (86.35%)
  Total Trylock Failures: 5640030 (13.65%)
  Blocking Locks after Trylock Fail: 5640030
  Approx. Avg Attempts/Window (24ms): 165322
  Approx. Avg Successes/Window (24ms): 142762
  Approx. Avg Failures/Window (24ms): 22559
--------------------------------------------------
Profiling komb_mutex with 20 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 20 threads (6.000 s runtime):
  Total Trylock Attempts: 20549445
  Total Trylock Successes: 19528854 (95.03%)
  Total Trylock Failures: 1020591 (4.97%)
  Blocking Locks after Trylock Fail: 1020591
  Approx. Avg Attempts/Window (24ms): 82196
  Approx. Avg Successes/Window (24ms): 78114
  Approx. Avg Failures/Window (24ms): 4082
--------------------------------------------------
Profiling pthread_mutex with 24 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 24 threads (6.000 s runtime):
  Total Trylock Attempts: 41276529
  Total Trylock Successes: 36382315 (88.14%)
  Total Trylock Failures: 4894214 (11.86%)
  Blocking Locks after Trylock Fail: 4894214
  Approx. Avg Attempts/Window (24ms): 165104
  Approx. Avg Successes/Window (24ms): 145527
  Approx. Avg Failures/Window (24ms): 19576
--------------------------------------------------
Profiling komb_mutex with 24 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 24 threads (6.000 s runtime):
  Total Trylock Attempts: 58676896
  Total Trylock Successes: 58412479 (99.55%)
  Total Trylock Failures: 264417 (0.45%)
  Blocking Locks after Trylock Fail: 264417
  Approx. Avg Attempts/Window (24ms): 234705
  Approx. Avg Successes/Window (24ms): 233647
  Approx. Avg Failures/Window (24ms): 1057
--------------------------------------------------
Profiling pthread_mutex with 28 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 28 threads (6.000 s runtime):
  Total Trylock Attempts: 43818735
  Total Trylock Successes: 38976576 (88.95%)
  Total Trylock Failures: 4842159 (11.05%)
  Blocking Locks after Trylock Fail: 4842159
  Approx. Avg Attempts/Window (24ms): 175272
  Approx. Avg Successes/Window (24ms): 155903
  Approx. Avg Failures/Window (24ms): 19368
--------------------------------------------------
Profiling komb_mutex with 28 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 28 threads (6.000 s runtime):
  Total Trylock Attempts: 60607495
  Total Trylock Successes: 60603475 (99.99%)
  Total Trylock Failures: 4020 (0.01%)
  Blocking Locks after Trylock Fail: 4020
  Approx. Avg Attempts/Window (24ms): 242427
  Approx. Avg Successes/Window (24ms): 242411
  Approx. Avg Failures/Window (24ms): 16
--------------------------------------------------
Profiling pthread_mutex with 32 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 32 threads (6.000 s runtime):
  Total Trylock Attempts: 46516114
  Total Trylock Successes: 41516268 (89.25%)
  Total Trylock Failures: 4999846 (10.75%)
  Blocking Locks after Trylock Fail: 4999846
  Approx. Avg Attempts/Window (24ms): 186062
  Approx. Avg Successes/Window (24ms): 166063
  Approx. Avg Failures/Window (24ms): 19999
--------------------------------------------------
Profiling komb_mutex with 32 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 32 threads (6.000 s runtime):
  Total Trylock Attempts: 42734814
  Total Trylock Successes: 42576375 (99.63%)
  Total Trylock Failures: 158439 (0.37%)
  Blocking Locks after Trylock Fail: 158439
  Approx. Avg Attempts/Window (24ms): 170937
  Approx. Avg Successes/Window (24ms): 170303
  Approx. Avg Failures/Window (24ms): 633
--------------------------------------------------
Profiling pthread_mutex with 40 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 40 threads (6.000 s runtime):
  Total Trylock Attempts: 49964405
  Total Trylock Successes: 45015325 (90.09%)
  Total Trylock Failures: 4949080 (9.91%)
  Blocking Locks after Trylock Fail: 4949080
  Approx. Avg Attempts/Window (24ms): 199855
  Approx. Avg Successes/Window (24ms): 180059
  Approx. Avg Failures/Window (24ms): 19796
--------------------------------------------------
Profiling komb_mutex with 40 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 40 threads (6.000 s runtime):
  Total Trylock Attempts: 42480096
  Total Trylock Successes: 42454242 (99.94%)
  Total Trylock Failures: 25854 (0.06%)
  Blocking Locks after Trylock Fail: 25854
  Approx. Avg Attempts/Window (24ms): 169918
  Approx. Avg Successes/Window (24ms): 169815
  Approx. Avg Failures/Window (24ms): 103
--------------------------------------------------
Profiling pthread_mutex with 56 threads for 6000 ms (window: 24 ms)...
Results for pthread_mutex with 56 threads (6.000 s runtime):
  Total Trylock Attempts: 52928849
  Total Trylock Successes: 47949552 (90.59%)
  Total Trylock Failures: 4979297 (9.41%)
  Blocking Locks after Trylock Fail: 4979297
  Approx. Avg Attempts/Window (24ms): 211713
  Approx. Avg Successes/Window (24ms): 191796
  Approx. Avg Failures/Window (24ms): 19916
--------------------------------------------------
Profiling komb_mutex with 56 threads for 6000 ms (window: 24 ms)...
Results for komb_mutex with 56 threads (6.000 s runtime):
  Total Trylock Attempts: 38987238
  Total Trylock Successes: 38957430 (99.92%)
  Total Trylock Failures: 29808 (0.08%)
  Blocking Locks after Trylock Fail: 29808
  Approx. Avg Attempts/Window (24ms): 155947
  Approx. Avg Successes/Window (24ms): 155828
  Approx. Avg Failures/Window (24ms): 119
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
plt.rcParams.update({'font.size': 16})
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
            axs[0].text(row['threads'], row['avg_failures_per_window'], f" {int(row['avg_failures_per_window'])}", va='center', ha='left',  color='darkred')
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
            axs[1].text(row['threads'], row['avg_successes_per_window'], f" {int(row['avg_successes_per_window'])}", va='center', ha='right',color='darkgreen')
else:
    axs[1].text(0.5, 0.5, 'No success data for komb_mutex or data missing', ha='center', va='center')
    axs[1].set_title('komb_mutex: Trylock Successes vs. Thread Count')


axs[1].set_xlabel('Number of Concurrent Threads')
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