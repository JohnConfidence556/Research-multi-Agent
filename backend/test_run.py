from graph import app

inputs = {
    "task": "Perform a competitive analysis of Nvidia (NVDA)",
    "messages": [],
    "revision_number": 0 # Adding our safety counter
}

print("--- WAR ROOM ACTIVATED ---")

# We run the graph and store the final result in a variable
final_output = None
for output in app.stream(inputs, config={"configurable": {"thread_id": "1"}}):
    for key, value in output.items():
        print(f"\nNode '{key}' completed.")
        final_output = value # Keep track of the last update

print("\n--- FINAL SUMMARY ---")
if final_output and "strategy_report" in final_output:
    print(final_output["strategy_report"])
else:
    print("Report generated. (Check state keys if this is empty)")